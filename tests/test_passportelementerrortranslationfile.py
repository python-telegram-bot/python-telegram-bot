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

from telegram import PassportElementErrorTranslationFile, PassportElementErrorDataField


@pytest.fixture(scope='class')
def passport_element_error_translation_file():
    return PassportElementErrorTranslationFile(TestPassportElementErrorTranslationFile.type,
                                               TestPassportElementErrorTranslationFile.file_hash,
                                               TestPassportElementErrorTranslationFile.message)


class TestPassportElementErrorTranslationFile(object):
    source = 'translation_file'
    type = 'test_type'
    file_hash = 'file_hash'
    message = 'Error message'

    def test_expected_values(self, passport_element_error_translation_file):
        assert passport_element_error_translation_file.source == self.source
        assert passport_element_error_translation_file.type == self.type
        assert passport_element_error_translation_file.file_hash == self.file_hash
        assert passport_element_error_translation_file.message == self.message

    def test_to_dict(self, passport_element_error_translation_file):
        passport_element_error_translation_file_dict = \
            passport_element_error_translation_file.to_dict()

        assert isinstance(passport_element_error_translation_file_dict, dict)
        assert (passport_element_error_translation_file_dict['source']
                == passport_element_error_translation_file.source)
        assert (passport_element_error_translation_file_dict['type']
                == passport_element_error_translation_file.type)
        assert (passport_element_error_translation_file_dict['file_hash']
                == passport_element_error_translation_file.file_hash)
        assert (passport_element_error_translation_file_dict['message']
                == passport_element_error_translation_file.message)

    def test_equality(self):
        a = PassportElementErrorTranslationFile(self.type, self.file_hash, self.message)
        b = PassportElementErrorTranslationFile(self.type, self.file_hash, self.message)
        c = PassportElementErrorTranslationFile(self.type, '', '')
        d = PassportElementErrorTranslationFile('', self.file_hash, '')
        e = PassportElementErrorTranslationFile('', '', self.message)
        f = PassportElementErrorDataField(self.type, '', '', self.message)

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
