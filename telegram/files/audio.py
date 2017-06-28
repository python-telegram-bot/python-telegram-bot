#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains an object that represents a Telegram Audio."""

from telegram import TelegramObject


class Audio(TelegramObject):
    """
    This object represents an audio file to be treated as music by the Telegram clients.

    Attributes:
        file_id (str): Unique identifier for this file.
        duration (int): Duration of the audio in seconds as defined by sender.
        performer (str): Optional. Performer of the audio as defined by sender or by audio tags.
        title (str): Optional. Title of the audio as defined by sender or by audio tags.
        mime_type (str): Optional. MIME type of the file as defined by sender.
        file_size (int): Optional. File size.

    Args:
        file_id (str): Unique identifier for this file.
        duration (int): Duration of the audio in seconds as defined by sender.
        performer (Optional[str]): Performer of the audio as defined by sender or by audio tags.
        title (Optional[str]): Title of the audio as defined by sender or by audio tags.
        mime_type (Optional[str]): MIME type of the file as defined by sender.
        file_size (Optional[int]): File size.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self,
                 file_id,
                 duration,
                 performer=None,
                 title=None,
                 mime_type=None,
                 file_size=None,
                 **kwargs):
        # Required
        self.file_id = str(file_id)
        self.duration = int(duration)
        # Optionals
        self.performer = performer
        self.title = title
        self.mime_type = mime_type
        self.file_size = file_size

        self._id_attrs = (self.file_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (:class:`telegram.Bot`):

        Returns:
            :class:`telegram.Audio`
        """

        if not data:
            return None

        return Audio(**data)
