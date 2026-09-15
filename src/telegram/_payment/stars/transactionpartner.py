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
"""This module contains the classes for Telegram Stars transaction partners."""

from typing import TYPE_CHECKING, ClassVar

from telegram import constants
from telegram._chat import Chat
from telegram._gifts import Gift
from telegram._paidmedia import PaidMedia
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import (
    parse_sequence_arg,
    to_timedelta,
)
from telegram._utils.dataclass import tg_dataclass, tg_field

from .affiliateinfo import AffiliateInfo

if TYPE_CHECKING:
    import datetime as dtm

    from telegram._user import User

    from .revenuewithdrawalstate import RevenueWithdrawalState


@tg_dataclass()
class TransactionPartner(TelegramObject):
    """This object describes the source of a transaction, or its recipient for outgoing
    transactions. Currently, it can be one of:

    * :class:`TransactionPartnerUser`
    * :class:`TransactionPartnerChat`
    * :class:`TransactionPartnerAffiliateProgram`
    * :class:`TransactionPartnerFragment`
    * :class:`TransactionPartnerTelegramAds`
    * :class:`TransactionPartnerTelegramApi`
    * :class:`TransactionPartnerOther`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.4

    .. versionchanged:: 21.11
        Added :class:`TransactionPartnerChat`

    Args:
        type (:obj:`str`): The type of the transaction partner.

    Attributes:
        type (:obj:`str`): The type of the transaction partner.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "affiliate_program": "TransactionPartnerAffiliateProgram",
            "chat": "TransactionPartnerChat",
            "fragment": "TransactionPartnerFragment",
            "other": "TransactionPartnerOther",
            "telegram_ads": "TransactionPartnerTelegramAds",
            "telegram_api": "TransactionPartnerTelegramApi",
            "user": "TransactionPartnerUser",
        },
    )

    AFFILIATE_PROGRAM: ClassVar[str] = constants.TransactionPartnerType.AFFILIATE_PROGRAM
    """:const:`telegram.constants.TransactionPartnerType.AFFILIATE_PROGRAM`

    .. versionadded:: 21.9
    """
    CHAT: ClassVar[str] = constants.TransactionPartnerType.CHAT
    """:const:`telegram.constants.TransactionPartnerType.CHAT`

    .. versionadded:: 21.11
    """
    FRAGMENT: ClassVar[str] = constants.TransactionPartnerType.FRAGMENT
    """:const:`telegram.constants.TransactionPartnerType.FRAGMENT`"""
    OTHER: ClassVar[str] = constants.TransactionPartnerType.OTHER
    """:const:`telegram.constants.TransactionPartnerType.OTHER`"""
    TELEGRAM_ADS: ClassVar[str] = constants.TransactionPartnerType.TELEGRAM_ADS
    """:const:`telegram.constants.TransactionPartnerType.TELEGRAM_ADS`"""
    TELEGRAM_API: ClassVar[str] = constants.TransactionPartnerType.TELEGRAM_API
    """:const:`telegram.constants.TransactionPartnerType.TELEGRAM_API`"""
    USER: ClassVar[str] = constants.TransactionPartnerType.USER
    """:const:`telegram.constants.TransactionPartnerType.USER`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.TransactionPartnerType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class TransactionPartnerAffiliateProgram(TransactionPartner):
    """Describes the affiliate program that issued the affiliate commission received via this
    transaction.

    This object is comparable in terms of equality. Two objects of this class are considered equal,
    if their :attr:`commission_per_mille` are equal.

    .. versionadded:: 21.9

    Args:
        sponsor_user (:class:`telegram.User`, optional): Information about the bot that sponsored
            the affiliate program
        commission_per_mille (:obj:`int`): The number of Telegram Stars received by the bot for
            each 1000 Telegram Stars received by the affiliate program sponsor from referred users.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.AFFILIATE_PROGRAM`.
        sponsor_user (:class:`telegram.User`): Optional. Information about the bot that sponsored
            the affiliate program
        commission_per_mille (:obj:`int`): The number of Telegram Stars received by the bot for
            each 1000 Telegram Stars received by the affiliate program sponsor from referred users.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=TransactionPartner.AFFILIATE_PROGRAM)
    # Required
    commission_per_mille: int = tg_field(compare=True)
    # Optional
    sponsor_user: "User | None" = tg_field(default=None)


@tg_dataclass()
class TransactionPartnerChat(TransactionPartner):
    """Describes a transaction with a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat` are equal.

    .. versionadded:: 21.11

    Args:
        chat (:class:`telegram.Chat`): Information about the chat.
        gift (:class:`telegram.Gift`, optional): The gift sent to the chat by the bot.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.CHAT`.
        chat (:class:`telegram.Chat`): Information about the chat.
        gift (:class:`telegram.Gift`): Optional. The gift sent to the user by the bot.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=TransactionPartner.CHAT)
    # Required
    chat: Chat = tg_field(compare=True)
    # Optional
    gift: Gift | None = tg_field(default=None)


