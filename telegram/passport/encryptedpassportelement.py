#!/usr/bin/env python
# flake8: noqa: E501
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
"""This module contains an object that represents a Telegram EncryptedPassportElement."""
from base64 import b64decode

from telegram import (TelegramObject, PassportFile, PersonalDetails, IdDocumentData,
                      ResidentialAddress)
from telegram.passport.credentials import decrypt_json


class EncryptedPassportElement(TelegramObject):
    """
    Contains information about documents or other Telegram Passport elements shared with the bot
    by the user. The data has been automatically decrypted by python-telegram-bot.

    Attributes:
        type (:obj:`str`): Element type. One of "personal_details", "passport", "driver_license",
            "identity_card", "internal_passport", "address", "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration", "temporary_registration", "phone_number",
            "email".
        data (:class:`telegram.PersonalDetails` or :class:`telegram.IdDocument` or :class:`telegram.ResidentialAddress` or :obj:`str`):
            Optional. Decrypted or encrypted data, available for "personal_details", "passport",
            "driver_license", "identity_card", "identity_passport" and "address" types.
        phone_number (:obj:`str`): Optional. User's verified phone number, available only for
            "phone_number" type.
        email (:obj:`str`): Optional. User's verified email address, available only for "email"
            type.
        files (List[:class:`telegram.PassportFile`]): Optional. Array of encrypted/decrypted files
            with documents provided by the user, available for "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration" and "temporary_registration" types.
        front_side (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            front side of the document, provided by the user. Available for "passport",
            "driver_license", "identity_card" and "internal_passport".
        reverse_side (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            reverse side of the document, provided by the user. Available for "driver_license" and
            "identity_card".
        selfie (:class:`telegram.PassportFile`): Optional. Encrypted/decrypted file with the
            selfie of the user holding a document, provided by the user; available for "passport",
            "driver_license", "identity_card" and "internal_passport".
        translation (List[:class:`telegram.PassportFile`]): Optional. Array of encrypted/decrypted
            files with translated versions of documents provided by the user. Available if
            requested for "passport", "driver_license", "identity_card", "internal_passport",
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration" and
            "temporary_registration" types.
        hash (:obj:`str`): Base64-encoded element hash for using in
            :class:`telegram.PassportElementErrorUnspecified`.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        type (:obj:`str`): Element type. One of "personal_details", "passport", "driver_license",
            "identity_card", "internal_passport", "address", "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration", "temporary_registration", "phone_number",
            "email".
        data (:class:`telegram.PersonalDetails` or :class:`telegram.IdDocument` or :class:`telegram.ResidentialAddress` or :obj:`str`, optional):
            Decrypted or encrypted data, available for "personal_details", "passport",
            "driver_license", "identity_card", "identity_passport" and "address" types.
        phone_number (:obj:`str`, optional): User's verified phone number, available only for
            "phone_number" type.
        email (:obj:`str`, optional): User's verified email address, available only for "email"
            type.
        files (List[:class:`telegram.PassportFile`], optional): Array of encrypted/decrypted files
            with documents provided by the user, available for "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration" and "temporary_registration" types.
        front_side (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            front side of the document, provided by the user. Available for "passport",
            "driver_license", "identity_card" and "internal_passport".
        reverse_side (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            reverse side of the document, provided by the user. Available for "driver_license" and
            "identity_card".
        selfie (:class:`telegram.PassportFile`, optional): Encrypted/decrypted file with the
            selfie of the user holding a document, provided by the user; available for "passport",
            "driver_license", "identity_card" and "internal_passport".
        translation (List[:class:`telegram.PassportFile`], optional): Array of encrypted/decrypted
            files with translated versions of documents provided by the user. Available if
            requested for "passport", "driver_license", "identity_card", "internal_passport",
            "utility_bill", "bank_statement", "rental_agreement", "passport_registration" and
            "temporary_registration" types.
        hash (:obj:`str`): Base64-encoded element hash for using in
            :class:`telegram.PassportElementErrorUnspecified`.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Note:
        This object is decrypted only when originating from
        :obj:`telegram.PassportData.decrypted_data`.
    """

    def __init__(self,
                 type,
                 data=None,
                 phone_number=None,
                 email=None,
                 files=None,
                 front_side=None,
                 reverse_side=None,
                 selfie=None,
                 translation=None,
                 hash=None,
                 bot=None,
                 credentials=None,
                 **kwargs):
        # Required
        self.type = type
        # Optionals
        self.data = data
        self.phone_number = phone_number
        self.email = email
        self.files = files
        self.front_side = front_side
        self.reverse_side = reverse_side
        self.selfie = selfie
        self.translation = translation
        self.hash = hash

        self._id_attrs = (self.type, self.data, self.phone_number, self.email, self.files,
                          self.front_side, self.reverse_side, self.selfie)

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(EncryptedPassportElement, cls).de_json(data, bot)

        data['files'] = PassportFile.de_list(data.get('files'), bot) or None
        data['front_side'] = PassportFile.de_json(data.get('front_side'), bot)
        data['reverse_side'] = PassportFile.de_json(data.get('reverse_side'), bot)
        data['selfie'] = PassportFile.de_json(data.get('selfie'), bot)
        data['translation'] = PassportFile.de_list(data.get('translation'), bot) or None

        return cls(bot=bot, **data)

    @classmethod
    def de_json_decrypted(cls, data, bot, credentials):
        if not data:
            return None

        data = super(EncryptedPassportElement, cls).de_json(data, bot)

        if data['type'] not in ('phone_number', 'email'):
            secure_data = getattr(credentials.secure_data, data['type'])

            if secure_data.data is not None:
                # If not already decrypted
                if not isinstance(data['data'], dict):
                    data['data'] = decrypt_json(b64decode(secure_data.data.secret),
                                                b64decode(secure_data.data.hash),
                                                b64decode(data['data']))
                if data['type'] == 'personal_details':
                    data['data'] = PersonalDetails.de_json(data['data'], bot=bot)
                elif data['type'] in ('passport', 'internal_passport',
                                      'driver_license', 'identity_card'):
                    data['data'] = IdDocumentData.de_json(data['data'], bot=bot)
                elif data['type'] == 'address':
                    data['data'] = ResidentialAddress.de_json(data['data'], bot=bot)

            data['files'] = PassportFile.de_list_decrypted(data.get('files'), bot,
                                                           secure_data.files) or None
            data['front_side'] = PassportFile.de_json_decrypted(data.get('front_side'), bot,
                                                                secure_data.front_side)
            data['reverse_side'] = PassportFile.de_json_decrypted(data.get('reverse_side'), bot,
                                                                  secure_data.reverse_side)
            data['selfie'] = PassportFile.de_json_decrypted(data.get('selfie'), bot,
                                                            secure_data.selfie)
            data['translation'] = PassportFile.de_list_decrypted(data.get('translation'), bot,
                                                                 secure_data.translation) or None

        return cls(bot=bot, **data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        encrypted_passport_elements = list()
        for element in data:
            encrypted_passport_elements.append(cls.de_json(element, bot))

        return encrypted_passport_elements

    def to_dict(self):
        data = super(EncryptedPassportElement, self).to_dict()

        if self.files:
            data['files'] = [p.to_dict() for p in self.files]
        if self.translation:
            data['translation'] = [p.to_dict() for p in self.translation]

        return data
