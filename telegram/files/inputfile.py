#!/usr/bin/env python
# pylint: disable=W0622,E0611
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

try:
    # python 3
    from email.generator import _make_boundary as choose_boundary
except ImportError:
    # python 2
    from mimetools import choose_boundary

import imghdr
import mimetypes
import os
import sys

from telegram import TelegramError

DEFAULT_MIME_TYPE = 'application/octet-stream'
USER_AGENT = 'Python Telegram Bot (https://github.com/python-telegram-bot/python-telegram-bot)'
FILE_TYPES = ('audio', 'document', 'photo', 'sticker', 'video', 'voice', 'certificate',
              'video_note', 'png_sticker')


class InputFile(object):
    """This object represents a Telegram InputFile.

    Attributes:
        data (:obj:`dict`): Data containing an inputfile.

    Args:
        data (:obj:`dict`): Data containing an inputfile.

    Raises:
        TelegramError

    """

    def __init__(self, data):
        self.data = data
        self.boundary = choose_boundary()

        for t in FILE_TYPES:
            if t in data:
                self.input_name = t
                self.input_file = data.pop(t)
                break
        else:
            raise TelegramError('Unknown inputfile type')

        if hasattr(self.input_file, 'read'):
            self.filename = None
            self.input_file_content = self.input_file.read()
            if 'filename' in data:
                self.filename = self.data.pop('filename')
            elif hasattr(self.input_file, 'name'):
                # on py2.7, pylint fails to understand this properly
                # pylint: disable=E1101
                self.filename = os.path.basename(self.input_file.name)

            try:
                self.mimetype = self.is_image(self.input_file_content)
                if not self.filename or '.' not in self.filename:
                    self.filename = self.mimetype.replace('/', '.')
            except TelegramError:
                if self.filename:
                    self.mimetype = mimetypes.guess_type(
                        self.filename)[0] or DEFAULT_MIME_TYPE
                else:
                    self.mimetype = DEFAULT_MIME_TYPE

    @property
    def headers(self):
        """:obj:`dict`: Headers."""

        return {'User-agent': USER_AGENT, 'Content-type': self.content_type}

    @property
    def content_type(self):
        """:obj:`str`: Content type"""
        return 'multipart/form-data; boundary=%s' % self.boundary

    def to_form(self):
        """Transform the inputfile to multipart/form data.

        Returns:
            :obj:`str`

        """
        form = []
        form_boundary = '--' + self.boundary

        # Add data fields
        for name in iter(self.data):
            value = self.data[name]
            form.extend([
                form_boundary, 'Content-Disposition: form-data; name="%s"' % name, '', str(value)
            ])

        # Add input_file to upload
        form.extend([
            form_boundary, 'Content-Disposition: form-data; name="%s"; filename="%s"' %
            (self.input_name,
             self.filename), 'Content-Type: %s' % self.mimetype, '', self.input_file_content
        ])

        form.append('--' + self.boundary + '--')
        form.append('')

        return self._parse(form)

    @staticmethod
    def _parse(form):
        if sys.version_info > (3,):
            # on Python 3 form needs to be byte encoded
            encoded_form = []
            for item in form:
                try:
                    encoded_form.append(item.encode())
                except AttributeError:
                    encoded_form.append(item)

            return b'\r\n'.join(encoded_form)
        return '\r\n'.join(form)

    @staticmethod
    def is_image(stream):
        """Check if the content file is an image by analyzing its headers.

        Args:
            stream (:obj:`str`): A str representing the content of a file.

        Returns:
            :obj:`str`: The str mime-type of an image.

        """
        image = imghdr.what(None, stream)
        if image:
            return 'image/%s' % image

        raise TelegramError('Could not parse file content')

    @staticmethod
    def is_inputfile(data):
        """Check if the request is a file request.

        Args:
            data (Dict[:obj:`str`, :obj:`str`]): A dict of (str, str) key/value pairs.

        Returns:
            :obj:`bool`

        """
        if data:
            file_type = [i for i in iter(data) if i in FILE_TYPES]

            if file_type:
                file_content = data[file_type[0]]

                return hasattr(file_content, 'read')

        return False
