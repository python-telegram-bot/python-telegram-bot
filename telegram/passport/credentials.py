#!/usr/bin/env python
#
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
try:
    import ujson as json
except ImportError:
    import json
from base64 import b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA512, SHA256, Hash, SHA1

from telegram import TelegramObject, TelegramError


class TelegramDecryptionError(TelegramError):
    """
    Something went wrong with decryption.
    """

    def __init__(self, message):
        super().__init__("TelegramDecryptionError: {}".format(message))


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
        file (:obj:`bool`): Force data to be treated as raw data, instead of trying to
            b64decode it.

    Raises:
        :class:`TelegramDecryptionError`: Given hash does not match hash of decrypted data.

    Returns:
        :obj:`bytes`: The decrypted data as bytes.

    """
    # Make a SHA512 hash of secret + update
    digest = Hash(SHA512(), backend=default_backend())
    digest.update(secret + hash)
    secret_hash_hash = digest.finalize()
    # First 32 chars is our key, next 16 is the initialisation vector
    key, iv = secret_hash_hash[:32], secret_hash_hash[32:32 + 16]
    # Init a AES-CBC cipher and decrypt the data
    cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    data = decryptor.update(data) + decryptor.finalize()
    # Calculate SHA256 hash of the decrypted data
    digest = Hash(SHA256(), backend=default_backend())
    digest.update(data)
    data_hash = digest.finalize()
    # If the newly calculated hash did not match the one telegram gave us
    if data_hash != hash:
        # Raise a error that is caught inside telegram.PassportData and transformed into a warning
        raise TelegramDecryptionError("Hashes are not equal! {} != {}".format(data_hash, hash))
    # Return data without padding
    return data[data[0]:]


def decrypt_json(secret, hash, data):
    """Decrypts data using secret and hash and then decodes utf-8 string and loads json"""
    return json.loads(decrypt(secret, hash, data).decode('utf-8'))


class EncryptedCredentials(TelegramObject):
    """Contains data required for decrypting and authenticating EncryptedPassportElement. See the
    Telegram Passport Documentation for a complete description of the data decryption and
    authentication processes.

    Attributes:
        data (:class:`telegram.Credentials` or :obj:`str`): Decrypted data with unique user's
            nonce, data hashes and secrets used for EncryptedPassportElement decryption and
            authentication or base64 encrypted data.
        hash (:obj:`str`): Base64-encoded data hash for data authentication.
        secret (:obj:`str`): Decrypted or encrypted secret used for decryption.

    Args:
        data (:class:`telegram.Credentials` or :obj:`str`): Decrypted data with unique user's
            nonce, data hashes and secrets used for EncryptedPassportElement decryption and
            authentication or base64 encrypted data.
        hash (:obj:`str`): Base64-encoded data hash for data authentication.
        secret (:obj:`str`): Decrypted or encrypted secret used for decryption.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Note:
        This object is decrypted only when originating from
        :obj:`telegram.PassportData.decrypted_credentials`.

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

        data = super().de_json(data, bot)

        return cls(bot=bot, **data)

    @property
    def decrypted_secret(self):
        """
        :obj:`str`: Lazily decrypt and return secret.

        Raises:
            telegram.TelegramDecryptionError: Decryption failed. Usually due to bad
                private/public key but can also suggest malformed/tampered data.
        """
        if self._decrypted_secret is None:
            # Try decrypting according to step 1 at
            # https://core.telegram.org/passport#decrypting-data
            # We make sure to base64 decode the secret first.
            # Telegram says to use OAEP padding so we do that. The Mask Generation Function
            # is the default for OAEP, the algorithm is the default for PHP which is what
            # Telegram's backend servers run.
            try:
                self._decrypted_secret = self.bot.private_key.decrypt(b64decode(self.secret), OAEP(
                    mgf=MGF1(algorithm=SHA1()),
                    algorithm=SHA1(),
                    label=None
                ))
            except ValueError as e:
                # If decryption fails raise exception
                raise TelegramDecryptionError(e)
        return self._decrypted_secret

    @property
    def decrypted_data(self):
        """
        :class:`telegram.Credentials`: Lazily decrypt and return credentials data. This object
            also contains the user specified nonce as
            `decrypted_data.nonce`.

        Raises:
            telegram.TelegramDecryptionError: Decryption failed. Usually due to bad
                private/public key but can also suggest malformed/tampered data.
        """
        if self._decrypted_data is None:
            self._decrypted_data = Credentials.de_json(decrypt_json(self.decrypted_secret,
                                                                    b64decode(self.hash),
                                                                    b64decode(self.data)),
                                                       self.bot)
        return self._decrypted_data


class Credentials(TelegramObject):
    """
    Attributes:
        secure_data (:class:`telegram.SecureData`): Credentials for encrypted data
        nonce (:obj:`str`): Bot-specified nonce
    """

    def __init__(self, secure_data, nonce, bot=None, **kwargs):
        # Required
        self.secure_data = secure_data
        self.nonce = nonce

        self.bot = bot

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['secure_data'] = SecureData.de_json(data.get('secure_data'), bot=bot)

        return cls(bot=bot, **data)


class SecureData(TelegramObject):
    """
    This object represents the credentials that were used to decrypt the encrypted data.
    All fields are optional and depend on fields that were requested.

    Attributes:
        personal_details (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            personal details.
        passport (:class:`telegram.SecureValue`, optional): Credentials for encrypted passport.
        internal_passport (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            internal passport.
        driver_license (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            driver license.
        identity_card (:class:`telegram.SecureValue`, optional): Credentials for encrypted ID card
        address (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            residential address.
        utility_bill (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            utility bill.
        bank_statement (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            bank statement.
        rental_agreement (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            rental agreement.
        passport_registration (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            registration from internal passport.
        temporary_registration (:class:`telegram.SecureValue`, optional): Credentials for encrypted
            temporary registration.
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
    This object represents the credentials that were used to decrypt the encrypted value.
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
        translation (List[:class:`telegram.FileCredentials`], optional): Credentials for an
            encrypted translation of the document. Available for "passport", "driver_license",
            "identity_card", "internal_passport", "utility_bill", "bank_statement",
            "rental_agreement", "passport_registration" and "temporary_registration".
        files (List[:class:`telegram.FileCredentials`], optional): Credentials for encrypted
            files. Available for "utility_bill", "bank_statement", "rental_agreement",
            "passport_registration" and "temporary_registration" types.

    """

    def __init__(self,
                 data=None,
                 front_side=None,
                 reverse_side=None,
                 selfie=None,
                 files=None,
                 translation=None,
                 bot=None,
                 **kwargs):
        self.data = data
        self.front_side = front_side
        self.reverse_side = reverse_side
        self.selfie = selfie
        self.files = files
        self.translation = translation

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
        data['translation'] = FileCredentials.de_list(data.get('translation'), bot=bot)

        return cls(bot=bot, **data)

    def to_dict(self):
        data = super().to_dict()

        data['files'] = [p.to_dict() for p in self.files]
        data['translation'] = [p.to_dict() for p in self.translation]

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
        super().__init__(data_hash, secret, **kwargs)

    def to_dict(self):
        data = super().to_dict()

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
        super().__init__(file_hash, secret, **kwargs)

    def to_dict(self):
        data = super().to_dict()

        del data['data_hash']
        del data['hash']

        return data
