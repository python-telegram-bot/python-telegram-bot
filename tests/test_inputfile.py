#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import os
import subprocess
import sys
from io import BytesIO

from telegram import InputFile


class TestInputFile(object):
    png = os.path.join('tests', 'data', 'game.png')

    def test_subprocess_pipe(self):
        if sys.platform == 'win32':
            cmd = ['type', self.png]
        else:
            cmd = ['cat', self.png]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=(sys.platform == 'win32'))
        in_file = InputFile(proc.stdout)

        assert in_file.input_file_content == open(self.png, 'rb').read()
        assert in_file.mimetype == 'image/png'
        assert in_file.filename == 'image.png'

        try:
            proc.kill()
        except ProcessLookupError:
            # This exception may be thrown if the process has finished before we had the chance
            # to kill it.
            pass

    def test_mimetypes(self):
        # Only test a few to make sure logic works okay
        assert InputFile(open('tests/data/telegram.jpg', 'rb')).mimetype == 'image/jpeg'
        if sys.version_info >= (3, 5):
            assert InputFile(open('tests/data/telegram.webp', 'rb')).mimetype == 'image/webp'
        assert InputFile(open('tests/data/telegram.mp3', 'rb')).mimetype == 'audio/mpeg'

        # Test guess from file
        assert InputFile(BytesIO(b'blah'), filename='tg.jpg').mimetype == 'image/jpeg'
        assert InputFile(BytesIO(b'blah'), filename='tg.mp3').mimetype == 'audio/mpeg'

        # Test fallback
        assert (InputFile(BytesIO(b'blah'), filename='tg.notaproperext').mimetype
                == 'application/octet-stream')
        assert InputFile(BytesIO(b'blah')).mimetype == 'application/octet-stream'

    def test_filenames(self):
        assert InputFile(open('tests/data/telegram.jpg', 'rb')).filename == 'telegram.jpg'
        assert InputFile(open('tests/data/telegram.jpg', 'rb'),
                         filename='blah').filename == 'blah'
        assert InputFile(open('tests/data/telegram.jpg', 'rb'),
                         filename='blah.jpg').filename == 'blah.jpg'
        assert InputFile(open('tests/data/telegram', 'rb')).filename == 'telegram'
        assert InputFile(open('tests/data/telegram', 'rb'),
                         filename='blah').filename == 'blah'
        assert InputFile(open('tests/data/telegram', 'rb'),
                         filename='blah.jpg').filename == 'blah.jpg'

        class MockedFileobject(object):
            # A open(?, 'rb') without a .name
            def __init__(self, f):
                self.f = open(f, 'rb')

            def read(self):
                return self.f.read()

        assert InputFile(MockedFileobject('tests/data/telegram.jpg')).filename == 'image.jpeg'
        assert InputFile(MockedFileobject('tests/data/telegram.jpg'),
                         filename='blah').filename == 'blah'
        assert InputFile(MockedFileobject('tests/data/telegram.jpg'),
                         filename='blah.jpg').filename == 'blah.jpg'
        assert InputFile(
            MockedFileobject('tests/data/telegram')).filename == 'application.octet-stream'
        assert InputFile(MockedFileobject('tests/data/telegram'),
                         filename='blah').filename == 'blah'
        assert InputFile(MockedFileobject('tests/data/telegram'),
                         filename='blah.jpg').filename == 'blah.jpg'
