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
from pathlib import Path

import pytest

PROJECT_ROOT_PATH = Path(__file__).parent.parent.resolve()
TEST_DATA_PATH = Path(__file__).parent.resolve() / "data"


def data_file(filename: str) -> Path:
    return TEST_DATA_PATH / filename


@pytest.fixture()
def mro_slots():
    def _mro_slots(_class, only_parents: bool = False):
        if only_parents:
            classes = _class.__class__.__mro__[1:-1]
        else:
            classes = _class.__class__.__mro__[:-1]

        return [
            attr
            for cls in classes
            if hasattr(cls, "__slots__")  # The Exception class doesn't have slots
            for attr in cls.__slots__
            if attr != "__dict__"  # left here for classes which still has __dict__
        ]

    return _mro_slots
