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
    """Contains data required for decrypting and authenticating EncryptedPassportElement. See the
    Telegram Passport Documentation for a complete description of the data decryption and
    authentication processes.

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file
        file_size (:obj:`int`): File size
        file_date (:obj:`int`): Unix time when the file was uploaded
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        file_id (:obj:`str`): Unique identifier for this file
        file_size (:obj:`int`): File size
        file_date (:obj:`int`): Unix time when the file was uploaded
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, file_id, file_size, file_date, bot=None, **kwargs):
        # Required
        self.file_id = file_id
        self.file_size = file_size
        self.file_date = file_date
        # Optionals
        self.bot = bot

        self._id_attrs = (self.file_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        passport_files = list()
        for passport_file in data:
            passport_files.append(cls.de_json(passport_file, bot))

        return passport_files
