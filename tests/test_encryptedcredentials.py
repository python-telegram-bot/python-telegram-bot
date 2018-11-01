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

import pytest

from telegram import EncryptedCredentials, PassportElementError


@pytest.fixture(scope='class')
def encrypted_credentials():
    return EncryptedCredentials(TestEncryptedCredentials.data,
                                TestEncryptedCredentials.hash,
                                TestEncryptedCredentials.secret)


class TestEncryptedCredentials(object):
    data = 'data'
    hash = 'hash'
    secret = 'secret'

    def test_expected_values(self, encrypted_credentials):
        assert encrypted_credentials.data == self.data
        assert encrypted_credentials.hash == self.hash
        assert encrypted_credentials.secret == self.secret

    def test_to_dict(self, encrypted_credentials):
        encrypted_credentials_dict = encrypted_credentials.to_dict()

        assert isinstance(encrypted_credentials_dict, dict)
        assert (encrypted_credentials_dict['data']
                == encrypted_credentials.data)
        assert (encrypted_credentials_dict['hash']
                == encrypted_credentials.hash)
        assert (encrypted_credentials_dict['secret']
                == encrypted_credentials.secret)

    def test_equality(self):
        a = EncryptedCredentials(self.data, self.hash, self.secret)
        b = EncryptedCredentials(self.data, self.hash, self.secret)
        c = EncryptedCredentials(self.data, '', '')
        d = EncryptedCredentials('', self.hash, '')
        e = EncryptedCredentials('', '', self.secret)
        f = PassportElementError('source', 'type', 'message')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)
