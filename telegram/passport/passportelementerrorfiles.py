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
"""This module contains the classes that represent Telegram PassportElementErrorFiles."""

from telegram import PassportElementError


class PassportElementErrorFiles(PassportElementError):
    """
    Represents an issue with a list of scans. The error is considered resolved when the file with
    the document scan changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            “utility_bill”, “bank_statement”, “rental_agreement”, “passport_registration”,
            “temporary_registration”
        file_hash (:obj:`str`): Base64-encoded data hash
        message (:obj:`str`): Error message

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            “utility_bill”, “bank_statement”, “rental_agreement”, “passport_registration”,
            “temporary_registration”
        file_hashes (List[:obj:`str`]): List of base64-encoded file hashes
        message (:obj:`str`): Error message
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 file_hashes,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorFiles, self).__init__('files', type, message)
        self.file_hashes = file_hashes

        self._id_attrs = ((self.source, self.type, self.message) +
                          tuple([file_hash for file_hash in file_hashes]))
