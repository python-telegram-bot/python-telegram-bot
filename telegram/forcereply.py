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
"""This module contains a object that represents a Telegram ForceReply."""

from telegram import ReplyMarkup


class ForceReply(ReplyMarkup):
    """This object represents a Telegram ForceReply.

    Attributes:
        force_reply (bool):
        selective (bool):

    Args:
        force_reply (bool):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        selective (Optional[bool]):
    """

    def __init__(self, force_reply=True, **kwargs):
        # Required
        self.force_reply = bool(force_reply)
        # Optionals
        self.selective = bool(kwargs.get('selective', False))

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.ForceReply:
        """
        if not data:
            return None

        return ForceReply(**data)
