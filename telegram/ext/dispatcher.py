#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
from functools import wraps
from threading import Thread, Lock, Event, current_thread, BoundedSemaphore
from time import sleep
from uuid import uuid4
from collections import defaultdict

from queue import Queue, Empty

from future.builtins import range

from telegram import TelegramError
from telegram.ext.handler import Handler
from telegram.utils.deprecate import deprecate
from telegram.utils.promise import Promise

logging.getLogger(__name__).addHandler(logging.NullHandler())
""":type: set[Thread]"""
DEFAULT_GROUP = 0


def run_async(func):
    """Function decorator that will run the function in a new thread.

    Using this decorator is only possible when only a single Dispatcher exist in the system.

    Args:
        func (function): The function to run in the thread.
        async_queue (Queue): The queue of the functions to be executed asynchronously.

    Returns:
        function:

    """

    @wraps(func)
    def async_func(*args, **kwargs):
        return Dispatcher.get_instance().run_async(func, *args, **kwargs)

    return async_func


class Dispatcher(object):
    """
    This class dispatches all kinds of updates to its registered handlers.

    Args:
        bot (telegram.Bot): The bot object that should be passed to the
            handlers
        update_queue (Queue): The synchronized queue that will contain the
            updates.
        job_queue (Optional[telegram.ext.JobQueue]): The ``JobQueue`` instance to pass onto handler
            callbacks
        workers (Optional[int]): Number of maximum concurrent worker threads for the ``@run_async``
            decorator

    """
    __singleton_lock = Lock()
    __singleton_semaphore = BoundedSemaphore()
    __singleton = None
    logger = logging.getLogger(__name__)

    def __init__(self, bot, update_queue, workers=4, exception_event=None, job_queue=None):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue
        self.workers = workers

        self.user_data = defaultdict(dict)
        """:type: dict[int, dict]"""
        self.chat_data = defaultdict(dict)
        """:type: dict[int, dict]"""

        self.handlers = {}
        """:type: dict[int, list[Handler]"""
        self.groups = []
        """:type: list[int]"""
        self.error_handlers = []

        self.running = False
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()
        self.__async_queue = Queue()
        self.__async_threads = set()

        # For backward compatibility, we allow a "singleton" mode for the dispatcher. When there's
        # only one instance of Dispatcher, it will be possible to use the `run_async` decorator.
        with self.__singleton_lock:
            if self.__singleton_semaphore.acquire(blocking=0):
                self._set_singleton(self)
            else:
                self._set_singleton(None)

    @classmethod
    def _reset_singleton(cls):
        # NOTE: This method was added mainly for test_updater benefit and specifically pypy. Never
        #       call it in production code.
        cls.__singleton_semaphore.release()

    def _init_async_threads(self, base_name, workers):
        base_name = '{}_'.format(base_name) if base_name else ''

        for i in range(workers):
            thread = Thread(target=self._pooled, name='{}{}'.format(base_name, i))
            self.__async_threads.add(thread)
            thread.start()

    @classmethod
    def _set_singleton(cls, val):
        cls.logger.debug('Setting singleton dispatcher as %s', val)
        cls.__singleton = weakref.ref(val) if val else None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of this class.

        Returns:
            Dispatcher

        """
        if cls.__singleton is not None:
            return cls.__singleton()
        else:
            raise RuntimeError('{} not initialized or multiple instances exist'.format(
                cls.__name__))

    def _pooled(self):
        """
        A wrapper to run a thread in a thread pool
        """
        thr_name = current_thread().getName()
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug("Closing run_async thread %s/%d", thr_name,
                                  len(self.__async_threads))
                break

            try:
                promise.run()

            except:
                self.logger.exception("run_async function raised exception")

    def run_async(self, func, *args, **kwargs):
        """Queue a function (with given args/kwargs) to be run asynchronously.

        Args:
            func (function): The function to run in the thread.
            args (Optional[tuple]): Arguments to `func`.
            kwargs (Optional[dict]): Keyword arguments to `func`.

        Returns:
            Promise

        """
        # TODO: handle exception in async threads
        #       set a threading.Event to notify caller thread
        promise = Promise(func, args, kwargs)
        self.__async_queue.put(promise)
        return promise

    def start(self):
        """
        Thread target of thread 'dispatcher'. Runs in background and processes
        the update queue.
        """

        if self.running:
            self.logger.warning('already running')
            return

        if self.__exception_event.is_set():
            msg = 'reusing dispatcher after exception event is forbidden'
            self.logger.error(msg)
            raise TelegramError(msg)

        self._init_async_threads(uuid4(), self.workers)
        self.running = True
        self.logger.debug('Dispatcher started')

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

        self.running = False
        self.logger.debug('Dispatcher thread stopped')

    def stop(self):
        """
        Stops the thread
        """
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
            self.logger.debug('Waiting for async thread {0}/{1} to end'.format(i + 1, total))
            thr.join()
            self.__async_threads.remove(thr)
            self.logger.debug('async thread {0}/{1} has ended'.format(i + 1, total))

    @property
    def has_running_threads(self):
        return self.running or bool(self.__async_threads)

    def process_update(self, update):
        """
        Processes a single update.

        Args:
            update (object):
        """

        # An error happened while polling
        if isinstance(update, TelegramError):
            self.dispatch_error(None, update)

        else:
            for group in self.groups:
                for handler in self.handlers[group]:
                    try:
                        if handler.check_update(update):
                            handler.handle_update(update, self)
                            break
                    # Dispatch any errors
                    except TelegramError as te:
                        self.logger.warn('A TelegramError was raised while processing the '
                                         'Update.')

                        try:
                            self.dispatch_error(update, te)
                        except Exception:
                            self.logger.exception('An uncaught error was raised while '
                                                  'handling the error')
                        finally:
                            break

                    # Errors should not stop the thread
                    except Exception:
                        self.logger.exception('An uncaught error was raised while '
                                              'processing the update')
                        break

    def add_handler(self, handler, group=DEFAULT_GROUP):
        """
        Register a handler.

        TL;DR: Order and priority counts. 0 or 1 handlers per group will be
        used.

        A handler must be an instance of a subclass of
        telegram.ext.Handler. All handlers are organized in groups with a
        numeric value. The default group is 0. All groups will be evaluated for
        handling an update, but only 0 or 1 handler per group will be used.

        The priority/order of handlers is determined as follows:

          * Priority of the group (lower group number == higher priority)

          * The first handler in a group which should handle an update will be
            used. Other handlers from the group will not be used. The order in
            which handlers were added to the group defines the priority.

        Args:
            handler (telegram.ext.Handler): A Handler instance
            group (Optional[int]): The group identifier. Default is 0
        """

        if not isinstance(handler, Handler):
            raise TypeError('handler is not an instance of {0}'.format(Handler.__name__))
        if not isinstance(group, int):
            raise TypeError('group is not int')

        if group not in self.handlers:
            self.handlers[group] = list()
            self.groups.append(group)
            self.groups = sorted(self.groups)

        self.handlers[group].append(handler)

    def remove_handler(self, handler, group=DEFAULT_GROUP):
        """
        Remove a handler from the specified group

        Args:
            handler (telegram.ext.Handler): A Handler instance
            group (optional[object]): The group identifier. Default is 0
        """
        if handler in self.handlers[group]:
            self.handlers[group].remove(handler)
            if not self.handlers[group]:
                del self.handlers[group]
                self.groups.remove(group)

    def add_error_handler(self, callback):
        """
        Registers an error handler in the Dispatcher.

        Args:
            handler (function): A function that takes ``Bot, Update,
                TelegramError`` as arguments.
        """

        self.error_handlers.append(callback)

    def remove_error_handler(self, callback):
        """
        De-registers an error handler.

        Args:
            handler (function):
        """

        if callback in self.error_handlers:
            self.error_handlers.remove(callback)

    def dispatch_error(self, update, error):
        """
        Dispatches an error.

        Args:
            update (object): The update that caused the error
            error (telegram.TelegramError): The Telegram error that was raised.
        """

        for callback in self.error_handlers:
            callback(self.bot, update, error)

    # old non-PEP8 Dispatcher methods
    m = "telegram.dispatcher."
    addHandler = deprecate(add_handler, m + "AddHandler", m + "add_handler")
    removeHandler = deprecate(remove_handler, m + "removeHandler", m + "remove_handler")
    addErrorHandler = deprecate(add_error_handler, m + "addErrorHandler", m + "add_error_handler")
    removeErrorHandler = deprecate(remove_error_handler, m + "removeErrorHandler",
                                   m + "remove_error_handler")
