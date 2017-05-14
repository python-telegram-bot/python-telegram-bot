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
"""This module contains an object that represents a Telegram MessageEntity."""

from telegram import User, TelegramObject


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example,
    hashtags, usernames, URLs, etc.

    Args:
        type (str):
        offset (int):
        length (int):
        url (Optional[str]):
        user (Optional[:class:`telegram.User`]):
    """

    def __init__(self, type, offset, length, url=None, user=None, **kwargs):
        # Required
        self.type = type
        self.offset = offset
        self.length = length
        # Optionals
        self.url = url
        self.user = user

    @staticmethod
    def de_json(data, bot):
        data = super(MessageEntity, MessageEntity).de_json(data, bot)

        data['user'] = User.de_json(data.get('user'), bot)

        return MessageEntity(**data)

    @staticmethod
    def de_list(data, bot):
        """
        Args:
            data (list):

        Returns:
            List<telegram.MessageEntity>:
        """
        if not data:
            return list()

        entities = list()
        for entity in data:
            entities.append(MessageEntity.de_json(entity, bot))

        return entities

    MENTION = 'mention'
    HASHTAG = 'hashtag'
    BOT_COMMAND = 'bot_command'
    URL = 'url'
    EMAIL = 'email'
    BOLD = 'bold'
    ITALIC = 'italic'
    CODE = 'code'
    PRE = 'pre'
    TEXT_LINK = 'text_link'
    TEXT_MENTION = 'text_mention'
    ALL_TYPES = [
        MENTION, HASHTAG, BOT_COMMAND, URL, EMAIL, BOLD, ITALIC, CODE, PRE, TEXT_LINK, TEXT_MENTION
    ]
