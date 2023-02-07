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
import inspect
import os
from pathlib import Path

from telegram.ext._utils.stack import was_called_by


class TestStack:
    def test_none_input(self):
        assert not was_called_by(None, None)

    def test_called_by_current_file(self):
        frame = inspect.currentframe()
        file = Path(__file__)
        assert was_called_by(frame, file)

    def test_called_by_file_in_symlink(self):
        tests_folder = Path(__file__).parent
        project_root = tests_folder.parent
        temp_symlink = project_root / "temp_tests"
        dummy_file_content = "import inspect\ndef dummy_func():\
            \n    return inspect.currentframe() "
        try:
            # Set up a call from a different file in a symlink directory,
            # then test it with its resolved path.
            # Here we expect `was_called_by` to recognize
            # "../temp_tests/dummy.py" as same as "../tests/dummy".
            os.symlink(tests_folder, temp_symlink)
            with open(temp_symlink / "dummy.py", 'w') as f:
                f.write(dummy_file_content)
            from temp_tests.dummy import dummy_func

            frame = dummy_func()
            file = tests_folder / "dummy.py"
            assert was_called_by(frame, file)
        finally:
            if os.path.exists(temp_symlink):
                os.unlink(temp_symlink)
            if os.path.exists(tests_folder / "dummy.py"):
                os.remove(tests_folder / "dummy.py")

    # Testing a call by a different file is somewhat hard but it's covered in
    # TestUpdater/Application.test_manual_init_warning
