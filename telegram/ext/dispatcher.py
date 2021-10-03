#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains the Dispatcher class."""

import logging
import weakref
from collections import defaultdict
from queue import Empty, Queue
from threading import BoundedSemaphore, Event, Lock, Thread, current_thread
from time import sleep
from typing import (
    TYPE_CHECKING,
    Callable,
    DefaultDict,
    Dict,
    List,
    Optional,
    Set,
    Union,
    Generic,
    TypeVar,
    overload,
    cast,
)
from uuid import uuid4

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import BasePersistence, ContextTypes, ExtBot
from telegram.ext.handler import Handler
from telegram.ext.callbackdatacache import CallbackDataCache
from telegram.utils.defaultvalue import DefaultValue, DEFAULT_FALSE
from telegram.utils.warnings import warn
from telegram.ext.utils.promise import Promise
from telegram.ext.utils.types import CCT, UD, CD, BD

if TYPE_CHECKING:
    from telegram import Bot
    from telegram.ext import JobQueue
    from telegram.ext.callbackcontext import CallbackContext

DEFAULT_GROUP: int = 0

UT = TypeVar('UT')


class DispatcherHandlerStop(Exception):
    """
    Raise this in a handler or an error handler to prevent execution of any other handler (even in
    different group).

    In order to use this exception in a :class:`telegram.ext.ConversationHandler`, pass the
    optional ``state`` parameter instead of returning the next state:

    .. code-block:: python

        def callback(update, context):
            ...
            raise DispatcherHandlerStop(next_state)

    Note:
        Has no effect, if the handler or error handler is run asynchronously.

    Attributes:
        state (:obj:`object`): Optional. The next state of the conversation.

    Args:
        state (:obj:`object`, optional): The next state of the conversation.
    """

    __slots__ = ('state',)

    def __init__(self, state: object = None) -> None:
        super().__init__()
        self.state = state


