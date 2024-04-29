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

"""
This file tests the case that PTB was installed *without* the optional dependency `passport`.
Currently this only means that cryptography is not installed.

Because imports in pytest are intricate, we just run
    pytest -k test_no_passport.py

with the TEST_WITH_OPT_DEPS environment variable set to False in addition to the regular test suite
"""
import pytest

from telegram import _bot as bot
from telegram._passport import credentials
from tests.auxil.envvars import TEST_WITH_OPT_DEPS


@pytest.mark.skipif(
    TEST_WITH_OPT_DEPS, reason="Only relevant if the optional dependency is not installed"
)
class TestNoPassportWithoutRequest:
    def test_bot_init(self, bot_info):
        with pytest.raises(RuntimeError, match="passport"):
            bot.Bot(bot_info["token"], private_key=1, private_key_password=2)

    def test_credentials_decrypt(self):
        with pytest.raises(RuntimeError, match="passport"):
            credentials.decrypt(1, 1, 1)

    def test_encrypted_credentials_decrypted_secret(self):
        ec = credentials.EncryptedCredentials("data", "hash", "secret")
        with pytest.raises(RuntimeError, match="passport"):
            ec.decrypted_secret
