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

from collections.abc import Sequence

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.types import JSONDict


@tg_dataclass()
class PassportElementError(TelegramObject):
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

    # Required
    source: str = tg_field(compare=True)
    type: str = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Include in initalizer for next relase
    message: str = tg_field(init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__
    def __init__(
        self, source: str, type: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        object.__setattr__(self, "source", str(source))
        object.__setattr__(self, "type", str(type))
        object.__setattr__(self, "message", str(message))
        TelegramObject.__init__(self, api_kwargs=api_kwargs)


@tg_dataclass()
class PassportElementErrorDataField(PassportElementError):
    """
    Represents an issue in one of the data fields that was provided by the user. The error is
    considered resolved when the field's value changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`field_name`, :attr:`data_hash` and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self,
        type: str,
        field_name: str,
        data_hash: str,
        message: str,
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        PassportElementError.__init__(self, "data", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "field_name", field_name)
        object.__setattr__(self, "data_hash", data_hash)


@tg_dataclass()
class PassportElementErrorFile(PassportElementError):
    """
    Represents an issue with a document scan. The error is considered resolved when the file with
    the document scan changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, file_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(self, "file", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "file_hash", file_hash)


@tg_dataclass()
class PassportElementErrorFiles(PassportElementError):
    """
    Represents an issue with a list of scans. The error is considered resolved when the list of
    files with the document scans changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hashes`, and :attr:`message` are equal.

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
    file_hashes: tuple[str, ...] = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self,
        type: str,
        file_hashes: Sequence[str],
        message: str,
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        PassportElementError.__init__(self, "files", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "file_hashes", parse_sequence_arg(file_hashes))


@tg_dataclass()
class PassportElementErrorFrontSide(PassportElementError):
    """
    Represents an issue with the front side of a document. The error is considered resolved when
    the file with the front side of the document changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, file_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(self, "front_side", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "file_hash", file_hash)


@tg_dataclass()
class PassportElementErrorReverseSide(PassportElementError):
    """
    Represents an issue with the reverse side of a document. The error is considered resolved when
    the file with the reverse side of the document changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, file_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(self, "reverse_side", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "file_hash", file_hash)


@tg_dataclass()
class PassportElementErrorSelfie(PassportElementError):
    """
    Represents an issue with the selfie with a document. The error is considered resolved when
    the file with the selfie changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, file_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(self, "selfie", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "file_hash", file_hash)


@tg_dataclass()
class PassportElementErrorTranslationFile(PassportElementError):
    """
    Represents an issue with one of the files that constitute the translation of a document.
    The error is considered resolved when the file changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, file_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(
            self, "translation_file", type, message, api_kwargs=api_kwargs
        )
        object.__setattr__(self, "file_hash", file_hash)


@tg_dataclass()
class PassportElementErrorTranslationFiles(PassportElementError):
    """
    Represents an issue with the translated version of a document. The error is considered
    resolved when a file with the document translation changes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`file_hashes`, and :attr:`message` are equal.

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
    file_hashes: tuple[str, ...] = tg_field(compare=True)
    # tags: deprecated NEXT.VERSION
    # Remove for next relase
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self,
        type: str,
        file_hashes: Sequence[str],
        message: str,
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        PassportElementError.__init__(
            self, "translation_files", type, message, api_kwargs=api_kwargs
        )
        object.__setattr__(self, "file_hashes", parse_sequence_arg(file_hashes))


@tg_dataclass()
class PassportElementErrorUnspecified(PassportElementError):
    """
    Represents an issue in an unspecified place. The error is considered resolved when new
    data is added.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.PassportElementError.source`, :attr:`type`,
    :attr:`element_hash`, and :attr:`message` are equal.

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
    message: str = tg_field(compare=True, init=False)

    # tags: deprecated NEXT.VERSION
    # Remove manual __init__, present here to preserve ordering
    def __init__(
        self, type: str, element_hash: str, message: str, *, api_kwargs: JSONDict | None = None
    ) -> None:
        PassportElementError.__init__(self, "unspecified", type, message, api_kwargs=api_kwargs)
        object.__setattr__(self, "element_hash", element_hash)
