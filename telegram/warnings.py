#! /usr/bin/env python
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
"""This module contains classes used for warnings issued by this library.

.. versionadded:: 20.0
"""

__all__ = ["PTBDeprecationWarning", "PTBRuntimeWarning", "PTBUserWarning"]


class PTBUserWarning(UserWarning):
    """
    Custom user warning class used for warnings in this library.

    .. seealso:: :wiki:`Exceptions, Warnings and Logging <Exceptions%2C-Warnings-and-Logging>`

    .. versionadded:: 20.0
    """

    __slots__ = ()


class PTBRuntimeWarning(PTBUserWarning, RuntimeWarning):
    """
    Custom runtime warning class used for warnings in this library.

    .. versionadded:: 20.0
    """

    __slots__ = ()


# https://www.python.org/dev/peps/pep-0565/ recommends using a custom warning class derived from
# DeprecationWarning. We also subclass from PTBUserWarning so users can easily 'switch off'
# warnings
class PTBDeprecationWarning(PTBUserWarning, DeprecationWarning):
    """
    Custom warning class for deprecations in this library.

    .. versionchanged:: 20.0
       Renamed TelegramDeprecationWarning to PTBDeprecationWarning.
    """

    __slots__ = ()
