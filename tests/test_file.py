#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import os
from pathlib import Path
from tempfile import TemporaryFile, mkstemp

import pytest
from flaky import flaky

from telegram import File, TelegramError, Voice


@pytest.fixture(scope='class')
def file(bot):
    return File(
        TestFile.file_id,
        TestFile.file_unique_id,
        file_path=TestFile.file_path,
        file_size=TestFile.file_size,
        bot=bot,
    )


@pytest.fixture(scope='class')
def local_file(bot):
    return File(
        TestFile.file_id,
        TestFile.file_unique_id,
        file_path=str(Path.cwd() / 'tests' / 'data' / 'local_file.txt'),
        file_size=TestFile.file_size,
        bot=bot,
    )


class TestFile:
    file_id = 'NOTVALIDDOESNOTMATTER'
    file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'
    file_path = (
        'https://api.org/file/bot133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0/document/file_3'
    )
    file_size = 28232
    file_content = 'Saint-Saëns'.encode()  # Intentionally contains unicode chars.

    def test_slot_behaviour(self, file, recwarn, mro_slots):
        for attr in file.__slots__:
            assert getattr(file, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not file.__dict__, f"got missing slot(s): {file.__dict__}"
        assert len(mro_slots(file)) == len(set(mro_slots(file))), "duplicate slot"
        file.custom, file.file_id = 'should give warning', self.file_id
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {
            'file_id': self.file_id,
            'file_unique_id': self.file_unique_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
        }
        new_file = File.de_json(json_dict, bot)

        assert new_file.file_id == self.file_id
        assert new_file.file_unique_id == self.file_unique_id
        assert new_file.file_path == self.file_path
        assert new_file.file_size == self.file_size

    def test_to_dict(self, file):
        file_dict = file.to_dict()

        assert isinstance(file_dict, dict)
        assert file_dict['file_id'] == file.file_id
        assert file_dict['file_unique_id'] == file.file_unique_id
        assert file_dict['file_path'] == file.file_path
        assert file_dict['file_size'] == file.file_size

    @flaky(3, 1)
    def test_error_get_empty_file_id(self, bot):
        with pytest.raises(TelegramError):
            bot.get_file(file_id='')

    def test_download_mutuall_exclusive(self, file):
        with pytest.raises(ValueError, match='custom_path and out are mutually exclusive'):
            file.download('custom_path', 'out')

    def test_download(self, monkeypatch, file):
        def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr('telegram.utils.request.Request.retrieve', test)
        out_file = file.download()

        try:
            with open(out_file, 'rb') as fobj:
                assert fobj.read() == self.file_content
        finally:
            os.unlink(out_file)

    def test_download_local_file(self, local_file):
        assert local_file.download() == local_file.file_path

    def test_download_custom_path(self, monkeypatch, file):
        def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr('telegram.utils.request.Request.retrieve', test)
        file_handle, custom_path = mkstemp()
        try:
            out_file = file.download(custom_path)
            assert out_file == custom_path

            with open(out_file, 'rb') as fobj:
                assert fobj.read() == self.file_content
        finally:
            os.close(file_handle)
            os.unlink(custom_path)

    def test_download_custom_path_local_file(self, local_file):
        file_handle, custom_path = mkstemp()
        try:
            out_file = local_file.download(custom_path)
            assert out_file == custom_path

            with open(out_file, 'rb') as fobj:
                assert fobj.read() == self.file_content
        finally:
            os.close(file_handle)
            os.unlink(custom_path)

    def test_download_no_filename(self, monkeypatch, file):
        def test(*args, **kwargs):
            return self.file_content

        file.file_path = None

        monkeypatch.setattr('telegram.utils.request.Request.retrieve', test)
        out_file = file.download()

        assert out_file[-len(file.file_id) :] == file.file_id
        try:
            with open(out_file, 'rb') as fobj:
                assert fobj.read() == self.file_content
        finally:
            os.unlink(out_file)

    def test_download_file_obj(self, monkeypatch, file):
        def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr('telegram.utils.request.Request.retrieve', test)
        with TemporaryFile() as custom_fobj:
            out_fobj = file.download(out=custom_fobj)
            assert out_fobj is custom_fobj

            out_fobj.seek(0)
            assert out_fobj.read() == self.file_content

    def test_download_file_obj_local_file(self, local_file):
        with TemporaryFile() as custom_fobj:
            out_fobj = local_file.download(out=custom_fobj)
            assert out_fobj is custom_fobj

            out_fobj.seek(0)
            assert out_fobj.read() == self.file_content

    def test_download_bytearray(self, monkeypatch, file):
        def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr('telegram.utils.request.Request.retrieve', test)

        # Check that a download to a newly allocated bytearray works.
        buf = file.download_as_bytearray()
        assert buf == bytearray(self.file_content)

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf

    def test_download_bytearray_local_file(self, local_file):
        # Check that a download to a newly allocated bytearray works.
        buf = local_file.download_as_bytearray()
        assert buf == bytearray(self.file_content)

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = local_file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf

    def test_equality(self, bot):
        a = File(self.file_id, self.file_unique_id, bot)
        b = File('', self.file_unique_id, bot)
        c = File(self.file_id, self.file_unique_id, None)
        d = File('', '', bot)
        e = Voice(self.file_id, self.file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
