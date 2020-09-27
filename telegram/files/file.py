#!/usr/bin/env python
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
"""This module contains an object that represents a Telegram File."""
from base64 import b64decode
from os.path import basename
import os

import urllib.parse as urllib_parse

from telegram import TelegramObject
from telegram.passport.credentials import decrypt

from typing import Any, Optional, IO, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot, FileCredentials


class File(TelegramObject):
    """
    This object represents a file ready to be downloaded. The file can be downloaded with
    :attr:`download`. It is guaranteed that the link will be valid for at least 1 hour. When the
    link expires, a new one can be requested by calling :meth:`telegram.Bot.get_file`.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Note:
        Maximum file size to download is 20 MB.

    Attributes:
        file_id (:obj:`str`): Identifier for this file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`str`): Optional. File size.
        file_path (:obj:`str`): Optional. File path. Use :attr:`download` to get the file.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`, optional): Optional. File size, if known.
        file_path (:obj:`str`, optional): File path. Use :attr:`download` to get the file.
        bot (:obj:`telegram.Bot`, optional): Bot to use with shortcut method.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Note:
        If you obtain an instance of this class from :attr:`telegram.PassportFile.get_file`,
        then it will automatically be decrypted as it downloads when you call :attr:`download()`.

    """

    def __init__(self,
                 file_id: str,
                 file_unique_id: str,
                 bot: 'Bot' = None,
                 file_size: int = None,
                 file_path: str = None,
                 **kwargs: Any):
        # Required
        self.file_id = str(file_id)
        self.file_unique_id = str(file_unique_id)
        # Optionals
        self.file_size = file_size
        self.file_path = file_path
        self.bot = bot
        self._credentials: Optional['FileCredentials'] = None

        self._id_attrs = (self.file_unique_id,)

    def download(self,
                 custom_path: str = None,
                 out: IO = None,
                 timeout: int = None) -> Union[str, IO]:
        """
        Download this file. By default, the file is saved in the current working directory with its
        original filename as reported by Telegram. If the file has no filename, it the file ID will
        be used as filename. If a :attr:`custom_path` is supplied, it will be saved to that path
        instead. If :attr:`out` is defined, the file contents will be saved to that object using
        the ``out.write`` method.

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
            if self._credentials:
                buf = decrypt(b64decode(self._credentials.secret),
                              b64decode(self._credentials.hash),
                              buf)
            out.write(buf)
            return out
        else:
            if custom_path:
                filename = custom_path
            elif self.file_path:
                filename = basename(self.file_path)
            else:
                filename = os.path.join(os.getcwd(), self.file_id)

            buf = self.bot.request.retrieve(url, timeout=timeout)
            if self._credentials:
                buf = decrypt(b64decode(self._credentials.secret),
                              b64decode(self._credentials.hash),
                              buf)
            with open(filename, 'wb') as fobj:
                fobj.write(buf)
            return filename

    def _get_encoded_url(self) -> str:
        """Convert any UTF-8 char in :obj:`File.file_path` into a url encoded ASCII string."""
        sres = urllib_parse.urlsplit(self.file_path)
        return urllib_parse.urlunsplit(urllib_parse.SplitResult(
            sres.scheme, sres.netloc, urllib_parse.quote(sres.path), sres.query, sres.fragment))

    def download_as_bytearray(self, buf: bytearray = None) -> bytes:
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

    def set_credentials(self, credentials: 'FileCredentials') -> None:
        self._credentials = credentials
