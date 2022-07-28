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
"""This module contains helper functions related to enums.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
import sys
from enum import Enum
from typing import Type, TypeVar, Union

if sys.version_info >= (3, 11):
    from enum import StrEnum

_A = TypeVar("_A")
_B = TypeVar("_B")
_Enum = TypeVar("_Enum", bound=Enum)


def get_member(enum: Type[_Enum], value: _A, default: _B) -> Union[_Enum, _A, _B]:
    """Tries to call ``enum(value)`` to convert the value into an enumeration member.
    If that fails, the ``default`` is returned.
    """
    try:
        return enum(value)
    except ValueError:
        return default


# Python 3.11 and above has a different output for mixin classes for IntEnum, StrEnum and IntFlag
# see https://docs.python.org/3.11/library/enum.html#notes. We want e.g. str(StrEnumTest.FOO) to
# return "StrEnumTest.FOO" instead of "foo".
if sys.version_info < (3, 11):

    class StringEnum(str, Enum):
        """Helper class for string enums where the value is not important to be displayed on
        stringification.
        """

        __slots__ = ()

        def __repr__(self) -> str:
            return f"<{self.__class__.__name__}.{self.name}>"

else:

    class StringEnum(StrEnum):
        """Helper class for string enums where the value is not important to be displayed on
        stringification.
        """

        __slots__ = ()

        def __repr__(self) -> str:
            return f"<{self.__class__.__name__}.{self.name}>"

        def __str__(self) -> str:
            return f"{self.__class__.__name__}.{self.name}"

        def __format__(self, format_spec: str) -> str:
            return str.__format__(self.value, format_spec)
