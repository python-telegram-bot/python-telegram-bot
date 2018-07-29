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
"""This module contains the classes that represent Telegram PassportElementErrorDataField."""

from telegram import PassportElementError


class PassportElementErrorDataField(PassportElementError):
    """
    Represents an issue in one of the data fields that was provided by the user. The error is
    considered resolved when the field's value changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            “personal_details”, “passport”, “driver_license”, “identity_card”, “internal_passport”,
            “address”
        field_name (:obj:`str`): Name of the data field which has the error
        data_hash (:obj:`str`): Base64-encoded data hash
        message (:obj:`str`): Error message

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            “personal_details”, “passport”, “driver_license”, “identity_card”, “internal_passport”,
            “address”
        field_name (:obj:`str`): Name of the data field which has the error
        data_hash (:obj:`str`): Base64-encoded data hash
        message (:obj:`str`): Error message
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 field_name,
                 data_hash,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorDataField, self).__init__('data', type, message)
        self.field_name = field_name
        self.data_hash = data_hash

        self._id_attrs = (self.source, self.type, self.field_name, self.data_hash, self.message)
