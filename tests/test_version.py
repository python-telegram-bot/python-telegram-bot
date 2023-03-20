#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

from telegram import (
    __bot_api_version__,
    __bot_api_version_info__,
    __version__,
    __version_info__,
    constants,
)
from telegram._version import Version


class TestVersion:
    def test_bot_api_version_and_info(self):
        assert __bot_api_version__ is constants.BOT_API_VERSION
        assert __bot_api_version_info__ is constants.BOT_API_VERSION_INFO

    def test_version_and_info(self):
        assert __version__ == str(__version_info__)

    @pytest.mark.parametrize(
        ("version", "expected"),
        [
            (Version(1, 2, 3, "alpha", 4), "1.2.3a4"),
            (Version(2, 3, 4, "beta", 5), "2.3.4b5"),
            (Version(1, 2, 3, "candidate", 4), "1.2.3rc4"),
            (Version(1, 2, 0, "alpha", 4), "1.2a4"),
            (Version(2, 3, 0, "beta", 5), "2.3b5"),
            (Version(1, 2, 0, "candidate", 4), "1.2rc4"),
            (Version(1, 2, 3, "final", 0), "1.2.3"),
            (Version(1, 2, 0, "final", 0), "1.2"),
        ],
    )
    def test_version_str(self, version, expected):
        assert str(version) == expected

    @pytest.mark.parametrize("use_tuple", [True, False])
    def test_version_info(self, use_tuple):
        version = Version(1, 2, 3, "beta", 4)
        assert isinstance(version, tuple)
        assert version.major == version[0]
        assert version.minor == version[1]
        assert version.micro == version[2]
        assert version.releaselevel == version[3]
        assert version.serial == version[4]

        class TestClass:
            def __new__(cls, *args):
                if use_tuple:
                    return tuple(args)
                return Version(*args)

        assert isinstance(TestClass(1, 2, 3, "beta", 4), tuple if use_tuple else Version)
        assert version == TestClass(1, 2, 3, "beta", 4)
        assert not (version < TestClass(1, 2, 3, "beta", 4))
        assert version > TestClass(1, 2, 3, "beta", 3)
        assert version > TestClass(1, 2, 3, "alpha", 4)
        assert version < TestClass(1, 2, 3, "candidate", 0)
        assert version < TestClass(1, 2, 3, "final", 0)
        assert version < TestClass(1, 2, 4, "final", 0)
        assert version < TestClass(1, 3, 4, "final", 0)

        assert version < (1, 3)
        assert version >= (1, 2, 3, "alpha")
        assert version > (1, 1)
        assert version <= (1, 2, 3, "beta", 4)
        assert version < (1, 2, 3, "candidate", 4)
        assert not (version > (1, 2, 3, "candidate", 4))
        assert version < (1, 2, 4)
        assert version > (1, 2, 2)
