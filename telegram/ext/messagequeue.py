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
from telegram.utils import promise

import functools
import sys
import time
import threading
if sys.version_info.major > 2:
    import queue as q
else:
    import Queue as q

# We need to count < 1s intervals, so the most accurate timer is needed
# Starting from Python 3.3 we have time.perf_counter which is the clock
#  with the highest resolution available to the system, so let's use it there.
# In Python 2.7, there's no perf_counter yet, so fallback on what we have:
#  on Windows, the best available is time.clock while time.time is on
#  another platforms (M. Lutz, "Learning Python," 4ed, p.630-634)
if sys.version_info.major == 3 and sys.version_info.minor >= 3:
    curtime = time.perf_counter  # pylint: disable=E1101
else:
    curtime = time.clock if sys.platform[:3] == 'win' else time.time


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
        autostart (:obj:`bool`, optional): If True, processor is started immediately after object's
            creation; if ``False``, should be started manually by `start` method. Defaults to True.
        name (:obj:`str`, optional): Thread's name. Defaults to ``'DelayQueue-N'``, where N is
            sequential number of object created.

    """

    _instcnt = 0  # instance counter

    def __init__(self,
                 queue=None,
                 burst_limit=30,
                 time_limit_ms=1000,
                 exc_route=None,
                 autostart=True,
                 name=None):
        self._queue = queue if queue is not None else q.Queue()
        self.burst_limit = burst_limit
        self.time_limit = time_limit_ms / 1000
        self.exc_route = (exc_route if exc_route is not None else self._default_exception_handler)
        self.__exit_req = False  # flag to gently exit thread
        self.__class__._instcnt += 1
        if name is None:
            name = '%s-%s' % (self.__class__.__name__, self.__class__._instcnt)
        super(DelayQueue, self).__init__(name=name)
        self.daemon = False
        if autostart:  # immediately start processing
            super(DelayQueue, self).start()

    def run(self):
        """
        Do not use the method except for unthreaded testing purposes, the method normally is
        automatically called by autostart argument.

        """

        times = []  # used to store each callable processing time
        while True:
            item = self._queue.get()
            if self.__exit_req:
                return  # shutdown thread
            # delay routine
            now = curtime()
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
            try:
                func, args, kwargs = item
                func(*args, **kwargs)
            except Exception as exc:  # re-route any exceptions
                self.exc_route(exc)  # to prevent thread exit

    def stop(self, timeout=None):
        """Used to gently stop processor and shutdown its thread.

        Args:
            timeout (:obj:`float`): Indicates maximum time to wait for processor to stop and its
                thread to exit. If timeout exceeds and processor has not stopped, method silently
                returns. :attr:`is_alive` could be used afterwards to check the actual status.
                ``timeout`` set to None, blocks until processor is shut down. Defaults to None.

        """

        self.__exit_req = True  # gently request
        self._queue.put(None)  # put something to unfreeze if frozen
        super(DelayQueue, self).join(timeout=timeout)

    @staticmethod
    def _default_exception_handler(exc):
        """
        Dummy exception handler which re-raises exception in thread. Could be possibly overwritten
        by subclasses.

        """

        raise exc

    def __call__(self, func, *args, **kwargs):
        """Used to process callbacks in throughput-limiting thread through queue.

        Args:
            func (:obj:`callable`): The actual function (or any callable) that is processed through
                queue.
            *args (:obj:`list`): Variable-length `func` arguments.
            **kwargs (:obj:`dict`): Arbitrary keyword-arguments to `func`.

        """

        if not self.is_alive() or self.__exit_req:
            raise DelayQueueError('Could not process callback in stopped thread')
        self._queue.put((func, args, kwargs))


# The most straightforward way to implement this is to use 2 sequenital delay
# queues, like on classic delay chain schematics in electronics.
# So, message path is:
# msg --> group delay if group msg, else no delay --> normal msg delay --> out
# This way OS threading scheduler cares of timings accuracy.
# (see time.time, time.clock, time.perf_counter, time.sleep @ docs.python.org)
class MessageQueue(object):
    """
    Implements callback processing with proper delays to avoid hitting Telegram's message limits.
    Contains two ``DelayQueue``, for group and for all messages, interconnected in delay chain.
    Callables are processed through *group* ``DelayQueue``, then through *all* ``DelayQueue`` for
    group-type messages. For non-group messages, only the *all* ``DelayQueue`` is used.

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
        autostart (:obj:`bool`, optional): If True, processors are started immediately after
            object's creation; if ``False``, should be started manually by :attr:`start` method.
            Defaults to ``True``.

    """

    def __init__(self,
                 all_burst_limit=30,
                 all_time_limit_ms=1000,
                 group_burst_limit=20,
                 group_time_limit_ms=60000,
                 exc_route=None,
                 autostart=True):
        # create accoring delay queues, use composition
        self._all_delayq = DelayQueue(
            burst_limit=all_burst_limit,
            time_limit_ms=all_time_limit_ms,
            exc_route=exc_route,
            autostart=autostart)
        self._group_delayq = DelayQueue(
            burst_limit=group_burst_limit,
            time_limit_ms=group_time_limit_ms,
            exc_route=exc_route,
            autostart=autostart)

    def start(self):
        """Method is used to manually start the ``MessageQueue`` processing."""
        self._all_delayq.start()
        self._group_delayq.start()

    def stop(self, timeout=None):
        self._group_delayq.stop(timeout=timeout)
        self._all_delayq.stop(timeout=timeout)

    stop.__doc__ = DelayQueue.stop.__doc__ or ''  # reuse docsting if any

    def __call__(self, promise, is_group_msg=False):
        """
        Processes callables in troughput-limiting queues to avoid hitting limits (specified with
        :attr:`burst_limit` and :attr:`time_limit`.

        Args:
            promise (:obj:`callable`): Mainly the ``telegram.utils.promise.Promise`` (see Notes for
                other callables), that is processed in delay queues.
            is_group_msg (:obj:`bool`, optional): Defines whether ``promise`` would be processed in
                group*+*all* ``DelayQueue``s (if set to ``True``), or only through *all*
                ``DelayQueue`` (if set to ``False``), resulting in needed delays to avoid
                hitting specified limits. Defaults to ``False``.

        Note:
            Method is designed to accept ``telegram.utils.promise.Promise`` as ``promise``
            argument, but other callables could be used too. For example, lambdas or simple
            functions could be used to wrap original func to be called with needed args. In that
            case, be sure that either wrapper func does not raise outside exceptions or the proper
            :attr:`exc_route` handler is provided.

        Returns:
            :obj:`callable`: Used as ``promise`` argument.

        """

        if not is_group_msg:  # ignore middle group delay
            self._all_delayq(promise)
        else:  # use middle group delay
            self._group_delayq(self._all_delayq, promise)
        return promise


def queuedmessage(method):
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
        queued (:obj:`bool`, optional): If set to ``True``, the ``MessageQueue`` is used to process
            output messages. Defaults to `self._is_queued_out`.
        isgroup (:obj:`bool`, optional): If set to ``True``, the message is meant to be group-type
            (as there's no obvious way to determine its type in other way at the moment).
            Group-type messages could have additional processing delay according to limits set
            in `self._out_queue`. Defaults to ``False``.

    Returns:
        ``telegram.utils.promise.Promise``: In case call is queued or original method's return
        value if it's not.

    """

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        queued = kwargs.pop('queued', self._is_messages_queued_default)
        isgroup = kwargs.pop('isgroup', False)
        if queued:
            prom = promise.Promise(method, (self, ) + args, kwargs)
            return self._msg_queue(prom, isgroup)
        return method(self, *args, **kwargs)

    return wrapped
