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
"""This module contains the CommandHandler and PrefixHandler classes."""
import re
import warnings
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from telegram import MessageEntity, Update
from telegram.ext import BaseFilter, Filters
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.types import SLT
from telegram.utils.helpers import DefaultValue, DEFAULT_FALSE

from .utils.types import CCT
from .handler import Handler

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class CommandHandler(Handler[Update, CCT]):
    """Handler class to handle Telegram commands.

    Commands are Telegram messages that start with ``/``, optionally followed by an ``@`` and the
    bot's name and/or some additional text. The handler will add a ``list`` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single or consecutive whitespace characters.

    By default the handler listens to messages as well as edited messages. To change this behavior
    use ``~Filters.update.edited_message`` in the filter argument.

    Note:
        * :class:`CommandHandler` does *not* handle (edited) channel posts.
        * :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a :obj:`dict` you
          can use to keep any data in will be sent to the :attr:`callback` function. Related to
          either the user or the chat that the update was sent in. For each update from the same
          user or in the same chat, it will be the same :obj:`dict`.

          Note that this is DEPRECATED, and you should use context based callbacks. See
          https://github.com/python-telegram-bot/python-telegram-bot/wiki\
          /Transition-guide-to-Version-12.0 for more info.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        command (:class:`telegram.utils.types.SLT[str]`):
            The command or list of commands this handler should listen for.
            Limitations are the same as described here https://core.telegram.org/bots#commands
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).
        allow_edited (:obj:`bool`, optional): Determines whether the handler should also accept
            edited messages. Default is :obj:`False`.
            DEPRECATED: Edited is allowed by default. To change this behavior use
            ``~Filters.update.edited_message``.
        pass_args (:obj:`bool`, optional): Determines whether the handler should be passed the
            arguments passed to the command as a keyword argument called ``args``. It will contain
            a list of strings, which is the text following the command split on single or
            consecutive whitespace characters. Default is :obj:`False`
            DEPRECATED: Please switch to context based callbacks.
        pass_update_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Raises:
        ValueError: when command is too long or has illegal chars.

    Attributes:
        command (:class:`telegram.utils.types.SLT[str]`):
            The command or list of commands this handler should listen for.
            Limitations are the same as described here https://core.telegram.org/bots#commands
        callback (:obj:`callable`): The callback function for this handler.
        filters (:class:`telegram.ext.BaseFilter`): Optional. Only allow updates with these
            Filters.
        allow_edited (:obj:`bool`): Determines whether the handler should also accept
            edited messages.
        pass_args (:obj:`bool`): Determines whether the handler should be passed
            ``args``.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
    """

    __slots__ = ('command', 'filters', 'pass_args')

    def __init__(
        self,
        command: SLT[str],
        callback: Callable[[Update, CCT], RT],
        filters: BaseFilter = None,
        allow_edited: bool = None,
        pass_args: bool = False,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = False,
        pass_chat_data: bool = False,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async,
        )

        if isinstance(command, str):
            self.command = [command.lower()]
        else:
            self.command = [x.lower() for x in command]
        for comm in self.command:
            if not re.match(r'^[\da-z_]{1,32}$', comm):
                raise ValueError('Command is not a valid bot command')

        if filters:
            self.filters = Filters.update.messages & filters
        else:
            self.filters = Filters.update.messages

        if allow_edited is not None:
            warnings.warn(
                'allow_edited is deprecated. See '
                'https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition'
                '-guide-to-Version-12.0 for more info',
                TelegramDeprecationWarning,
                stacklevel=2,
            )
            if not allow_edited:
                self.filters &= ~Filters.update.edited_message
        self.pass_args = pass_args

    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`list`: The list of args for the handler.

        """
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if (
                message.entities
                and message.entities[0].type == MessageEntity.BOT_COMMAND
                and message.entities[0].offset == 0
                and message.text
                and message.bot
            ):
                command = message.text[1 : message.entities[0].length]
                args = message.text.split()[1:]
                command_parts = command.split('@')
                command_parts.append(message.bot.username)

                if not (
                    command_parts[0].lower() in self.command
                    and command_parts[1].lower() == message.bot.username.lower()
                ):
                    return None

                filter_result = self.filters(update)
                if filter_result:
                    return args, filter_result
                return False
        return None

    def collect_optional_args(
        self,
        dispatcher: 'Dispatcher',
        update: Update = None,
        check_result: Optional[Union[bool, Tuple[List[str], Optional[bool]]]] = None,
    ) -> Dict[str, object]:
        """Provide text after the command to the callback the ``args`` argument as list, split on
        single whitespaces.
        """
        optional_args = super().collect_optional_args(dispatcher, update)
        if self.pass_args and isinstance(check_result, tuple):
            optional_args['args'] = check_result[0]
        return optional_args

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: Optional[Union[bool, Tuple[List[str], Optional[bool]]]],
    ) -> None:
        """Add text after the command to :attr:`CallbackContext.args` as list, split on single
        whitespaces and add output of data filters to :attr:`CallbackContext` as well.
        """
        if isinstance(check_result, tuple):
            context.args = check_result[0]
            if isinstance(check_result[1], dict):
                context.update(check_result[1])


class PrefixHandler(CommandHandler):
    """Handler class to handle custom prefix commands.

    This is a intermediate handler between :class:`MessageHandler` and :class:`CommandHandler`.
    It supports configurable commands with the same options as CommandHandler. It will respond to
    every combination of :attr:`prefix` and :attr:`command`. It will add a ``list`` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single or consecutive whitespace characters.

    Examples:

        Single prefix and command:

        .. code:: python

            PrefixHandler('!', 'test', callback)  # will respond to '!test'.

        Multiple prefixes, single command:

        .. code:: python

            PrefixHandler(['!', '#'], 'test', callback)  # will respond to '!test' and '#test'.

        Multiple prefixes and commands:

        .. code:: python

            PrefixHandler(['!', '#'], ['test', 'help'], callback)  # will respond to '!test', \
            '#test', '!help' and '#help'.


    By default the handler listens to messages as well as edited messages. To change this behavior
    use ``~Filters.update.edited_message``.

    Note:
        * :class:`PrefixHandler` does *not* handle (edited) channel posts.
        * :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a :obj:`dict` you
          can use to keep any data in will be sent to the :attr:`callback` function. Related to
          either the user or the chat that the update was sent in. For each update from the same
          user or in the same chat, it will be the same :obj:`dict`.

          Note that this is DEPRECATED, and you should use context based callbacks. See
          https://github.com/python-telegram-bot/python-telegram-bot/wiki\
        /Transition-guide-to-Version-12.0 for more info.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        prefix (:class:`telegram.utils.types.SLT[str]`):
            The prefix(es) that will precede :attr:`command`.
        command (:class:`telegram.utils.types.SLT[str]`):
            The command or list of commands this handler should listen for.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).
        pass_args (:obj:`bool`, optional): Determines whether the handler should be passed the
            arguments passed to the command as a keyword argument called ``args``. It will contain
            a list of strings, which is the text following the command split on single or
            consecutive whitespace characters. Default is :obj:`False`
            DEPRECATED: Please switch to context based callbacks.
        pass_update_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        filters (:class:`telegram.ext.BaseFilter`): Optional. Only allow updates with these
            Filters.
        pass_args (:obj:`bool`): Determines whether the handler should be passed
            ``args``.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    # 'prefix' is a class property, & 'command' is included in the superclass, so they're left out.
    __slots__ = ('_prefix', '_command', '_commands')

    def __init__(
        self,
        prefix: SLT[str],
        command: SLT[str],
        callback: Callable[[Update, CCT], RT],
        filters: BaseFilter = None,
        pass_args: bool = False,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = False,
        pass_chat_data: bool = False,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):

        self._prefix: List[str] = []
        self._command: List[str] = []
        self._commands: List[str] = []

        super().__init__(
            'nocommand',
            callback,
            filters=filters,
            allow_edited=None,
            pass_args=pass_args,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async,
        )

        self.prefix = prefix  # type: ignore[assignment]
        self.command = command  # type: ignore[assignment]
        self._build_commands()

    @property
    def prefix(self) -> List[str]:
        """
        The prefixes that will precede :attr:`command`.

        Returns:
            List[:obj:`str`]
        """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: Union[str, List[str]]) -> None:
        if isinstance(prefix, str):
            self._prefix = [prefix.lower()]
        else:
            self._prefix = prefix
        self._build_commands()

    @property  # type: ignore[override]
    def command(self) -> List[str]:  # type: ignore[override]
        """
        The list of commands this handler should listen for.

        Returns:
            List[:obj:`str`]
        """
        return self._command

    @command.setter
    def command(self, command: Union[str, List[str]]) -> None:
        if isinstance(command, str):
            self._command = [command.lower()]
        else:
            self._command = command
        self._build_commands()

    def _build_commands(self) -> None:
        self._commands = [x.lower() + y.lower() for x in self.prefix for y in self.command]

    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`list`: The list of args for the handler.

        """
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if message.text:
                text_list = message.text.split()
                if text_list[0].lower() not in self._commands:
                    return None
                filter_result = self.filters(update)
                if filter_result:
                    return text_list[1:], filter_result
                return False
        return None
