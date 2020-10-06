#!/usr/bin/env python
# pylint: disable=R0903
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2020
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
"""This module contains an object that represents a type of a Telegram Poll."""
from telegram import TelegramObject
from typing import Any


class KeyboardButtonPollType(TelegramObject):
    """This object represents type of a poll, which is allowed to be created
    and sent when the corresponding button is pressed.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    Attributes:
        type (:obj:`str`): Optional. If :attr:`telegram.Poll.QUIZ` is passed, the user will be
            allowed to create only polls in the quiz mode. If :attr:`telegram.Poll.REGULAR` is
            passed, only regular polls will be allowed. Otherwise, the user will be allowed to
            create a poll of any type.
    """
    def __init__(self, type: str = None, **kwargs: Any):
        self.type = type

        self._id_attrs = (self.type,)
