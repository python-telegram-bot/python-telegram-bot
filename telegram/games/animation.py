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
"""This module contains an object that represents a Telegram Animation."""
from telegram import PhotoSize
from telegram import TelegramObject


class Animation(TelegramObject):
    """This object represents an animation file to be displayed in the message containing a game.

    Attributes:
        file_id (:obj:`str`): Unique file identifier.
        thumb (:class:`telegram.PhotoSize`): Optional. Animation thumbnail as defined
            by sender.
        file_name (:obj:`str`): Optional. Original animation filename as defined by sender.
        mime_type (:obj:`str`): Optional. MIME type of the file as defined by sender.
        file_size (:obj:`int`): Optional. File size.

    Args:
        file_id (:obj:`str`): Unique file identifier.
        thumb (:class:`telegram.PhotoSize`, optional): Animation thumbnail as defined by sender.
        file_name (:obj:`str`, optional): Original animation filename as defined by sender.
        mime_type (:obj:`str`, optional): MIME type of the file as defined by sender.
        file_size (:obj:`int`, optional): File size.

    """

    def __init__(self,
                 file_id,
                 thumb=None,
                 file_name=None,
                 mime_type=None,
                 file_size=None,
                 **kwargs):
        self.file_id = file_id
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

        self._id_attrs = (self.file_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Animation, cls).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return cls(**data)
