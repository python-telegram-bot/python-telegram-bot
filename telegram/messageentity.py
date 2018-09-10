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
"""This module contains an object that represents a Telegram MessageEntity."""

from telegram import User, TelegramObject


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example, hashtags,
    usernames, URLs, etc.

    Attributes:
        type (:obj:`str`): Type of the entity.
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`): Optional. Url that will be opened after user taps on the text.
        user (:class:`telegram.User`): Optional. The mentioned user.

    Args:
        type (:obj:`str`): Type of the entity. Can be mention (@username), hashtag, bot_command,
            url, email, bold (bold text), italic (italic text), code (monowidth string), pre
            (monowidth block), text_link (for clickable text URLs), text_mention (for users
            without usernames).
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`, optional): For "text_link" only, url that will be opened after usertaps on
            the text.
        user (:class:`telegram.User`, optional): For "text_mention" only, the mentioned user.

    """

    def __init__(self, type, offset, length, url=None, user=None, **kwargs):
        # Required
        self.type = type
        self.offset = offset
        self.length = length
        # Optionals
        self.url = url
        self.user = user

    @classmethod
    def de_json(cls, data, bot):
        data = super(MessageEntity, cls).de_json(data, bot)

        if not data:
            return None

        data['user'] = User.de_json(data.get('user'), bot)

        return cls(**data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return list()

        entities = list()
        for entity in data:
            entities.append(cls.de_json(entity, bot))

        return entities

    MENTION = 'mention'
    """:obj:`str`: 'mention'"""
    HASHTAG = 'hashtag'
    """:obj:`str`: 'hashtag'"""
    CASHTAG = 'cashtag'
    """:obj:`str`: 'cashtag'"""
    PHONE_NUMBER = 'phone_number'
    """:obj:`str`: 'phone_number'"""
    BOT_COMMAND = 'bot_command'
    """:obj:`str`: 'bot_command'"""
    URL = 'url'
    """:obj:`str`: 'url'"""
    EMAIL = 'email'
    """:obj:`str`: 'email'"""
    BOLD = 'bold'
    """:obj:`str`: 'bold'"""
    ITALIC = 'italic'
    """:obj:`str`: 'italic'"""
    CODE = 'code'
    """:obj:`str`: 'code'"""
    PRE = 'pre'
    """:obj:`str`: 'pre'"""
    TEXT_LINK = 'text_link'
    """:obj:`str`: 'text_link'"""
    TEXT_MENTION = 'text_mention'
    """:obj:`str`: 'text_mention'"""
    ALL_TYPES = [
        MENTION, HASHTAG, CASHTAG, PHONE_NUMBER, BOT_COMMAND, URL,
        EMAIL, BOLD, ITALIC, CODE, PRE, TEXT_LINK, TEXT_MENTION
    ]
    """List[:obj:`str`]: List of all the types."""
