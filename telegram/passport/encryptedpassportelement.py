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
"""This module contains an object that represents a Telegram EncryptedPassportElement."""

from telegram import TelegramObject, PassportFile
from telegram.passport.credentials import decrypt_json


class EncryptedPassportElement(TelegramObject):
    """Contains information about documents or other Telegram Passport elements shared with the bot
       by the user.

    Attributes:
        type (:obj:`str`): Element type. One of “personal_details”, “passport”, “driver_license”,
            “identity_card”, “internal_passport”, “address”, “utility_bill”, “bank_statement”,
            “rental_agreement”, “passport_registration”, “temporary_registration”, “phone_number”,
            “email”.
        data (:obj:`str`): Optional. Base64-encoded encrypted Telegram Passport element data
            provided by the user, available for “personal_details”, “passport”, “driver_license”,
            “identity_card”, “identity_passport” and “address” types. Can be decrypted and verified
            using the accompanying EncryptedCredentials.
        phone_number (:obj:`str`): Optional. User's verified phone number, available only for
            “phone_number” type
        email (:obj:`str`): Optional. User's verified email address, available only for “email”
            type
        files (List[:class:`telegram.PassportFile`]): Optional. Array of encrypted files with
            documents provided by the user, available for “utility_bill”, “bank_statement”,
            “rental_agreement”, “passport_registration” and “temporary_registration” types.
            Files can be decrypted and verified using the accompanying EncryptedCredentials.
        front_side (:class:`PassportFile`): Optional. Encrypted file with the front side of the
            document, provided by the user. Available for “passport”, “driver_license”,
            “identity_card” and “internal_passport”. The file can be decrypted and verified using
            the accompanying EncryptedCredentials.
        reverse_side (:class:`PassportFile`): Optional. Encrypted file with the reverse side of the
            document, provided by the user. Available for “driver_license” and “identity_card”.
            The file can be decrypted and verified using the accompanying EncryptedCredentials.
        selfie (:class:`PassportFile`): Optional. Encrypted file with the selfie of the user
            holding a document, provided by the user; available for “passport”, “driver_license”,
            “identity_card” and “internal_passport”. The file can be decrypted and verified using
            the accompanying EncryptedCredentials.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        type (:obj:`str`): Element type. One of “personal_details”, “passport”, “driver_license”,
            “identity_card”, “internal_passport”, “address”, “utility_bill”, “bank_statement”,
            “rental_agreement”, “passport_registration”, “temporary_registration”, “phone_number”,
            “email”.
        data (:obj:`str`, optional): Base64-encoded encrypted Telegram Passport element data
            provided by the user, available for “personal_details”, “passport”, “driver_license”,
            “identity_card”, “identity_passport” and “address” types. Can be decrypted and verified
            using the accompanying EncryptedCredentials.
        phone_number (:obj:`str`, optional): User's verified phone number, available only for
            “phone_number” type
        email (:obj:`str`, optional): User's verified email address, available only for “email”
            type
        files (List[:class:`telegram.PassportFile`], optional): Array of encrypted files with
            documents provided by the user, available for “utility_bill”, “bank_statement”,
            “rental_agreement”, “passport_registration” and “temporary_registration” types.
            Files can be decrypted and verified using the accompanying EncryptedCredentials.
        front_side (:class:`PassportFile`, optional): Encrypted file with the front side of the
            document, provided by the user. Available for “passport”, “driver_license”,
            “identity_card” and “internal_passport”. The file can be decrypted and verified using
            the accompanying EncryptedCredentials.
        reverse_side (:class:`PassportFile`, optional): Encrypted file with the reverse side of the
            document, provided by the user. Available for “driver_license” and “identity_card”.
            The file can be decrypted and verified using the accompanying EncryptedCredentials.
        selfie (:class:`PassportFile`, optional): Encrypted file with the selfie of the user
            holding a document, provided by the user; available for “passport”, “driver_license”,
            “identity_card” and “internal_passport”. The file can be decrypted and verified using
            the accompanying EncryptedCredentials.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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

        self._id_attrs = (self.type, self.data, self.phone_number, self.email, self.files,
                          self.front_side, self.reverse_side, self.selfie)

        self.bot = bot
        self._credentials = credentials

    # noinspection PyMethodOverriding
    @classmethod
    def de_json(cls, data, bot, credentials):
        if not data:
            return None

        secure_data = None
        if data['type'] not in ('phone_number', 'email'):
            secure_data = getattr(credentials.data.secure_data, data['type'])

            data['data'] = decrypt_json(secure_data.data.secret,
                                        secure_data.data.hash,
                                        data['data'])

            if secure_data:
                data['files'] = PassportFile.de_list(data.get('files'), bot, secure_data)
                data['front_side'] = PassportFile.de_json(data.get('front_side'),
                                                          bot, secure_data.front_side)
                data['reverse_side'] = PassportFile.de_json(data.get('reverse_side'),
                                                            bot, secure_data.reverse_side)
                data['selfie'] = PassportFile.de_json(data.get('selfie'),
                                                      bot, secure_data.selfie)

        return cls(bot=bot, credentials=secure_data, **data)

    @classmethod
    def de_list(cls, data, bot, credentials):
        if not data:
            return []

        encrypted_passport_elements = list()
        for element in data:
            encrypted_passport_elements.append(cls.de_json(element, bot, credentials))

        return encrypted_passport_elements

    def to_dict(self):
        data = super(EncryptedPassportElement, self).to_dict()

        if self.files:
            data['files'] = [p.to_dict() for p in self.files]

        return data
