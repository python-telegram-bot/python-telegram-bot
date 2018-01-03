#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
    pass


def warn_deprecate_obj(old, new, stacklevel=3):
    warnings.warn(
        '{0} is being deprecated, please use {1} from now on.'.format(old, new),
        category=TelegramDeprecationWarning,
        stacklevel=stacklevel)


def deprecate(func, old, new):
    """Warn users invoking old to switch to the new function."""

    def f(*args, **kwargs):
        warn_deprecate_obj(old, new)
        return func(*args, **kwargs)

    return f
