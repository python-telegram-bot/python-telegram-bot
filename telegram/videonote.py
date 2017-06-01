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
"""This module contains an object that represents a Telegram VideoNote."""

from telegram import PhotoSize, TelegramObject


class VideoNote(TelegramObject):
    """This object represents a Telegram VideoNote.

    Attributes:
        file_id (str): Unique identifier for this file
        length (int): Video width and height as defined by sender
        duration (int): Duration of the video in seconds as defined by sender
        thumb (Optional[:class:`telegram.PhotoSize`]): Video thumbnail
        file_size (Optional[int]): File size
    """

    def __init__(self, file_id, length, duration, thumb=None, file_size=None, **kwargs):
        # Required
        self.file_id = str(file_id)
        self.length = int(length)
        self.duration = int(duration)
        # Optionals
        self.thumb = thumb
        self.file_size = file_size

        self._id_attrs = (self.file_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.VideoNote:
        """
        if not data:
            return None

        data = super(VideoNote, VideoNote).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return VideoNote(**data)
