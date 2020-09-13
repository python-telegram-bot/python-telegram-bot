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
"""This module contains an object that represents a Telegram Voice."""

from telegram import TelegramObject
from telegram.utils.types import JSONDict
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot, File


class Voice(TelegramObject):
    """This object represents a voice note.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Attributes:
        file_id (:obj:`str`): Identifier for this file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        duration (:obj:`int`): Duration of the audio in seconds as defined by sender.
        mime_type (:obj:`str`): Optional. MIME type of the file as defined by sender.
        file_size (:obj:`int`): Optional. File size.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        duration (:obj:`int`, optional): Duration of the audio in seconds as defined by sender.
        mime_type (:obj:`str`, optional): MIME type of the file as defined by sender.
        file_size (:obj:`int`, optional): File size.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 file_id: str,
                 file_unique_id: str,
                 duration: int,
                 mime_type: str = None,
                 file_size: int = None,
                 bot: 'Bot' = None,
                 **kwargs: Any):
        # Required
        self.file_id = str(file_id)
        self.file_unique_id = str(file_unique_id)
        self.duration = int(duration)
        # Optionals
        self.mime_type = mime_type
        self.file_size = file_size
        self.bot = bot

        self._id_attrs = (self.file_unique_id,)

    def get_file(self, timeout: int = None, api_kwargs: JSONDict = None) -> 'File':
        """Convenience wrapper over :attr:`telegram.Bot.get_file`

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
        return self.bot.get_file(self.file_id, timeout=timeout, api_kwargs=api_kwargs)
