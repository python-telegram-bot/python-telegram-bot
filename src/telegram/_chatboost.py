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
"""This module contains the classes that represent Telegram ChatBoosts."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._chat import Chat
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ChatBoostAdded(TelegramObject):
    """
    This object represents a service message about a user boosting a chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`boost_count` are equal.

    .. versionadded:: 21.0

    Args:
        boost_count (:obj:`int`): Number of boosts added by the user.

    Attributes:
        boost_count (:obj:`int`): Number of boosts added by the user.

    """

    boost_count: int = tg_field(compare=True)


@tg_dataclass()
class ChatBoostSource(TelegramObject):
    """
    Base class for Telegram ChatBoostSource objects. It can be one of:

    * :class:`telegram.ChatBoostSourcePremium`
    * :class:`telegram.ChatBoostSourceGiftCode`
    * :class:`telegram.ChatBoostSourceGiveaway`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`source` is equal.

    .. versionadded:: 20.8

    Args:
        source (:obj:`str`): The source of the chat boost. Can be one of:
            :attr:`~telegram.ChatBoostSource.PREMIUM`, :attr:`~telegram.ChatBoostSource.GIFT_CODE`,
            or :attr:`~telegram.ChatBoostSource.GIVEAWAY`.

    Attributes:
        source (:obj:`str`): The source of the chat boost. Can be one of:
            :attr:`~telegram.ChatBoostSource.PREMIUM`, :attr:`~telegram.ChatBoostSource.GIFT_CODE`,
            or :attr:`~telegram.ChatBoostSource.GIVEAWAY`.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "source",
        {
            "premium": "ChatBoostSourcePremium",
            "gift_code": "ChatBoostSourceGiftCode",
            "giveaway": "ChatBoostSourceGiveaway",
        },
    )

    PREMIUM: ClassVar[str] = constants.ChatBoostSources.PREMIUM
    """:const:`telegram.constants.ChatBoostSources.PREMIUM`"""
    GIFT_CODE: ClassVar[str] = constants.ChatBoostSources.GIFT_CODE
    """:const:`telegram.constants.ChatBoostSources.GIFT_CODE`"""
    GIVEAWAY: ClassVar[str] = constants.ChatBoostSources.GIVEAWAY
    """:const:`telegram.constants.ChatBoostSources.GIVEAWAY`"""

    @staticmethod
    def _source_converter(value: str) -> str:
        return enum.get_member(constants.ChatBoostSources, value, value)

    source: str = tg_field(compare=True, default=None, converter=_source_converter)


@tg_dataclass()
class ChatBoostSourcePremium(ChatBoostSource):
    """
    The boost was obtained by subscribing to Telegram Premium or by gifting a Telegram Premium
    subscription to another user.

    .. versionadded:: 20.8

    Args:
        user (:class:`telegram.User`): User that boosted the chat.

    Attributes:
        source (:obj:`str`): The source of the chat boost. Always
            :attr:`~telegram.ChatBoostSource.PREMIUM`.
        user (:class:`telegram.User`): User that boosted the chat.
    """

    # Attribute only (init=False)
    source: str = tg_field(init=False, default=ChatBoostSource.PREMIUM)

    user: User = tg_field()


@tg_dataclass()
class ChatBoostSourceGiftCode(ChatBoostSource):
    """
    The boost was obtained by the creation of Telegram Premium gift codes to boost a chat. Each
    such code boosts the chat 4 times for the duration of the corresponding Telegram Premium
    subscription.

    .. versionadded:: 20.8

    Args:
        user (:class:`telegram.User`): User for which the gift code was created.

    Attributes:
        source (:obj:`str`): The source of the chat boost. Always
            :attr:`~telegram.ChatBoostSource.GIFT_CODE`.
        user (:class:`telegram.User`): User for which the gift code was created.
    """

    # Attribute only (init=False)
    source: str = tg_field(init=False, default=ChatBoostSource.PREMIUM)

    user: User = tg_field()


