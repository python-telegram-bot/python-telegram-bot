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
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, TypeVar, Union

from telegram import MessageEntity, Update
from telegram._utils.defaultvalue import DEFAULT_TRUE
from telegram._utils.types import SLT, DVInput
from telegram.ext import filters as filters_module
from telegram.ext._handler import Handler
from telegram.ext._utils.types import CCT, HandlerCallback

if TYPE_CHECKING:
    from telegram.ext import Application

RT = TypeVar("RT")


class CommandHandler(Handler[Update, CCT]):
    """Handler class to handle Telegram commands.

    Commands are Telegram messages that start with ``/``, optionally followed by an ``@`` and the
    bot's name and/or some additional text. The handler will add a :obj:`list` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single or consecutive whitespace characters.

    By default, the handler listens to messages as well as edited messages. To change this behavior
    use :attr:`~filters.UpdateType.EDITED_MESSAGE <telegram.ext.filters.UpdateType.EDITED_MESSAGE>`
    in the filter argument.

    Note:
        * :class:`CommandHandler` does *not* handle (edited) channel posts.

    Warning:
        When setting :paramref:`block` to :obj:`False`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        command (:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`]):
            The command or list of commands this handler should listen for.
            Limitations are the same as described `here <https://core.telegram.org/bots#commands>`_
        callback (:term:`coroutine function`): The callback function for this handler. Will be
            called when :meth:`check_update` has determined that an update should be processed by
            this handler. Callback signature::

                async def callback(update: Update, context: CallbackContext)

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.filters.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :mod:`telegram.ext.filters`. Filters can be combined using bitwise
            operators (``&`` for :keyword:`and`, ``|`` for :keyword:`or`, ``~`` for :keyword:`not`)
        block (:obj:`bool`, optional): Determines whether the return value of the callback should
            be awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`. Defaults to :obj:`True`.

    Raises:
        :exc:`ValueError`: When the command is too long or has illegal chars.

    Attributes:
        command (:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`]):
            The command or list of commands this handler should listen for.
            Limitations are the same as described `here <https://core.telegram.org/bots#commands>`_
        callback (:term:`coroutine function`): The callback function for this handler.
        filters (:class:`telegram.ext.filters.BaseFilter`): Optional. Only allow updates with these
            Filters.
        block (:obj:`bool`): Determines whether the return value of the callback should be
            awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`.
    """

    __slots__ = ("command", "filters")

    def __init__(
        self,
        command: SLT[str],
        callback: HandlerCallback[Update, CCT, RT],
        filters: filters_module.BaseFilter = None,
        block: DVInput[bool] = DEFAULT_TRUE,
    ):
        super().__init__(callback, block=block)

        if isinstance(command, str):
            self.command = [command.lower()]
        else:
            self.command = [x.lower() for x in command]
        for comm in self.command:
            if not re.match(r"^[\da-z_]{1,32}$", comm):
                raise ValueError(f"Command `{comm}` is not a valid bot command")

        self.filters = filters if filters is not None else filters_module.UpdateType.MESSAGES

    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        """Determines whether an update should be passed to this handler's :attr:`callback`.

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
                and message.get_bot()
            ):
                command = message.text[1 : message.entities[0].length]
                args = message.text.split()[1:]
                command_parts = command.split("@")
                command_parts.append(message.get_bot().username)

                if not (
                    command_parts[0].lower() in self.command
                    and command_parts[1].lower() == message.get_bot().username.lower()
                ):
                    return None

                filter_result = self.filters.check_update(update)
                if filter_result:
                    return args, filter_result
                return False
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,
        application: "Application",
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

    This is an intermediate handler between :class:`MessageHandler` and :class:`CommandHandler`.
    It supports configurable commands with the same options as :class:`CommandHandler`. It will
    respond to every combination of :attr:`prefix` and :attr:`command`. It will add a :obj:`list`
    to the :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of
    strings, which is the text following the command split on single or consecutive whitespace
    characters.

    Examples:

        Single prefix and command:

        .. code:: python

            PrefixHandler("!", "test", callback)  # will respond to '!test'.

        Multiple prefixes, single command:

        .. code:: python

            PrefixHandler(["!", "#"], "test", callback)  # will respond to '!test' and '#test'.

        Multiple prefixes and commands:

        .. code:: python

            PrefixHandler(
                ["!", "#"], ["test", "help"], callback
            )  # will respond to '!test', '#test', '!help' and '#help'.


    By default, the handler listens to messages as well as edited messages. To change this behavior
    use :attr:`~filters.UpdateType.EDITED_MESSAGE <telegram.ext.filters.UpdateType.EDITED_MESSAGE>`

    Note:
        * :class:`PrefixHandler` does *not* handle (edited) channel posts.

    Warning:
        When setting :paramref:`block` to :obj:`False`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        prefix (:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`]):
            The prefix(es) that will precede :attr:`command`.
        command (:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`]):
            The command or list of commands this handler should listen for.
        callback (:term:`coroutine function`): The callback function for this handler. Will be
            called when :meth:`check_update` has determined that an update should be processed by
            this handler. Callback signature::

                async def callback(update: Update, context: CallbackContext)

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.filters.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :mod:`telegram.ext.filters`. Filters can be combined using bitwise
            operators (``&`` for :keyword:`and`, ``|`` for :keyword:`or`, ``~`` for :keyword:`not`)
        block (:obj:`bool`, optional): Determines whether the return value of the callback should
            be awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`. Defaults to :obj:`True`.

    Attributes:
        callback (:term:`coroutine function`): The callback function for this handler.
        filters (:class:`telegram.ext.filters.BaseFilter`): Optional. Only allow updates with these
            Filters.
        block (:obj:`bool`): Determines whether the return value of the callback should be
            awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`.

    """

    # 'prefix' is a class property, & 'command' is included in the superclass, so they're left out.
    __slots__ = ("_prefix", "_command", "_commands")

    def __init__(
        self,
        prefix: SLT[str],
        command: SLT[str],
        callback: HandlerCallback[Update, CCT, RT],
        filters: filters_module.BaseFilter = None,
        block: DVInput[bool] = DEFAULT_TRUE,
    ):

        self._prefix: List[str] = []
        self._command: List[str] = []
        self._commands: List[str] = []

        super().__init__(
            "nocommand",
            callback,
            filters=filters,
            block=block,
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
        """Determines whether an update should be passed to this handler's :attr:`callback`.

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
                filter_result = self.filters.check_update(update)
                if filter_result:
                    return text_list[1:], filter_result
                return False
        return None
