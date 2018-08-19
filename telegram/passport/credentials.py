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
import binascii
import json
from base64 import b64decode

from future.utils import bord

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

from telegram import TelegramObject


class _TelegramDecryptionError(Exception):
    pass


def decrypt(secret, hash, data):
    """
    Decrypt per telegram docs at https://core.telegram.org/passport.

    Args:
        secret (:obj:`str` or :obj:`bytes`): The encryption secret, either as bytes or as a
            base64 encoded string.
        hash (:obj:`str` or :obj:`bytes`): The hash, either as bytes or as a
            base64 encoded string.
        data (:obj:`str` or :obj:`bytes`): The data to decrypt, either as bytes or as a
            base64 encoded string.

    Raises:
        :class:`TelegramDecryptionError`: Raised if the given hash does not match the hash of
            decrypted data

    Returns:
        :obj:`bytes`: The decrypted data as bytes

    """
    try:
        secret = b64decode(secret)
    except (binascii.Error, TypeError):
        pass
    try:
        hash = b64decode(hash)
    except (binascii.Error, TypeError):
        pass
    try:
        data = b64decode(data)
    except (binascii.Error, TypeError):
        pass
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
        raise _TelegramDecryptionError("Hashes are not equal! {} != {}".format(data_hash, hash))
    return data[bord(data[0]):]


def decrypt_json(secret, hash, data):
    """Decrypts data using secret and hash and then decodes utf-8 string and loads json"""
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

        # If already decrypted
        if isinstance(data['data'], dict):
            data['data'] = Credentials.de_json(data['data'], bot=bot)
        else:
            try:
                data['secret'] = bot.private_key.decrypt(b64decode(data.get('secret')), OAEP(
                    mgf=MGF1(algorithm=SHA1()),
                    algorithm=SHA1(),
                    label=None
                ))
            except ValueError as e:
                raise _TelegramDecryptionError(e)

            data['data'] = Credentials.de_json(decrypt_json(data.get('secret'),
                                                            data.get('hash'),
                                                            data.get('data')),
                                               bot=bot)

        return cls(bot=bot, **data)


class Credentials(TelegramObject):
    """
    Attributes:
        secure_data (:class:`telegram.SecureData`): Credentials for encrypted data
        payload (:obj:`str`): Bot-specified payload
    """

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
    """
    This object represents the credentials required to decrypt encrypted data.
    All fields are optional and depend on fields that were requested.

    Attributes:
        personal_details (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            personal details
        passport (:class:`telegram.SecureValue`, optional): Credentials for encrypted passport
        internal_passport (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            internal passport
        driver_license (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            driver license
        identity_card (:class:`telegram.SecureValue`, optional): Credentials for encrypted ID card
        address (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            residential address
        utility_bill (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            utility bill
        bank_statement (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            bank statement
        rental_agreement (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            rental agreement
        passport_registration (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            registration from internal passport
        temporary_registration (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            temporary registration
    """

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
    """
    This object represents the credentials required to decrypt encrypted value.
    All fields are optional and depend on the type of field.

    Attributes:
        data (:class:`telegram.DataCredentials`, optional): Credentials for encrypted Telegram
            Passport data. Available for "personal_details", "passport", "driver_license",
            "identity_card", "identity_passport" and "address" types.
        front_side (:class:`telegram.FileCredentials`, optional): Credentials for encrypted
            document's front side. Available for "passport", "driver_license", "identity_card"
            and "internal_passport".
        reverse_side (:class:`telegram.FileCredentials`, optional): Credentials for encrypted
            document's reverse side. Available for "driver_license" and "identity_card".
        selfie (:class:`telegram.FileCredentials`, optional): Credentials for encrypted selfie
            of the user with a document. Can be available for "passport", "driver_license",
            "identity_card" and "internal_passport".
        files (:class:`telegram.Array of FileCredentials`, optional): Credentials for encrypted
            files. Available for "utility_bill", "bank_statement", "rental_agreement",
            "passport_registration" and "temporary_registration" types.

    """

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

    def to_dict(self):
        data = super(SecureValue, self).to_dict()

        data['files'] = [p.to_dict() for p in self.files]

        return data


class _CredentialsBase(TelegramObject):
    """Base class for DataCredentials and FileCredentials."""

    def __init__(self, hash, secret, bot=None, **kwargs):
        self.hash = hash
        self.secret = secret

        # Aliases just be be sure
        self.file_hash = self.hash
        self.data_hash = self.hash

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
        for c in data:
            credentials.append(cls.de_json(c, bot=bot))

        return credentials


class DataCredentials(_CredentialsBase):
    """
    These credentials can be used to decrypt encrypted data from the data field in
    EncryptedPassportData.

    Args:
        data_hash (:obj:`str`): Checksum of encrypted data
        secret (:obj:`str`): Secret of encrypted data

    Attributes:
        hash (:obj:`str`): Checksum of encrypted data
        secret (:obj:`str`): Secret of encrypted data
    """

    def __init__(self, data_hash, secret, **kwargs):
        super(DataCredentials, self).__init__(data_hash, secret, **kwargs)

    def to_dict(self):
        data = super(DataCredentials, self).to_dict()

        del data['file_hash']
        del data['hash']

        return data


class FileCredentials(_CredentialsBase):
    """
        These credentials can be used to decrypt encrypted files from the front_side,
        reverse_side, selfie and files fields in EncryptedPassportData.

        Args:
            file_hash (:obj:`str`): Checksum of encrypted file
            secret (:obj:`str`): Secret of encrypted file

        Attributes:
            hash (:obj:`str`): Checksum of encrypted file
            secret (:obj:`str`): Secret of encrypted file
        """

    def __init__(self, file_hash, secret, **kwargs):
        super(FileCredentials, self).__init__(file_hash, secret, **kwargs)

    def to_dict(self):
        data = super(FileCredentials, self).to_dict()

        del data['data_hash']
        del data['hash']

        return data
