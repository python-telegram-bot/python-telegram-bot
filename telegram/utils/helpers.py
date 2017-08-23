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
from telegram import User, Message

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


def mention(user, html=False, name=None):
    """
    Args:
        user (:obj:`int` | :class:`telegram.User` | :class:`telegram.Message`)
            The user's id, or User object, or a Message from the user which you want to mention.
        html (:obj:`bool`) Default output as markdown, pass True to use HTML.
        name (:obj:`str`) The name the mention is showing. Required when id is provided in user.
            Optional if User or Message is provided and will overwrite the name in user.

    Returns:
        str:
    """
    if not user:
        return None

    if isinstance(user, Message):
        user = Message.from_user

    if isinstance(user, int) and name:
        if html:
            return '<a href="tg://user?id={}">{}</a>'.format(user, escape_html(name))
        else:
            return "[{}](tg://user?id={}".format(escape_markdown(name), user)

    elif isinstance(user, User):
        if not name:
            if user.last_name:
                fullname = '{} {}'.format(user.first_name, user.last_name)
            else:
                fullname = user.first_name

            if html:
                return '<a href="tg://user?id={}">{}</a>'.format(user.id, escape_html(fullname))
            else:
                return "[{}](tg://user?id={}".format(escape_markdown(fullname), user.id)
        else:
            if html:
                return '<a href="tg://user?id={}">{}</a>'.format(user.id, escape_html(name))
            else:
                return "[{}](tg://user?id={}".format(escape_markdown(name), user.id)
