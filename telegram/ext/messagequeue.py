#!/usr/bin/env python
#
# Module author:
# Tymofii A. Khodniev (thodnev) <thodnev@mail.ru>
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/]
"""A throughput-limiting message processor for Telegram bots."""

import functools
import time
import threading
import queue as q

from typing import Callable, Any, TYPE_CHECKING, List, NoReturn, ClassVar, Dict

from telegram.utils.promise import Promise

if TYPE_CHECKING:
    from telegram import Bot

# We need to count < 1s intervals, so the most accurate timer is needed
curtime = time.perf_counter


class DelayQueueError(RuntimeError):
    """Indicates processing errors."""

    pass


class DelayQueue(threading.Thread):
    """
    Processes callbacks from queue with specified throughput limits. Creates a separate thread to
    process callbacks with delays.

    Attributes:
        burst_limit (:obj:`int`): Number of maximum callbacks to process per time-window.
        time_limit (:obj:`int`): Defines width of time-window used when each processing limit is
            calculated.
        exc_route (:obj:`callable`): A callable, accepting 1 positional argument; used to route
            exceptions from processor thread to main thread;
        name (:obj:`str`): Thread's name.

    Args:
        queue (:obj:`Queue`, optional): Used to pass callbacks to thread. Creates ``Queue``
            implicitly if not provided.
        burst_limit (:obj:`int`, optional): Number of maximum callbacks to process per time-window
            defined by :attr:`time_limit_ms`. Defaults to 30.
        time_limit_ms (:obj:`int`, optional): Defines width of time-window used when each
            processing limit is calculated. Defaults to 1000.
        exc_route (:obj:`callable`, optional): A callable, accepting 1 positional argument; used to
            route exceptions from processor thread to main thread; is called on `Exception`
            subclass exceptions. If not provided, exceptions are routed through dummy handler,
            which re-raises them.
        autostart (:obj:`bool`, optional): If :obj:`True`, processor is started immediately after
            object's creation; if :obj:`False`, should be started manually by `start` method.
            Defaults to :obj:`True`.
        name (:obj:`str`, optional): Thread's name. Defaults to ``'DelayQueue-N'``, where N is
            sequential number of object created.

    """

    _instcnt = 0  # instance counter

    def __init__(
        self,
        queue: q.Queue = None,
        burst_limit: int = 30,
        time_limit_ms: int = 1000,
        exc_route: Callable[[Exception], None] = None,
        autostart: bool = True,
        name: str = None,
    ):
        self._queue = queue if queue is not None else q.Queue()
        self.burst_limit = burst_limit
        self.time_limit = time_limit_ms / 1000
        self.exc_route = exc_route if exc_route is not None else self._default_exception_handler
        self.__exit_req = False  # flag to gently exit thread
        self.__class__._instcnt += 1
        if name is None:
            name = '{}-{}'.format(self.__class__.__name__, self.__class__._instcnt)
        super().__init__(name=name)
        self.daemon = False
        if autostart:  # immediately start processing
            super().start()

    def run(self) -> None:
        """
        Do not use the method except for unthreaded testing purposes, the method normally is
        automatically called by autostart argument.

        """

        times: List[float] = []  # used to store each callable processing time
        while True:
            promise = self._queue.get()
            if self.__exit_req:
                return  # shutdown thread
            # delay routine
            now = time.perf_counter()
            t_delta = now - self.time_limit  # calculate early to improve perf.
            if times and t_delta > times[-1]:
                # if last call was before the limit time-window
                # used to impr. perf. in long-interval calls case
                times = [now]
            else:
                # collect last in current limit time-window
                times = [t for t in times if t >= t_delta]
                times.append(now)
            if len(times) >= self.burst_limit:  # if throughput limit was hit
                time.sleep(times[1] - t_delta)
            # finally process one
            promise.run()
            if promise.exception:
                self.exc_route(promise.exception)  # re-route any exceptions

    def stop(self, timeout: float = None) -> None:
        """Used to gently stop processor and shutdown its thread.

        Args:
            timeout (:obj:`float`): Indicates maximum time to wait for processor to stop and its
                thread to exit. If timeout exceeds and processor has not stopped, method silently
                returns. :attr:`is_alive` could be used afterwards to check the actual status.
                ``timeout`` set to :obj:`None`, blocks until processor is shut down.
                Defaults to :obj:`None`.

        """

        self.__exit_req = True  # gently request
        self._queue.put(None)  # put something to unfreeze if frozen
        super().join(timeout=timeout)

    @staticmethod
    def _default_exception_handler(exc: Exception) -> NoReturn:
        """
        Dummy exception handler which re-raises exception in thread. Could be possibly overwritten
        by subclasses.

        """

        raise exc

    def process(self, func: Callable, args: Any, kwargs: Any) -> Promise:
        """Used to process callbacks in throughput-limiting thread through queue.

        Args:
            func (:obj:`callable`): The actual function (or any callable) that is processed through
                queue.
            *args (:obj:`list`): Variable-length `func` arguments.
            **kwargs (:obj:`dict`): Arbitrary keyword-arguments to `func`.

        """

        if not self.is_alive() or self.__exit_req:
            raise DelayQueueError('Could not process callback in stopped thread')
        promise = Promise(func, args, kwargs)
        self._queue.put(promise)
        return promise


