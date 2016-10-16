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
"""This module contains an object that represents a Telegram Animation."""
from telegram import PhotoSize
from telegram import TelegramObject


class Animation(TelegramObject):
    """This object represents a Telegram Animation.

    Attributes:
        file_id (str): Unique file identifier.

    Keyword Args:
        thumb (Optional[:class:`telegram.PhotoSize`]): Animation thumbnail as defined by sender.
        file_name (Optional[str]): Original animation filename as defined by sender.
        mime_type (Optional[str]): MIME type of the file as defined by sender.
        file_size (Optional[int]): File size.

    """

    def __init__(self, file_id, **kwargs):
        self.file_id = file_id
        self.thumb = kwargs.get('thumb')
        self.file_name = kwargs.get('file_name')
        self.mime_type = kwargs.get('mime_type')
        self.file_size = kwargs.get('file_size')

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Game:
        """
        if not data:
            return None

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return Animation(**data)
