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
from threading import Thread, BoundedSemaphore, Lock, Event, current_thread
from time import sleep

# Adjust for differences in Python versions
try:
    from queue import Empty  # flake8: noqa
except ImportError:
    from Queue import Empty  # flake8: noqa

from telegram import (TelegramError, NullHandler)
from telegram.ext.handler import Handler

logging.getLogger(__name__).addHandler(NullHandler())

semaphore = None
async_threads = set()
""":type: set[Thread]"""
async_lock = Lock()
DEFAULT_GROUP = 0


def run_async(func):
    """
    Function decorator that will run the function in a new thread.

    Args:
        func (function): The function to run in the thread.

    Returns:
        function:
    """

    # TODO: handle exception in async threads
    #       set a threading.Event to notify caller thread

    @wraps(func)
    def pooled(*pargs, **kwargs):
        """
        A wrapper to run a thread in a thread pool
        """
        result = func(*pargs, **kwargs)
        semaphore.release()
        with async_lock:
            async_threads.remove(current_thread())
        return result

    @wraps(func)
    def async_func(*pargs, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        thread = Thread(target=pooled, args=pargs, kwargs=kwargs)
        semaphore.acquire()
        with async_lock:
            async_threads.add(thread)
        thread.start()
        return thread

    return async_func


class Dispatcher(object):
    """
    This class dispatches all kinds of updates to its registered handlers.

    Args:
        bot (telegram.Bot): The bot object that should be passed to the
            handlers
        update_queue (telegram.UpdateQueue): The synchronized queue that will
            contain the updates.
    """
    def __init__(self, bot, update_queue, workers=4, exception_event=None):
        self.bot = bot
        self.update_queue = update_queue

        self.handlers = {}
        self.error_handlers = []

        self.logger = logging.getLogger(__name__)
        self.running = False
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()

        global semaphore
        if not semaphore:
            semaphore = BoundedSemaphore(value=workers)
        else:
            self.logger.debug('Semaphore already initialized, skipping.')

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

        while True:
            try:
                # Pop update from update queue.
                update = self.update_queue.get(True, 1)
            except Empty:
                if self.__stop_event.is_set():
                    self.logger.debug('orderly stopping')
                    break
                elif self.__exception_event.is_set():
                    self.logger.critical(
                        'stopping due to exception in another thread')
                    break
                continue

            self.logger.debug('Processing Update: %s' % update)
            self.processUpdate(update)

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

    def processUpdate(self, update):
        """
        Processes a single update.

        Args:
            update (any):
        """

        # An error happened while polling
        if isinstance(update, TelegramError):
            self.dispatchError(None, update)

        else:
            for group in self.handlers.values():
                handler_triggered = False

                for handler in group:
                    try:
                        if handler.checkUpdate(update):
                            handler_triggered = True
                            handler.handleUpdate(update, self)
                    # Dispatch any errors
                    except TelegramError as te:
                        self.logger.warn(
                            'Error was raised while processing Update.')

                        try:
                            self.dispatchError(update, te)
                        except:
                            self.logger.exception(
                                'An uncaught error was raised while '
                                'handling the error')

                    # Errors should not stop the thread
                    except:
                        self.logger.exception(
                            'An uncaught error was raised while '
                            'processing the update')

                    finally:
                        if handler_triggered:
                            break

    def addHandler(self, handler, group=DEFAULT_GROUP):
        """
        Register a handler. A handler must be an instance of a subclass of
        telegram.ext.Handler. All handlers are organized in groups, the default
        group is int(0), but any object can identify a group. Every update will
        be tested against each handler in each group from first-added to last-
        added. If the update has been handled in one group, it will not be
        tested against other handlers in that group. That means an update can
        only be handled 0 or 1 times per group, but multiple times across all
        groups.

        Args:
            handler (Handler): A Handler instance
            group (object): The group identifier
        """

        if not isinstance(handler, Handler):
            raise TypeError('Handler is no instance of telegram.ext.Handler')

        if group not in self.handlers:
            self.handlers[group] = list()

        self.handlers[group].append(handler)

    def removeHandler(self, handler, group=DEFAULT_GROUP):
        """
        Remove a handler from the specified group

        Args:
            handler (Handler): A Handler instance
            group (object): The group identifier
        """
        if handler in self.handlers[group]:
            self.handlers[group].remove(handler)

    def addErrorHandler(self, callback):
        """
        Registers an error handler in the Dispatcher.

        Args:
            handler (function): A function that takes (Bot, TelegramError) as
                arguments.
        """

        self.error_handlers.append(callback)

    def removeErrorHandler(self, callback):
        """
        De-registers an error handler.

        Args:
            handler (any):
        """

        if callback in self.error_handlers:
            self.error_handlers.remove(callback)

    def dispatchError(self, update, error):
        """
        Dispatches an error.

        Args:
            update (any): The update that caused the error
            error (telegram.TelegramError): The Telegram error that was raised.
        """

        for callback in self.error_handlers:
            callback(self.bot, update, error)
