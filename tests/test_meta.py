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
import os

import pytest

from tests.auxil.envvars import env_var_2_bool

skip_disabled = pytest.mark.skipif(
    not env_var_2_bool(os.getenv("TEST_BUILD", "")), reason="TEST_BUILD not enabled"
)


# To make the tests agnostic of the cwd
@pytest.fixture(autouse=True)
def _change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.config.rootdir)


@skip_disabled
def test_build():
    assert os.system("python setup.py bdist_dumb") == 0  # pragma: no cover


@skip_disabled
def test_build_raw():
    assert os.system("python setup-raw.py bdist_dumb") == 0  # pragma: no cover
