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
    """This object represents a video message (available in Telegram apps as of v.4.0).

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file.
        length (:obj:`int`): Video width and height as defined by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`): Optional. Video thumbnail.
        file_size (:obj:`int`): Optional. File size.

    Args:
        file_id (:obj:`str`): Unique identifier for this file.
        length (:obj:`int`): Video width and height as defined by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`, optional): Video thumbnail.
        file_size (:obj:`int`, optional): File size.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(VideoNote, cls).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return cls(**data)
