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
"""This module contains an object that represents a Encrypted Passport Credentials."""
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

    @property
    def decrypted_secret(self):
        if not self._decrypted_secret:
            secret = b64decode(self.secret)
            self._decrypted_secret = self.bot.private_key.decrypt(secret, OAEP(
                mgf=MGF1(algorithm=SHA1()),
                algorithm=SHA1(),
                label=None
            ))
        return self._decrypted_secret

    @property
    def decrypted_data(self):
        if not self._decrypted_data:
            self._decrypted_data = decrypt_json(self.decrypted_secret, self.hash, self.data)
        return self._decrypted_data

    @property
    def payload(self):
        return self.decrypted_data['payload']

    @property
    def secure_data(self):
        return self.decrypted_data['secure_data']

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(bot=bot, **data)
