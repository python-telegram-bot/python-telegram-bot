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

"""
This module contains convenience utility functions that proved to be useful in productive use of the
python-telegram-bot library.

Feel free to suggest your own helper methods by filing a PR on GitHub.
"""

import json
import logging
import time
import re
from collections import OrderedDict
from telegram import ChatAction
from telegram import ParseMode, Update

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


def chat_id_from_update(update: Update):
    """
    Gets the chat_id attribute value from all types of Telegram messages

    :param update: The update to check
    :return: the value of the corresponding chat_id
    """
    chat_id = None
    try:
        chat_id = update.message.from_user.id
    except (NameError, AttributeError):
        try:
            chat_id = update.inline_query.from_user.id
        except (NameError, AttributeError):
            try:
                chat_id = update.chosen_inline_result.from_user.id
            except (NameError, AttributeError):
                try:
                    chat_id = update.callback_query.from_user.id
                except (NameError, AttributeError):
                    logger.error("No chat_id available in update.")
    return chat_id


def is_inline_message(update: Update):
    """
    Checks if a given update arose from an inline message

    :param update: The update to check
    :return: True if update contains an inline message
    """
    try:
        if update.callback_query.inline_message_id == '':
            return False
    except (NameError, AttributeError):
        return False
    # otherwise
    return True


def parse_markdown_text(update: Update):
    """
    Parses entities from an update to recreate the original markdown-formatted message text

    :param update: The update to check
    :return: The original markdown-formatted message text
    """
    entities = parse_entities_from_update(update)
    text = message_text_from_update(update)

    for e in entities:
        modified = None
        pos = e.offset
        length = e.length

        if e.type == "bold":
            text = text[:pos] + '*' + text[pos:pos + length] + '*' + text[pos + length:]
            modified = 2
        if e.type == "italic":
            text = text[:pos] + '_' + text[pos:pos + length] + '_' + text[pos + length:]
            modified = 2
        if e.type == "code":
            text = text[:pos] + '`' + text[pos:pos + length] + '`' + text[pos + length:]
            modified = 2
        if e.type == "pre":
            text = text[:pos] + '```\n' + text[pos:pos + length] + '\n```' + text[pos + length:]
            modified = 8

        # update offsets of all entities to the right
        if modified:
            for other in entities:
                if other.offset > pos:
                    other.offset += modified
    return text


def message_from_update(update: Update):
    """
    Gets the message argument from all types of Telegram messages

    :param update: The update to check for message attribute
    :return: The message attribute of update
    """
    message = None
    try:
        message = update.message
    except (NameError, AttributeError):
        try:
            message = update.callback_query.message
        except (NameError, AttributeError):
            logger.error("No message available in update.")
    return message


def parse_entities_from_update(update: Update):
    """
    Parses entities from all types of messages

    :param update: The update to check
    :return: The output of [...].message.parse_entities()
    """
    return message_from_update(update).parse_entities()


def message_text_from_update(update: Update):
    """ Get message text from all types of messages """
    return message_from_update(update).text


def message_id_from_update(update: Update):
    """
    Gets the message_id attribute from all types of Telegram messages

    :param update: The update to check
    :return: The message_id of the corresponding update
    """
    try:
        return update.callback_query.message.message_id
    except (NameError, AttributeError):
        try:
            message_id = update.callback_query.inline_message_id
            return message_id if message_id != '' else None
        except (NameError, AttributeError):
            return None


def escape_markdown(text: str):
    """
    Escapes all markdown characters used by Telegram to mark up messages

    :param text: The text to process
    :return: `text` with all markdown symbols escaped by a \ character
    """
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def callback_str_from_dict(d: dict):
    """
    Uses the `json` module to create a short as possible string from a dictionary.

    The generated string complies with Telegram's length constrains for the `callback_data`_ attribute in
    InlineKeyboardButtons.

    :param d: A native `dict`
    :return: An uglified JSON-representation of your dict
    """

    uglified = json.dumps(d, separators=(',', ':'))
    if len(uglified) > 64:
        raise ValueError("Telegram restricts callback_data to a maximum of 64 bytes.")
    return uglified


def wait(bot, update, pause_duration=1.8):
    """
    Displays a visual indicator that 'more is coming' to the user.

    Use this if you want a more interactive conversation with your users by sending a message, giving them some time to
    read it and then send the next chunk of text. Use the `pause_duration` argument to specify the waiting time;
    1.8 seconds proved to feel natural.

    Attention: This method pauses thread execution which might cause problems in callback handlers.

    :param bot: Supply bot and update of your handler function
    :param update: Supply bot and update of your handler function
    :param pause_duration: Time in seconds until the next command is executed
    """
    chat_id = chat_id_from_update(update)
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    time.sleep(pause_duration)


def order_dict_lexi(d: dict):
    """
    Helper function to order a dictionary lexicographically by its keys (from A to Z)
    :param d: The dict to order
    :return: A new `OrderedDict` sorted lexicographically
    """
    res = OrderedDict()
    for k, v in sorted(d.items()):
        if isinstance(v, dict):
            res[k] = order_dict_lexi(v)
        else:
            res[k] = v
    return res


def send_md_message(bot, chat_id, text: str, **kwargs):
    """
    Sends a Markdown-formatted message to `chat_id`

    :param bot: Your bot from a callback handler
    :param chat_id: The recipient's chat_id
    :param text: The text to send
    :param kwargs: Additional keyword arguments
    :return: The output of bot.send_message
    """
    return bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, **kwargs)