#!/usr/bin/env python

"""
This module contains the Broadcaster class.
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
    Function decorator that will run the function in a new thread.

    Args:
        func (function): The function to run in the thread.

    Returns:
        function:
    """

    @wraps(func)
    def pooled(*args, **kwargs):
        """
        A wrapper to run a thread in a thread pool
        """
        global running_async, async_lock
        result = func(*args, **kwargs)
        semaphore.release()
        with async_lock:
            running_async -= 1
        return result

    @wraps(func)
    def async_func(*args, **kwargs):
        """
        A wrapper to run a function in a thread
        """
        global running_async, async_lock
        thread = Thread(target=pooled, args=args, kwargs=kwargs)
        semaphore.acquire()
        with async_lock:
            running_async += 1
        thread.start()
        return thread

    return async_func


class Broadcaster:
    """
    This class broadcasts all kinds of updates to its registered handlers.

    A handler is a function that usually takes the following parameters:
        bot: The telegram.Bot instance that received the message
        update: The update that should be handled by the handler

    Error handlers take an additional parameter:
        error: The TelegramError instance that was raised during processing the
            update

    All handlers, except error handlers, can also request more information by
    appending one or more of the following arguments in their argument list for
    convenience:
        update_queue: The Queue instance which contains all new updates and is
            processed by the Broadcaster. Be careful with this - you might
            create an infinite loop.
        args: If the update is an instance str or telegram.Update, this will be
            a list that contains the content of the message split on spaces,
            except the first word (usually the command).
            Example: '/add item1 item2 item3' -> ['item1', 'item2', 'item3']
            For other updates, args will be None

    Attributes:

    Args:
        bot (telegram.Bot): The bot object that should be passed to the
        handlers update_queue (queue.Queue): The synchronized queue that will
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
        Thread target of thread 'broadcaster'. Runs in background and processes
        the update queue.
        """

        self.running = True
        self.logger.info('Broadcaster thread started')

        while True:
            update = None

            try:
                # Pop update from update queue.
                # Blocks if no updates are available.
                update = self.update_queue.get()

                if type(update) is self._Stop:
                    break

                self.processUpdate(update)

            # Broadcast any errors
            except TelegramError as te:
                self.broadcastError(update, te)

        self.logger.info('Broadcaster thread stopped')

    def stop(self):
        """
        Stops the thread
        """
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
                self.broadcastType(update)
                handled = True

        # string update
        if type(update) is str and update.startswith('/'):
            self.broadcastStringCommand(update)
            handled = True
        elif type(update) is str:
            self.broadcastStringRegex(update)
            handled = True

        # An error happened while polling
        if isinstance(update, TelegramError):
            self.broadcastError(None, update)
            handled = True

        # Telegram update (regex)
        if isinstance(update, Update):
            self.broadcastTelegramRegex(update)
            handled = True

        # Telegram update (command)
        if isinstance(update, Update) \
                and update.message.text.startswith('/'):
            self.broadcastTelegramCommand(update)
            handled = True

        # Telegram update (message)
        elif isinstance(update, Update):
            self.broadcastTelegramMessage(update)
            handled = True

        # Update not recognized
        if not handled:
            self.broadcastError(update, TelegramError(
                "Received update of unknown type %s" % type(update)))

    # Add Handlers
    def addTelegramMessageHandler(self, handler):
        """
        Registers a message handler in the Broadcaster.

        Args:
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        self.telegram_message_handlers.append(handler)

    def addTelegramCommandHandler(self, command, handler):
        """
        Registers a command handler in the Broadcaster.

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
        Registers a regex handler in the Broadcaster. If handlers will be
        called if re.match(matcher, update.message.text) is True.

        Args:
            matcher (__Regex): A regex string or compiled regex object that
                matches on messages that handler should be listening to
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        if matcher not in self.telegram_regex_handlers:
            self.telegram_regex_handlers[matcher] = []

        self.telegram_regex_handlers[matcher].append(handler)

    def addStringCommandHandler(self, command, handler):
        """
        Registers a string-command handler in the Broadcaster.

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
        Registers a regex handler in the Broadcaster. If handlers will be
        called if re.match(matcher, string) is True.

        Args:
            matcher (__Regex): A regex string or compiled regex object that
                matches on the string input that handler should be listening to
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        if matcher not in self.string_regex_handlers:
            self.string_regex_handlers[matcher] = []

        self.string_regex_handlers[matcher].append(handler)

    def addUnknownTelegramCommandHandler(self, handler):
        """
        Registers a command handler in the Broadcaster, that will receive all
        commands that have no associated handler.

        Args:
            handler (function): A function that takes (Bot, Update, *args) as
                arguments.
        """

        self.unknown_telegram_command_handlers.append(handler)

    def addUnknownStringCommandHandler(self, handler):
        """
        Registers a string-command handler in the Broadcaster, that will
        receive all commands that have no associated handler.

        Args:
            handler (function): A function that takes (Bot, str, *args) as
                arguments.
        """

        self.unknown_string_command_handlers.append(handler)

    def addErrorHandler(self, handler):
        """
        Registers an error handler in the Broadcaster.

        Args:
            handler (function): A function that takes (Bot, TelegramError) as
                arguments.
        """

        self.error_handlers.append(handler)

    def addTypeHandler(self, the_type, handler):
        """
        Registers a type handler in the Broadcaster. This allows you to send
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
            matcher (str): The regex matcher object
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
            matcher (str): The regex matcher object
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

    def broadcastTelegramCommand(self, update):
        """
        Broadcasts an update that contains a command.

        Args:
            command (str): The command keyword
            update (telegram.Update): The Telegram update that contains the
                command
        """

        command = update.message.text.split(' ')[0][1:].split('@')[0]

        if command in self.telegram_command_handlers:
            self.broadcastTo(self.telegram_command_handlers[command], update)
        else:
            self.broadcastTo(self.unknown_telegram_command_handlers, update)

    def broadcastTelegramRegex(self, update):
        """
        Broadcasts an update to all regex handlers that match the message
        string.

        Args:
            command (str): The command keyword
            update (telegram.Update): The Telegram update that contains the
                command
        """

        matching_handlers = []

        for matcher in self.telegram_regex_handlers:
            if match(matcher, update.message.text):
                for handler in self.telegram_regex_handlers[matcher]:
                    matching_handlers.append(handler)

        self.broadcastTo(matching_handlers, update)

    def broadcastStringCommand(self, update):
        """
        Broadcasts a string-update that contains a command.

        Args:
            update (str): The string input
        """

        command = update.split(' ')[0][1:]

        if command in self.string_command_handlers:
            self.broadcastTo(self.string_command_handlers[command], update)
        else:
            self.broadcastTo(self.unknown_string_command_handlers, update)

    def broadcastStringRegex(self, update):
        """
        Broadcasts an update to all string regex handlers that match the
        string.

        Args:
            command (str): The command keyword
            update (telegram.Update): The Telegram update that contains the
                command
        """

        matching_handlers = []

        for matcher in self.string_regex_handlers:
            if match(matcher, update):
                for handler in self.string_regex_handlers[matcher]:
                    matching_handlers.append(handler)

        self.broadcastTo(matching_handlers, update)

    def broadcastType(self, update):
        """
        Broadcasts an update of any type.

        Args:
            update (any): The update
        """

        for t in self.type_handlers:
            if isinstance(update, t):
                self.broadcastTo(self.type_handlers[t], update)
        else:
            self.broadcastError(update, TelegramError(
                "Received update of unknown type %s" % type(update)))

    def broadcastTelegramMessage(self, update):
        """
        Broadcasts an update that contains a regular message.

        Args:
            update (telegram.Update): The Telegram update that contains the
                message.
        """

        self.broadcastTo(self.telegram_message_handlers, update)

    def broadcastError(self, update, error):
        """
        Broadcasts an error.

        Args:
            update (any): The pdate that caused the error
            error (telegram.TelegramError): The Telegram error that was raised.
        """

        for handler in self.error_handlers:
            handler(self.bot, update, error)

    def broadcastTo(self, handlers, update):
        """
        Broadcasts an update to a list of handlers.

        Args:
            handlers (list): A list of handler-functions.
            update (any): The update to be broadcasted
        """

        for handler in handlers:
            self.call_handler(handler, update)

    def call_handler(self, handler, update):
        """
        Calls an update handler. Checks the handler for keyword arguments and
        fills them, if possible.

        Args:
            handler (function): An update handler function
            update (any): An update
        """
        kwargs = {}
        fargs = getargspec(handler).args

        if 'update_queue' in fargs:
            kwargs['update_queue'] = self.update_queue
        elif 'args' in fargs:
            if isinstance(update, Update):
                args = update.message.text.split(' ')[1:]
            elif isinstance(update, str):
                args = update.split(' ')[1:]
            else:
                args = None

            kwargs['args'] = args

        handler(self.bot, update, **kwargs)
