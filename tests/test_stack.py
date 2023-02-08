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
from pathlib import Path

from telegram.ext._utils.stack import was_called_by


class TestStack:
    def test_none_input(self):
        assert not was_called_by(None, None)

    def test_called_by_current_file(self):
        frame = inspect.currentframe()
        file = Path(__file__)
        assert was_called_by(frame, file)

    def test_called_by_symlink_file(self, tmp_path):
        # Set up a call from a linked file in a temp directory,
        # then test it with its resolved path.
        # Here we expect `was_called_by` to recognize
        # "`tmp_path`/foo_link.py" as same as "`tmp_path`/foo.py".
        temp_file = tmp_path / "foo.py"
        foo_content = "import inspect\ndef foo_func():\
            \n    return inspect.currentframe()"
        with temp_file.open("w") as f:
            f.write(foo_content)
        symlink_file = tmp_path / "foo_link.py"
        symlink_file.symlink_to(temp_file)
        import sys

        sys.path.append(tmp_path.as_posix())
        from foo_link import foo_func

        frame = foo_func()
        assert was_called_by(frame, temp_file)

    def test_called_by_symlink_file_nested(self, tmp_path):
        # Same as test_called_by_symlink_file except
        # foo_func is nested inside bar_func to test
        # if `was_called_by` can resolve paths in recursion.
        temp_file1 = tmp_path / "foo.py"
        foo_content = "import inspect\ndef foo_func():\
            \n    return inspect.currentframe()"
        with temp_file1.open("w") as f:
            f.write(foo_content)
        temp_file2 = tmp_path / "bar.py"
        bar_content = "from foo import foo_func\ndef bar_func():\
            \n    return foo_func()"
        with temp_file2.open("w") as f:
            f.write(bar_content)
        symlink_file2 = tmp_path / "bar_link.py"
        symlink_file2.symlink_to(temp_file2)
        import sys

        sys.path.append(tmp_path.as_posix())
        from bar_link import bar_func

        frame = bar_func()
        assert was_called_by(frame, temp_file2)

    # Testing a call by a different file is somewhat hard but it's covered in
    # TestUpdater/Application.test_manual_init_warning
