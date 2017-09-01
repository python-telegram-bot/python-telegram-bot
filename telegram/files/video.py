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
"""This module contains an object that represents a Telegram Video."""

from telegram import PhotoSize, TelegramObject


class Video(TelegramObject):
    """This object represents a video file.

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file.
        width (:obj:`int`): Video width as defined by sender.
        height (:obj:`int`): Video height as defined by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`): Optional. Video thumbnail.
        mime_type (:obj:`str`): Optional. Mime type of a file as defined by sender.
        file_size (:obj:`int`): Optional. File size.

    Args:
        file_id (:obj:`str`): Unique identifier for this file.
        width (:obj:`int`): Video width as defined by sender.
        height (:obj:`int`): Video height as defined by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`, optional): Video thumbnail.
        mime_type (:obj:`str`, optional): Mime type of a file as defined by sender.
        file_size (:obj:`int`, optional): File size.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 file_id,
                 width,
                 height,
                 duration,
                 thumb=None,
                 mime_type=None,
                 file_size=None,
                 **kwargs):
        # Required
        self.file_id = str(file_id)
        self.width = int(width)
        self.height = int(height)
        self.duration = int(duration)
        # Optionals
        self.thumb = thumb
        self.mime_type = mime_type
        self.file_size = file_size

        self._id_attrs = (self.file_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Video, cls).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return cls(**data)
