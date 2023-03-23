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

from _pytest.recwarn import WarningsRecorder

from telegram._utils import warnings_transition
from telegram.warnings import PTBDeprecationWarning


def check_thumb_deprecation_warnings_for_args_and_attrs(
    recwarn: WarningsRecorder,
    calling_file: str,
    deprecated_name: str = "thumb",
    new_name: str = "thumbnail",
    expected_recwarn_length: int = 2,
) -> bool:
    """Check that the correct deprecation warnings are issued. This includes

    * a warning for using the deprecated `thumb...` argument
    * a warning for using the deprecated `thumb...` attribute

    Args:
        recwarn: pytest's recwarn fixture.
        calling_file: The file that called this function.
        deprecated_name: Name of deprecated argument/attribute to check in the warning text.
        new_name: Name of new argument/attribute to check in the warning text.
        expected_recwarn_length: expected number of warnings issued.

    Returns:
        True if the correct deprecation warnings were raised, False otherwise.

    Raises:
        AssertionError: If the correct deprecation warnings were not raised.
    """
    names = (
        ("argument", "attribute")
        if expected_recwarn_length == 2
        else ("argument", "argument", "attribute")
    )
    actual_recwarn_length = len(recwarn)
    assert actual_recwarn_length == expected_recwarn_length, (
        f"expected recwarn length {expected_recwarn_length}, actual length {actual_recwarn_length}"
        f". Contents: {[item.message for item in recwarn.list]}"
    )
    for i in range(expected_recwarn_length):
        assert issubclass(recwarn[i].category, PTBDeprecationWarning)
        assert f"{names[i]} '{deprecated_name}' to '{new_name}'" in str(recwarn[i].message), (
            f'Warning issued by file {recwarn[i].filename} ("{str(recwarn[i].message)}") '
            "does not contain expected phrase: "
            f"\"{names[i]} '{deprecated_name}' to '{new_name}'\""
        )

        assert recwarn[i].filename == calling_file, (
            f'Warning for {names[i]} ("{str(recwarn[i].message)}") was issued by file '
            f"{recwarn[i].filename}, expected {calling_file} or {warnings_transition.__file__}"
        )

    return True
