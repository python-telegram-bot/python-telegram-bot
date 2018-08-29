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
"""This module contains the classes that represent Telegram PassportElementError."""

from telegram import TelegramObject


class PassportElementError(TelegramObject):
    """Baseclass for the PassportElementError* classes.

    Attributes:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        message (:obj:`str`): Error message

    Args:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, source, type, message, **kwargs):
        # Required
        self.source = str(source)
        self.type = str(type)
        self.message = str(message)

        self._id_attrs = (self.source, self.type)


class PassportElementErrorDataField(PassportElementError):
    """
    Represents an issue in one of the data fields that was provided by the user. The error is
    considered resolved when the field's value changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            "personal_details", "passport", "driver_license", "identity_card", "internal_passport",
            "address".
        field_name (:obj:`str`): Name of the data field which has the error.
        data_hash (:obj:`str`): Base64-encoded data hash.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            "personal_details", "passport", "driver_license", "identity_card", "internal_passport",
            "address".
        field_name (:obj:`str`): Name of the data field which has the error.
        data_hash (:obj:`str`): Base64-encoded data hash.
        message (:obj:`str`): Error message.
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


class PassportElementErrorFile(PassportElementError):
    """
    Represents an issue with a document scan. The error is considered resolved when the file with
    the document scan changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration",
            "temporary_registration".
        file_hash (:obj:`str`): Base64-encoded file hash.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration",
            "temporary_registration".
        file_hash (:obj:`str`): Base64-encoded file hash.
        message (:obj:`str`): Error message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 file_hash,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorFile, self).__init__('file', type, message)
        self.file_hash = file_hash

        self._id_attrs = (self.source, self.type, self.file_hash, self.message)


class PassportElementErrorFiles(PassportElementError):
    """
    Represents an issue with a list of scans. The error is considered resolved when the file with
    the document scan changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration",
            "temporary_registration".
        file_hash (:obj:`str`): Base64-encoded file hash.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration",
            "temporary_registration".
        file_hashes (List[:obj:`str`]): List of base64-encoded file hashes.
        message (:obj:`str`): Error message.
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


class PassportElementErrorFrontSide(PassportElementError):
    """
    Represents an issue with the front side of a document. The error is considered resolved when
    the file with the front side of the document changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "passport", "driver_license", "identity_card", "internal_passport".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the front side of the
            document.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "passport", "driver_license", "identity_card", "internal_passport".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the front side of the
            document.
        message (:obj:`str`): Error message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 file_hash,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorFrontSide, self).__init__('front_side', type, message)
        self.file_hash = file_hash

        self._id_attrs = (self.source, self.type, self.file_hash, self.message)


class PassportElementErrorReverseSide(PassportElementError):
    """
    Represents an issue with the front side of a document. The error is considered resolved when
    the file with the reverse side of the document changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "passport", "driver_license", "identity_card", "internal_passport".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the reverse side of the
            document.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "driver_license", "identity_card".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the reverse side of the
            document.
        message (:obj:`str`): Error message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 file_hash,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorReverseSide, self).__init__('reverse_side', type, message)
        self.file_hash = file_hash

        self._id_attrs = (self.source, self.type, self.file_hash, self.message)


class PassportElementErrorSelfie(PassportElementError):
    """
    Represents an issue with the selfie with a document. The error is considered resolved when
    the file with the selfie changes.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "passport", "driver_license", "identity_card", "internal_passport".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the selfie.
        message (:obj:`str`): Error message.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            "passport", "driver_license", "identity_card", "internal_passport".
        file_hash (:obj:`str`): Base64-encoded hash of the file with the selfie.
        message (:obj:`str`): Error message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 type,
                 file_hash,
                 message,
                 **kwargs):
        # Required
        super(PassportElementErrorSelfie, self).__init__('selfie', type, message)
        self.file_hash = file_hash

        self._id_attrs = (self.source, self.type, self.file_hash, self.message)
