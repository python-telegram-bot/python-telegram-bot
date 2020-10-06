#!/usr/bin/env python
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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains the Dispatcher class."""

import logging
import warnings
import weakref
from functools import wraps
from threading import Thread, Lock, Event, current_thread, BoundedSemaphore
from time import sleep
from uuid import uuid4
from collections import defaultdict

from queue import Queue, Empty

from telegram import TelegramError, Update
from telegram.ext.handler import Handler
from telegram.ext.callbackcontext import CallbackContext
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.promise import Promise
from telegram.ext import BasePersistence

from typing import Any, Callable, TYPE_CHECKING, Optional, Union, DefaultDict, Dict, List, Set

from telegram.utils.types import HandlerArg

if TYPE_CHECKING:
    from telegram import Bot
    from telegram.ext import JobQueue

DEFAULT_GROUP = 0


def run_async(func: Callable[[Update, CallbackContext],
                             Any]) -> Callable[[Update, CallbackContext], Any]:
    """
    Function decorator that will run the function in a new thread.

    Will run :attr:`telegram.ext.Dispatcher.run_async`.

    Using this decorator is only possible when only a single Dispatcher exist in the system.

    Note:
        DEPRECATED. Use :attr:`telegram.ext.Dispatcher.run_async` directly instead or the
        :attr:`Handler.run_async` parameter.

    Warning:
        If you're using ``@run_async`` you cannot rely on adding custom attributes to
        :class:`telegram.ext.CallbackContext`. See its docs for more info.
    """

    @wraps(func)
    def async_func(*args: Any, **kwargs: Any) -> Any:
        warnings.warn('The @run_async decorator is deprecated. Use the `run_async` parameter of'
                      '`Dispatcher.add_handler` or `Dispatcher.run_async` instead.',
                      TelegramDeprecationWarning,
                      stacklevel=2)
        return Dispatcher.get_instance()._run_async(func, *args, update=None, error_handling=False,
                                                    **kwargs)

    return async_func


class DispatcherHandlerStop(Exception):
    """
    Raise this in handler to prevent execution any other handler (even in different group).

    In order to use this exception in a :class:`telegram.ext.ConversationHandler`, pass the
    optional ``state`` parameter instead of returning the next state:

    .. code-block:: python

        def callback(update, context):
            ...
            raise DispatcherHandlerStop(next_state)

    Attributes:
        state (:obj:`object`): Optional. The next state of the conversation.

    Args:
        state (:obj:`object`, optional): The next state of the conversation.
    """
    def __init__(self, state: object = None) -> None:
        super().__init__()
        self.state = state


class Dispatcher:
    """This class dispatches all kinds of updates to its registered handlers.

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

    Args:
        bot (:class:`telegram.Bot`): The bot object that should be passed to the handlers.
        update_queue (:obj:`Queue`): The synchronized queue that will contain the updates.
        job_queue (:class:`telegram.ext.JobQueue`, optional): The :class:`telegram.ext.JobQueue`
                instance to pass onto handler callbacks.
        workers (:obj:`int`, optional): Number of maximum concurrent worker threads for the
            ``@run_async`` decorator and :meth:`run_async`. Defaults to 4.
        persistence (:class:`telegram.ext.BasePersistence`, optional): The persistence class to
            store data that should be persistent over restarts.
        use_context (:obj:`bool`, optional): If set to :obj:`True` uses the context based callback
            API (ignored if `dispatcher` argument is used). Defaults to :obj:`True`.
            **New users**: set this to :obj:`True`.

    """

    __singleton_lock = Lock()
    __singleton_semaphore = BoundedSemaphore()
    __singleton = None
    logger = logging.getLogger(__name__)

    def __init__(self,
                 bot: 'Bot',
                 update_queue: Queue,
                 workers: int = 4,
                 exception_event: Event = None,
                 job_queue: 'JobQueue' = None,
                 persistence: BasePersistence = None,
                 use_context: bool = True):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue
        self.workers = workers
        self.use_context = use_context

        if not use_context:
            warnings.warn('Old Handler API is deprecated - see https://git.io/fxJuV for details',
                          TelegramDeprecationWarning, stacklevel=3)

        self.user_data: DefaultDict[int, Dict[Any, Any]] = defaultdict(dict)
        self.chat_data: DefaultDict[int, Dict[Any, Any]] = defaultdict(dict)
        self.bot_data = {}
        self.persistence: Optional[BasePersistence] = None
        self._update_persistence_lock = Lock()
        if persistence:
            if not isinstance(persistence, BasePersistence):
                raise TypeError("persistence must be based on telegram.ext.BasePersistence")
            self.persistence = persistence
            self.persistence.set_bot(self.bot)
            if self.persistence.store_user_data:
                self.user_data = self.persistence.get_user_data()
                if not isinstance(self.user_data, defaultdict):
                    raise ValueError("user_data must be of type defaultdict")
            if self.persistence.store_chat_data:
                self.chat_data = self.persistence.get_chat_data()
                if not isinstance(self.chat_data, defaultdict):
                    raise ValueError("chat_data must be of type defaultdict")
            if self.persistence.store_bot_data:
                self.bot_data = self.persistence.get_bot_data()
                if not isinstance(self.bot_data, dict):
                    raise ValueError("bot_data must be of type dict")
        else:
            self.persistence = None

        self.handlers: Dict[int, List[Handler]] = {}
        """Dict[:obj:`int`, List[:class:`telegram.ext.Handler`]]: Holds the handlers per group."""
        self.groups: List[int] = []
        """List[:obj:`int`]: A list with all groups."""
        self.error_handlers: Dict[Callable, bool] = {}
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
            if self.__singleton_semaphore.acquire(blocking=False):
                self._set_singleton(self)
            else:
                self._set_singleton(None)

    @property
    def exception_event(self) -> Event:
        return self.__exception_event

    def _init_async_threads(self, base_name: str, workers: int) -> None:
        base_name = '{}_'.format(base_name) if base_name else ''

        for i in range(workers):
            thread = Thread(target=self._pooled, name='Bot:{}:worker:{}{}'.format(self.bot.id,
                                                                                  base_name, i))
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
        else:
            raise RuntimeError('{} not initialized or multiple instances exist'.format(
                cls.__name__))

    def _pooled(self) -> None:
        thr_name = current_thread().getName()
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug("Closing run_async thread %s/%d", thr_name,
                                  len(self.__async_threads))
                break

            promise.run()

            if not promise.exception:
                self.update_persistence(update=promise.update)
                continue

            if isinstance(promise.exception, DispatcherHandlerStop):
                self.logger.warning(
                    'DispatcherHandlerStop is not supported with async functions; func: %s',
                    promise.pooled_function.__name__)
                continue

            # Avoid infinite recursion of error handlers.
            if promise.pooled_function in self.error_handlers:
                self.logger.error('An uncaught error was raised while handling the error.')
                continue

            # Don't perform error handling for a `Promise` with deactivated error handling. This
            # should happen only via the deprecated `@run_async` decorator or `Promises` created
            # within error handlers
            if not promise.error_handling:
                self.logger.error('A promise with deactivated error handling raised an error.')
                continue

            # If we arrive here, an exception happened in the promise and was neither
            # DispatcherHandlerStop nor raised by an error handler. So we can and must handle it
            try:
                self.dispatch_error(promise.update, promise.exception, promise=promise)
            except Exception:
                self.logger.exception('An uncaught error was raised while handling the error.')

    def run_async(self,
                  func: Callable[..., Any],
                  *args: Any,
                  update: HandlerArg = None,
                  **kwargs: Any) -> Promise:
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
            update (:class:`telegram.Update`, optional): The update associated with the functions
                call. If passed, it will be available in the error handlers, in case an exception
                is raised by :attr:`func`.
            **kwargs (:obj:`dict`, optional): Keyword arguments to ``func``.

        Returns:
            Promise

        """
        return self._run_async(func, *args, update=update, error_handling=True, **kwargs)

    def _run_async(self,
                   func: Callable[..., Any],
                   *args: Any,
                   update: HandlerArg = None,
                   error_handling: bool = True,
                   **kwargs: Any) -> Promise:
        # TODO: Remove error_handling parameter once we drop the @run_async decorator
        promise = Promise(func, args, kwargs, update=update, error_handling=error_handling)
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
                elif self.__exception_event.is_set():
                    self.logger.critical('stopping due to exception in another thread')
                    break
                continue

            self.logger.debug('Processing Update: %s' % update)
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
            self.logger.debug('Waiting for async thread {}/{} to end'.format(i + 1, total))
            thr.join()
            self.__async_threads.remove(thr)
            self.logger.debug('async thread {}/{} has ended'.format(i + 1, total))

    @property
    def has_running_threads(self) -> bool:
        return self.running or bool(self.__async_threads)

    def process_update(self, update: Union[str, Update, TelegramError]) -> None:
        """Processes a single update.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | :class:`telegram.TelegramError`):
                The update to process.

        """

        # An error happened while polling
        if isinstance(update, TelegramError):
            try:
                self.dispatch_error(None, update)
            except Exception:
                self.logger.exception('An uncaught error was raised while handling the error.')
            return

        context = None

        for group in self.groups:
            try:
                for handler in self.handlers[group]:
                    check = handler.check_update(update)
                    if check is not None and check is not False:
                        if not context and self.use_context:
                            context = CallbackContext.from_update(update, self)
                        handler.handle_update(update, self, check, context)

                        # If handler runs async updating immediately doesn't make sense
                        if not handler.run_async:
                            self.update_persistence(update=update)
                        break

            # Stop processing with any other handler.
            except DispatcherHandlerStop:
                self.logger.debug('Stopping further handlers due to DispatcherHandlerStop')
                self.update_persistence(update=update)
                break

            # Dispatch any error.
            except Exception as e:
                try:
                    self.dispatch_error(update, e)
                except DispatcherHandlerStop:
                    self.logger.debug('Error handler stopped further handlers')
                    break
                # Errors should not stop the thread.
                except Exception:
                    self.logger.exception('An uncaught error was raised while handling the error.')

    def add_handler(self, handler: Handler, group: int = DEFAULT_GROUP) -> None:
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
        from .conversationhandler import ConversationHandler

        if not isinstance(handler, Handler):
            raise TypeError('handler is not an instance of {}'.format(Handler.__name__))
        if not isinstance(group, int):
            raise TypeError('group is not int')
        if isinstance(handler, ConversationHandler) and handler.persistent and handler.name:
            if not self.persistence:
                raise ValueError(
                    "ConversationHandler {} can not be persistent if dispatcher has no "
                    "persistence".format(handler.name))
            handler.persistence = self.persistence
            handler.conversations = self.persistence.get_conversations(handler.name)

        if group not in self.handlers:
            self.handlers[group] = list()
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

    def update_persistence(self, update: HandlerArg = None) -> None:
        """Update :attr:`user_data`, :attr:`chat_data` and :attr:`bot_data` in :attr:`persistence`.

        Args:
            update (:class:`telegram.Update`, optional): The update to process. If passed, only the
            corresponding ``user_data`` and ``chat_data`` will be updated.
        """
        with self._update_persistence_lock:
            self.__update_persistence(update)

    def __update_persistence(self, update: HandlerArg = None) -> None:
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

            if self.persistence.store_bot_data:
                try:
                    self.persistence.update_bot_data(self.bot_data)
                except Exception as e:
                    try:
                        self.dispatch_error(update, e)
                    except Exception:
                        message = 'Saving bot data raised an error and an ' \
                                  'uncaught error was raised while handling ' \
                                  'the error with an error_handler'
                        self.logger.exception(message)
            if self.persistence.store_chat_data:
                for chat_id in chat_ids:
                    try:
                        self.persistence.update_chat_data(chat_id, self.chat_data[chat_id])
                    except Exception as e:
                        try:
                            self.dispatch_error(update, e)
                        except Exception:
                            message = 'Saving chat data raised an error and an ' \
                                      'uncaught error was raised while handling ' \
                                      'the error with an error_handler'
                            self.logger.exception(message)
            if self.persistence.store_user_data:
                for user_id in user_ids:
                    try:
                        self.persistence.update_user_data(user_id, self.user_data[user_id])
                    except Exception as e:
                        try:
                            self.dispatch_error(update, e)
                        except Exception:
                            message = 'Saving user data raised an error and an ' \
                                      'uncaught error was raised while handling ' \
                                      'the error with an error_handler'
                            self.logger.exception(message)

    def add_error_handler(self,
                          callback: Callable[[Any, CallbackContext], None],
                          run_async: bool = False) -> None:
        """Registers an error handler in the Dispatcher. This handler will receive every error
        which happens in your bot.

        Note:
            Attempts to add the same callback multiple times will be ignored.

        Warning:
            The errors handled within these handlers won't show up in the logger, so you
            need to make sure that you reraise the error.

        Args:
            callback (:obj:`callable`): The callback function for this error handler. Will be
                called when an error is raised. Callback signature for context based API:

                ``def callback(update: Update, context: CallbackContext)``

                The error that happened will be present in context.error.
            run_async (:obj:`bool`, optional): Whether this handlers callback should be run
                asynchronously using :meth:`run_async`. Defaults to :obj:`False`.

        Note:
            See https://git.io/fxJuV for more info about switching to context based API.
        """
        if callback in self.error_handlers:
            self.logger.debug('The callback is already registered as an error handler. Ignoring.')
            return
        self.error_handlers[callback] = run_async

    def remove_error_handler(self, callback: Callable[[Any, CallbackContext], None]) -> None:
        """Removes an error handler.

        Args:
            callback (:obj:`callable`): The error handler to remove.

        """
        self.error_handlers.pop(callback, None)

    def dispatch_error(self,
                       update: Optional[HandlerArg],
                       error: Exception,
                       promise: Promise = None) -> None:
        """Dispatches an error.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | None): The update that caused the error
            error (:obj:`Exception`): The error that was raised.
            promise (:class:`telegram.utils.Promise`, optional): The promise whose pooled function
                raised the error.

        """
        async_args = None if not promise else promise.args
        async_kwargs = None if not promise else promise.kwargs

        if self.error_handlers:
            for callback, run_async in self.error_handlers.items():
                if self.use_context:
                    context = CallbackContext.from_error(update, error, self,
                                                         async_args=async_args,
                                                         async_kwargs=async_kwargs)
                    if run_async:
                        self.run_async(callback, update, context, update=update)
                    else:
                        callback(update, context)
                else:
                    if run_async:
                        self.run_async(callback, self.bot, update, error, update=update)
                    else:
                        callback(self.bot, update, error)

        else:
            self.logger.exception(
                'No error handlers are registered, logging exception.', exc_info=error)
