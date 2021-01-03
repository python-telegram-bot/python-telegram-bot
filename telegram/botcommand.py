#!/usr/bin/env python
# pylint: disable=R0903
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
from typing import Any

from telegram import TelegramObject


class BotCommand(TelegramObject):
    """
    This object represents a bot command.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`command` and :attr:`description` are equal.

    Args:
        command (:obj:`str`): Text of the command, 1-32 characters. Can contain only lowercase
            English letters, digits and underscores.
        description (:obj:`str`): Description of the command, 3-256 characters.

    Attributes:
        command (:obj:`str`): Text of the command.
        description (:obj:`str`): Description of the command.

    """

    def __init__(self, command: str, description: str, **_kwargs: Any):
        self.command = command
        self.description = description

        self._id_attrs = (self.command, self.description)
