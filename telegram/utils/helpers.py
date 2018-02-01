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

import re
from collections import OrderedDict
import signal
from datetime import datetime

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    from html import escape as escape_html  # noqa: F401
except ImportError:
    from cgi import escape as escape_html  # noqa: F401


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


def _extract_urls_from_text(text):
    """
    Returns a list of urls from a text string.
    URLs without a leading `http://` or `www.` won't be found.
    """
    out = []
    for word in text.split(' '):
        thing = urlparse(word.strip())
        if thing.scheme:
            out.append(word)
    return out


def extract_urls(message):
    """
    Extracts all Hyperlinks that are contained in a message. This includes
    message entities and the media caption. The links are returned in lexicographically
    ascending order.

    Note: Exact duplicates are removed, but there may still be URLs that link
    to the same resource.

    Args:
        message (:obj:`telegram.Message`) The message to extract from

    Returns:
        :obj:`list`: A list of URLs contained in the message
    """
    from telegram import MessageEntity

    results = message.parse_entities(types=[MessageEntity.URL, MessageEntity.TEXT_LINK])
    all_urls = [v if k.type == MessageEntity.URL else k.url for k, v in results.items()]

    if message.caption:
        all_urls += _extract_urls_from_text(message.caption)

    # Strip trailing slash from URL so we can compare them for equality
    stripped_urls = [x[:-1] if x[-1] == '/' else x for x in all_urls]

    urls = set(stripped_urls)
    return sorted(list(urls))
