#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import logging
import subprocess
import sys
from io import BytesIO

import pytest

from telegram import InputFile
from tests.conftest import data_file


@pytest.fixture(scope='class')
def png_file():
    return data_file('game.png')


class TestInputFile:
    def test_slot_behaviour(self, mro_slots):
        inst = InputFile(BytesIO(b'blah'), filename='tg.jpg')
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_subprocess_pipe(self, png_file):
        cmd_str = 'type' if sys.platform == 'win32' else 'cat'
        cmd = [cmd_str, str(png_file)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=(sys.platform == 'win32'))
        in_file = InputFile(proc.stdout)

        assert in_file.input_file_content == png_file.read_bytes()
        assert in_file.mimetype == 'image/png'
        assert in_file.filename == 'image.png'

        try:
            proc.kill()
        except ProcessLookupError:
            # This exception may be thrown if the process has finished before we had the chance
            # to kill it.
            pass

    def test_mimetypes(self, caplog):
        # Only test a few to make sure logic works okay
        assert InputFile(data_file('telegram.jpg').open('rb')).mimetype == 'image/jpeg'
        assert InputFile(data_file('telegram.webp').open('rb')).mimetype == 'image/webp'
        assert InputFile(data_file('telegram.mp3').open('rb')).mimetype == 'audio/mpeg'

        # Test guess from file
        assert InputFile(BytesIO(b'blah'), filename='tg.jpg').mimetype == 'image/jpeg'
        assert InputFile(BytesIO(b'blah'), filename='tg.mp3').mimetype == 'audio/mpeg'

        # Test fallback
        assert (
            InputFile(BytesIO(b'blah'), filename='tg.notaproperext').mimetype
            == 'application/octet-stream'
        )
        assert InputFile(BytesIO(b'blah')).mimetype == 'application/octet-stream'

        # Test string file
        with caplog.at_level(logging.DEBUG):
            assert InputFile(data_file('text_file.txt').open()).mimetype == 'text/plain'

            assert len(caplog.records) == 1
            assert caplog.records[0].getMessage().startswith('Could not parse file content')

    def test_filenames(self):
        assert InputFile(data_file('telegram.jpg').open('rb')).filename == 'telegram.jpg'
        assert InputFile(data_file('telegram.jpg').open('rb'), filename='blah').filename == 'blah'
        assert (
            InputFile(data_file('telegram.jpg').open('rb'), filename='blah.jpg').filename
            == 'blah.jpg'
        )
        assert InputFile(data_file('telegram').open('rb')).filename == 'telegram'
        assert InputFile(data_file('telegram').open('rb'), filename='blah').filename == 'blah'
        assert (
            InputFile(data_file('telegram').open('rb'), filename='blah.jpg').filename == 'blah.jpg'
        )

        class MockedFileobject:
            # A open(?, 'rb') without a .name
            def __init__(self, f):
                self.f = f.open('rb')

            def read(self):
                return self.f.read()

        assert InputFile(MockedFileobject(data_file('telegram.jpg'))).filename == 'image.jpeg'
        assert (
            InputFile(MockedFileobject(data_file('telegram.jpg')), filename='blah').filename
            == 'blah'
        )
        assert (
            InputFile(MockedFileobject(data_file('telegram.jpg')), filename='blah.jpg').filename
            == 'blah.jpg'
        )
        assert (
            InputFile(MockedFileobject(data_file('telegram'))).filename
            == 'application.octet-stream'
        )
        assert (
            InputFile(MockedFileobject(data_file('telegram')), filename='blah').filename == 'blah'
        )
        assert (
            InputFile(MockedFileobject(data_file('telegram')), filename='blah.jpg').filename
            == 'blah.jpg'
        )

    def test_send_bytes(self, bot, chat_id):
        # We test this here and not at the respective test modules because it's not worth
        # duplicating the test for the different methods
        message = bot.send_document(chat_id, data_file('text_file.txt').read_bytes())
        out = BytesIO()

        assert message.document.get_file().download(out=out)

        out.seek(0)

        assert out.read().decode('utf-8') == 'PTB Rocks!'
