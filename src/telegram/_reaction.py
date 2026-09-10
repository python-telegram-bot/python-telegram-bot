#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from typing import ClassVar, Literal

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ReactionType(TelegramObject):
    """Base class for Telegram ReactionType Objects.
    There exist :class:`telegram.ReactionTypeEmoji`, :class:`telegram.ReactionTypeCustomEmoji`
    and :class:`telegram.ReactionTypePaid`.

    .. versionadded:: 20.8
    .. versionchanged:: 21.5

        Added paid reaction.

    Args:
        type (:obj:`str`): Type of the reaction. Can be
            :attr:`~telegram.ReactionType.EMOJI`, :attr:`~telegram.ReactionType.CUSTOM_EMOJI` or
            :attr:`~telegram.ReactionType.PAID`.
    Attributes:
        type (:obj:`str`): Type of the reaction. Can be
            :attr:`~telegram.ReactionType.EMOJI`, :attr:`~telegram.ReactionType.CUSTOM_EMOJI` or
            :attr:`~telegram.ReactionType.PAID`.

    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "emoji": "ReactionTypeEmoji",
            "custom_emoji": "ReactionTypeCustomEmoji",
            "paid": "ReactionTypePaid",
        },
    )

    EMOJI: ClassVar[constants.ReactionType] = constants.ReactionType.EMOJI
    """:const:`telegram.constants.ReactionType.EMOJI`"""
    CUSTOM_EMOJI: ClassVar[constants.ReactionType] = constants.ReactionType.CUSTOM_EMOJI
    """:const:`telegram.constants.ReactionType.CUSTOM_EMOJI`"""
    PAID: ClassVar[constants.ReactionType] = constants.ReactionType.PAID
    """:const:`telegram.constants.ReactionType.PAID`

    .. versionadded:: 21.5
    """

    @staticmethod
    def _type_converter(
        value: Literal["emoji", "custom_emoji", "paid"] | constants.ReactionType,
    ) -> str:
        return enum.get_member(constants.MessageOriginType, value, value)

    # Required by all subclasses
    type: str = tg_field(converter=_type_converter)


@tg_dataclass()
class ReactionTypeEmoji(ReactionType):
    """
    Represents a reaction with a normal emoji.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if the :attr:`emoji` is equal.

    .. versionadded:: 20.8

    Args:
        emoji (:obj:`str`): Reaction emoji. It can be one of
            :const:`telegram.constants.ReactionEmoji`.

    Attributes:
        type (:obj:`str`): Type of the reaction,
            always :tg-const:`telegram.ReactionType.EMOJI`.
        emoji (:obj:`str`): Reaction emoji. It can be one of
        :const:`telegram.constants.ReactionEmoji`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=ReactionType.EMOJI)
    # Required
    emoji: str = tg_field(compare=True)


@tg_dataclass()
class ReactionTypeCustomEmoji(ReactionType):
    """
    Represents a reaction with a custom emoji.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if the :attr:`custom_emoji_id` is equal.

    .. versionadded:: 20.8

    Args:
        custom_emoji_id (:obj:`str`): Custom emoji identifier.

    Attributes:
        type (:obj:`str`): Type of the reaction,
            always :tg-const:`telegram.ReactionType.CUSTOM_EMOJI`.
        custom_emoji_id (:obj:`str`): Custom emoji identifier.

    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=ReactionType.CUSTOM_EMOJI)
    # Required
    custom_emoji_id: str = tg_field(compare=True)


@tg_dataclass()
class ReactionTypePaid(ReactionType):
    """
    The reaction is paid.

    .. versionadded:: 21.5

    Attributes:
        type (:obj:`str`): Type of the reaction,
            always :tg-const:`telegram.ReactionType.PAID`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=ReactionType.PAID)


@tg_dataclass()
class ReactionCount(TelegramObject):
    """This class represents a reaction added to a message along with the number of times it was
    added.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if the :attr:`type` and :attr:`total_count` is equal.

    .. versionadded:: 20.8

    Args:
        type (:class:`telegram.ReactionType`): Type of the reaction.
        total_count (:obj:`int`): Number of times the reaction was added.

    Attributes:
        type (:class:`telegram.ReactionType`): Type of the reaction.
        total_count (:obj:`int`): Number of times the reaction was added.
    """

    type: ReactionType = tg_field(compare=True)
    total_count: int = tg_field(compare=True)
