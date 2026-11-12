#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains an object that represents a Telegram Bot Command."""

from typing import ClassVar

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class BotCommand(TelegramObject):
    """
    This object represents a bot command.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`command` and :attr:`description` are equal.

    Args:
        command (:obj:`str`): Text of the command; :tg-const:`telegram.BotCommand.MIN_COMMAND`-
            :tg-const:`telegram.BotCommand.MAX_COMMAND` characters. Can contain only lowercase
            English letters, digits and underscores.
        description (:obj:`str`): Description of the command;
            :tg-const:`telegram.BotCommand.MIN_DESCRIPTION`-
            :tg-const:`telegram.BotCommand.MAX_DESCRIPTION` characters.

    Attributes:
        command (:obj:`str`): Text of the command; :tg-const:`telegram.BotCommand.MIN_COMMAND`-
            :tg-const:`telegram.BotCommand.MAX_COMMAND` characters. Can contain only lowercase
            English letters, digits and underscores.
        description (:obj:`str`): Description of the command;
            :tg-const:`telegram.BotCommand.MIN_DESCRIPTION`-
            :tg-const:`telegram.BotCommand.MAX_DESCRIPTION` characters.

    """

    command: str = tg_field(compare=True)
    description: str = tg_field(compare=True)

    # TODO: https://docs.python.org/3.13/library/typing.html#typing.ClassVar
    MIN_COMMAND: ClassVar[int] = constants.BotCommandLimit.MIN_COMMAND
    """:const:`telegram.constants.BotCommandLimit.MIN_COMMAND`

    .. versionadded:: 20.0
    """
    MAX_COMMAND: ClassVar[int] = constants.BotCommandLimit.MAX_COMMAND
    """:const:`telegram.constants.BotCommandLimit.MAX_COMMAND`

    .. versionadded:: 20.0
    """
    MIN_DESCRIPTION: ClassVar[int] = constants.BotCommandLimit.MIN_DESCRIPTION
    """:const:`telegram.constants.BotCommandLimit.MIN_DESCRIPTION`

    .. versionadded:: 20.0
    """
    MAX_DESCRIPTION: ClassVar[int] = constants.BotCommandLimit.MAX_DESCRIPTION
    """:const:`telegram.constants.BotCommandLimit.MAX_DESCRIPTION`

    .. versionadded:: 20.0
    """
