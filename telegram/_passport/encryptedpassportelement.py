#!/usr/bin/env python
# flake8: noqa: E501
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""This module contains an object that represents a Telegram EncryptedPassportElement."""
from base64 import b64decode
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Union

from telegram._passport.credentials import decrypt_json
from telegram._passport.data import IdDocumentData, PersonalDetails, ResidentialAddress
from telegram._passport.passportfile import PassportFile
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot, Credentials


class EncryptedPassportElement(TelegramObject):
    """
    Contains information about documents or other Telegram Passport elements shared with the bot
    by the user. The data has been automatically decrypted by python-telegram-bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`data`, :attr:`phone_number`, :attr:`email`,
    :attr:`files`, :attr:`front_side`, :attr:`reverse_side` and :attr:`selfie` are equal.

    Note:
        This object is decrypted only when originating from
        :attr:`telegram.PassportData.decrypted_data`.

    Args:
        type (:obj:`str`): Element type. One of "personal_details", "passport", "driver_license",
            "identity_card", "internal_passport", "address", "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration", "temporary_registration", "phone_number",
            "email".
        hash (:obj:`str`): Base64-encoded element hash for using in
            :class:`telegram.PassportElementErrorUnspecified`.
        data (:class:`telegram.PersonalDetails` | :class:`telegram.IdDocumentData` | \
            :class:`telegram.ResidentialAddress` | :obj:`str`, optional):
            Decrypted or encrypted data; available only for "personal_details", "passport",
            "driver_license", "identity_card", "internal_passport" and "address" types.
        phone_number (:obj:`str`, optional): User's verified phone number; available only for
            "phone_number" type.
        email (:obj:`str`, optional): User's verified email address; available only for "email"
            type.
        files (Sequence[:class:`telegram.PassportFile`], optional): Array of encrypted/decrypted
            files with documents provided by the user; available only for "utility_bill",
            "bank_statement", "rental_agreement", "passport_registration" and
            "temporary_registration" types.

            .. versionchanged:: 20.0
                |sequenceclassargs|

        front_side (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            front side of the document, provided by the user; Available only for "passport",
            "driver_license", "identity_card" and "internal_passport".
        reverse_side (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            reverse side of the document, provided by the user; Available only for
            "driver_license" and "identity_card".
        selfie (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            selfie of the user holding a document, provided by the user; available if requested for
            "passport", "driver_license", "identity_card" and "internal_passport".
        translation (Sequence[:class:`telegram.PassportFile`], optional): Array of
            encrypted/decrypted files with translated versions of documents provided by the user;
            available if requested requested for "passport", "driver_license", "identity_card",
            "internal_passport", "utility_bill", "bank_statement", "rental_agreement",
            "passport_registration" and "temporary_registration" types.

            .. versionchanged:: 20.0
                |sequenceclassargs|

    Attributes:
        type (:obj:`str`): Element type. One of "personal_details", "passport", "driver_license",
            "identity_card", "internal_passport", "address", "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration", "temporary_registration", "phone_number",
            "email".
        hash (:obj:`str`): Base64-encoded element hash for using in
            :class:`telegram.PassportElementErrorUnspecified`.
        data (:class:`telegram.PersonalDetails` | :class:`telegram.IdDocumentData` | \
            :class:`telegram.ResidentialAddress` | :obj:`str`):
            Optional. Decrypted or encrypted data; available only for "personal_details",
            "passport", "driver_license", "identity_card", "internal_passport" and "address" types.
        phone_number (:obj:`str`): Optional. User's verified phone number; available only for
            "phone_number" type.
        email (:obj:`str`): Optional. User's verified email address; available only for "email"
            type.
        files (tuple[:class:`telegram.PassportFile`]): Optional. Array of encrypted/decrypted
            files with documents provided by the user; available only for "utility_bill",
            "bank_statement", "rental_agreement", "passport_registration" and
            "temporary_registration" types.

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|

        front_side (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            front side of the document, provided by the user; available only for "passport",
            "driver_license", "identity_card" and "internal_passport".
        reverse_side (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            reverse side of the document, provided by the user; available only for "driver_license"
            and "identity_card".
        selfie (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            selfie of the user holding a document, provided by the user; available if requested for
            "passport", "driver_license", "identity_card" and "internal_passport".
        translation (tuple[:class:`telegram.PassportFile`]): Optional. Array of
            encrypted/decrypted files with translated versions of documents provided by the user;
            available if requested for "passport", "driver_license", "identity_card",
            "internal_passport", "utility_bill", "bank_statement", "rental_agreement",
            "passport_registration" and "temporary_registration" types.

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|

    """

    __slots__ = (
        "data",
        "email",
        "files",
        "front_side",
        "hash",
        "phone_number",
        "reverse_side",
        "selfie",
        "translation",
        "type",
    )

    def __init__(
        self,
        type: str,  # pylint: disable=redefined-builtin
        hash: str,  # pylint: disable=redefined-builtin
        data: Optional[Union[PersonalDetails, IdDocumentData, ResidentialAddress]] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        files: Optional[Sequence[PassportFile]] = None,
        front_side: Optional[PassportFile] = None,
        reverse_side: Optional[PassportFile] = None,
        selfie: Optional[PassportFile] = None,
        translation: Optional[Sequence[PassportFile]] = None,
        # TODO: Remove the credentials argument in 22.0 or later
        credentials: Optional[  # pylint: disable=unused-argument  # noqa: ARG002
            "Credentials"
        ] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.type: str = type
        # Optionals
        self.data: Optional[Union[PersonalDetails, IdDocumentData, ResidentialAddress]] = data
        self.phone_number: Optional[str] = phone_number
        self.email: Optional[str] = email
        self.files: tuple[PassportFile, ...] = parse_sequence_arg(files)
        self.front_side: Optional[PassportFile] = front_side
        self.reverse_side: Optional[PassportFile] = reverse_side
        self.selfie: Optional[PassportFile] = selfie
        self.translation: tuple[PassportFile, ...] = parse_sequence_arg(translation)
        self.hash: str = hash

        self._id_attrs = (
            self.type,
            self.data,
            self.phone_number,
            self.email,
            self.files,
            self.front_side,
            self.reverse_side,
            self.selfie,
        )

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["EncryptedPassportElement"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["files"] = PassportFile.de_list(data.get("files"), bot) or None
        data["front_side"] = PassportFile.de_json(data.get("front_side"), bot)
        data["reverse_side"] = PassportFile.de_json(data.get("reverse_side"), bot)
        data["selfie"] = PassportFile.de_json(data.get("selfie"), bot)
        data["translation"] = PassportFile.de_list(data.get("translation"), bot) or None

        return super().de_json(data=data, bot=bot)

    @classmethod
    def de_json_decrypted(
        cls, data: Optional[JSONDict], bot: Optional["Bot"], credentials: "Credentials"
    ) -> Optional["EncryptedPassportElement"]:
        """Variant of :meth:`telegram.TelegramObject.de_json` that also takes into account
        passport credentials.

        Args:
            data (dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot` | :obj:`None`): The bot associated with these object.
                May be :obj:`None`, in which case shortcut methods will not be available.

                .. versionchanged:: 21.4
                   :paramref:`bot` is now optional and defaults to :obj:`None`

                .. deprecated:: 21.4
                   This argument will be converted to an optional argument in future versions.
            credentials (:class:`telegram.FileCredentials`): The credentials

        Returns:
            :class:`telegram.EncryptedPassportElement`:

        """
        if not data:
            return None

        if data["type"] not in ("phone_number", "email"):
            secure_data = getattr(credentials.secure_data, data["type"])

            if secure_data.data is not None:
                # If not already decrypted
                if not isinstance(data["data"], dict):
                    data["data"] = decrypt_json(
                        b64decode(secure_data.data.secret),
                        b64decode(secure_data.data.hash),
                        b64decode(data["data"]),
                    )
                if data["type"] == "personal_details":
                    data["data"] = PersonalDetails.de_json(data["data"], bot=bot)
                elif data["type"] in (
                    "passport",
                    "internal_passport",
                    "driver_license",
                    "identity_card",
                ):
                    data["data"] = IdDocumentData.de_json(data["data"], bot=bot)
                elif data["type"] == "address":
                    data["data"] = ResidentialAddress.de_json(data["data"], bot=bot)

            data["files"] = (
                PassportFile.de_list_decrypted(data.get("files"), bot, secure_data.files) or None
            )
            data["front_side"] = PassportFile.de_json_decrypted(
                data.get("front_side"), bot, secure_data.front_side
            )
            data["reverse_side"] = PassportFile.de_json_decrypted(
                data.get("reverse_side"), bot, secure_data.reverse_side
            )
            data["selfie"] = PassportFile.de_json_decrypted(
                data.get("selfie"), bot, secure_data.selfie
            )
            data["translation"] = (
                PassportFile.de_list_decrypted(
                    data.get("translation"), bot, secure_data.translation
                )
                or None
            )

        return super().de_json(data=data, bot=bot)
