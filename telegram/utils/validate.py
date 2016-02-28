#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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

"""This module contains functions to validate function arguments"""

try:
    type(basestring)
except NameError:
    basestring = str


def validate_string(arg, name):
    """
    Validate a string argument. Raises a ValueError if `arg` is neither an
    instance of basestring (Python 2) or str (Python 3) nor None.

    Args:
        arg (basestring): The value to be tested
        name (str): The name of the argument, for the error message
    """
    if not isinstance(arg, basestring) and arg is not None:
        raise ValueError(name + " is not a string")
