#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from typing import TYPE_CHECKING, Any, List, Optional, ClassVar

from telegram import TelegramObject, User, constants
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example, hashtags,
    usernames, URLs, etc.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`offset` and :attr:`length` are equal.

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

    Attributes:
        type (:obj:`str`): Type of the entity.
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`): Optional. Url that will be opened after user taps on the text.
        user (:class:`telegram.User`): Optional. The mentioned user.
        language (:obj:`str`): Optional. Programming language of the entity text.

    """

    def __init__(
        self,
        type: str,  # pylint: disable=W0622
        offset: int,
        length: int,
        url: str = None,
        user: User = None,
        language: str = None,
        **_kwargs: Any,
    ):
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

    MENTION: ClassVar[str] = constants.MESSAGEENTITY_MENTION
    """:const:`telegram.constants.MESSAGEENTITY_MENTION`"""
    HASHTAG: ClassVar[str] = constants.MESSAGEENTITY_HASHTAG
    """:const:`telegram.constants.MESSAGEENTITY_HASHTAG`"""
    CASHTAG: ClassVar[str] = constants.MESSAGEENTITY_CASHTAG
    """:const:`telegram.constants.MESSAGEENTITY_CASHTAG`"""
    PHONE_NUMBER: ClassVar[str] = constants.MESSAGEENTITY_PHONE_NUMBER
    """:const:`telegram.constants.MESSAGEENTITY_PHONE_NUMBER`"""
    BOT_COMMAND: ClassVar[str] = constants.MESSAGEENTITY_BOT_COMMAND
    """:const:`telegram.constants.MESSAGEENTITY_BOT_COMMAND`"""
    URL: ClassVar[str] = constants.MESSAGEENTITY_URL
    """:const:`telegram.constants.MESSAGEENTITY_URL`"""
    EMAIL: ClassVar[str] = constants.MESSAGEENTITY_EMAIL
    """:const:`telegram.constants.MESSAGEENTITY_EMAIL`"""
    BOLD: ClassVar[str] = constants.MESSAGEENTITY_BOLD
    """:const:`telegram.constants.MESSAGEENTITY_BOLD`"""
    ITALIC: ClassVar[str] = constants.MESSAGEENTITY_ITALIC
    """:const:`telegram.constants.MESSAGEENTITY_ITALIC`"""
    CODE: ClassVar[str] = constants.MESSAGEENTITY_CODE
    """:const:`telegram.constants.MESSAGEENTITY_CODE`"""
    PRE: ClassVar[str] = constants.MESSAGEENTITY_PRE
    """:const:`telegram.constants.MESSAGEENTITY_PRE`"""
    TEXT_LINK: ClassVar[str] = constants.MESSAGEENTITY_TEXT_LINK
    """:const:`telegram.constants.MESSAGEENTITY_TEXT_LINK`"""
    TEXT_MENTION: ClassVar[str] = constants.MESSAGEENTITY_TEXT_MENTION
    """:const:`telegram.constants.MESSAGEENTITY_TEXT_MENTION`"""
    UNDERLINE: ClassVar[str] = constants.MESSAGEENTITY_UNDERLINE
    """:const:`telegram.constants.MESSAGEENTITY_UNDERLINE`"""
    STRIKETHROUGH: ClassVar[str] = constants.MESSAGEENTITY_STRIKETHROUGH
    """:const:`telegram.constants.MESSAGEENTITY_STRIKETHROUGH`"""
    ALL_TYPES: ClassVar[List[str]] = constants.MESSAGEENTITY_ALL_TYPES
    """:const:`telegram.constants.MESSAGEENTITY_ALL_TYPES`\n
    List of all the types"""
