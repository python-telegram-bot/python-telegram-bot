#!/usr/bin/env python
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
import sys
from platform import python_implementation

import pytest


def call_pre_commit_hook(hook_id):
    __tracebackhide__ = True
    return os.system(' '.join(['pre-commit', 'run', '--all-files', hook_id]))  # pragma: no cover


@pytest.mark.nocoverage
@pytest.mark.parametrize('hook_id', argvalues=('yapf', 'flake8', 'pylint'))
@pytest.mark.skipif(not (os.getenv('TRAVIS') or os.getenv('APPVEYOR')), reason='Not running in CI')
@pytest.mark.skipif(not sys.version_info[:2] == (3, 6) or python_implementation() != 'CPython',
                    reason='Only running pre-commit-hooks on newest tested python version, '
                           'as they are slow and consistent across platforms.')
def test_pre_commit_hook(hook_id):
    assert call_pre_commit_hook(hook_id) == 0  # pragma: no cover


@pytest.mark.nocoverage
@pytest.mark.skipif(
    not sys.version_info[:2] in ((3, 6), (2, 7)) or python_implementation() != 'CPython',
    reason='Only testing build on 2.7 and 3.6')
def test_build():
    assert os.system('python setup.py bdist_dumb') == 0  # pragma: no cover