@tg_dataclass()
class ChatBoostSourceGiveaway(ChatBoostSource):
    """
    The boost was obtained by the creation of a Telegram Premium giveaway or a Telegram Star.
    This boosts the chat 4 times for the duration of the corresponding Telegram Premium
    subscription for Telegram Premium giveaways and :attr:`prize_star_count` / 500 times for
    one year for Telegram Star giveaways.

    .. versionadded:: 20.8

    Args:
        giveaway_message_id (:obj:`int`): Identifier of a message in the chat with the giveaway;
            the message could have been deleted already. May be 0 if the message isn't sent yet.
        user (:class:`telegram.User`, optional): User that won the prize in the giveaway if any;
            for Telegram Premium giveaways only.
        prize_star_count (:obj:`int`, optional): The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        is_unclaimed (:obj:`bool`, optional): :obj:`True`, if the giveaway was completed, but
            there was no user to win the prize.

    Attributes:
        source (:obj:`str`): Source of the boost. Always
            :attr:`~telegram.ChatBoostSource.GIVEAWAY`.
        giveaway_message_id (:obj:`int`): Identifier of a message in the chat with the giveaway;
            the message could have been deleted already. May be 0 if the message isn't sent yet.
        user (:class:`telegram.User`): Optional. User that won the prize in the giveaway if any.
        prize_star_count (:obj:`int`): Optional. The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        is_unclaimed (:obj:`bool`): Optional. :obj:`True`, if the giveaway was completed, but
            there was no user to win the prize.
    """

    # Attribute only (init=False)
    source: str = tg_field(init=False, default=ChatBoostSource.GIVEAWAY)

    giveaway_message_id: int = tg_field()
    user: User | None = tg_field(default=None)
    is_unclaimed: bool | None = tg_field(default=None)
    prize_star_count: int | None = tg_field(default=None)


@tg_dataclass()
class ChatBoost(TelegramObject):
    """
    This object contains information about a chat boost.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`boost_id`, :attr:`add_date`, :attr:`expiration_date`,
    and :attr:`source` are equal.

    .. versionadded:: 20.8

    Args:
        boost_id (:obj:`str`): Unique identifier of the boost.
        add_date (:obj:`datetime.datetime`): Point in time when the chat was boosted.
        expiration_date (:obj:`datetime.datetime`): Point in time when the boost
            will automatically expire, unless the booster's Telegram Premium subscription is
            prolonged.
        source (:class:`telegram.ChatBoostSource`): Source of the added boost.

    Attributes:
        boost_id (:obj:`str`): Unique identifier of the boost.
        add_date (:obj:`datetime.datetime`): Point in time when the chat was boosted.
            |datetime_localization|
        expiration_date (:obj:`datetime.datetime`): Point in time when the boost
            will automatically expire, unless the booster's Telegram Premium subscription is
            prolonged. |datetime_localization|
        source (:class:`telegram.ChatBoostSource`): Source of the added boost.
    """

    boost_id: str = tg_field(compare=True)
    add_date: dtm.datetime = tg_field(compare=True)
    expiration_date: dtm.datetime = tg_field(compare=True)
    source: ChatBoostSource = tg_field(compare=True)


@tg_dataclass()
class ChatBoostUpdated(TelegramObject):
    """This object represents a boost added to a chat or changed.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, and :attr:`boost` are equal.

    .. versionadded:: 20.8

    Args:
        chat (:class:`telegram.Chat`): Chat which was boosted.
        boost (:class:`telegram.ChatBoost`): Information about the chat boost.

    Attributes:
        chat (:class:`telegram.Chat`): Chat which was boosted.
        boost (:class:`telegram.ChatBoost`): Information about the chat boost.
    """

    chat: Chat = tg_field(compare=True)
    boost: ChatBoost = tg_field(compare=True)


@tg_dataclass()
class ChatBoostRemoved(TelegramObject):
    """
    This object represents a boost removed from a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, :attr:`boost_id`, :attr:`remove_date`, and
    :attr:`source` are equal.

    Args:
        chat (:class:`telegram.Chat`): Chat which was boosted.
        boost_id (:obj:`str`): Unique identifier of the boost.
        remove_date (:obj:`datetime.datetime`): Point in time when the boost was removed.
        source (:class:`telegram.ChatBoostSource`): Source of the removed boost.

    Attributes:
        chat (:class:`telegram.Chat`): Chat which was boosted.
        boost_id (:obj:`str`): Unique identifier of the boost.
        remove_date (:obj:`datetime.datetime`): Point in time when the boost was removed.
            |datetime_localization|
        source (:class:`telegram.ChatBoostSource`): Source of the removed boost.
    """

    chat: Chat = tg_field(compare=True)
    boost_id: str = tg_field(compare=True)
    remove_date: dtm.datetime = tg_field(compare=True)
    source: ChatBoostSource = tg_field(compare=True)


@tg_dataclass()
class UserChatBoosts(TelegramObject):
    """This object represents a list of boosts added to a chat by a user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`boosts` are equal.

    .. versionadded:: 20.8

    Args:
        boosts (Sequence[:class:`telegram.ChatBoost`]): List of boosts added to the chat by the
            user.

    Attributes:
        boosts (tuple[:class:`telegram.ChatBoost`]): List of boosts added to the chat by the user.
    """

    boosts: tuple[ChatBoost, ...] = tg_field(compare=True, converter=parse_sequence_arg)