class Dispatcher(Generic[CCT, UD, CD, BD]):
    """This class dispatches all kinds of updates to its registered handlers.

    Args:
        bot (:class:`telegram.Bot`): The bot object that should be passed to the handlers.
        update_queue (:obj:`Queue`): The synchronized queue that will contain the updates.
        job_queue (:class:`telegram.ext.JobQueue`, optional): The :class:`telegram.ext.JobQueue`
                instance to pass onto handler callbacks.
        workers (:obj:`int`, optional): Number of maximum concurrent worker threads for the
            ``@run_async`` decorator and :meth:`run_async`. Defaults to 4.
        persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence class to
            store data that should be persistent over restarts.
        context_types (:class:`telegram.ext.ContextTypes`, optional): Pass an instance
            of :class:`telegram.ext.ContextTypes` to customize the types used in the
            ``context`` interface. If not passed, the defaults documented in
            :class:`telegram.ext.ContextTypes` will be used.

            .. versionadded:: 13.6

    Attributes:
        bot (:class:`telegram.Bot`): The bot object that should be passed to the handlers.
        update_queue (:obj:`Queue`): The synchronized queue that will contain the updates.
        job_queue (:class:`telegram.ext.JobQueue`): Optional. The :class:`telegram.ext.JobQueue`
            instance to pass onto handler callbacks.
        workers (:obj:`int`, optional): Number of maximum concurrent worker threads for the
            ``@run_async`` decorator and :meth:`run_async`.
        user_data (:obj:`defaultdict`): A dictionary handlers can use to store data for the user.
        chat_data (:obj:`defaultdict`): A dictionary handlers can use to store data for the chat.
        bot_data (:obj:`dict`): A dictionary handlers can use to store data for the bot.
        persistence (:class:`telegram.ext.BasePersistence`): Optional. The persistence class to
            store data that should be persistent over restarts.
        context_types (:class:`telegram.ext.ContextTypes`): Container for the types used
            in the ``context`` interface.

            .. versionadded:: 13.6

    """

    # Allowing '__weakref__' creation here since we need it for the singleton
    __slots__ = (
        'workers',
        'persistence',
        'update_queue',
        'job_queue',
        'user_data',
        'chat_data',
        'bot_data',
        '_update_persistence_lock',
        'handlers',
        'groups',
        'error_handlers',
        'running',
        '__stop_event',
        '__exception_event',
        '__async_queue',
        '__async_threads',
        'bot',
        '__weakref__',
        'context_types',
    )

    __singleton_lock = Lock()
    __singleton_semaphore = BoundedSemaphore()
    __singleton = None
    logger = logging.getLogger(__name__)

    @overload
    def __init__(
        self: 'Dispatcher[CallbackContext[Dict, Dict, Dict], Dict, Dict, Dict]',
        bot: 'Bot',
        update_queue: Queue,
        workers: int = 4,
        exception_event: Event = None,
        job_queue: 'JobQueue' = None,
        persistence: BasePersistence = None,
    ):
        ...

    @overload
    def __init__(
        self: 'Dispatcher[CCT, UD, CD, BD]',
        bot: 'Bot',
        update_queue: Queue,
        workers: int = 4,
        exception_event: Event = None,
        job_queue: 'JobQueue' = None,
        persistence: BasePersistence = None,
        context_types: ContextTypes[CCT, UD, CD, BD] = None,
    ):
        ...

    def __init__(
        self,
        bot: 'Bot',
        update_queue: Queue,
        workers: int = 4,
        exception_event: Event = None,
        job_queue: 'JobQueue' = None,
        persistence: BasePersistence = None,
        context_types: ContextTypes[CCT, UD, CD, BD] = None,
    ):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue
        self.workers = workers
        self.context_types = cast(ContextTypes[CCT, UD, CD, BD], context_types or ContextTypes())

        if self.workers < 1:
            warn(
                'Asynchronous callbacks can not be processed without at least one worker thread.',
                stacklevel=2,
            )

        self.user_data: DefaultDict[int, UD] = defaultdict(self.context_types.user_data)
        self.chat_data: DefaultDict[int, CD] = defaultdict(self.context_types.chat_data)
        self.bot_data = self.context_types.bot_data()
        self.persistence: Optional[BasePersistence] = None
        self._update_persistence_lock = Lock()
        if persistence:
            if not isinstance(persistence, BasePersistence):
                raise TypeError("persistence must be based on telegram.ext.BasePersistence")
            self.persistence = persistence
            self.persistence.set_bot(self.bot)
            if self.persistence.store_data.user_data:
                self.user_data = self.persistence.get_user_data()
                if not isinstance(self.user_data, defaultdict):
                    raise ValueError("user_data must be of type defaultdict")
            if self.persistence.store_data.chat_data:
                self.chat_data = self.persistence.get_chat_data()
                if not isinstance(self.chat_data, defaultdict):
                    raise ValueError("chat_data must be of type defaultdict")
            if self.persistence.store_data.bot_data:
                self.bot_data = self.persistence.get_bot_data()
                if not isinstance(self.bot_data, self.context_types.bot_data):
                    raise ValueError(
                        f"bot_data must be of type {self.context_types.bot_data.__name__}"
                    )
            if self.persistence.store_data.callback_data:
                self.bot = cast(ExtBot, self.bot)
                persistent_data = self.persistence.get_callback_data()
                if persistent_data is not None:
                    if not isinstance(persistent_data, tuple) and len(persistent_data) != 2:
                        raise ValueError('callback_data must be a 2-tuple')
                    self.bot.callback_data_cache = CallbackDataCache(
                        self.bot,
                        self.bot.callback_data_cache.maxsize,
                        persistent_data=persistent_data,
                    )
        else:
            self.persistence = None

        self.handlers: Dict[int, List[Handler]] = {}
        """Dict[:obj:`int`, List[:class:`telegram.ext.Handler`]]: Holds the handlers per group."""
        self.groups: List[int] = []
        """List[:obj:`int`]: A list with all groups."""
        self.error_handlers: Dict[Callable, Union[bool, DefaultValue]] = {}
        """Dict[:obj:`callable`, :obj:`bool`]: A dict, where the keys are error handlers and the
        values indicate whether they are to be run asynchronously."""

        self.running = False
        """:obj:`bool`: Indicates if this dispatcher is running."""
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()
        self.__async_queue: Queue = Queue()
        self.__async_threads: Set[Thread] = set()

        # For backward compatibility, we allow a "singleton" mode for the dispatcher. When there's
        # only one instance of Dispatcher, it will be possible to use the `run_async` decorator.
        with self.__singleton_lock:
            if self.__singleton_semaphore.acquire(blocking=False):  # pylint: disable=R1732
                self._set_singleton(self)
            else:
                self._set_singleton(None)

    @property
    def exception_event(self) -> Event:  # skipcq: PY-D0003
        return self.__exception_event

    def _init_async_threads(self, base_name: str, workers: int) -> None:
        base_name = f'{base_name}_' if base_name else ''

        for i in range(workers):
            thread = Thread(target=self._pooled, name=f'Bot:{self.bot.id}:worker:{base_name}{i}')
            self.__async_threads.add(thread)
            thread.start()

    @classmethod
    def _set_singleton(cls, val: Optional['Dispatcher']) -> None:
        cls.logger.debug('Setting singleton dispatcher as %s', val)
        cls.__singleton = weakref.ref(val) if val else None

    @classmethod
    def get_instance(cls) -> 'Dispatcher':
        """Get the singleton instance of this class.

        Returns:
            :class:`telegram.ext.Dispatcher`

        Raises:
            RuntimeError

        """
        if cls.__singleton is not None:
            return cls.__singleton()  # type: ignore[return-value] # pylint: disable=not-callable
        raise RuntimeError(f'{cls.__name__} not initialized or multiple instances exist')

    def _pooled(self) -> None:
        thr_name = current_thread().name
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug(
                    "Closing run_async thread %s/%d", thr_name, len(self.__async_threads)
                )
                break

            promise.run()

            if not promise.exception:
                self.update_persistence(update=promise.update)
                continue

            if isinstance(promise.exception, DispatcherHandlerStop):
                warn(
                    'DispatcherHandlerStop is not supported with async functions; '
                    f'func: {promise.pooled_function.__name__}',
                )
                continue

            # Avoid infinite recursion of error handlers.
            if promise.pooled_function in self.error_handlers:
                self.logger.exception(
                    'An error was raised and an uncaught error was raised while '
                    'handling the error with an error_handler.',
                    exc_info=promise.exception,
                )
                continue

            # If we arrive here, an exception happened in the promise and was neither
            # DispatcherHandlerStop nor raised by an error handler. So we can and must handle it
            self.dispatch_error(promise.update, promise.exception, promise=promise)

    def run_async(
        self, func: Callable[..., object], *args: object, update: object = None, **kwargs: object
    ) -> Promise:
        """
        Queue a function (with given args/kwargs) to be run asynchronously. Exceptions raised
        by the function will be handled by the error handlers registered with
        :meth:`add_error_handler`.

        Warning:
            * If you're using ``@run_async``/:meth:`run_async` you cannot rely on adding custom
              attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.
            * Calling a function through :meth:`run_async` from within an error handler can lead to
              an infinite error handling loop.

        Args:
            func (:obj:`callable`): The function to run in the thread.
            *args (:obj:`tuple`, optional): Arguments to ``func``.
            update (:class:`telegram.Update` | :obj:`object`, optional): The update associated with
                the functions call. If passed, it will be available in the error handlers, in case
                an exception is raised by :attr:`func`.
            **kwargs (:obj:`dict`, optional): Keyword arguments to ``func``.

        Returns:
            Promise

        """
        promise = Promise(func, args, kwargs, update=update)
        self.__async_queue.put(promise)
        return promise

    def start(self, ready: Event = None) -> None:
        """Thread target of thread 'dispatcher'.

        Runs in background and processes the update queue.

        Args:
            ready (:obj:`threading.Event`, optional): If specified, the event will be set once the
                dispatcher is ready.

        """
        if self.running:
            self.logger.warning('already running')
            if ready is not None:
                ready.set()
            return

        if self.__exception_event.is_set():
            msg = 'reusing dispatcher after exception event is forbidden'
            self.logger.error(msg)
            raise TelegramError(msg)

        self._init_async_threads(str(uuid4()), self.workers)
        self.running = True
        self.logger.debug('Dispatcher started')

        if ready is not None:
            ready.set()

        while 1:
            try:
                # Pop update from update queue.
                update = self.update_queue.get(True, 1)
            except Empty:
                if self.__stop_event.is_set():
                    self.logger.debug('orderly stopping')
                    break
                if self.__exception_event.is_set():
                    self.logger.critical('stopping due to exception in another thread')
                    break
                continue

            self.logger.debug('Processing Update: %s', update)
            self.process_update(update)
            self.update_queue.task_done()

        self.running = False
        self.logger.debug('Dispatcher thread stopped')

    def stop(self) -> None:
        """Stops the thread."""
        if self.running:
            self.__stop_event.set()
            while self.running:
                sleep(0.1)
            self.__stop_event.clear()

        # async threads must be join()ed only after the dispatcher thread was joined,
        # otherwise we can still have new async threads dispatched
        threads = list(self.__async_threads)
        total = len(threads)

        # Stop all threads in the thread pool by put()ting one non-tuple per thread
        for i in range(total):
            self.__async_queue.put(None)

        for i, thr in enumerate(threads):
            self.logger.debug('Waiting for async thread %s/%s to end', i + 1, total)
            thr.join()
            self.__async_threads.remove(thr)
            self.logger.debug('async thread %s/%s has ended', i + 1, total)

    @property
    def has_running_threads(self) -> bool:  # skipcq: PY-D0003
        return self.running or bool(self.__async_threads)

    def process_update(self, update: object) -> None:
        """Processes a single update and updates the persistence.

        Note:
            If the update is handled by least one synchronously running handlers (i.e.
            ``run_async=False``), :meth:`update_persistence` is called *once* after all handlers
            synchronous handlers are done. Each asynchronously running handler will trigger
            :meth:`update_persistence` on its own.

        Args:
            update (:class:`telegram.Update` | :obj:`object` | \
                :class:`telegram.error.TelegramError`):
                The update to process.

        """
        # An error happened while polling
        if isinstance(update, TelegramError):
            self.dispatch_error(None, update)
            return

        context = None
        handled = False
        sync_modes = []

        for group in self.groups:
            try:
                for handler in self.handlers[group]:
                    check = handler.check_update(update)
                    if check is not None and check is not False:
                        if not context:
                            context = self.context_types.context.from_update(update, self)
                            context.refresh_data()
                        handled = True
                        sync_modes.append(handler.run_async)
                        handler.handle_update(update, self, check, context)
                        break

            # Stop processing with any other handler.
            except DispatcherHandlerStop:
                self.logger.debug('Stopping further handlers due to DispatcherHandlerStop')
                self.update_persistence(update=update)
                break

            # Dispatch any error.
            except Exception as exc:
                if self.dispatch_error(update, exc):
                    self.logger.debug('Error handler stopped further handlers.')
                    break

        # Update persistence, if handled
        handled_only_async = all(sync_modes)
        if handled:
            # Respect default settings
            if (
                all(mode is DEFAULT_FALSE for mode in sync_modes)
                and isinstance(self.bot, ExtBot)
                and self.bot.defaults
            ):
                handled_only_async = self.bot.defaults.run_async
            # If update was only handled by async handlers, we don't need to update here
            if not handled_only_async:
                self.update_persistence(update=update)

    def add_handler(self, handler: Handler[UT, CCT], group: int = DEFAULT_GROUP) -> None:
        """Register a handler.

        TL;DR: Order and priority counts. 0 or 1 handlers per group will be used. End handling of
        update with :class:`telegram.ext.DispatcherHandlerStop`.

        A handler must be an instance of a subclass of :class:`telegram.ext.Handler`. All handlers
        are organized in groups with a numeric value. The default group is 0. All groups will be
        evaluated for handling an update, but only 0 or 1 handler per group will be used. If
        :class:`telegram.ext.DispatcherHandlerStop` is raised from one of the handlers, no further
        handlers (regardless of the group) will be called.

        The priority/order of handlers is determined as follows:

          * Priority of the group (lower group number == higher priority)
          * The first handler in a group which should handle an update (see
            :attr:`telegram.ext.Handler.check_update`) will be used. Other handlers from the
            group will not be used. The order in which handlers were added to the group defines the
            priority.

        Args:
            handler (:class:`telegram.ext.Handler`): A Handler instance.
            group (:obj:`int`, optional): The group identifier. Default is 0.

        """
        # Unfortunately due to circular imports this has to be here
        from .conversationhandler import ConversationHandler  # pylint: disable=C0415

        if not isinstance(handler, Handler):
            raise TypeError(f'handler is not an instance of {Handler.__name__}')
        if not isinstance(group, int):
            raise TypeError('group is not int')
        # For some reason MyPy infers the type of handler is <nothing> here,
        # so for now we just ignore all the errors
        if (
            isinstance(handler, ConversationHandler)
            and handler.persistent  # type: ignore[attr-defined]
            and handler.name  # type: ignore[attr-defined]
        ):
            if not self.persistence:
                raise ValueError(
                    f"ConversationHandler {handler.name} "  # type: ignore[attr-defined]
                    f"can not be persistent if dispatcher has no persistence"
                )
            handler.persistence = self.persistence  # type: ignore[attr-defined]
            handler.conversations = (  # type: ignore[attr-defined]
                self.persistence.get_conversations(handler.name)  # type: ignore[attr-defined]
            )

        if group not in self.handlers:
            self.handlers[group] = []
            self.groups.append(group)
            self.groups = sorted(self.groups)

        self.handlers[group].append(handler)

    def remove_handler(self, handler: Handler, group: int = DEFAULT_GROUP) -> None:
        """Remove a handler from the specified group.

        Args:
            handler (:class:`telegram.ext.Handler`): A Handler instance.
            group (:obj:`object`, optional): The group identifier. Default is 0.

        """
        if handler in self.handlers[group]:
            self.handlers[group].remove(handler)
            if not self.handlers[group]:
                del self.handlers[group]
                self.groups.remove(group)

    def update_persistence(self, update: object = None) -> None:
        """Update :attr:`user_data`, :attr:`chat_data` and :attr:`bot_data` in :attr:`persistence`.

        Args:
            update (:class:`telegram.Update`, optional): The update to process. If passed, only the
                corresponding ``user_data`` and ``chat_data`` will be updated.
        """
        with self._update_persistence_lock:
            self.__update_persistence(update)

    def __update_persistence(self, update: object = None) -> None:
        if self.persistence:
            # We use list() here in order to decouple chat_ids from self.chat_data, as dict view
            # objects will change, when the dict does and we want to loop over chat_ids
            chat_ids = list(self.chat_data.keys())
            user_ids = list(self.user_data.keys())

            if isinstance(update, Update):
                if update.effective_chat:
                    chat_ids = [update.effective_chat.id]
                else:
                    chat_ids = []
                if update.effective_user:
                    user_ids = [update.effective_user.id]
                else:
                    user_ids = []

            if self.persistence.store_data.callback_data:
                self.bot = cast(ExtBot, self.bot)
                try:
                    self.persistence.update_callback_data(
                        self.bot.callback_data_cache.persistence_data
                    )
                except Exception as exc:
                    self.dispatch_error(update, exc)
            if self.persistence.store_data.bot_data:
                try:
                    self.persistence.update_bot_data(self.bot_data)
                except Exception as exc:
                    self.dispatch_error(update, exc)
            if self.persistence.store_data.chat_data:
                for chat_id in chat_ids:
                    try:
                        self.persistence.update_chat_data(chat_id, self.chat_data[chat_id])
                    except Exception as exc:
                        self.dispatch_error(update, exc)
            if self.persistence.store_data.user_data:
                for user_id in user_ids:
                    try:
                        self.persistence.update_user_data(user_id, self.user_data[user_id])
                    except Exception as exc:
                        self.dispatch_error(update, exc)

    def add_error_handler(
        self,
        callback: Callable[[object, CCT], None],
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,  # pylint: disable=W0621
    ) -> None:
        """Registers an error handler in the Dispatcher. This handler will receive every error
        which happens in your bot. See the docs of :meth:`dispatch_error` for more details on how
        errors are handled.

        Note:
            Attempts to add the same callback multiple times will be ignored.

        Args:
            callback (:obj:`callable`): The callback function for this error handler. Will be
                called when an error is raised.
            Callback signature:


            ``def callback(update: Update, context: CallbackContext)``

                The error that happened will be present in context.error.
            run_async (:obj:`bool`, optional): Whether this handlers callback should be run
                asynchronously using :meth:`run_async`. Defaults to :obj:`False`.
        """
        if callback in self.error_handlers:
            self.logger.debug('The callback is already registered as an error handler. Ignoring.')
            return

        if (
            run_async is DEFAULT_FALSE
            and isinstance(self.bot, ExtBot)
            and self.bot.defaults
            and self.bot.defaults.run_async
        ):
            run_async = True

        self.error_handlers[callback] = run_async

    def remove_error_handler(self, callback: Callable[[object, CCT], None]) -> None:
        """Removes an error handler.

        Args:
            callback (:obj:`callable`): The error handler to remove.

        """
        self.error_handlers.pop(callback, None)

    def dispatch_error(
        self,
        update: Optional[object],
        error: Exception,
        promise: Promise = None,
    ) -> bool:
        """Dispatches an error by passing it to all error handlers registered with
        :meth:`add_error_handler`. If one of the error handlers raises
        :class:`telegram.ext.DispatcherHandlerStop`, the update will not be handled by other error
        handlers or handlers (even in other groups). All other exceptions raised by an error
        handler will just be logged.

        .. versionchanged:: 14.0

            * Exceptions raised by error handlers are now properly logged.
            * :class:`telegram.ext.DispatcherHandlerStop` is no longer reraised but converted into
              the return value.

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update that caused the error.
            error (:obj:`Exception`): The error that was raised.
            promise (:class:`telegram.utils.Promise`, optional): The promise whose pooled function
                raised the error.

        Returns:
            :obj:`bool`: :obj:`True` if one of the error handlers raised
                :class:`telegram.ext.DispatcherHandlerStop`. :obj:`False`, otherwise.
        """
        async_args = None if not promise else promise.args
        async_kwargs = None if not promise else promise.kwargs

        if self.error_handlers:
            for callback, run_async in self.error_handlers.items():  # pylint: disable=W0621
                context = self.context_types.context.from_error(
                    update, error, self, async_args=async_args, async_kwargs=async_kwargs
                )
                if run_async:
                    self.run_async(callback, update, context, update=update)
                else:
                    try:
                        callback(update, context)
                    except DispatcherHandlerStop:
                        return True
                    except Exception as exc:
                        self.logger.exception(
                            'An error was raised and an uncaught error was raised while '
                            'handling the error with an error_handler.',
                            exc_info=exc,
                        )
            return False

        self.logger.exception(
            'No error handlers are registered, logging exception.', exc_info=error
        )
        return False
