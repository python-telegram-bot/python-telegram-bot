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
"""This module contains helper functions."""

import re
from datetime import datetime

try:
    from html import escape as escape_html  # noqa: F401
except ImportError:
    from cgi import escape as escape_html  # noqa: F401

# Not using future.backports.datetime here as datetime value might be an input from the user,
# making every isinstace() call more delicate. So we just use our own compat layer.
if hasattr(datetime, 'timestamp'):
    # Python 3.3+
    def _timestamp(dt_obj):
        return dt_obj.timestamp()
else:
    # Python < 3.3 (incl 2.7)
    from time import mktime

    def _timestamp(dt_obj):
        return mktime(dt_obj.timetuple())


def escape_markdown(text):
    """Helper function to escape telegram markup symbols."""
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

    return int(_timestamp(dt_obj))


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


def mention_html(user_id, name):
    """
    Args:
        user_id (:obj:`int`) The user's id which you want to mention.
        name (:obj:`str`) The name the mention is showing.

    Returns:
        :obj:`str`: The inline mention for the user as html.
    """
    if isinstance(user_id, int):
        return '<a href="tg://user?id={}">{}</a>'.format(user_id, escape_html(name))


def mention_markdown(user_id, name):
    """
    Args:
        user_id (:obj:`int`) The user's id which you want to mention.
        name (:obj:`str`) The name the mention is showing.

    Returns:
        :obj:`str`: The inline mention for the user as markdown.
    """
    if isinstance(user_id, int):
        return '[{}](tg://user?id={})'.format(escape_markdown(name), user_id)
