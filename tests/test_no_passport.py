#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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

with the TEST_NO_PASSPORT environment variable set in addition to the regular test suite.
Because actually uninstalling the optional dependencies would lead to errors in the test suite we
just mock the import to raise the expected exception.

Note that a fixture that just does this for every test that needs it is a nice idea, but for some
reason makes test_updater.py hang indefinitely on GitHub Actions (at least when Hinrich tried that)
"""
import os
from importlib import reload
from unittest import mock

import pytest

from telegram import bot
from telegram.passport import credentials
from tests.conftest import env_var_2_bool

TEST_NO_PASSPORT = env_var_2_bool(os.getenv('TEST_NO_PASSPORT', False))

if TEST_NO_PASSPORT:
    orig_import = __import__

    def import_mock(module_name, *args, **kwargs):
        if module_name.startswith('cryptography'):
            raise ModuleNotFoundError('We are testing without cryptography here')
        return orig_import(module_name, *args, **kwargs)

    with mock.patch('builtins.__import__', side_effect=import_mock):
        reload(bot)
        reload(credentials)


class TestNoPassport:
    """
    The monkeypatches simulate cryptography not being installed even when TEST_NO_PASSPORT is
    False, though that doesn't test the actual imports
    """

    def test_bot_init(self, bot_info, monkeypatch):
        if not TEST_NO_PASSPORT:
            monkeypatch.setattr(bot, 'CRYPTO_INSTALLED', False)
        with pytest.raises(RuntimeError, match='passport'):
            bot.Bot(bot_info['token'], private_key=1, private_key_password=2)

    def test_credentials_decrypt(self, monkeypatch):
        if not TEST_NO_PASSPORT:
            monkeypatch.setattr(credentials, 'CRYPTO_INSTALLED', False)
        with pytest.raises(RuntimeError, match='passport'):
            credentials.decrypt(1, 1, 1)

    def test_encrypted_credentials_decrypted_secret(self, monkeypatch):
        if not TEST_NO_PASSPORT:
            monkeypatch.setattr(credentials, 'CRYPTO_INSTALLED', False)
        ec = credentials.EncryptedCredentials('data', 'hash', 'secret')
        with pytest.raises(RuntimeError, match='passport'):
            ec.decrypted_secret
