#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
import contextlib
import subprocess
import sys
from pathlib import Path

import pytest

import telegram._utils.datetime
import telegram._utils.files
from telegram import Animation, InputFile, MessageEntity
from tests.auxil.files import TEST_DATA_PATH, data_file


class TestFiles:
    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            (str(data_file("game.gif")), True),
            (str(TEST_DATA_PATH), False),
            (data_file("game.gif"), True),
            (TEST_DATA_PATH, False),
            ("https:/api.org/file/botTOKEN/document/file_3", False),
            (None, False),
        ],
    )
    def test_is_local_file(self, string, expected):
        assert telegram._utils.files.is_local_file(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected_local", "expected_non_local"),
        [
            (data_file("game.gif"), data_file("game.gif").as_uri(), InputFile),
            (TEST_DATA_PATH, TEST_DATA_PATH, TEST_DATA_PATH),
            ("file://foobar", "file://foobar", ValueError),
            (str(data_file("game.gif")), data_file("game.gif").as_uri(), InputFile),
            (str(TEST_DATA_PATH), str(TEST_DATA_PATH), str(TEST_DATA_PATH)),
            (
                "https:/api.org/file/botTOKEN/document/file_3",
                "https:/api.org/file/botTOKEN/document/file_3",
                "https:/api.org/file/botTOKEN/document/file_3",
            ),
        ],
        ids=[
            "Path(local_file)",
            "Path(directory)",
            "file_uri",
            "str-path local file",
            "str-path directory",
            "URL",
        ],
    )
    def test_parse_file_input_string(self, string, expected_local, expected_non_local):
        assert telegram._utils.files.parse_file_input(string, local_mode=True) == expected_local

        if expected_non_local is InputFile:
            assert isinstance(
                telegram._utils.files.parse_file_input(string, local_mode=False), InputFile
            )
        elif expected_non_local is ValueError:
            with pytest.raises(ValueError, match="but local mode is not enabled."):
                telegram._utils.files.parse_file_input(string, local_mode=False)
        else:
            assert (
                telegram._utils.files.parse_file_input(string, local_mode=False)
                == expected_non_local
            )

    def test_parse_file_input_file_like(self):
        source_file = data_file("game.gif")
        with source_file.open("rb") as file:
            parsed = telegram._utils.files.parse_file_input(file)

        assert isinstance(parsed, InputFile)
        assert parsed.filename == "game.gif"

        with source_file.open("rb") as file:
            parsed = telegram._utils.files.parse_file_input(file, filename="test_file")

        assert isinstance(parsed, InputFile)
        assert parsed.filename == "test_file"

    def test_parse_file_input_bytes(self):
        source_file = data_file("text_file.txt")
        parsed = telegram._utils.files.parse_file_input(source_file.read_bytes())

        assert isinstance(parsed, InputFile)
        assert parsed.filename == "application.octet-stream"

        parsed = telegram._utils.files.parse_file_input(
            source_file.read_bytes(), filename="test_file"
        )

        assert isinstance(parsed, InputFile)
        assert parsed.filename == "test_file"

    def test_parse_file_input_tg_object(self):
        animation = Animation("file_id", "unique_id", 1, 1, 1)
        assert telegram._utils.files.parse_file_input(animation, Animation) == "file_id"
        assert telegram._utils.files.parse_file_input(animation, MessageEntity) is animation

    @pytest.mark.parametrize("obj", [{1: 2}, [1, 2], (1, 2)])
    def test_parse_file_input_other(self, obj):
        assert telegram._utils.files.parse_file_input(obj) is obj

    @pytest.mark.parametrize("attach", [True, False])
    def test_parse_file_input_attach(self, attach):
        source_file = data_file("text_file.txt")
        parsed = telegram._utils.files.parse_file_input(source_file.read_bytes(), attach=attach)

        assert isinstance(parsed, InputFile)
        assert bool(parsed.attach_name) is attach

    def test_load_file_none(self):
        assert telegram._utils.files.load_file(None) == (None, None)

    @pytest.mark.parametrize("arg", [b"bytes", "string", InputFile(b"content"), Path("file/path")])
    def test_load_file_no_file(self, arg):
        out = telegram._utils.files.load_file(arg)
        assert out[0] is None
        assert out[1] is arg

    def test_load_file_file_handle(self):
        out = telegram._utils.files.load_file(data_file("telegram.gif").open("rb"))
        assert out[0] == "telegram.gif"
        assert out[1] == data_file("telegram.gif").read_bytes()

    def test_load_file_subprocess_pipe(self):
        png_file = data_file("telegram.png")
        cmd_str = "type" if sys.platform == "win32" else "cat"
        cmd = [cmd_str, str(png_file)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=(sys.platform == "win32"))
        out = telegram._utils.files.load_file(proc.stdout)

        assert out[0] is None
        assert out[1] == png_file.read_bytes()

        with contextlib.suppress(ProcessLookupError):
            proc.kill()
            # This exception may be thrown if the process has finished before we had the chance
            # to kill it.
