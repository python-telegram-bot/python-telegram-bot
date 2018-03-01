#!/usr/bin/env python
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
"""This module contains an object that represents a Telegram File."""
from os.path import basename

from future.backports.urllib import parse as urllib_parse

from telegram import TelegramObject


class File(TelegramObject):
    """
    This object represents a file ready to be downloaded. The file can be downloaded with
    :attr:`download`. It is guaranteed that the link will be valid for at least 1 hour. When the
    link expires, a new one can be requested by calling getFile.

    Note:
        Maximum file size to download is 20 MB

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file.
        file_size (:obj:`str`): Optional. File size.
        file_path (:obj:`str`): Optional. File path. Use :attr:`download` to get the file.

    Args:
        file_id (:obj:`str`): Unique identifier for this file.
        file_size (:obj:`int`, optional): Optional. File size, if known.
        file_path (:obj:`str`, optional): File path. Use :attr:`download` to get the file.
        bot (:obj:`telegram.Bot`, optional): Bot to use with shortcut method.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, file_id, bot=None, file_size=None, file_path=None, **kwargs):
        # Required
        self.file_id = str(file_id)

        # Optionals
        self.file_size = file_size
        self.file_path = file_path

        self.bot = bot

        self._id_attrs = (self.file_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)

    def download(self, custom_path=None, out=None, timeout=None):
        """
        Download this file. By default, the file is saved in the current working directory with its
        original filename as reported by Telegram. If a :attr:`custom_path` is supplied, it will be
        saved to that path instead. If :attr:`out` is defined, the file contents will be saved to
        that object using the ``out.write`` method.

        Note:
            :attr:`custom_path` and :attr:`out` are mutually exclusive.

        Args:
            custom_path (:obj:`str`, optional): Custom path.
            out (:obj:`io.BufferedWriter`, optional): A file-like object. Must be opened for
                writing in binary mode, if applicable.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
            :obj:`str` | :obj:`io.BufferedWriter`: The same object as :attr:`out` if specified.
            Otherwise, returns the filename downloaded to.

        Raises:
            ValueError: If both :attr:`custom_path` and :attr:`out` are passed.

        """
        if custom_path is not None and out is not None:
            raise ValueError('custom_path and out are mutually exclusive')

        # Convert any UTF-8 char into a url encoded ASCII string.
        url = self._get_encoded_url()

        if out:
            buf = self.bot.request.retrieve(url)
            out.write(buf)
            return out
        else:
            if custom_path:
                filename = custom_path
            else:
                filename = basename(self.file_path)

            self.bot.request.download(url, filename, timeout=timeout)
            return filename

    def _get_encoded_url(self):
        """Convert any UTF-8 char in :obj:`File.file_path` into a url encoded ASCII string."""
        sres = urllib_parse.urlsplit(self.file_path)
        return urllib_parse.urlunsplit(urllib_parse.SplitResult(
            sres.scheme, sres.netloc, urllib_parse.quote(sres.path), sres.query, sres.fragment))

    def download_as_bytearray(self, buf=None):
        """Download this file and return it as a bytearray.

        Args:
            buf (:obj:`bytearray`, optional): Extend the given bytearray with the downloaded data.

        Returns:
            :obj:`bytearray`: The same object as :attr:`buf` if it was specified. Otherwise a newly
            allocated :obj:`bytearray`.

        """
        if buf is None:
            buf = bytearray()

        buf.extend(self.bot.request.retrieve(self._get_encoded_url()))
        return buf
