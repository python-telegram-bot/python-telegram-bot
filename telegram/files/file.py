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
"""This module contains an object that represents a Telegram File."""

from os.path import basename

from telegram import TelegramObject


class File(TelegramObject):
    """This object represents a Telegram File.

    Attributes:
        file_id (str):
        file_size (str):
        file_path (str):

    Args:
        file_id (str):
        bot (telegram.Bot):
        file_size (Optional[int]):
        file_path (Optional[str]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, file_id, bot, file_size=None, file_path=None, **kwargs):
        # Required
        self.file_id = str(file_id)

        # Optionals
        self.file_size = file_size
        if file_path:
            self.file_path = str(file_path)

        self.bot = bot

        self._id_attrs = (self.file_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.File:
        """
        if not data:
            return None

        return File(bot=bot, **data)

    def download(self, custom_path=None, out=None, timeout=None):
        """
        Download this file. By default, the file is saved in the current working directory with its
        original filename as reported by Telegram. If a ``custom_path`` is supplied, it will be
        saved to that path instead. If ``out`` is defined, the file contents will be saved to that
        object using the ``out.write`` method. ``custom_path`` and ``out`` are mutually exclusive.

        Args:
            custom_path (Optional[str]): Custom path.
            out (Optional[object]): A file-like object. Must be opened in binary mode, if
                applicable.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Raises:
            ValueError: If both ``custom_path`` and ``out`` are passed.

        """

        if custom_path is not None and out is not None:
            raise ValueError('custom_path and out are mutually exclusive')

        url = self.file_path

        if out:
            buf = self.bot.request.retrieve(url)
            out.write(buf)

        else:
            if custom_path:
                filename = custom_path
            else:
                filename = basename(url)

            self.bot.request.download(url, filename, timeout=timeout)
