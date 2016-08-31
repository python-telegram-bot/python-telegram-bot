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
from functools import wraps
from threading import Thread, Lock, Event, current_thread
from dummy_threading import Lock as DummyLock
from time import sleep
from queue import Queue, Empty

from future.builtins import range

from telegram import TelegramError
from telegram.ext.handler import Handler
from telegram.utils.deprecate import deprecate
from telegram.utils.promise import Promise

logging.getLogger(__name__).addHandler(logging.NullHandler())

_ASYNC_QUEUE = Queue()
_ASYNC_THREADS = set()
""":type: set[Thread]"""
DEFAULT_GROUP = 0


def run_async(func, async_queue=_ASYNC_QUEUE):
    """
    Function decorator that will run the function in a new thread.

    Args:
        func (function): The function to run in the thread.
        aysnc_queue (Queue): The queue of the functions to be executed asynchronously.

    Returns:
        function:

    """
    # TODO: handle exception in async threads
    #       set a threading.Event to notify caller thread

    @wraps(func)
    def async_func(*args, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        promise = Promise(func, args, kwargs)
        async_queue.put(promise)
        return promise

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
        no_singleton (Optional[bool]): Set this to True if you need more than one dispatcher
            instance. Dispatchers created that way do not support the global `run_async` decorator.

    """
    __async_lock = Lock()  # guards singleton constructor

    def __init__(self, bot, update_queue, workers=4, exception_event=None, job_queue=None,
                 no_singleton=False):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue

        self.handlers = {}
        """:type: dict[int, list[Handler]"""
        self.groups = []
        """:type: list[int]"""
        self.error_handlers = []

        self.logger = logging.getLogger(__name__)
        self.running = False
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()

        if not no_singleton:
            self.__async_lock = DummyLock()
            self.__async_queue = Queue()
            self.__async_threads = set()
            self._init_async_threads(workers)
        else:
            self.__async_queue = _ASYNC_QUEUE
            self.__async_threads = _ASYNC_THREADS
            with self.__async_lock:
                if self.__async_threads:
                    raise RuntimeError('Dispatcher singleton already initialized')
                self._init_async_threads(workers)

    def _init_async_threads(self, workers):
        for i in range(workers):
            thread = Thread(target=self._pooled, name=str(i))
            _ASYNC_THREADS.add(thread)
            thread.start()

    def _pooled(self):
        """
        A wrapper to run a thread in a thread pool
        """
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                logging.getLogger(__name__).debug(
                    "Closing run_async thread %s/%d",
                    (current_thread().getName(), len(self.__async_threads)))
                break

            try:
                promise.run()

            except:
                logging.getLogger(__name__).exception("run_async function raised exception")

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
        with self.__async_lock:
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
            handler (Handler): A Handler instance
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
            handler (Handler): A Handler instance
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
