#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
from flaky import flaky

from telegram import File, TelegramError, Voice


@pytest.fixture(scope='class')
def file(bot):
    return File(TestFile.file_id,
                file_path=TestFile.file_path,
                file_size=TestFile.file_size,
                bot=bot)


class TestFile(object):
    file_id = 'NOTVALIDDOESNOTMATTER'
    file_path = (
        u'https://api.org/file/bot133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0/document/file_3')
    file_size = 28232

    def test_de_json(self, bot):
        json_dict = {
            'file_id': self.file_id,
            'file_path': self.file_path,
            'file_size': self.file_size
        }
        new_file = File.de_json(json_dict, bot)

        assert new_file.file_id == self.file_id
        assert new_file.file_path == self.file_path
        assert new_file.file_size == self.file_size

    def test_to_dict(self, file):
        file_dict = file.to_dict()

        assert isinstance(file_dict, dict)
        assert file_dict['file_id'] == file.file_id
        assert file_dict['file_path'] == file.file_path
        assert file_dict['file_size'] == file.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_get_empty_file_id(self, bot):
        with pytest.raises(TelegramError):
            bot.get_file(file_id='')

    def test_download(self, monkeypatch, file):
        def test(*args, **kwargs):
            raise TelegramError('test worked')

        monkeypatch.setattr('telegram.utils.request.Request.download', test)
        with pytest.raises(TelegramError, match='test worked'):
            file.download()

    def test_equality(self, bot):
        a = File(self.file_id, bot)
        b = File(self.file_id, bot)
        c = File(self.file_id, None)
        d = File('', bot)
        e = Voice(self.file_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
