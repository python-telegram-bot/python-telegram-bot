#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

from typing import TYPE_CHECKING, ClassVar, List, Optional

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example, hashtags,
    usernames, URLs, etc.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`offset` and :attr:`length` are equal.

    Args:
        type (:obj:`str`): Type of the entity. Can be :attr:`MENTION` (@username),
            :attr:`HASHTAG`, :attr:`BOT_COMMAND`,
            :attr:`URL`, :attr:`EMAIL`, :attr:`PHONE_NUMBER`, :attr:`BOLD` (bold text),
            :attr:`ITALIC` (italic text), :attr:`STRIKETHROUGH`, :attr:`SPOILER` (spoiler message),
            :attr:`CODE` (monowidth string), :attr:`PRE` (monowidth block), :attr:`TEXT_LINK` (for
            clickable text URLs), :attr:`TEXT_MENTION` (for users without usernames),
            :attr:`CUSTOM_EMOJI` (for inline custom emoji stickers).

            .. versionadded:: 20.0
                Added inline custom emoji
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`, optional): For :attr:`TEXT_LINK` only, url that will be opened after
            user taps on the text.
        user (:class:`telegram.User`, optional): For :attr:`TEXT_MENTION` only, the mentioned
             user.
        language (:obj:`str`, optional): For :attr:`PRE` only, the programming language of
            the entity text.
        custom_emoji_id (:obj:`str`, optional): For :attr:`CUSTOM_EMOJI` only, unique identifier
            of the custom emoji. Use :meth:`telegram.Bot.get_custom_emoji_stickers` to get full
            information about the sticker.

            .. versionadded:: 20.0
    Attributes:
        type (:obj:`str`): Type of the entity. Can be :attr:`MENTION` (@username),
            :attr:`HASHTAG`, :attr:`BOT_COMMAND`,
            :attr:`URL`, :attr:`EMAIL`, :attr:`PHONE_NUMBER`, :attr:`BOLD` (bold text),
            :attr:`ITALIC` (italic text), :attr:`STRIKETHROUGH`, :attr:`SPOILER` (spoiler message),
            :attr:`CODE` (monowidth string), :attr:`PRE` (monowidth block), :attr:`TEXT_LINK` (for
            clickable text URLs), :attr:`TEXT_MENTION` (for users without usernames),
            :attr:`CUSTOM_EMOJI` (for inline custom emoji stickers).

            .. versionadded:: 20.0
                Added inline custom emoji
        offset (:obj:`int`): Offset in UTF-16 code units to the start of the entity.
        length (:obj:`int`): Length of the entity in UTF-16 code units.
        url (:obj:`str`): Optional. For :attr:`TEXT_LINK` only, url that will be opened after
            user taps on the text.
        user (:class:`telegram.User`): Optional. For :attr:`TEXT_MENTION` only, the mentioned
             user.
        language (:obj:`str`): Optional. For :attr:`PRE` only, the programming language of
            the entity text.
        custom_emoji_id (:obj:`str`): Optional. For :attr:`CUSTOM_EMOJI` only, unique identifier
            of the custom emoji. Use :meth:`telegram.Bot.get_custom_emoji_stickers` to get full
            information about the sticker.

            .. versionadded:: 20.0

    """

    __slots__ = ("length", "url", "user", "type", "language", "offset", "custom_emoji_id")

    def __init__(
        self,
        type: str,  # pylint: disable=redefined-builtin
        offset: int,
        length: int,
        url: Optional[str] = None,
        user: Optional[User] = None,
        language: Optional[str] = None,
        custom_emoji_id: Optional[str] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.type: str = enum.get_member(constants.MessageEntityType, type, type)
        self.offset: int = offset
        self.length: int = length
        # Optionals
        self.url: Optional[str] = url
        self.user: Optional[User] = user
        self.language: Optional[str] = language
        self.custom_emoji_id: Optional[str] = custom_emoji_id

        self._id_attrs = (self.type, self.offset, self.length)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["MessageEntity"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.get("user"), bot)

        return super().de_json(data=data, bot=bot)

    MENTION: ClassVar[str] = constants.MessageEntityType.MENTION
    """:const:`telegram.constants.MessageEntityType.MENTION`"""
    HASHTAG: ClassVar[str] = constants.MessageEntityType.HASHTAG
    """:const:`telegram.constants.MessageEntityType.HASHTAG`"""
    CASHTAG: ClassVar[str] = constants.MessageEntityType.CASHTAG
    """:const:`telegram.constants.MessageEntityType.CASHTAG`"""
    PHONE_NUMBER: ClassVar[str] = constants.MessageEntityType.PHONE_NUMBER
    """:const:`telegram.constants.MessageEntityType.PHONE_NUMBER`"""
    BOT_COMMAND: ClassVar[str] = constants.MessageEntityType.BOT_COMMAND
    """:const:`telegram.constants.MessageEntityType.BOT_COMMAND`"""
    URL: ClassVar[str] = constants.MessageEntityType.URL
    """:const:`telegram.constants.MessageEntityType.URL`"""
    EMAIL: ClassVar[str] = constants.MessageEntityType.EMAIL
    """:const:`telegram.constants.MessageEntityType.EMAIL`"""
    BOLD: ClassVar[str] = constants.MessageEntityType.BOLD
    """:const:`telegram.constants.MessageEntityType.BOLD`"""
    ITALIC: ClassVar[str] = constants.MessageEntityType.ITALIC
    """:const:`telegram.constants.MessageEntityType.ITALIC`"""
    CODE: ClassVar[str] = constants.MessageEntityType.CODE
    """:const:`telegram.constants.MessageEntityType.CODE`"""
    PRE: ClassVar[str] = constants.MessageEntityType.PRE
    """:const:`telegram.constants.MessageEntityType.PRE`"""
    TEXT_LINK: ClassVar[str] = constants.MessageEntityType.TEXT_LINK
    """:const:`telegram.constants.MessageEntityType.TEXT_LINK`"""
    TEXT_MENTION: ClassVar[str] = constants.MessageEntityType.TEXT_MENTION
    """:const:`telegram.constants.MessageEntityType.TEXT_MENTION`"""
    UNDERLINE: ClassVar[str] = constants.MessageEntityType.UNDERLINE
    """:const:`telegram.constants.MessageEntityType.UNDERLINE`"""
    STRIKETHROUGH: ClassVar[str] = constants.MessageEntityType.STRIKETHROUGH
    """:const:`telegram.constants.MessageEntityType.STRIKETHROUGH`"""
    SPOILER: ClassVar[str] = constants.MessageEntityType.SPOILER
    """:const:`telegram.constants.MessageEntityType.SPOILER`

    .. versionadded:: 13.10
    """
    CUSTOM_EMOJI: ClassVar[str] = constants.MessageEntityType.CUSTOM_EMOJI
    """:const:`telegram.constants.MessageEntityType.CUSTOM_EMOJI`

    .. versionadded:: 20.0
    """
    ALL_TYPES: ClassVar[List[str]] = list(constants.MessageEntityType)
    """List[:obj:`str`]: A list of all available message entity types."""
