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
""" This module contains helper functions """

import re


def extract_chat_and_user(update):
    """
    Helper method to get the sender's chat and user objects from an arbitrary update

    Args:
        update (:class:`telegram.Update`): The update presumably containing chat or user objects

    Returns:
        tuple: of (chat, user), with None-values if no object could not be found in the update.
    """
    user = None
    chat = None

    if update.message:
        user = update.message.from_user
        chat = update.message.chat

    elif update.edited_message:
        user = update.edited_message.from_user
        chat = update.edited_message.chat

    elif update.inline_query:
        user = update.inline_query.from_user

    elif update.chosen_inline_result:
        user = update.chosen_inline_result.from_user

    elif update.callback_query:
        user = update.callback_query.from_user
        chat = update.callback_query.message.chat if update.callback_query.message else None

    return chat, user


def extract_message_text(update):
    """
    Helper method to get the message text from an arbitrary update

    Args:
        update (:class:`telegram.Update`): The update presumably containing message text

    Returns:
        str: The extracted message text

    Raises:
        ValueError: If no message text was found in the update

    """
    if update.message:
        return update.message.text
    elif update.edited_message:
        return update.edited_message.text
    elif update.callback_query:
        return update.callback_query.message.text
    else:
        raise ValueError("Update contains no message text.")


def extract_entities(update):
    """
    Helper method to get parsed entities from an arbitrary update

    Args:
        update (:class:`telegram.Update`): The update presumably containing entities

    Returns:
        dict[:class:`telegram.MessageEntity`, ``str``]: A dictionary of entities mapped to the
            text that belongs to them, calculated based on UTF-16 codepoints.

    Raises:
        ValueError: If no entities were found in the update

    """
    if update.message:
        return update.message.parse_entities()
    elif update.edited_message:
        return update.edited_message.parse_entities()
    elif update.callback_query:
        return update.callback_query.message.parse_entities()
    else:
        raise ValueError("No message object found in update, therefore no entities available.")


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)
