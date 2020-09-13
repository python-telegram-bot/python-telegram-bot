#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
from telegram.utils.types import JSONDict
from typing import Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Bot


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example, hashtags,
    usernames, URLs, etc.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`offset` and :attr`length` are equal.

    Attributes:
        type (:obj:`str`): Type of the entity.
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`): Optional. Url that will be opened after user taps on the text.
        user (:class:`telegram.User`): Optional. The mentioned user.
        language (:obj:`str`): Optional. Programming language of the entity text.

    Args:
        type (:obj:`str`): Type of the entity. Can be mention (@username), hashtag, bot_command,
            url, email, phone_number, bold (bold text), italic (italic text), strikethrough,
            code (monowidth string), pre (monowidth block), text_link (for clickable text URLs),
            text_mention (for users without usernames).
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`, optional): For :attr:`TEXT_LINK` only, url that will be opened after
            user taps on the text.
        user (:class:`telegram.User`, optional): For :attr:`TEXT_MENTION` only, the mentioned
             user.
        language (:obj:`str`, optional): For :attr:`PRE` only, the programming language of
            the entity text.

    """

    def __init__(self,
                 type: str,
                 offset: int,
                 length: int,
                 url: str = None,
                 user: User = None,
                 language: str = None,
                 **kwargs: Any):
        # Required
        self.type = type
        self.offset = offset
        self.length = length
        # Optionals
        self.url = url
        self.user = user
        self.language = language

        self._id_attrs = (self.type, self.offset, self.length)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['MessageEntity']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['user'] = User.de_json(data.get('user'), bot)

        return cls(**data)

    MENTION: str = 'mention'
    """:obj:`str`: 'mention'"""
    HASHTAG: str = 'hashtag'
    """:obj:`str`: 'hashtag'"""
    CASHTAG: str = 'cashtag'
    """:obj:`str`: 'cashtag'"""
    PHONE_NUMBER: str = 'phone_number'
    """:obj:`str`: 'phone_number'"""
    BOT_COMMAND: str = 'bot_command'
    """:obj:`str`: 'bot_command'"""
    URL: str = 'url'
    """:obj:`str`: 'url'"""
    EMAIL: str = 'email'
    """:obj:`str`: 'email'"""
    BOLD: str = 'bold'
    """:obj:`str`: 'bold'"""
    ITALIC: str = 'italic'
    """:obj:`str`: 'italic'"""
    CODE: str = 'code'
    """:obj:`str`: 'code'"""
    PRE: str = 'pre'
    """:obj:`str`: 'pre'"""
    TEXT_LINK: str = 'text_link'
    """:obj:`str`: 'text_link'"""
    TEXT_MENTION: str = 'text_mention'
    """:obj:`str`: 'text_mention'"""
    UNDERLINE: str = 'underline'
    """:obj:`str`: 'underline'"""
    STRIKETHROUGH: str = 'strikethrough'
    """:obj:`str`: 'strikethrough'"""
    ALL_TYPES: List[str] = [
        MENTION, HASHTAG, CASHTAG, PHONE_NUMBER, BOT_COMMAND, URL,
        EMAIL, BOLD, ITALIC, CODE, PRE, TEXT_LINK, TEXT_MENTION, UNDERLINE, STRIKETHROUGH
    ]
    """List[:obj:`str`]: List of all the types."""
