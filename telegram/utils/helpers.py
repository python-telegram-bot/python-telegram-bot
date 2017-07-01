#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
""" This module contains helper functions """

import re
from datetime import datetime
from time import mktime

try:
    from html import escape as escape_html  # noqa: F401
except ImportError:
    from cgi import escape as escape_html  # noqa: F401


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def to_timestamp(dt_obj):
    """
    Args:
        dt_obj (:class:`datetime.datetime`):

    Returns:
        int:
    """
    if not dt_obj:
        return None

    try:
        # Python 3.3+
        return int(dt_obj.timestamp())
    except AttributeError:
        # Python 3 (< 3.3) and Python 2
        return int(mktime(dt_obj.timetuple()))


def from_timestamp(unixtime):
    """
    Args:
        unixtime (int):

    Returns:
        datetime.datetime:
    """
    if not unixtime:
        return None

    return datetime.fromtimestamp(unixtime)
