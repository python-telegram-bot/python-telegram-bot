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
from pathlib import Path

import pytest

import telegram.utils.datetime
import telegram.utils.files
from telegram import InputFile, Animation, MessageEntity


class TestFiles:
    @pytest.mark.parametrize(
        'string,expected',
        [
            ('tests/data/game.gif', True),
            ('tests/data', False),
            (str(Path.cwd() / 'tests' / 'data' / 'game.gif'), True),
            (str(Path.cwd() / 'tests' / 'data'), False),
            (Path.cwd() / 'tests' / 'data' / 'game.gif', True),
            (Path.cwd() / 'tests' / 'data', False),
            ('https:/api.org/file/botTOKEN/document/file_3', False),
            (None, False),
        ],
    )
    def test_is_local_file(self, string, expected):
        assert telegram.utils.files.is_local_file(string) == expected

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('tests/data/game.gif', (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri()),
            ('tests/data', 'tests/data'),
            ('file://foobar', 'file://foobar'),
            (
                str(Path.cwd() / 'tests' / 'data' / 'game.gif'),
                (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri(),
            ),
            (str(Path.cwd() / 'tests' / 'data'), str(Path.cwd() / 'tests' / 'data')),
            (
                Path.cwd() / 'tests' / 'data' / 'game.gif',
                (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri(),
            ),
            (Path.cwd() / 'tests' / 'data', Path.cwd() / 'tests' / 'data'),
            (
                'https:/api.org/file/botTOKEN/document/file_3',
                'https:/api.org/file/botTOKEN/document/file_3',
            ),
        ],
    )
    def test_parse_file_input_string(self, string, expected):
        assert telegram.utils.files.parse_file_input(string) == expected

    def test_parse_file_input_file_like(self):
        source_file = Path('tests/data/game.gif')
        with source_file.open('rb') as file:
            parsed = telegram.utils.files.parse_file_input(file)

        assert isinstance(parsed, InputFile)
        assert not parsed.attach
        assert parsed.filename == 'game.gif'

        with source_file.open('rb') as file:
            parsed = telegram.utils.files.parse_file_input(file, attach=True, filename='test_file')

        assert isinstance(parsed, InputFile)
        assert parsed.attach
        assert parsed.filename == 'test_file'

    def test_parse_file_input_bytes(self):
        source_file = Path('tests/data/text_file.txt')
        parsed = telegram.utils.files.parse_file_input(source_file.read_bytes())

        assert isinstance(parsed, InputFile)
        assert not parsed.attach
        assert parsed.filename == 'application.octet-stream'

        parsed = telegram.utils.files.parse_file_input(
            source_file.read_bytes(), attach=True, filename='test_file'
        )

        assert isinstance(parsed, InputFile)
        assert parsed.attach
        assert parsed.filename == 'test_file'

    def test_parse_file_input_tg_object(self):
        animation = Animation('file_id', 'unique_id', 1, 1, 1)
        assert telegram.utils.files.parse_file_input(animation, Animation) == 'file_id'
        assert telegram.utils.files.parse_file_input(animation, MessageEntity) is animation

    @pytest.mark.parametrize('obj', [{1: 2}, [1, 2], (1, 2)])
    def test_parse_file_input_other(self, obj):
        assert telegram.utils.files.parse_file_input(obj) is obj
