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
import inspect
from pathlib import Path

from telegram.ext._utils.stack import was_called_by


class TestStack:
    def test_none_input(self):
        assert not was_called_by(None, None)

    def test_called_by_current_file(self):
        frame = inspect.currentframe()
        file = Path(__file__)
        assert was_called_by(frame, file)

    # Testing a call by a different file is somewhat hard but it's covered in
    # TestUpdater/Application.test_manual_init_warning
