#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
# pylint: disable=redefined-builtin
"""This module contains the classes that represent Telegram PassportElementError."""

import dataclasses

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.types import JSONDict


@tg_dataclass()
class _BasePassportElementError(TelegramObject):
    source: str = tg_field(compare=True)
    type: str = tg_field(compare=True)


@dataclasses.dataclass(frozen=True, slots=False, repr=False, eq=False, match_args=False)
class PassportElementError(_BasePassportElementError):
    """Baseclass for the PassportElementError* classes.

    This object represents an error in the Telegram Passport element which was submitted that
    should be resolved by the user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`source` and :attr:`type` are equal.

    Args:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        message (:obj:`str`): Error message.

    Attributes:
        source (:obj:`str`): Error source.
        type (:obj:`str`): The section of the user's Telegram Passport which has the error.
        message (:obj:`str`): Error message.

    """

    # tags: deprecated NEXT.VERSION
    # Use automatic slots and __init__
    # We currently define explicit slots instead of dataclass fields
    # to allow subclasses to control `message` parameter ordering

    __slots__ = ("message",)

    def __init__(
        self,
        source: str,
        type: str,
        message: str,
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        super().__init__(source, type, api_kwargs=api_kwargs)

        object.__setattr__(self, "message", str(message))


@tg_dataclass()
class PassportElementErrorDataField(PassportElementError):
    """
    Represents an issue in one of the data fields that was provided by the user. The error is
    considered resolved when the field's value changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`field_name`, :attr:`data_hash` and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            ``"personal_details"``, ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"address"``.
        field_name (:obj:`str`): Name of the data field which has the error.
        data_hash (:obj:`str`): Base64-encoded data hash.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the error, one of
            ``"personal_details"``, ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"address"``.
        field_name (:obj:`str`): Name of the data field which has the error.
        data_hash (:obj:`str`): Base64-encoded data hash.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="data")
    # Required
    field_name: str = tg_field(compare=True)
    data_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorFile(PassportElementError):
    """
    Represents an issue with a document scan. The error is considered resolved when the file with
    the document scan changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"utility_bill"``, ``"bank_statement"``, ``"rental_agreement"``,
            ``"passport_registration"``, ``"temporary_registration"``.
        file_hash (:obj:`str`): Base64-encoded file hash.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"utility_bill"``, ``"bank_statement"``, ``"rental_agreement"``,
            ``"passport_registration"``, ``"temporary_registration"``.
        file_hash (:obj:`str`): Base64-encoded file hash.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="file")
    # Required
    file_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorFiles(PassportElementError):
    """
    Represents an issue with a list of scans. The error is considered resolved when the list of
    files with the document scans changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hashes`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"utility_bill"``, ``"bank_statement"``, ``"rental_agreement"``,
            ``"passport_registration"``, ``"temporary_registration"``.
        file_hashes (Sequence[:obj:`str`]): List of base64-encoded file hashes.

            .. versionchanged:: 22.0
                |sequenceargs|
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"utility_bill"``, ``"bank_statement"``, ``"rental_agreement"``,
            ``"passport_registration"``, ``"temporary_registration"``.
        file_hashes (tuple[:obj:`str`]): List of base64-encoded file hashes.

            .. versionchanged:: 22.0
                |tupleclassattrs|
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="files")
    # Required
    file_hashes: tuple[str, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorFrontSide(PassportElementError):
    """
    Represents an issue with the front side of a document. The error is considered resolved when
    the file with the front side of the document changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"passport"``, ``"driver_license"``, ``"identity_card"``, ``"internal_passport"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the front side of the
            document.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"passport"``, ``"driver_license"``, ``"identity_card"``, ``"internal_passport"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the front side of the
            document.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="front_side")
    # Required
    file_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorReverseSide(PassportElementError):
    """
    Represents an issue with the reverse side of a document. The error is considered resolved when
    the file with the reverse side of the document changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"driver_license"``, ``"identity_card"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the reverse side of the
            document.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"driver_license"``, ``"identity_card"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the reverse side of the
            document.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="reverse_side")
    # Required
    file_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorSelfie(PassportElementError):
    """
    Represents an issue with the selfie with a document. The error is considered resolved when
    the file with the selfie changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"passport"``, ``"driver_license"``, ``"identity_card"``, ``"internal_passport"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the selfie.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): The section of the user's Telegram Passport which has the issue, one of
            ``"passport"``, ``"driver_license"``, ``"identity_card"``, ``"internal_passport"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file with the selfie.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="selfie")
    # Required
    file_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorTranslationFile(PassportElementError):
    """
    Represents an issue with one of the files that constitute the translation of a document.
    The error is considered resolved when the file changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue,
            one of ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"utility_bill"``, ``"bank_statement"``,
            ``"rental_agreement"``, ``"passport_registration"``, ``"temporary_registration"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue,
            one of ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"utility_bill"``, ``"bank_statement"``,
            ``"rental_agreement"``, ``"passport_registration"``, ``"temporary_registration"``.
        file_hash (:obj:`str`): Base64-encoded hash of the file.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="translation_file")
    # Required
    file_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorTranslationFiles(PassportElementError):
    """
    Represents an issue with the translated version of a document. The error is considered
    resolved when a file with the document translation changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hashes`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue,
            one of ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"utility_bill"``, ``"bank_statement"``,
            ``"rental_agreement"``, ``"passport_registration"``, ``"temporary_registration"``.
        file_hashes (Sequence[:obj:`str`]): List of base64-encoded file hashes.

            .. versionchanged:: 22.0
                |sequenceargs|
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue,
            one of ``"passport"``, ``"driver_license"``, ``"identity_card"``,
            ``"internal_passport"``, ``"utility_bill"``, ``"bank_statement"``,
            ``"rental_agreement"``, ``"passport_registration"``, ``"temporary_registration"``.
        file_hashes (tuple[:obj:`str`]): List of base64-encoded file hashes.

            .. versionchanged:: 22.0
                |tupleclassattrs|
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="translation_files")
    # Required
    file_hashes: tuple[str, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)


@tg_dataclass()
class PassportElementErrorUnspecified(PassportElementError):
    """
    Represents an issue in an unspecified place. The error is considered resolved when new
    data is added.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`element_hash`, and :attr:`message` are equal.

    .. deprecated:: NEXT.VERSION
        Passing :paramref:`message` positionally is deprecated. Its position will change in
        a future release.

    Args:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue.
        element_hash (:obj:`str`): Base64-encoded element hash.
        message (:obj:`str`): Error message.

    Attributes:
        type (:obj:`str`): Type of element of the user's Telegram Passport which has the issue.
        element_hash (:obj:`str`): Base64-encoded element hash.
        message (:obj:`str`): Error message.

    """

    # Attribute only (init=False)
    source: str = tg_field(compare=True, init=False, default="unspecified")
    # Required
    element_hash: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True)
