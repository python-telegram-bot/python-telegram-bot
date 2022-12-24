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
import os
import platform

import pytest

from tests.conftest import env_var_2_bool

skip_disabled = pytest.mark.skipif(
    not env_var_2_bool(os.getenv("TEST_BUILD", False)), reason="TEST_BUILD not enabled"
)


# To make the tests agnostic of the cwd
@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.config.rootdir)


@skip_disabled
@pytest.mark.skipif(platform.system() != "Windows", reason="Cmdline stuff for only windows")
class TestSetupWindows:
    @classmethod
    def setup_class(cls):
        """Added so we can setup a venv folder"""
        os.system("python -m venv venv_setup_test")

    @classmethod
    def teardown_class(cls):
        """Remove the venv folder and other build stuff"""
        os.system('for %d in (build dist venv_setup_test) do rmdir "%~d" /s /q')
        os.system("pip install -r requirements.txt")

    def test_build(self):
        assert (
            os.system(".\\venv_setup_test\\Scripts\\python.exe setup.py bdist_dumb") == 0
        )  # pragma: no cover
        # this is a neat hack, convincing the local python venv that ptb isn't installed
        # there are more files (see above), but this one is the one python apperently uses to
        # discover local packages
        os.system("rmdir /s /q python_telegram_bot.egg-info")

    def test_build_raw(self):
        assert (
            os.system(".\\venv_setup_test\\Scripts\\python.exe setup-raw.py bdist_dumb") == 0
        )  # pragma: no cover
        os.system("rmdir /s /q python_telegram_bot_raw.egg-info")


@skip_disabled
def test_build_with_telegram_package():
    os.system("pip install telegram")
    res = os.popen("python setup.py bdist_dumb")
    assert "Both libraries provide a Python package called `telegram`" in res.read()
    assert res.close() != 0
    res = os.popen("python setup-raw.py bdist_dumb")
    assert "Both libraries provide a Python package called `telegram`" in res.read()
    assert res.close() != 0


@skip_disabled
def test_build_with_telegram_raw_package():
    os.system("pip uninstall -y telegram")
    os.system("pip install python-telegram-bot --pre")
    res = os.popen("python setup-raw.py bdist_dumb")
    assert "uninstall python-telegram-bot " in res.read()
    assert res.close() != 0
    os.system("pip uninstall -y python-telegram-bot")


@skip_disabled
def test_build_with_telegram_not_raw_package():
    os.system("pip install python-telegram-bot-raw --pre")
    res = os.popen("python setup.py bdist_dumb")
    assert "uninstall python-telegram-bot-raw " in res.read()
    assert res.close() != 0
    os.system("pip uninstall -y python-telegram-bot-raw")


@skip_disabled
def test_build_with_local_telegram_package():
    res = os.popen("python setup.py bdist_dumb")
    assert "Please rename it" in res.read()
    assert res.close() != 0
    res = os.popen("python setup-raw.py bdist_dumb")
    assert "Please rename it" in res.read()
    assert res.close() != 0
