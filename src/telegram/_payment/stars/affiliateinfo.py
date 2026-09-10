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
# along with this program. If not, see [http://www.gnu.org/licenses/].
"""This module contains the classes for Telegram Stars affiliates."""

from typing import TYPE_CHECKING

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field

if TYPE_CHECKING:
    from telegram._chat import Chat
    from telegram._user import User


@tg_dataclass()
class AffiliateInfo(TelegramObject):
    """Contains information about the affiliate that received a commission via this transaction.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`affiliate_user`, :attr:`affiliate_chat`,
    :attr:`commission_per_mille`, :attr:`amount`, and :attr:`nanostar_amount` are equal.

    .. versionadded:: 21.9

    Args:
        affiliate_user (:class:`telegram.User`, optional): The bot or the user that received an
            affiliate commission if it was received by a bot or a user
        affiliate_chat (:class:`telegram.Chat`, optional): The chat that received an affiliate
            commission if it was received by a chat
        commission_per_mille (:obj:`int`): The number of Telegram Stars received by the affiliate
            for each 1000 Telegram Stars received by the bot from referred users
        amount (:obj:`int`): Integer amount of Telegram Stars received by the affiliate from the
            transaction, rounded to 0; can be negative for refunds
        nanostar_amount (:obj:`int`, optional): The number of
            :tg-const:`~telegram.constants.Nanostar.VALUE` shares of Telegram
            Stars received by the affiliate; from
            :tg-const:`~telegram.constants.NanostarLimit.MIN_AMOUNT` to
            :tg-const:`~telegram.constants.NanostarLimit.MAX_AMOUNT`;
            can be negative for refunds

    Attributes:
        affiliate_user (:class:`telegram.User`): Optional. The bot or the user that received an
            affiliate commission if it was received by a bot or a user
        affiliate_chat (:class:`telegram.Chat`): Optional. The chat that received an affiliate
            commission if it was received by a chat
        commission_per_mille (:obj:`int`): The number of Telegram Stars received by the affiliate
            for each 1000 Telegram Stars received by the bot from referred users
        amount (:obj:`int`): Integer amount of Telegram Stars received by the affiliate from the
            transaction, rounded to 0; can be negative for refunds
        nanostar_amount (:obj:`int`): Optional. The number of
            :tg-const:`~telegram.constants.Nanostar.VALUE` shares of Telegram
            Stars received by the affiliate; from
            :tg-const:`~telegram.constants.NanostarLimit.MIN_AMOUNT` to
            :tg-const:`~telegram.constants.NanostarLimit.MAX_AMOUNT`;
            can be negative for refunds
    """

    commission_per_mille: int = tg_field(compare=True)
    amount: int = tg_field(compare=True)
    affiliate_user: "User | None" = tg_field(compare=True, default=None)
    affiliate_chat: "Chat | None" = tg_field(compare=True, default=None)
    nanostar_amount: int | None = tg_field(compare=True, default=None)
