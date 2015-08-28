#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents a Telegram Document"""

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
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        thumb (Optional[:class:`telegram.PhotoSize`]):
        file_name (Optional[str]):
        mime_type (Optional[str]):
        file_size (Optional[int]):
    """

    def __init__(self,
                 file_id,
                 **kwargs):
        # Required
        self.file_id = file_id
        # Optionals
        self.thumb = kwargs.get('thumb')
        self.file_name = kwargs.get('file_name', '')
        self.mime_type = kwargs.get('mime_type', '')
        self.file_size = int(kwargs.get('file_size', 0))

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.Document:
        """
        if not data:
            return None

        document = dict()

        # Required
        document['file_id'] = data['file_id']
        # Optionals
        document['thumb'] = PhotoSize.de_json(data.get('thumb'))
        document['file_name'] = data.get('file_name')
        document['mime_type'] = data.get('mime_type')
        document['file_size'] = data.get('file_size', 0)

        return Document(**document)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = dict()

        # Required
        data['file_id'] = self.file_id
        # Optionals
        if self.thumb:
            data['thumb'] = self.thumb.to_dict()
        if self.file_name:
            data['file_name'] = self.file_name
        if self.mime_type:
            data['mime_type'] = self.mime_type
        if self.file_size:
            data['file_size'] = self.file_size

        return data