# The most straightforward way to implement this is to use 2 sequential delay
# queues, like on classic delay chain schematics in electronics.
# So, message path is:
# msg --> group delay if group msg, else no delay --> normal msg delay --> out
# This way OS threading scheduler cares of timings accuracy.
# (see time.time, time.clock, time.perf_counter, time.sleep @ docs.python.org)
class MessageQueue:
    """
    Implements callback processing with proper delays to avoid hitting Telegram's message limits.
    Contains two ``DelayQueue``, for group and for all messages, interconnected in delay chain.
    Callables are processed through *group* ``DelayQueue``, then through *all* ``DelayQueue`` for
    group-type messages. For non-group messages, only the *all* ``DelayQueue`` is used.

    Attributes:
        running (:obj:`bool`): Whether this message queue has started it's delay queues or not.

    Args:
        all_burst_limit (:obj:`int`, optional): Number of maximum *all-type* callbacks to process
            per time-window defined by :attr:`all_time_limit_ms`. Defaults to 30.
        all_time_limit_ms (:obj:`int`, optional): Defines width of *all-type* time-window used when
            each processing limit is calculated. Defaults to 1000 ms.
        group_burst_limit (:obj:`int`, optional): Number of maximum *group-type* callbacks to
            process per time-window defined by :attr:`group_time_limit_ms`. Defaults to 20.
        group_time_limit_ms (:obj:`int`, optional): Defines width of *group-type* time-window used
            when each processing limit is calculated. Defaults to 60000 ms.
        exc_route (:obj:`callable`, optional): A callable, accepting one positional argument; used
            to route exceptions from processor threads to main thread; is called on ``Exception``
            subclass exceptions. If not provided, exceptions are routed through dummy handler,
            which re-raises them.
        autostart (:obj:`bool`, optional): If :obj:`True`, processors are started immediately after
            object's creation; if :obj:`False`, should be started manually by :attr:`start` method.
            Defaults to :obj:`True`.

    """

    def __init__(
        self,
        all_burst_limit: int = 30,
        all_time_limit_ms: int = 1000,
        group_burst_limit: int = 20,
        group_time_limit_ms: int = 60000,
        exc_route: Callable[[Exception], None] = None,
        autostart: bool = True,
    ):
        self.running = False
        self._delay_queues: Dict[str, DelayQueue] = {
            self.DEFAULT_QUEUE: DelayQueue(
                burst_limit=all_burst_limit,
                time_limit_ms=all_time_limit_ms,
                exc_route=exc_route,
                autostart=autostart,
            ),
            self.GROUP_QUEUE: DelayQueue(
                burst_limit=group_burst_limit,
                time_limit_ms=group_time_limit_ms,
                exc_route=exc_route,
                autostart=autostart,
            ),
        }

    def start(self) -> None:
        """Method is used to manually start the ``MessageQueue`` processing."""
        for dq in self._delay_queues.values():
            dq.start()

    def stop(self, timeout: float = None) -> None:
        for dq in self._delay_queues.values():
            dq.stop()

    stop.__doc__ = DelayQueue.stop.__doc__ or ''  # reuse docstring if any

    def process(self, func: Callable, delay_queue: str, *args: Any, **kwargs: Any) -> Promise:
        """
        Processes callables in throughput-limiting queues to avoid hitting limits (specified with
        :attr:`burst_limit` and :attr:`time_limit`.

        Returns:
            :class:`telegram.ext.Promise`.

        """
        return self._delay_queues[delay_queue].process(func, args, kwargs)

    DEFAULT_QUEUE: ClassVar[str] = 'default_delay_queue'
    """:obj:`str`: The default delay queue."""
    GROUP_QUEUE: ClassVar[str] = 'group_delay_queue'
    """:obj:`str`: The default delay queue for group requests."""


def queuedmessage(method: Callable) -> Callable:
    """A decorator to be used with :attr:`telegram.Bot` send* methods.

    Note:
        As it probably wouldn't be a good idea to make this decorator a property, it has been coded
        as decorator function, so it implies that first positional argument to wrapped MUST be
        self.

    The next object attributes are used by decorator:

    Attributes:
        self._is_messages_queued_default (:obj:`bool`): Value to provide class-defaults to
            ``queued`` kwarg if not provided during wrapped method call.
        self._msg_queue (:class:`telegram.ext.messagequeue.MessageQueue`): The actual
            ``MessageQueue`` used to delay outbound messages according to specified time-limits.

    Wrapped method starts accepting the next kwargs:

    Args:
        queued (:obj:`bool`, optional): If set to :obj:`True`, the ``MessageQueue`` is used to
            process output messages. Defaults to `self._is_queued_out`.
        isgroup (:obj:`bool`, optional): If set to :obj:`True`, the message is meant to be
            group-type(as there's no obvious way to determine its type in other way at the moment).
            Group-type messages could have additional processing delay according to limits set
            in `self._out_queue`. Defaults to :obj:`False`.

    Returns:
        ``telegram.utils.promise.Promise``: In case call is queued or original method's return
        value if it's not.

    """

    @functools.wraps(method)
    def wrapped(self: 'Bot', *args: Any, **kwargs: Any) -> Any:
        queued = kwargs.pop(
            'queued', self._is_messages_queued_default  # type: ignore[attr-defined]
        )
        is_group = kwargs.pop('isgroup', False)
        if queued:
            if not is_group:
                return self._msg_queue.process(  # type: ignore[attr-defined]
                    method, MessageQueue.DEFAULT_QUEUE, self, *args, **kwargs
                )
            return self._msg_queue.process(  # type: ignore[attr-defined]
                method, MessageQueue.GROUP_QUEUE, self, *args, **kwargs
            )
        return method(self, *args, **kwargs)

    return wrapped
