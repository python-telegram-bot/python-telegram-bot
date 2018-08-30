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
"""This module contains an object that represents a Encrypted PassportFile."""

from telegram import TelegramObject


class PassportFile(TelegramObject):
    """
    This object represents a file uploaded to Telegram Passport. Currently all Telegram Passport
    files are in JPEG format when decrypted and don't exceed 10MB.

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file.
        file_size (:obj:`int`): File size.
        file_date (:obj:`int`): Unix time when the file was uploaded.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        file_id (:obj:`str`): Unique identifier for this file.
        file_size (:obj:`int`): File size.
        file_date (:obj:`int`): Unix time when the file was uploaded.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, file_id, file_date, file_size=None, bot=None, credentials=None, **kwargs):
        # Required
        self.file_id = file_id
        self.file_size = file_size
        self.file_date = file_date
        # Optionals
        self.bot = bot
        self._credentials = credentials

        self._id_attrs = (self.file_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(PassportFile, cls).de_json(data, bot)

        return cls(bot=bot, **data)

    @classmethod
    def de_json_decrypted(cls, data, bot, credentials):
        if not data:
            return None

        data = super(PassportFile, cls).de_json(data, bot)

        data['credentials'] = credentials

        return cls(bot=bot, **data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        return [cls.de_json(passport_file, bot) for passport_file in data]

    @classmethod
    def de_list_decrypted(cls, data, bot, credentials):
        if not data:
            return []

        return [cls.de_json_decrypted(passport_file, bot, credentials[i])
                for i, passport_file in enumerate(data)]

    def get_file(self, timeout=None, **kwargs):
        """
        Wrapper over :attr:`telegram.Bot.get_file`. Will automatically assign the correct
        credentials to the returned :class:`telegram.File` if originating from
        :obj:`telegram.PassportData.decrypted_data`.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.TelegramError`

        """
        file = self.bot.get_file(self.file_id, timeout=timeout, **kwargs)
        file.set_credentials(self._credentials)
        return file
