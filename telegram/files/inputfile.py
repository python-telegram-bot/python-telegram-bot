#!/usr/bin/env python
# pylint: disable=W0622,E0611
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
"""This module contains an object that represents a Telegram InputFile."""

import imghdr
import mimetypes
import os
from uuid import uuid4

from telegram import TelegramError

from typing import IO, Tuple, Optional

DEFAULT_MIME_TYPE = 'application/octet-stream'


class InputFile:
    """This object represents a Telegram InputFile.

    Attributes:
        input_file_content (:obj:`bytes`): The binary content of the file to send.
        filename (:obj:`str`): Optional. Filename for the file to be sent.
        attach (:obj:`str`): Optional. Attach id for sending multiple files.

    Args:
        obj (:obj:`File handler`): An open file descriptor.
        filename (:obj:`str`, optional): Filename for this InputFile.
        attach (:obj:`bool`, optional): Whether this should be send as one file or is part of a
            collection of files.

    Raises:
        TelegramError

    """

    def __init__(self, obj: IO, filename: str = None, attach: bool = None):
        self.filename = None
        self.input_file_content = obj.read()
        self.attach = 'attached' + uuid4().hex if attach else None

        if filename:
            self.filename = filename
        elif (hasattr(obj, 'name') and not isinstance(obj.name, int)):
            self.filename = os.path.basename(obj.name)

        try:
            self.mimetype = self.is_image(self.input_file_content)
        except TelegramError:
            if self.filename:
                self.mimetype = mimetypes.guess_type(
                    self.filename)[0] or DEFAULT_MIME_TYPE
            else:
                self.mimetype = DEFAULT_MIME_TYPE
        if not self.filename:
            self.filename = self.mimetype.replace('/', '.')

    @property
    def field_tuple(self) -> Tuple[str, bytes, str]:
        return self.filename, self.input_file_content, self.mimetype

    @staticmethod
    def is_image(stream: bytes) -> str:
        """Check if the content file is an image by analyzing its headers.

        Args:
            stream (:obj:`bytes`): A byte stream representing the content of a file.

        Returns:
            :obj:`str`: The str mime-type of an image.

        """
        image = imghdr.what(None, stream)
        if image:
            return 'image/%s' % image

        raise TelegramError('Could not parse file content')

    @staticmethod
    def is_file(obj: object) -> bool:
        return hasattr(obj, 'read')

    def to_dict(self) -> Optional[str]:
        if self.attach:
            return 'attach://' + self.attach
        return None
