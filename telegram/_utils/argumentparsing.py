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
"""This module contains helper functions related to parsing arguments for classes and methods.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from typing import Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def parse_sequence_arg(arg: Optional[Sequence[T]]) -> Tuple[T, ...]:
    """Parses an optional sequence into a tuple

    Args:
        arg (:obj:`Sequence`): The sequence to parse.

    Returns:
        :obj:`Tuple`: The sequence converted to a tuple or an empty tuple.
    """
    return tuple(arg) if arg else ()
