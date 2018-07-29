#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
"""This module contains the classes that represent Telegram PassportElementError."""

from telegram import TelegramObject


class PassportElementError(TelegramObject):
    """Baseclass for the PassportElementError* classes.

    Attributes:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        message (:obj:`str`): Error message

    Args:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, source, type, message, **kwargs):
        # Required
        self.source = str(type)
        self.type = str(type)
        self.message = str(message)

        self._id_attrs = (self.source, self.type)
