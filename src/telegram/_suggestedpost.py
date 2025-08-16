#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains objects related to Telegram suggested posts."""

import datetime as dtm
from typing import TYPE_CHECKING, Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import de_json_optional
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class SuggestedPostPrice(TelegramObject):
    """
    Desribes price of a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`currency` and :attr:`amount` are equal.

    Args:
        currency (:obj:`str`):
            Currency in which the post will be paid. Currently, must be one of “XTR” for Telegram
            Stars or “TON” for toncoins.
        amount (:obj:`int`):
            The amount of the currency that will be paid for the post in the smallest units of the
            currency, i.e. Telegram Stars or nanotoncoins. Currently, price in Telegram Stars must
            be between 5 and 100000, and price in nanotoncoins must be between
            10000000 and 10000000000000.

    Attributes:
        currency (:obj:`str`):
            Currency in which the post will be paid. Currently, must be one of “XTR” for Telegram
            Stars or “TON” for toncoins.
        amount (:obj:`int`):
            The amount of the currency that will be paid for the post in the smallest units of the
            currency, i.e. Telegram Stars or nanotoncoins. Currently, price in Telegram Stars must
            be between 5 and 100000, and price in nanotoncoins must be between
            10000000 and 10000000000000.

    """

    __slots__ = ("amount", "currency")

    def __init__(
        self,
        currency: str,
        amount: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.currency: str = currency
        self.amount: Optional[dtm.datetime] = amount

        self._id_attrs = (self.currency, self.amount)

        self._freeze()


class SuggestedPostParameters(TelegramObject):
    """
    Contains parameters of a post that is being suggested by the bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`price` and :attr:`send_date` are equal.

    Args:
        price (:class:`telegram.SuggestedPostPrice`, optional):
            Proposed price for the post. If the field is omitted, then the post is unpaid..
        send_date (:class:`datetime.datetime`, optional):
            Proposed send date of the post. If specified, then the date
            must be between 300 second and 2678400 seconds (30 days) in the future. If the field is
            omitted, then the post can be published at any time within 30 days at the sole
            discretion of the user who approves it.

            |datetime_localization|

    Attributes:
        price (:class:`telegram.SuggestedPostPrice`):
            Optional. Proposed price for the post. If the field is omitted, then the post
            is unpaid.
        send_date (:obj:`d`):
            Optional. Proposed send date of the post. If specified, then the date
            must be between 300 second and 2678400 seconds (30 days) in the future. If the field is
            omitted, then the post can be published at any time within 30 days at the sole
            discretion of the user who approves it.

            |datetime_localization|

    """

    __slots__ = ("price", "send_date")

    def __init__(
        self,
        price: Optional[SuggestedPostPrice],
        send_date: Optional[dtm.datetime] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.price: Optional[SuggestedPostPrice] = price
        self.send_date: Optional[dtm.datetime] = send_date

        self._id_attrs = (self.price, self.send_date)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: JSONDict, bot: Optional["Bot"] = None
    ) -> "SuggestedPostParameters":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["price"] = de_json_optional(data.get("price"), SuggestedPostPrice, bot)

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["send_date"] = from_timestamp(data.get("send_date"), tzinfo=loc_tzinfo)

        return super().de_json(data=data, bot=bot)
