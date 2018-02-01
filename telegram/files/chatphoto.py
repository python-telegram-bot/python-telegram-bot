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
"""This module contains an object that represents a Telegram ChatPhoto."""

# TODO: add direct download shortcuts.

from telegram import TelegramObject


class ChatPhoto(TelegramObject):
    """This object represents a chat photo.

    Attributes:
        small_file_id (:obj:`str`): Unique file identifier of small (160x160) chat photo.
        big_file_id (:obj:`str`): Unique file identifier of big (640x640) chat photo.

    Args:
        small_file_id (:obj:`str`): Unique file identifier of small (160x160) chat photo. This
            file_id can be used only for photo download.
        big_file_id (:obj:`str`): Unique file identifier of big (640x640) chat photo. This file_id
            can be used only for photo download.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, small_file_id, big_file_id, bot=None, **kwargs):
        self.small_file_id = small_file_id
        self.big_file_id = big_file_id

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)
