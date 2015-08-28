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

"""This module contains a object that represents a Telegram Audio"""

from telegram import TelegramObject


class Audio(TelegramObject):
    """This object represents a Telegram Audio.

    Attributes:
        file_id (str):
        duration (int):
        performer (str):
        title (str):
        mime_type (str):
        file_size (int):

    Args:
        file_id (str):
        duration (int):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        performer (Optional[str]):
        title (Optional[str]):
        mime_type (Optional[str]):
        file_size (Optional[int]):
    """

    def __init__(self,
                 file_id,
                 duration,
                 **kwargs):
        # Required
        self.file_id = file_id
        self.duration = int(duration)
        # Optionals
        self.performer = kwargs.get('performer', '')
        self.title = kwargs.get('title', '')
        self.mime_type = kwargs.get('mime_type', '')
        self.file_size = int(kwargs.get('file_size', 0))

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.Audio:
        """
        if not data:
            return None

        audio = dict()

        # Required
        audio['file_id'] = data['file_id']
        audio['duration'] = data['duration']
        # Optionals
        audio['performer'] = data.get('performer')
        audio['title'] = data.get('title')
        audio['mime_type'] = data.get('mime_type')
        audio['file_size'] = data.get('file_size', 0)

        return Audio(**audio)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = dict()

        # Required
        data['file_id'] = self.file_id
        data['duration'] = self.duration
        # Optionals
        if self.performer:
            data['performer'] = self.performer
        if self.title:
            data['title'] = self.title
        if self.mime_type:
            data['mime_type'] = self.mime_type
        if self.file_size:
            data['file_size'] = self.file_size

        return data