@tg_dataclass()
class TransactionPartnerFragment(TransactionPartner):
    """Describes a withdrawal transaction with Fragment.

    .. versionadded:: 21.4

    Args:
        withdrawal_state (:class:`telegram.RevenueWithdrawalState`, optional): State of the
            transaction if the transaction is outgoing.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.FRAGMENT`.
        withdrawal_state (:class:`telegram.RevenueWithdrawalState`): Optional. State of the
            transaction if the transaction is outgoing.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=TransactionPartner.FRAGMENT)
    # Optional
    withdrawal_state: "RevenueWithdrawalState | None" = tg_field(default=None)


@tg_dataclass()
class TransactionPartnerUser(TransactionPartner):
    """Describes a transaction with a user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` and :attr:`transaction_type` are equal.

    .. versionadded:: 21.4

    .. versionchanged:: 22.1
       Equality comparison now includes the new required argument :paramref:`transaction_type`,
       introduced in Bot API 9.0.

    Args:
        transaction_type (:obj:`str`): Type of the transaction, currently one of
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT` for payments via
            invoices, :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            for payments for paid media,
            :tg-const:`telegram.constants.TransactionPartnerUser.GIFT_PURCHASE` for gifts sent by
            the bot, :tg-const:`telegram.constants.TransactionPartnerUser.PREMIUM_PURCHASE`
            for Telegram Premium subscriptions gifted by the bot,
            :tg-const:`telegram.constants.TransactionPartnerUser.BUSINESS_ACCOUNT_TRANSFER` for
            direct transfers from managed business accounts.

            .. versionadded:: 22.1
        user (:class:`telegram.User`): Information about the user.
        affiliate (:class:`telegram.AffiliateInfo`, optional): Information about the affiliate that
            received a commission via this transaction. Can be available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT`
            and :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            transactions.

            .. versionadded:: 21.9
        invoice_payload (:obj:`str`, optional): Bot-specified invoice payload. Can be available
            only for :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT`
            transactions.
        subscription_period (:obj:`int` | :class:`datetime.timedelta`, optional): The duration of
            the paid subscription. Can be available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT` transactions.

            .. versionadded:: 21.8

            .. versionchanged:: v22.2
                Accepts :obj:`int` objects as well as :class:`datetime.timedelta`.
        paid_media (Sequence[:class:`telegram.PaidMedia`], optional): Information about the paid
            media bought by the user. for
            :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            transactions only.

            .. versionadded:: 21.5
        paid_media_payload (:obj:`str`, optional): Bot-specified paid media payload. Can be
            available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT` transactions.

            .. versionadded:: 21.6
        gift (:class:`telegram.Gift`, optional): The gift sent to the user by the bot; for
            :tg-const:`telegram.constants.TransactionPartnerUser.GIFT_PURCHASE` transactions only.

            .. versionadded:: 21.8
        premium_subscription_duration (:obj:`int`, optional): Number of months the gifted Telegram
            Premium subscription will be active for; for
            :tg-const:`telegram.constants.TransactionPartnerUser.PREMIUM_PURCHASE`
            transactions only.

            .. versionadded:: 22.1

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.USER`.
        transaction_type (:obj:`str`): Type of the transaction, currently one of
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT` for payments via
            invoices, :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            for payments for paid media,
            :tg-const:`telegram.constants.TransactionPartnerUser.GIFT_PURCHASE` for gifts sent by
            the bot, :tg-const:`telegram.constants.TransactionPartnerUser.PREMIUM_PURCHASE`
            for Telegram Premium subscriptions gifted by the bot,
            :tg-const:`telegram.constants.TransactionPartnerUser.BUSINESS_ACCOUNT_TRANSFER` for
            direct transfers from managed business accounts.

            .. versionadded:: 22.1
        user (:class:`telegram.User`): Information about the user.
        affiliate (:class:`telegram.AffiliateInfo`): Optional. Information about the affiliate that
            received a commission via this transaction. Can be available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT`
            and :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            transactions.

            .. versionadded:: 21.9
        invoice_payload (:obj:`str`): Optional. Bot-specified invoice payload. Can be available
            only for :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT`
            transactions.
        subscription_period (:class:`datetime.timedelta`): Optional. The duration of the paid
            subscription. Can be available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.INVOICE_PAYMENT` transactions.

            .. versionadded:: 21.8
        paid_media (tuple[:class:`telegram.PaidMedia`]): Optional. Information about the paid
            media bought by the user. for
            :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT`
            transactions only.

            .. versionadded:: 21.5
        paid_media_payload (:obj:`str`): Optional. Bot-specified paid media payload. Can be
            available only for
            :tg-const:`telegram.constants.TransactionPartnerUser.PAID_MEDIA_PAYMENT` transactions.

            .. versionadded:: 21.6
        gift (:class:`telegram.Gift`): Optional. The gift sent to the user by the bot; for
            :tg-const:`telegram.constants.TransactionPartnerUser.GIFT_PURCHASE` transactions only.

            .. versionadded:: 21.8
        premium_subscription_duration (:obj:`int`): Optional. Number of months the gifted Telegram
            Premium subscription will be active for; for
            :tg-const:`telegram.constants.TransactionPartnerUser.PREMIUM_PURCHASE`
            transactions only.

            .. versionadded:: 22.1

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=TransactionPartner.USER)
    # Required
    transaction_type: str = tg_field(compare=True)
    user: "User" = tg_field(compare=True)
    # Optional
    invoice_payload: str | None = tg_field(default=None)
    paid_media: tuple[PaidMedia, ...] | None = tg_field(default=None, converter=parse_sequence_arg)
    paid_media_payload: str | None = tg_field(default=None)
    subscription_period: "dtm.timedelta | None" = tg_field(default=None, converter=to_timedelta)
    gift: Gift | None = tg_field(default=None)
    affiliate: AffiliateInfo | None = tg_field(default=None)
    premium_subscription_duration: int | None = tg_field(default=None)


@tg_dataclass()
class TransactionPartnerOther(TransactionPartner):
    """Describes a transaction with an unknown partner.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.OTHER`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=TransactionPartner.OTHER)


@tg_dataclass()
class TransactionPartnerTelegramAds(TransactionPartner):
    """Describes a withdrawal transaction to the Telegram Ads platform.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.TELEGRAM_ADS`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=TransactionPartner.TELEGRAM_ADS)


@tg_dataclass()
class TransactionPartnerTelegramApi(TransactionPartner):
    """Describes a transaction with payment for
    `paid broadcasting <https://core.telegram.org/bots/api#paid-broadcasts>`_.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_count` is equal.

    .. versionadded:: 21.7

    Args:
        request_count (:obj:`int`): The number of successful requests that exceeded regular limits
            and were therefore billed.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.TELEGRAM_API`.
        request_count (:obj:`int`): The number of successful requests that exceeded regular limits
            and were therefore billed.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=TransactionPartner.TELEGRAM_API)
    # Required
    request_count: int = tg_field(compare=True)
