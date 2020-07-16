#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
from telegram import TelegramObject

from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot, File


class ChatPhoto(TelegramObject):
    """This object represents a chat photo.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`small_file_unique_id` and :attr:`big_file_unique_id` are
    equal.

    Attributes:
        small_file_id (:obj:`str`): File identifier of small (160x160) chat photo.
            This file_id can be used only for photo download and only for as long
            as the photo is not changed.
        small_file_unique_id (:obj:`str`): Unique file identifier of small (160x160) chat photo,
            which is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        big_file_id (:obj:`str`): File identifier of big (640x640) chat photo.
            This file_id can be used only for photo download and only for as long as
            the photo is not changed.
        big_file_unique_id (:obj:`str`): Unique file identifier of big (640x640) chat photo,
            which is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
    Args:
        small_file_id (:obj:`str`): Unique file identifier of small (160x160) chat photo. This
            file_id can be used only for photo download and only for as long
            as the photo is not changed.
        small_file_unique_id (:obj:`str`): Unique file identifier of small (160x160) chat photo,
            which is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        big_file_id (:obj:`str`): Unique file identifier of big (640x640) chat photo. This file_id
            can be used only for photo download and only for as long as the photo is not changed.
        big_file_unique_id (:obj:`str`): Unique file identifier of big (640x640) chat photo,
            which is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 small_file_id: str,
                 small_file_unique_id: str,
                 big_file_id: str,
                 big_file_unique_id: str,
                 bot: 'Bot' = None,
                 **kwargs: Any):
        self.small_file_id = small_file_id
        self.small_file_unique_id = small_file_unique_id
        self.big_file_id = big_file_id
        self.big_file_unique_id = big_file_unique_id

        self.bot = bot

        self._id_attrs = (self.small_file_unique_id, self.big_file_unique_id,)

    def get_small_file(self, timeout: int = None, **kwargs: Any) -> 'File':
        """Convenience wrapper over :attr:`telegram.Bot.get_file` for getting the
        small (160x160) chat photo

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.TelegramError`

        """
        return self.bot.get_file(self.small_file_id, timeout=timeout, **kwargs)

    def get_big_file(self, timeout: int = None, **kwargs: Any) -> 'File':
        """Convenience wrapper over :attr:`telegram.Bot.get_file` for getting the
        big (640x640) chat photo

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.TelegramError`

        """
        return self.bot.get_file(self.big_file_id, timeout=timeout, **kwargs)
