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
"""This module contains an object that represents a Telegram Document."""

from telegram import PhotoSize, TelegramObject


class Document(TelegramObject):
    """This object represents a Telegram Document.

    Attributes:
        file_id (str):
        thumb (:class:`telegram.PhotoSize`):
        file_name (str):
        mime_type (str):
        file_size (int):

    Args:
        file_id (str):
        thumb (Optional[:class:`telegram.PhotoSize`]):
        file_name (Optional[str]):
        mime_type (Optional[str]):
        file_size (Optional[int]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 file_id,
                 thumb=None,
                 file_name=None,
                 mime_type=None,
                 file_size=None,
                 **kwargs):
        # Required
        self.file_id = str(file_id)
        # Optionals
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Document:
        """
        if not data:
            return None

        data = super(Document, Document).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return Document(**data)
