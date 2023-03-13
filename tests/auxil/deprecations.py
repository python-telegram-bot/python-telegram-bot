#!/usr/bin/env python

#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].

#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].

from _pytest.recwarn import WarningsRecorder

from telegram.warnings import PTBDeprecationWarning


def check_thumb_deprecation_warnings(recwarn: WarningsRecorder, calling_file: str) -> bool:
    """Check that the correct deprecation warnings are issued. This includes

    * a warning for using the deprecated `thumb` argument
    * a warning for using the deprecated `thumb` attribute

    Args:
        recwarn: pytest's recwarn fixture.
        calling_file: The file that called this function.

    Returns:
        True if the correct deprecation warnings were raised, False otherwise.

    Raises:
        AssertionError: If the correct deprecation warnings were not raised.
    """
    names = ("argument", "attribute")
    assert len(recwarn) == 2
    for i in range(2):
        assert issubclass(recwarn[i].category, PTBDeprecationWarning)
        assert f"{names[i]} 'thumb' to 'thumbnail'" in str(recwarn[i].message)
        assert (
            recwarn[i].filename == calling_file
        ), f"Warning for {names[i]} issued by file {recwarn[i].filename}, expected {calling_file}"

    return True
