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
import json
from base64 import b64decode

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers.algorithms import AES
    from cryptography.hazmat.primitives.ciphers.modes import CBC
    from cryptography.hazmat.primitives.hashes import SHA512, SHA256, Hash, SHA1

    CRYPTO = True
except ImportError:
    CRYPTO = False
from future.utils import string_types

from telegram import TelegramObject


def decrypt(secret, hash, data):
    if isinstance(secret, string_types):
        secret = b64decode(secret)
    if isinstance(hash, string_types):
        hash = b64decode(hash)
    if isinstance(data, string_types):
        data = b64decode(data)
    digest = Hash(SHA512(), backend=default_backend())
    digest.update(secret + hash)
    secret_hash_hash = digest.finalize()
    key, iv = secret_hash_hash[:32], secret_hash_hash[32:32 + 16]
    cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    data = decryptor.update(data) + decryptor.finalize()
    digest = Hash(SHA256(), backend=default_backend())
    digest.update(data)
    data_hash = digest.finalize()
    if data_hash != hash:
        raise Exception("ERROR! Hashes are not equal! "
                        "{} != {}".format(data_hash, hash))  # TODO: Add proper exception
    return data[data[0]:]


def decrypt_json(secret, hash, data):
    return json.loads(decrypt(secret, hash, data).decode('utf-8'))


class EncryptedCredentials(TelegramObject):
    """Contains data required for decrypting and authenticating EncryptedPassportElement. See the
    Telegram Passport Documentation for a complete description of the data decryption and
    authentication processes.

    Attributes:
        data (:obj:`str`): Base64-encoded encrypted JSON-serialized data with unique user's
            payload, data hashes and secrets required for EncryptedPassportElement decryption and
            authentication
        hash (:obj:`str`): Base64-encoded data hash for data authentication
        secret (:obj:`str`): Base64-encoded secret, encrypted with the bot's public RSA key,
            required for data decryption

    Args:
        data (:obj:`str`): Base64-encoded encrypted JSON-serialized data with unique user's
            payload, data hashes and secrets required for EncryptedPassportElement decryption and
            authentication
        hash (:obj:`str`): Base64-encoded data hash for data authentication
        secret (:obj:`str`): Base64-encoded secret, encrypted with the bot's public RSA key,
            required for data decryption
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, data, hash, secret, bot=None, **kwargs):
        # Required
        self.data = data
        self.hash = hash
        self.secret = secret

        self._id_attrs = (self.data, self.hash, self.secret)

        self.bot = bot

        self._decrypted_secret = None
        self._decrypted_data = None

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['secret'] = bot.private_key.decrypt(b64decode(data.get('secret')), OAEP(
            mgf=MGF1(algorithm=SHA1()),
            algorithm=SHA1(),
            label=None
        ))
        data['data'] = Credentials.de_json(decrypt_json(data.get('secret'),
                                                        data.get('hash'),
                                                        data.get('data')),
                                           bot=bot)

        return cls(bot=bot, **data)


class Credentials(TelegramObject):
    def __init__(self, secure_data, payload, bot=None, **kwargs):
        # Required
        self.secure_data = secure_data
        self.payload = payload

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['secure_data'] = SecureData.de_json(data.get('secure_data'), bot=bot)

        return cls(bot=bot, **data)


class SecureData(TelegramObject):
    def __init__(self,
                 personal_details=None,
                 passport=None,
                 internal_passport=None,
                 driver_license=None,
                 identity_card=None,
                 address=None,
                 utility_bill=None,
                 bank_statement=None,
                 rental_agreement=None,
                 passport_registration=None,
                 temporary_registration=None,
                 bot=None,
                 **kwargs):
        # Optionals
        self.temporary_registration = temporary_registration
        self.passport_registration = passport_registration
        self.rental_agreement = rental_agreement
        self.bank_statement = bank_statement
        self.utility_bill = utility_bill
        self.address = address
        self.identity_card = identity_card
        self.driver_license = driver_license
        self.internal_passport = internal_passport
        self.passport = passport
        self.personal_details = personal_details

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['temporary_registration'] = SecureValue.de_json(data.get('temporary_registration'),
                                                             bot=bot)
        data['passport_registration'] = SecureValue.de_json(data.get('passport_registration'),
                                                            bot=bot)
        data['rental_agreement'] = SecureValue.de_json(data.get('rental_agreement'), bot=bot)
        data['bank_statement'] = SecureValue.de_json(data.get('bank_statement'), bot=bot)
        data['utility_bill'] = SecureValue.de_json(data.get('utility_bill'), bot=bot)
        data['address'] = SecureValue.de_json(data.get('address'), bot=bot)
        data['identity_card'] = SecureValue.de_json(data.get('identity_card'), bot=bot)
        data['driver_license'] = SecureValue.de_json(data.get('driver_license'), bot=bot)
        data['internal_passport'] = SecureValue.de_json(data.get('internal_passport'), bot=bot)
        data['passport'] = SecureValue.de_json(data.get('passport'), bot=bot)
        data['personal_details'] = SecureValue.de_json(data.get('personal_details'), bot=bot)

        return cls(bot=bot, **data)


class SecureValue(TelegramObject):
    def __init__(self,
                 data=None,
                 front_side=None,
                 reverse_side=None,
                 selfie=None,
                 files=None,
                 bot=None,
                 **kwargs):
        self.data = data
        self.front_side = front_side
        self.reverse_side = reverse_side
        self.selfie = selfie
        self.files = files

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['data'] = DataCredentials.de_json(data.get('data'), bot=bot)
        data['front_side'] = FileCredentials.de_json(data.get('front_side'), bot=bot)
        data['reverse_side'] = FileCredentials.de_json(data.get('reverse_side'), bot=bot)
        data['selfie'] = FileCredentials.de_json(data.get('selfie'), bot=bot)
        data['files'] = FileCredentials.de_list(data.get('files'), bot=bot)

        return cls(bot=bot, **data)


class _CredentialsBase(TelegramObject):
    def __init__(self, hash, secret, bot=None, **kwargs):
        self.hash = hash
        self.secret = secret

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        credentials = list()
        for credentials in data:
            credentials.append(cls.de_json(credentials, bot=bot))

        return credentials


class DataCredentials(_CredentialsBase):
    def __init__(self, data_hash, secret, **kwargs):
        super(DataCredentials, self).__init__(data_hash, secret, **kwargs)


class FileCredentials(_CredentialsBase):
    def __init__(self, file_hash, secret, **kwargs):
        super(FileCredentials, self).__init__(file_hash, secret, **kwargs)
