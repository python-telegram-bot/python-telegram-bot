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
"""This module contains helper functions."""
from html import escape

import re
import signal
from datetime import datetime

# From https://stackoverflow.com/questions/2549939/get-signal-names-from-numbers-in-python
_signames = {v: k
             for k, v in reversed(sorted(vars(signal).items()))
             if k.startswith('SIG') and not k.startswith('SIG_')}


def get_signal_name(signum):
    """Returns the signal name of the given signal number."""
    return _signames[signum]


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
        return u'<a href="tg://user?id={}">{}</a>'.format(user_id, escape(name))


def mention_markdown(user_id, name):
    """
    Args:
        user_id (:obj:`int`) The user's id which you want to mention.
        name (:obj:`str`) The name the mention is showing.

    Returns:
        :obj:`str`: The inline mention for the user as markdown.
    """
    if isinstance(user_id, int):
        return u'[{}](tg://user?id={})'.format(escape_markdown(name), user_id)


def effective_message_type(entity):
    """
    Extracts the type of message as a string identifier from a :class:`telegram.Message` or a
    :class:`telegram.Update`.

    Args:
        entity (:obj:`Update` | :obj:`Message`) The ``update`` or ``message`` to extract from

    Returns:
        str: One of ``Message.MESSAGE_TYPES``

    """

    # Importing on file-level yields cyclic Import Errors
    from telegram import Message
    from telegram import Update

    if isinstance(entity, Message):
        message = entity
    elif isinstance(entity, Update):
        message = entity.effective_message
    else:
        raise TypeError("entity is not Message or Update (got: {})".format(type(entity)))

    for i in Message.MESSAGE_TYPES:
        if getattr(message, i, None):
            return i

    return None
