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
from collections import defaultdict

try:
    import ujson as json
except ImportError:
    import json
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

    return datetime.utcfromtimestamp(unixtime)


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


def create_deep_linked_url(bot_username, payload=None, group=False):
    """
    Creates a deep-linked URL for this ``bot_username`` with the specified ``payload``.
    See  https://core.telegram.org/bots#deep-linking to learn more.

    The ``payload`` may consist of the following characters: ``A-Z, a-z, 0-9, _, -``

    Note:
        Works well in conjunction with
        ``CommandHandler("start", callback, filters = Filters.regex('payload'))``

    Examples:
        ``create_deep_linked_url(bot.get_me().username, "some-params")``

    Args:
        bot_username (:obj:`str`): The username to link to
        payload (:obj:`str`, optional): Parameters to encode in the created URL
        group (:obj:`bool`, optional): If `True` the user is prompted to select a group to add the
            bot to. If `False`, opens a one-on-one conversation with the bot. Defaults to `False`.

    Returns:
        :obj:`str`: An URL to start the bot with specific parameters
    """
    if bot_username is None or len(bot_username) <= 3:
        raise ValueError("You must provide a valid bot_username.")

    base_url = 'https://t.me/{}'.format(bot_username)
    if not payload:
        return base_url

    if len(payload) > 64:
        raise ValueError("The deep-linking payload must not exceed 64 characters.")

    if not re.match(r'^[A-Za-z0-9_-]+$', payload):
        raise ValueError("Only the following characters are allowed for deep-linked "
                         "URLs: A-Z, a-z, 0-9, _ and -")

    if group:
        key = 'startgroup'
    else:
        key = 'start'

    return '{0}?{1}={2}'.format(
        base_url,
        key,
        payload
    )


def enocde_conversations_to_json(conversations):
    """Helper method to encode a conversations dict (that uses tuples as keys) to a
    JSON-serializable way. Use :attr:`_decode_conversations_from_json` to decode.

    Args:
        conversations (:obj:`dict`): The conversations dict to transofrm to JSON.

    Returns:
        :obj:`str`: The JSON-serialized conversations dict
    """
    tmp = {}
    for handler, states in conversations.items():
        tmp[handler] = {}
        for key, state in states.items():
            tmp[handler][json.dumps(key)] = state
    return json.dumps(tmp)


def decode_conversations_from_json(json_string):
    """Helper method to decode a conversations dict (that uses tuples as keys) from a
    JSON-string created with :attr:`_encode_conversations_to_json`.

    Args:
        json_string (:obj:`str`): The conversations dict as JSON string.

    Returns:
        :obj:`dict`: The conversations dict after decoding
    """
    tmp = json.loads(json_string)
    conversations = {}
    for handler, states in tmp.items():
        conversations[handler] = {}
        for key, state in states.items():
            conversations[handler][tuple(json.loads(key))] = state
    return conversations


def decode_user_chat_data_from_json(data):
    """Helper method to decode chat or user data (that uses ints as keys) from a
    JSON-string.

    Args:
        data (:obj:`str`): The user/chat_data dict as JSON string.

    Returns:
        :obj:`dict`: The user/chat_data defaultdict after decoding
    """

    tmp = defaultdict(dict)
    decoded_data = json.loads(data)
    for user, data in decoded_data.items():
        user = int(user)
        tmp[user] = {}
        for key, value in data.items():
            try:
                key = int(key)
            except ValueError:
                pass
            tmp[user][key] = value
    return tmp
