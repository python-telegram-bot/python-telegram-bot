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
"""This module contains objects related to Telegram suggested posts."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._message import Message
from telegram._payment.stars.staramount import StarAmount
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class SuggestedPostPrice(TelegramObject):
    """
    Desribes the price of a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`currency` and :attr:`amount` are equal.

    .. versionadded:: 22.4

    Args:
        currency (:obj:`str`):
            Currency in which the post will be paid. Currently, must be one of ``“XTR”`` for
            Telegram Stars or ``“TON”`` for toncoins.
        amount (:obj:`int`):
            The amount of the currency that will be paid for the post in the smallest units of the
            currency, i.e. Telegram Stars or nanotoncoins. Currently, price in Telegram Stars must
            be between :tg-const:`telegram.constants.SuggestedPost.MIN_PRICE_STARS`
            and :tg-const:`telegram.constants.SuggestedPost.MAX_PRICE_STARS`, and price in
            nanotoncoins must be between
            :tg-const:`telegram.constants.SuggestedPost.MIN_PRICE_NANOTONCOINS`
            and :tg-const:`telegram.constants.SuggestedPost.MAX_PRICE_NANOTONCOINS`.

    Attributes:
        currency (:obj:`str`):
            Currency in which the post will be paid. Currently, must be one of ``“XTR”`` for
            Telegram Stars or ``“TON”`` for toncoins.
        amount (:obj:`int`):
            The amount of the currency that will be paid for the post in the smallest units of the
            currency, i.e. Telegram Stars or nanotoncoins. Currently, price in Telegram Stars must
            be between :tg-const:`telegram.constants.SuggestedPost.MIN_PRICE_STARS`
            and :tg-const:`telegram.constants.SuggestedPost.MAX_PRICE_STARS`, and price in
            nanotoncoins must be between
            :tg-const:`telegram.constants.SuggestedPost.MIN_PRICE_NANOTONCOINS`
            and :tg-const:`telegram.constants.SuggestedPost.MAX_PRICE_NANOTONCOINS`.
    """

    currency: str = tg_field(compare=True)
    amount: int = tg_field(compare=True)


@tg_dataclass()
class SuggestedPostParameters(TelegramObject):
    """
    Contains parameters of a post that is being suggested by the bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`price` and :attr:`send_date` are equal.

    .. versionadded:: 22.4

    Args:
        price (:class:`telegram.SuggestedPostPrice`, optional):
            Proposed price for the post. If the field is omitted, then the post is unpaid.
        send_date (:class:`datetime.datetime`, optional):
            Proposed send date of the post. If specified, then the date
            must be between :tg-const:`telegram.constants.SuggestedPost.MIN_SEND_DATE`
            second and :tg-const:`telegram.constants.SuggestedPost.MAX_SEND_DATE` seconds (30 days)
            in the future. If the field is omitted, then the post can be published at any time
            within :tg-const:`telegram.constants.SuggestedPost.MAX_SEND_DATE` seconds (30 days) at
            the sole discretion of the user who approves it.
            |datetime_localization|

    Attributes:
        price (:class:`telegram.SuggestedPostPrice`):
            Optional. Proposed price for the post. If the field is omitted, then the post
            is unpaid.
        send_date (:class:`datetime.datetime`):
            Optional. Proposed send date of the post. If specified, then the date
            must be between :tg-const:`telegram.constants.SuggestedPost.MIN_SEND_DATE`
            second and :tg-const:`telegram.constants.SuggestedPost.MAX_SEND_DATE` seconds (30 days)
            in the future. If the field is omitted, then the post can be published at any time
            within :tg-const:`telegram.constants.SuggestedPost.MAX_SEND_DATE` seconds (30 days) at
            the sole discretion of the user who approves it.
            |datetime_localization|

    """

    # Optional
    price: SuggestedPostPrice | None = tg_field(compare=True, default=None)
    send_date: dtm.datetime | None = tg_field(compare=True, default=None)


@tg_dataclass()
class SuggestedPostInfo(TelegramObject):
    """
    Contains information about a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`state` and :attr:`price` are equal.

    .. versionadded:: 22.4

    Args:
        state (:obj:`str`):
            State of the suggested post. Currently, it can be one of
            :tg-const:`~telegram.constants.SuggestedPostInfoState.PENDING`,
            :tg-const:`~telegram.constants.SuggestedPostInfoState.APPROVED`,
            :tg-const:`~telegram.constants.SuggestedPostInfoState.DECLINED`.
        price (:obj:`SuggestedPostPrice`, optional):
            Proposed price of the post. If the field is omitted, then the post is unpaid.
        send_date (:class:`datetime.datetime`, optional):
            Proposed send date of the post. If the field is omitted, then the post can be published
            at any time within 30 days at the sole discretion of the user or administrator who
            approves it.
            |datetime_localization|

    Attributes:
        state (:obj:`str`):
            State of the suggested post. Currently, it can be one of
            :tg-const:`~telegram.constants.SuggestedPostInfoState.PENDING`,
            :tg-const:`~telegram.constants.SuggestedPostInfoState.APPROVED`,
            :tg-const:`~telegram.constants.SuggestedPostInfoState.DECLINED`.
        price (:obj:`SuggestedPostPrice`):
            Optional. Proposed price of the post. If the field is omitted, then the post is unpaid.
        send_date (:class:`datetime.datetime`):
            Optional. Proposed send date of the post. If the field is omitted, then the post can be
            published at any time within 30 days at the sole discretion of the user or
            administrator who approves it.
            |datetime_localization|

    """

    PENDING: ClassVar[str] = constants.SuggestedPostInfoState.PENDING
    """:const:`telegram.constants.SuggestedPostInfoState.PENDING`"""
    APPROVED: ClassVar[str] = constants.SuggestedPostInfoState.APPROVED
    """:const:`telegram.constants.SuggestedPostInfoState.APPROVED`"""
    DECLINED: ClassVar[str] = constants.SuggestedPostInfoState.DECLINED
    """:const:`telegram.constants.SuggestedPostInfoState.DECLINED`"""

    @staticmethod
    def _state_converter(value: str) -> str:
        return enum.get_member(constants.SuggestedPostInfoState, value, value)

    # Required
    state: str = tg_field(compare=True, converter=_state_converter)
    # Optional
    price: SuggestedPostPrice | None = tg_field(compare=True, default=None)
    send_date: dtm.datetime | None = tg_field(default=None)


@tg_dataclass()
class SuggestedPostDeclined(TelegramObject):
    """
    Describes a service message about the rejection of a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`suggested_post_message` and :attr:`comment` are equal.

    .. versionadded:: 22.4

    Args:
        suggested_post_message (:class:`telegram.Message`, optional):
            Message containing the suggested post. Note that the :class:`~telegram.Message` object
            in this field will not contain the :attr:`~telegram.Message.reply_to_message` field
            even if it itself is a reply.
        comment (:obj:`str`, optional):
            Comment with which the post was declined.

    Attributes:
        suggested_post_message (:class:`telegram.Message`):
            Optional. Message containing the suggested post. Note that the
            :class:`~telegram.Message` object in this field will not contain
            the :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        comment (:obj:`str`):
            Optional. Comment with which the post was declined.

    """

    suggested_post_message: Message | None = tg_field(compare=True, default=None)
    comment: str | None = tg_field(compare=True, default=None)


@tg_dataclass()
class SuggestedPostPaid(TelegramObject):
    """
    Describes a service message about a successful payment for a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if all of their attributes are equal.

    .. versionadded:: 22.4

    Args:
        suggested_post_message (:class:`telegram.Message`, optional):
            Message containing the suggested post. Note that the :class:`~telegram.Message` object
            in this field will not contain the :attr:`~telegram.Message.reply_to_message` field
            even if it itself is a reply.
        currency (:obj:`str`):
            Currency in which the payment was made. Currently, one of ``“XTR”`` for Telegram Stars
            or ``“TON”`` for toncoins.
        amount (:obj:`int`, optional):
            The amount of the currency that was received by the channel in nanotoncoins; for
            payments in toncoins only.
        star_amount (:class:`telegram.StarAmount`, optional):
            The amount of Telegram Stars that was received by the channel; for payments in Telegram
            Stars only.


    Attributes:
        suggested_post_message (:class:`telegram.Message`):
            Optional. Message containing the suggested post. Note that the
            :class:`~telegram.Message` object in this field will not contain
            the :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        currency (:obj:`str`):
            Currency in which the payment was made. Currently, one of ``“XTR”`` for Telegram Stars
            or ``“TON”`` for toncoins.
        amount (:obj:`int`):
            Optional. The amount of the currency that was received by the channel in nanotoncoins;
            for payments in toncoins only.
        star_amount (:class:`telegram.StarAmount`):
            Optional. The amount of Telegram Stars that was received by the channel; for payments
            in Telegram Stars only.

    """

    # Required
    currency: str = tg_field(compare=True)
    # Optional
    suggested_post_message: Message | None = tg_field(compare=True, default=None)
    amount: int | None = tg_field(compare=True, default=None)
    star_amount: StarAmount | None = tg_field(compare=True, default=None)


@tg_dataclass()
class SuggestedPostRefunded(TelegramObject):
    """
    Describes a service message about a payment refund for a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`suggested_post_message` and :attr:`reason` are equal.

    .. versionadded:: 22.4

    Args:
        suggested_post_message (:class:`telegram.Message`, optional):
            Message containing the suggested post. Note that the :class:`~telegram.Message` object
            in this field will not contain the :attr:`~telegram.Message.reply_to_message` field
            even if it itself is a reply.
        reason (:obj:`str`):
            Reason for the refund. Currently,
            one of :tg-const:`telegram.constants.SuggestedPostRefunded.POST_DELETED` if the post
            was deleted within 24 hours of being posted or removed from scheduled messages without
            being posted, or :tg-const:`telegram.constants.SuggestedPostRefunded.PAYMENT_REFUNDED`
            if the payer refunded their payment.

    Attributes:
        suggested_post_message (:class:`telegram.Message`):
            Optional. Message containing the suggested post. Note that the
            :class:`~telegram.Message` object in this field will not contain
            the :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        reason (:obj:`str`):
            Reason for the refund. Currently,
            one of :tg-const:`telegram.constants.SuggestedPostRefunded.POST_DELETED` if the post
            was deleted within 24 hours of being posted or removed from scheduled messages without
            being posted, or :tg-const:`telegram.constants.SuggestedPostRefunded.PAYMENT_REFUNDED`
            if the payer refunded their payment.

    """

    # Required
    reason: str = tg_field(compare=True)
    # Optional
    suggested_post_message: Message | None = tg_field(compare=True, default=None)


@tg_dataclass()
class SuggestedPostApproved(TelegramObject):
    """
    Describes a service message about the approval of a suggested post.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if all of their attributes are equal.

    .. versionadded:: 22.4

    Args:
        suggested_post_message (:class:`telegram.Message`, optional):
            Message containing the suggested post. Note that the :class:`~telegram.Message` object
            in this field will not contain the :attr:`~telegram.Message.reply_to_message` field
            even if it itself is a reply.
        price (:obj:`SuggestedPostPrice`, optional):
            Amount paid for the post.
        send_date (:class:`datetime.datetime`):
            Date when the post will be published.
            |datetime_localization|

    Attributes:
        suggested_post_message (:class:`telegram.Message`):
            Optional. Message containing the suggested post. Note that the
            :class:`~telegram.Message` object in this field will not contain
            the :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        price (:obj:`SuggestedPostPrice`):
            Optional. Amount paid for the post.
        send_date (:class:`datetime.datetime`):
            Date when the post will be published.
            |datetime_localization|

    """

    # Rrequired
    send_date: dtm.datetime = tg_field(compare=True)
    # Optional
    suggested_post_message: Message | None = tg_field(compare=True, default=None)
    price: SuggestedPostPrice | None = tg_field(compare=True, default=None)


@tg_dataclass()
class SuggestedPostApprovalFailed(TelegramObject):
    """
    Describes a service message about the failed approval of a suggested post. Currently, only
    caused by insufficient user funds at the time of approval.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`suggested_post_message` and :attr:`price` are equal.

    .. versionadded:: 22.4

    Args:
        suggested_post_message (:class:`telegram.Message`, optional):
            Message containing the suggested post. Note that the :class:`~telegram.Message` object
            in this field will not contain the :attr:`~telegram.Message.reply_to_message` field
            even if it itself is a reply.
        price (:obj:`SuggestedPostPrice`):
            Expected price of the post.

    Attributes:
        suggested_post_message (:class:`telegram.Message`):
            Optional. Message containing the suggested post. Note that the
            :class:`~telegram.Message` object in this field will not contain
            the :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        price (:obj:`SuggestedPostPrice`):
            Expected price of the post.

    """

    # Required
    price: SuggestedPostPrice = tg_field(compare=True)
    # Optional
    suggested_post_message: Message | None = tg_field(compare=True, default=None)
