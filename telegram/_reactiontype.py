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
"""This module contains objects that represents a Telegram ReactionType."""
from typing import TYPE_CHECKING, Final, Optional

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ReactionType(TelegramObject):
    """Base class for Telegram ReactionType Objects.
    There exist :class:`telegram.ReactionTypeEmoji` and :class:`telegram.ReactionTypeCustomEmoji`.

    .. versionadded:: NEXT.VERSION

    Args:
        type (:obj:`str`): Type of the reaction. Can be
            :attr:`~telegram.ReactionType.EMOJI` or :attr:`~telegram.ReactionType.CUSTOM_EMOJI`.
    Attributes:
        type (:obj:`str`): Type of the reaction. Can be
            :attr:`~telegram.ReactionType.EMOJI` or :attr:`~telegram.ReactionType.CUSTOM_EMOJI`.

    """

    __slots__ = ("type",)

    EMOJI: Final[str] = constants.ReactionType.EMOJI
    """:const:`telegram.constants.ReactionType.EMOJI`"""
    CUSTOM_EMOJI: Final[str] = constants.ReactionType.CUSTOM_EMOJI
    """:const:`telegram.constants.ReactionType.CUSTOM_EMOJI`"""

    def __init__(
        self,
        # TODO we can use Literals here as well tbh...
        type: str,  # pylint: disable=redefined-builtin
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required by all subclasses
        self.type: str = type

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ReactionType"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        if cls is ReactionType and data.get("type") in [cls.EMOJI, cls.CUSTOM_EMOJI]:
            reaction_type = data.pop("type")
            if reaction_type == cls.EMOJI:
                return ReactionTypeEmoji.de_json(data=data, bot=bot)
            return ReactionTypeCustomEmoji.de_json(data=data, bot=bot)

        return super().de_json(data=data, bot=bot)


class ReactionTypeEmoji(ReactionType):
    """
    Represents a reaction with a normal emoji.

    .. versionadded:: NEXT.VERSION


    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if the :attr:`emoji` is equal.

    Args:
        emoji (:obj:`str`): Reaction emoji. It can be one of
        :const:`telegram.constants.ReactionEmojis`.

    Attributes:
        type (:obj:`str`): Type of the reaction,
            always :tg-const:`telegram.ReactionType.EMOJI`.
        emoji (:obj:`str`): Reaction emoji. It can be one of
        :const:`telegram.constants.ReactionEmojis`.
    """

    __slots__ = ("emoji",)

    def __init__(
        self,
        emoji: str,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(type=ReactionType.EMOJI, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.emoji: str = emoji
            self._id_attrs = (self.emoji,)


class ReactionTypeCustomEmoji(ReactionType):
    """
    Represents a reaction with a custom emoji.

    .. versionadded:: NEXT.VERSION

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if the :attr:`custom_emoji_id` is equal.

    Args:
        custom_emoji_id (:obj:`str`): Custom emoji identifier.

    Attributes:
        type (:obj:`str`): Type of the reaction,
            always :tg-const:`telegram.ReactionType.CUSTOM_EMOJI`.
        custom_emoji_id (:obj:`str`): Custom emoji identifier.
    """

    __slots__ = ("custom_emoji_id",)

    def __init__(
        self,
        custom_emoji_id: str,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(type=ReactionType.CUSTOM_EMOJI, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.custom_emoji_id: str = custom_emoji_id
            self._id_attrs = (self.custom_emoji_id,)
