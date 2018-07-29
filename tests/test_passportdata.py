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

from telegram import PassportData, EncryptedPassportElement, EncryptedCredentials


@pytest.fixture(scope='class')
def passport_data(bot):
    return PassportData(TestPassportData.data,
                        TestPassportData.credentials,
                        bot=bot)


class TestPassportData(object):
    data = [EncryptedPassportElement('type', 'data')]
    credentials = EncryptedCredentials('data', 'hash', 'secret')

    def test_expected_values(self, passport_data):
        assert passport_data.data == self.data
        assert passport_data.credentials == self.credentials

    def test_de_json(self, bot):
        json_dict = {'data': [data.to_dict() for data in self.data],
                     'credentials': self.credentials.to_dict()}
        passport_data = PassportData.de_json(json_dict, bot)

        assert isinstance(passport_data.data, list)
        assert passport_data.data == self.data
        assert passport_data.credentials == self.credentials

    def test_to_dict(self, passport_data):
        passport_data_dict = passport_data.to_dict()

        assert isinstance(passport_data_dict, dict)
        assert isinstance(passport_data_dict['data'], list)
        assert (passport_data_dict['credentials'] ==
                passport_data.credentials.to_dict())

    def test_equality(self):
        a = PassportData(self.data, self.credentials)
        b = PassportData(self.data, self.credentials)
        c = PassportData(self.data,
                         EncryptedCredentials('wrong_data', 'wrong_hash', 'wrong_secret'))

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
