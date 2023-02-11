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
import logging
import sys
from pathlib import Path

import pytest

from telegram.ext._utils.stack import was_called_by


def symlink_to(source: Path, target: Path) -> None:
    """Wrapper around Path.symlink_to that pytest-skips OS Errors.
    Useful e.g. for making tests not fail locally due to permission errors.
    """
    try:
        source.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"Skipping due to OS error while creating symlink: {exc!r}")


class TestStack:
    def test_none_input(self):
        assert not was_called_by(None, None)

    def test_called_by_current_file(self):
        # Testing a call by a different file is somewhat hard but it's covered in
        # TestUpdater/Application.test_manual_init_warning
        frame = inspect.currentframe()
        file = Path(__file__)
        assert was_called_by(frame, file)

    def test_exception(self, monkeypatch, caplog):
        def resolve(self):
            raise RuntimeError("Can Not Resolve")

        with caplog.at_level(logging.DEBUG):
            monkeypatch.setattr(Path, "resolve", resolve)
            assert not was_called_by(inspect.currentframe(), None)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == logging.DEBUG
        assert caplog.records[0].getMessage().startswith("Failed to check")
        assert caplog.records[0].exc_info[0] is RuntimeError
        assert "Can Not Resolve" in str(caplog.records[0].exc_info[1])

    def test_called_by_symlink_file(self, tmp_path):
        # Set up a call from a linked file in a temp directory,
        # then test it with its resolved path.
        # Here we expect `was_called_by` to recognize
        # "`tmp_path`/caller_link.py" as same as "`tmp_path`/caller.py".
        temp_file = tmp_path / "caller.py"
        caller_content = """
import inspect
def caller_func():
    return inspect.currentframe()
        """
        with temp_file.open("w") as f:
            f.write(caller_content)

        symlink_file = tmp_path / "caller_link.py"
        symlink_to(symlink_file, temp_file)

        sys.path.append(tmp_path.as_posix())
        from caller_link import caller_func

        frame = caller_func()
        assert was_called_by(frame, temp_file)

    def test_called_by_symlink_file_nested(self, tmp_path):
        # Same as test_called_by_symlink_file except
        # inner_func is nested inside outer_func to test
        # if `was_called_by` can resolve paths in recursion.
        temp_file1 = tmp_path / "inner.py"
        inner_content = """
import inspect
def inner_func():
    return inspect.currentframe()
        """
        with temp_file1.open("w") as f:
            f.write(inner_content)

        temp_file2 = tmp_path / "outer.py"
        outer_content = """
from inner import inner_func
def outer_func():
    return inner_func()
        """
        with temp_file2.open("w") as f:
            f.write(outer_content)

        symlink_file2 = tmp_path / "outer_link.py"
        symlink_to(symlink_file2, temp_file2)

        sys.path.append(tmp_path.as_posix())
        from outer_link import outer_func

        frame = outer_func()
        assert was_called_by(frame, temp_file2)
