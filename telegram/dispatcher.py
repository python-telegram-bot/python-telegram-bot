#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <devs@python-telegram-bot.org>
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


"""
This module contains the Dispatcher class.
"""
import logging
from functools import wraps
from inspect import getargspec
from threading import Thread, BoundedSemaphore, Lock
from re import match

from telegram import (TelegramError, Update, NullHandler)

H = NullHandler()
logging.getLogger(__name__).addHandler(H)

semaphore = None
running_async = 0
async_lock = Lock()


def run_async(func):
    """
    Function decorator that will run the function in a new thread. A function
    decorated with this will have to include **kwargs in their parameter list,
    which will contain all optional parameters.

    Args:
        func (function): The function to run in the thread.

    Returns:
        function:
    """

    @wraps(func)
    def pooled(*pargs, **kwargs):
        """
        A wrapper to run a thread in a thread pool
        """
        global running_async, async_lock
        result = func(*pargs, **kwargs)
        semaphore.release()
        with async_lock:
            running_async -= 1
        return result

    @wraps(func)
    def async_func(*pargs, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        global running_async, async_lock
        thread = Thread(target=pooled, args=pargs, kwargs=kwargs)
        semaphore.acquire()
        with async_lock:
            running_async += 1
        thread.start()
        return thread

    return async_func


class Dispatcher:
    """
    This class dispatches all kinds of updates to its registered handlers.
    A handler is a function that usually takes the following parameters

        bot:
            The telegram.Bot instance that received the message
        update:
            The update that should be handled by the handler

    Error handlers take an additional parameter

        error:
            The TelegramError instance that was raised during processing the
            update

    All handlers, except error handlers, can also request more information by
    appending one or more of the following arguments in their argument list for
    convenience

        update_queue:
            The Queue instance which contains all new updates and is
            processed by the Dispatcher. Be careful with this - you might
            create an infinite loop.
        args:
            If the update is an instance str or telegram.Update, this will be
            a list that contains the content of the message split on spaces,
            except the first word (usually the command).
            Example: '/add item1 item2 item3' -> ['item1', 'item2', 'item3']
            For other updates, args will be None

    For regex-based handlers, you can also request information about the match.
    For all other handlers, these will be None

        groups:
            A tuple that contains the result of
            re.match(matcher, ...).groups()
        groupdict:
            A dictionary that contains the result of
            re.match(matcher, ...).groupdict()

    Args:
        bot (telegram.Bot): The bot object that should be passed to the
            handlers
        update_queue (queue.Queue): The synchronized queue that will
            contain the updates.
    """
    def __init__(self, bot, update_queue, workers=4):
        self.bot = bot
        self.update_queue = update_queue
        self.telegram_message_handlers = []
        self.telegram_command_handlers = {}
        self.telegram_regex_handlers = {}
        self.string_regex_handlers = {}
        self.string_command_handlers = {}
        self.type_handlers = {}
        self.unknown_telegram_command_handlers = []
        self.unknown_string_command_handlers = []
        self.error_handlers = []
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.__lock = Lock()

        global semaphore
        if not semaphore:
            semaphore = BoundedSemaphore(value=workers)
        else:
            self.logger.info("Semaphore already initialized, skipping.")

    class _Stop(object):
        """
        A class which objects can be passed into the update queue to stop the
        thread
        """
        pass

    def start(self):
        """
        Thread target of thread 'dispatcher'. Runs in background and processes
        the update queue.
        """

        self.__lock.acquire()
        if not self.running:
            self.running = True
            self.__lock.release()
            self.logger.info('Dispatcher thread started')

            while True:
                update = None

                try:
                    # Pop update from update queue.
                    # Blocks if no updates are available.
                    update = self.update_queue.get()

                    if type(update) is self._Stop:
                        break

                    self.processUpdate(update)
                    self.logger.debug('Processed Update: %s' % update)

                # Dispatch any errors
                except TelegramError as te:
                    self.logger.warn("Error was raised while processing "
                                     "Update.")
                    self.dispatchError(update, te)

                # All other errors should not stop the thread, just print them
                except:
                    self.logger.exception("An uncaught error was raised while "
                                          "processing an update")
        else:
            self.__lock.release()
        self.logger.info('Dispatcher thread stopped')

    def stop(self):
        """
        Stops the thread
        """
        with self.__lock:
            if self.running:
                self.running = False
                self.update_queue.put(self._Stop())

    def processUpdate(self, update):
        """
        Processes a single update.

        Args:
            update (any):
        """

        handled = False

        # Custom type handlers
        for t in self.type_handlers:
            if isinstance(update, t):
                self.dispatchType(update)
                handled = True

        # string update
        if type(update) is str and update.startswith('/'):
            self.dispatchStringCommand(update)
            handled = True
        elif type(update) is str:
            self.dispatchRegex(update)
            handled = True

        # An error happened while polling
        if isinstance(update, TelegramError):
            self.dispatchError(None, update)
            handled = True

        # Telegram update (regex)
        if isinstance(update, Update):
            self.dispatchRegex(update)
            handled = True

        # Telegram update (command)
        if isinstance(update, Update) \
                and update.message.text.startswith('/'):
            self.dispatchTelegramCommand(update)
            handled = True

        # Telegram update (message)
        elif isinstance(update, Update):
            self.dispatchTelegramMessage(update)
            handled = True

        # Update not recognized
        if not handled:
            self.dispatchError(update, TelegramError(
                "Received update of unknown type %s" % type(update)))

    # Add Handlers
    def addTelegramMessageHandler(self, handler):
        """
        Registers a message handler in the Dispatcher.

        Args:
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        self.telegram_message_handlers.append(handler)

    def addTelegramCommandHandler(self, command, handler):
        """
        Registers a command handler in the Dispatcher.

        Args:
            command (str): The command keyword that this handler should be
                listening to.
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        if command not in self.telegram_command_handlers:
            self.telegram_command_handlers[command] = []

        self.telegram_command_handlers[command].append(handler)

    def addTelegramRegexHandler(self, matcher, handler):
        """
        Registers a regex handler in the Dispatcher. If handlers will be
        called if re.match(matcher, update.message.text) is True.

        Args:
            matcher (str/__Regex): A regex string or compiled regex object that
                matches on messages that handler should be listening to
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        if matcher not in self.telegram_regex_handlers:
            self.telegram_regex_handlers[matcher] = []

        self.telegram_regex_handlers[matcher].append(handler)

    def addStringCommandHandler(self, command, handler):
        """
        Registers a string-command handler in the Dispatcher.

        Args:
            command (str): The command keyword that this handler should be
                listening to.
            handler (function): A function that takes (Bot, str, *args) as
                arguments.
        """

        if command not in self.string_command_handlers:
            self.string_command_handlers[command] = []

        self.string_command_handlers[command].append(handler)

    def addStringRegexHandler(self, matcher, handler):
        """
        Registers a regex handler in the Dispatcher. If handlers will be
        called if re.match(matcher, string) is True.

        Args:
            matcher (str/__Regex): A regex string or compiled regex object that
                matches on the string input that handler should be listening to
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        if matcher not in self.string_regex_handlers:
            self.string_regex_handlers[matcher] = []

        self.string_regex_handlers[matcher].append(handler)

    def addUnknownTelegramCommandHandler(self, handler):
        """
        Registers a command handler in the Dispatcher, that will receive all
        commands that have no associated handler.

        Args:
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        self.unknown_telegram_command_handlers.append(handler)

    def addUnknownStringCommandHandler(self, handler):
        """
        Registers a string-command handler in the Dispatcher, that will
        receive all commands that have no associated handler.

        Args:
            handler (function): A function that takes (Bot, str, *args) as
                arguments.
        """

        self.unknown_string_command_handlers.append(handler)

    def addErrorHandler(self, handler):
        """
        Registers an error handler in the Dispatcher.

        Args:
            handler (function): A function that takes (Bot, TelegramError) as
                arguments.
        """

        self.error_handlers.append(handler)

    def addTypeHandler(self, the_type, handler):
        """
        Registers a type handler in the Dispatcher. This allows you to send
        any type of object into the update queue.

        Args:
            the_type (type): The type this handler should listen to
            handler (function): A function that takes (Bot, type, *args) as
                arguments.
        """

        if the_type not in self.type_handlers:
            self.type_handlers[the_type] = []

        self.type_handlers[the_type].append(handler)

    # Remove Handlers
    def removeTelegramMessageHandler(self, handler):
        """
        De-registers a message handler.

        Args:
            handler (any):
        """

        if handler in self.telegram_message_handlers:
            self.telegram_message_handlers.remove(handler)

    def removeTelegramCommandHandler(self, command, handler):
        """
        De-registers a command handler.

        Args:
            command (str): The command
            handler (any):
        """

        if command in self.telegram_command_handlers \
                and handler in self.telegram_command_handlers[command]:
            self.telegram_command_handlers[command].remove(handler)

    def removeTelegramRegexHandler(self, matcher, handler):
        """
        De-registers a regex handler.

        Args:
            matcher (str/__Regex): The regex matcher object or string
            handler (any):
        """

        if matcher in self.telegram_regex_handlers \
                and handler in self.telegram_regex_handlers[matcher]:
            self.telegram_regex_handlers[matcher].remove(handler)

    def removeStringCommandHandler(self, command, handler):
        """
        De-registers a string-command handler.

        Args:
            command (str): The command
            handler (any):
        """

        if command in self.string_command_handlers \
                and handler in self.string_command_handlers[command]:
            self.string_command_handlers[command].remove(handler)

    def removeStringRegexHandler(self, matcher, handler):
        """
        De-registers a regex handler.

        Args:
            matcher (str/__Regex): The regex matcher object or string
            handler (any):
        """

        if matcher in self.string_regex_handlers \
                and handler in self.string_regex_handlers[matcher]:
            self.string_regex_handlers[matcher].remove(handler)

    def removeUnknownTelegramCommandHandler(self, handler):
        """
        De-registers an unknown-command handler.

        Args:
            handler (any):
        """

        if handler in self.unknown_telegram_command_handlers:
            self.unknown_telegram_command_handlers.remove(handler)

    def removeUnknownStringCommandHandler(self, handler):
        """
        De-registers an unknown-command handler.

        Args:
            handler (any):
        """

        if handler in self.unknown_string_command_handlers:
            self.unknown_string_command_handlers.remove(handler)

    def removeErrorHandler(self, handler):
        """
        De-registers an error handler.

        Args:
            handler (any):
        """

        if handler in self.error_handlers:
            self.error_handlers.remove(handler)

    def removeTypeHandler(self, the_type, handler):
        """
        De-registers a type handler.

        Args:
            handler (any):
        """

        if the_type in self.type_handlers \
                and handler in self.type_handlers[the_type]:
            self.type_handlers[the_type].remove(handler)

    def dispatchTelegramCommand(self, update):
        """
        Dispatches an update that contains a command.

        Args:
            command (str): The command keyword
            update (telegram.Update): The Telegram update that contains the
                command
        """

        command = update.message.text.split(' ')[0][1:].split('@')[0]

        if command in self.telegram_command_handlers:
            self.dispatchTo(self.telegram_command_handlers[command], update)
        else:
            self.dispatchTo(self.unknown_telegram_command_handlers, update)

    def dispatchRegex(self, update):
        """
        Dispatches an update to all string or telegram regex handlers that
        match the string/message content.

        Args:
            update (str, Update): The update that should be checked for matches
        """

        if isinstance(update, Update):
            handlers = self.telegram_regex_handlers
            to_match = update.message.text
        elif isinstance(update, str):
            handlers = self.string_regex_handlers
            to_match = update

        for matcher in handlers:
            m = match(matcher, to_match)
            if m:
                for handler in handlers[matcher]:
                    self.call_handler(handler,
                                      update,
                                      groups=m.groups(),
                                      groupdict=m.groupdict())

    def dispatchStringCommand(self, update):
        """
        Dispatches a string-update that contains a command.

        Args:
            update (str): The string input
        """

        command = update.split(' ')[0][1:]

        if command in self.string_command_handlers:
            self.dispatchTo(self.string_command_handlers[command], update)
        else:
            self.dispatchTo(self.unknown_string_command_handlers, update)

    def dispatchType(self, update):
        """
        Dispatches an update of any type.

        Args:
            update (any): The update
        """

        for t in self.type_handlers:
            if isinstance(update, t):
                self.dispatchTo(self.type_handlers[t], update)

    def dispatchTelegramMessage(self, update):
        """
        Dispatches an update that contains a regular message.

        Args:
            update (telegram.Update): The Telegram update that contains the
                message.
        """

        self.dispatchTo(self.telegram_message_handlers, update)

    def dispatchError(self, update, error):
        """
        Dispatches an error.

        Args:
            update (any): The pdate that caused the error
            error (telegram.TelegramError): The Telegram error that was raised.
        """

        for handler in self.error_handlers:
            handler(self.bot, update, error)

    def dispatchTo(self, handlers, update, **kwargs):
        """
        Dispatches an update to a list of handlers.

        Args:
            handlers (list): A list of handler-functions.
            update (any): The update to be dispatched
        """

        for handler in handlers:
            self.call_handler(handler, update, **kwargs)

    def call_handler(self, handler, update, **kwargs):
        """
        Calls an update handler. Checks the handler for keyword arguments and
        fills them, if possible.

        Args:
            handler (function): An update handler function
            update (any): An update
        """

        target_kwargs = {}
        fargs = getargspec(handler).args

        '''
        async handlers will receive all optional arguments, since we can't
        their argument list.
        '''

        is_async = 'pargs' == getargspec(handler).varargs

        if is_async or 'update_queue' in fargs:
            target_kwargs['update_queue'] = self.update_queue

        if is_async or 'args' in fargs:
            if isinstance(update, Update):
                args = update.message.text.split(' ')[1:]
            elif isinstance(update, str):
                args = update.split(' ')[1:]
            else:
                args = None

            target_kwargs['args'] = args

        if is_async or 'groups' in fargs:
            target_kwargs['groups'] = kwargs.get('groups', None)

        if is_async or 'groupdict' in fargs:
            target_kwargs['groupdict'] = kwargs.get('groupdict', None)

        handler(self.bot, update, **target_kwargs)
