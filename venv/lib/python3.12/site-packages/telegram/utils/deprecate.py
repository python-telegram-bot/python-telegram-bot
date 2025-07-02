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
"""This module facilitates the deprecation of functions."""

import warnings


# We use our own DeprecationWarning since they are muted by default and "UserWarning" makes it
# seem like it's the user that issued the warning
# We name it something else so that you don't get confused when you attempt to suppress it
class TelegramDeprecationWarning(Warning):
    """Custom warning class for deprecations in this library."""

    __slots__ = ()


# Function to warn users that setting custom attributes is deprecated (Use only in __setattr__!)
# Checks if a custom attribute is added by checking length of dictionary before & after
# assigning attribute. This is the fastest way to do it (I hope!).
def set_new_attribute_deprecated(self: object, key: str, value: object) -> None:
    """Warns the user if they set custom attributes on PTB objects."""
    org = len(self.__dict__)
    object.__setattr__(self, key, value)
    new = len(self.__dict__)
    if new > org:
        warnings.warn(
            f"Setting custom attributes such as {key!r} on objects such as "
            f"{self.__class__.__name__!r} of the PTB library is deprecated.",
            TelegramDeprecationWarning,
            stacklevel=3,
        )
