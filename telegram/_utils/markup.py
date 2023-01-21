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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains a helper function for Telegram's ReplyMarkups

.. versionchanged:: 20.0
   Previously, the contents of this module were available through the (no longer existing)
   class ``telegram.ReplyMarkup``.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from collections.abc import Sequence


def check_keyboard_type(keyboard: object) -> bool:
    """Checks if the keyboard provided is of the correct type - A sequence of sequences.
    Implicitly tested in the init-tests of `{Inline, Reply}KeyboardMarkup`
    """
    # string and bytes may actually be used for ReplyKeyboardMarkup in which case each button
    # would contain a single character. But that use case should be discouraged and we don't
    # allow it here.
    if not isinstance(keyboard, Sequence) or isinstance(keyboard, (str, bytes)):
        return False

    # Determine the dimension of the keyboard.
    def dim(keyboard: Sequence, current_dim: int = 0) -> int:
        if isinstance(keyboard, Sequence) and not isinstance(keyboard, (str, bytes)):
            current_dim += 1
            return dim(keyboard[0], current_dim)
        return current_dim

    if dim(keyboard) >= 3:
        return False

    for row in keyboard:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)):
            return False
    return True
