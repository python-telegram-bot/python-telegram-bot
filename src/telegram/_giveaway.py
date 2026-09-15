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
"""This module contains an objects that are related to Telegram giveaways."""

import datetime as dtm
from typing import TYPE_CHECKING

from telegram._chat import Chat
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field

if TYPE_CHECKING:
    from telegram import Message


@tg_dataclass()
class Giveaway(TelegramObject):
    """This object represents a message about a scheduled giveaway.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chats`, :attr:`winners_selection_date` and
    :attr:`winner_count` are equal.

    .. versionadded:: 20.8

    Args:
        chats (tuple[:class:`telegram.Chat`]): The list of chats which the user must join to
            participate in the giveaway.
        winners_selection_date (:class:`datetime.datetime`): The date when the giveaway winner will
            be selected. |datetime_localization|
        winner_count (:obj:`int`): The number of users which are supposed to be selected as winners
            of the giveaway.
        only_new_members (:obj:`True`, optional): If :obj:`True`, only users who join the chats
            after the giveaway started should be eligible to win.
        has_public_winners (:obj:`True`, optional): :obj:`True`, if the list of giveaway winners
            will be visible to everyone
        prize_description (:obj:`str`, optional): Description of additional giveaway prize
        country_codes (Sequence[:obj:`str`]): A list of two-letter ISO 3166-1 alpha-2
            country codes indicating the countries from which eligible users for the giveaway must
            come. If empty, then all users can participate in the giveaway. Users with a phone
            number that was bought on Fragment can always participate in giveaways.
        prize_star_count (:obj:`int`, optional): The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        premium_subscription_month_count (:obj:`int`, optional): The number of months the Telegram
            Premium subscription won from the giveaway will be active for; for Telegram Premium
            giveaways only.

    Attributes:
        chats (Sequence[:class:`telegram.Chat`]): The list of chats which the user must join to
            participate in the giveaway.
        winners_selection_date (:class:`datetime.datetime`): The date when the giveaway winner will
            be selected. |datetime_localization|
        winner_count (:obj:`int`): The number of users which are supposed to be selected as winners
            of the giveaway.
        only_new_members (:obj:`True`): Optional. If :obj:`True`, only users who join the chats
            after the giveaway started should be eligible to win.
        has_public_winners (:obj:`True`): Optional. :obj:`True`, if the list of giveaway winners
            will be visible to everyone
        prize_description (:obj:`str`): Optional. Description of additional giveaway prize
        country_codes (tuple[:obj:`str`]): Optional. A tuple of two-letter ISO 3166-1 alpha-2
            country codes indicating the countries from which eligible users for the giveaway must
            come. If empty, then all users can participate in the giveaway. Users with a phone
            number that was bought on Fragment can always participate in giveaways.
        prize_star_count (:obj:`int`): Optional. The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        premium_subscription_month_count (:obj:`int`): Optional. The number of months the Telegram
            Premium subscription won from the giveaway will be active for; for Telegram Premium
            giveaways only.
    """

    chats: tuple[Chat, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    winners_selection_date: dtm.datetime = tg_field(compare=True)
    winner_count: int = tg_field(compare=True)
    only_new_members: bool | None = tg_field(default=None)
    has_public_winners: bool | None = tg_field(default=None)
    prize_description: str | None = tg_field(default=None)
    country_codes: tuple[str, ...] = tg_field(default=None, converter=parse_sequence_arg)
    premium_subscription_month_count: int | None = tg_field(default=None)
    prize_star_count: int | None = tg_field(default=None)


@tg_dataclass()
class GiveawayCreated(TelegramObject):
    """This object represents a service message about the creation of a scheduled giveaway.

    Args:
        prize_star_count (:obj:`int`, optional): The number of Telegram Stars to be
            split between giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6

    Attributes:
        prize_star_count (:obj:`int`): Optional. The number of Telegram Stars to be
            split between giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6

    """

    prize_star_count: int | None = tg_field(default=None)


@tg_dataclass()
class GiveawayWinners(TelegramObject):
    """This object represents a message about the completion of a giveaway with public winners.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, :attr:`giveaway_message_id`,
    :attr:`winners_selection_date`, :attr:`winner_count` and :attr:`winners` are equal.

    .. versionadded:: 20.8

    Args:
        chat (:class:`telegram.Chat`): The chat that created the giveaway
        giveaway_message_id (:obj:`int`): Identifier of the message with the giveaway in the chat
        winners_selection_date (:class:`datetime.datetime`): Point in time when winners of the
            giveaway were selected. |datetime_localization|
        winner_count (:obj:`int`): Total number of winners in the giveaway
        winners	(Sequence[:class:`telegram.User`]): List of up to
            :tg-const:`telegram.constants.GiveawayLimit.MAX_WINNERS` winners of the giveaway
        prize_star_count (:obj:`int`, optional): The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        additional_chat_count (:obj:`int`, optional): The number of other chats the user had to
            join in order to be eligible for the giveaway
        premium_subscription_month_count (:obj:`int`, optional): The number of months the Telegram
            Premium subscription won from the giveaway will be active for
        unclaimed_prize_count (:obj:`int`, optional): Number of undistributed prizes
        only_new_members (:obj:`True`, optional): :obj:`True`, if only users who had joined the
            chats after the giveaway started were eligible to win
        was_refunded (:obj:`True`, optional): :obj:`True`, if the giveaway was canceled because the
            payment for it was refunded
        prize_description (:obj:`str`, optional): Description of additional giveaway prize

    Attributes:
        chat (:class:`telegram.Chat`): The chat that created the giveaway
        giveaway_message_id (:obj:`int`): Identifier of the message with the giveaway in the chat
        winners_selection_date (:class:`datetime.datetime`): Point in time when winners of the
            giveaway were selected. |datetime_localization|
        winner_count (:obj:`int`): Total number of winners in the giveaway
        winners	(tuple[:class:`telegram.User`]): tuple of up to
            :tg-const:`telegram.constants.GiveawayLimit.MAX_WINNERS` winners of the giveaway
        additional_chat_count (:obj:`int`): Optional. The number of other chats the user had to
            join in order to be eligible for the giveaway
        prize_star_count (:obj:`int`): Optional. The number of Telegram Stars to be split between
            giveaway winners; for Telegram Star giveaways only.

            .. versionadded:: 21.6
        premium_subscription_month_count (:obj:`int`): Optional. The number of months the Telegram
            Premium subscription won from the giveaway will be active for
        unclaimed_prize_count (:obj:`int`): Optional. Number of undistributed prizes
        only_new_members (:obj:`True`): Optional. :obj:`True`, if only users who had joined the
            chats after the giveaway started were eligible to win
        was_refunded (:obj:`True`): Optional. :obj:`True`, if the giveaway was canceled because the
            payment for it was refunded
        prize_description (:obj:`str`): Optional. Description of additional giveaway prize
    """

    chat: Chat = tg_field(compare=True)
    giveaway_message_id: int = tg_field(compare=True)
    winners_selection_date: dtm.datetime = tg_field(compare=True)
    winner_count: int = tg_field(compare=True)
    winners: tuple[User, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    additional_chat_count: int | None = tg_field(default=None)
    premium_subscription_month_count: int | None = tg_field(default=None)
    unclaimed_prize_count: int | None = tg_field(default=None)
    only_new_members: bool | None = tg_field(default=None)
    was_refunded: bool | None = tg_field(default=None)
    prize_description: str | None = tg_field(default=None)
    prize_star_count: int | None = tg_field(default=None)


@tg_dataclass()
class GiveawayCompleted(TelegramObject):
    """This object represents a service message about the completion of a giveaway without public
    winners.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`winner_count` and :attr:`unclaimed_prize_count` are equal.

    .. versionadded:: 20.8


    Args:
        winner_count (:obj:`int`): Number of winners in the giveaway
        unclaimed_prize_count (:obj:`int`, optional): Number of undistributed prizes
        giveaway_message (:class:`telegram.Message`, optional): Message with the giveaway that was
            completed, if it wasn't deleted
        is_star_giveaway (:obj:`bool`, optional): :obj:`True`, if the giveaway is a Telegram Star
            giveaway. Otherwise, currently, the giveaway is a Telegram Premium giveaway.

            .. versionadded:: 21.6
    Attributes:
        winner_count (:obj:`int`): Number of winners in the giveaway
        unclaimed_prize_count (:obj:`int`): Optional. Number of undistributed prizes
        giveaway_message (:class:`telegram.Message`): Optional. Message with the giveaway that was
            completed, if it wasn't deleted
        is_star_giveaway (:obj:`bool`): Optional. :obj:`True`, if the giveaway is a Telegram Star
            giveaway. Otherwise, currently, the giveaway is a Telegram Premium giveaway.

            .. versionadded:: 21.6
    """

    winner_count: int = tg_field(compare=True)
    unclaimed_prize_count: int | None = tg_field(compare=True, default=None)
    giveaway_message: "Message | None" = tg_field(default=None)
    is_star_giveaway: bool | None = tg_field(default=None)
