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

from telegram import PassportElementErrorDataField, PassportElementErrorSelfie


@pytest.fixture(scope='class')
def passport_element_error_data_field():
    return PassportElementErrorDataField(TestPassportElementErrorDataField.type,
                                         TestPassportElementErrorDataField.field_name,
                                         TestPassportElementErrorDataField.data_hash,
                                         TestPassportElementErrorDataField.message)


class TestPassportElementErrorDataField(object):
    source = 'data'
    type = 'test_type'
    field_name = 'test_field'
    data_hash = 'data_hash'
    message = 'Error message'

    def test_expected_values(self, passport_element_error_data_field):
        assert passport_element_error_data_field.source == self.source
        assert passport_element_error_data_field.type == self.type
        assert passport_element_error_data_field.field_name == self.field_name
        assert passport_element_error_data_field.data_hash == self.data_hash
        assert passport_element_error_data_field.message == self.message

    def test_to_dict(self, passport_element_error_data_field):
        passport_element_error_data_field_dict = passport_element_error_data_field.to_dict()

        assert isinstance(passport_element_error_data_field_dict, dict)
        assert (passport_element_error_data_field_dict['source']
                == passport_element_error_data_field.source)
        assert (passport_element_error_data_field_dict['type']
                == passport_element_error_data_field.type)
        assert (passport_element_error_data_field_dict['field_name']
                == passport_element_error_data_field.field_name)
        assert (passport_element_error_data_field_dict['data_hash']
                == passport_element_error_data_field.data_hash)
        assert (passport_element_error_data_field_dict['message']
                == passport_element_error_data_field.message)

    def test_equality(self):
        a = PassportElementErrorDataField(self.type, self.field_name, self.data_hash, self.message)
        b = PassportElementErrorDataField(self.type, self.field_name, self.data_hash, self.message)
        c = PassportElementErrorDataField(self.type, '', '', '')
        d = PassportElementErrorDataField('', self.field_name, '', '')
        e = PassportElementErrorDataField('', '', self.data_hash, '')
        f = PassportElementErrorDataField('', '', '', self.message)
        g = PassportElementErrorSelfie(self.type, '', self.message)

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

        assert a != g
        assert hash(a) != hash(g)
