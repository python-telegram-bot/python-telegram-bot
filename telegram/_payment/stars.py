#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
# pylint: disable=redefined-builtin
"""This module contains the classes for Telegram Stars transactions."""

import datetime as dtm
from collections.abc import Sequence
from typing import TYPE_CHECKING, Final, Optional

from telegram import constants
from telegram._chat import Chat
from telegram._gifts import Gift
from telegram._paidmedia import PaidMedia
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class RevenueWithdrawalState(TelegramObject):
    """This object escribes the state of a revenue withdrawal operation. Currently, it can be one
    of:

    * :class:`telegram.RevenueWithdrawalStatePending`
    * :class:`telegram.RevenueWithdrawalStateSucceeded`
    * :class:`telegram.RevenueWithdrawalStateFailed`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): The type of the state.

    Attributes:
        type (:obj:`str`): The type of the state.
    """

    __slots__ = ("type",)

    PENDING: Final[str] = constants.RevenueWithdrawalStateType.PENDING
    """:const:`telegram.constants.RevenueWithdrawalStateType.PENDING`"""
    SUCCEEDED: Final[str] = constants.RevenueWithdrawalStateType.SUCCEEDED
    """:const:`telegram.constants.RevenueWithdrawalStateType.SUCCEEDED`"""
    FAILED: Final[str] = constants.RevenueWithdrawalStateType.FAILED
    """:const:`telegram.constants.RevenueWithdrawalStateType.FAILED`"""

    def __init__(self, type: str, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.RevenueWithdrawalStateType, type, type)

        self._id_attrs = (self.type,)
        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["RevenueWithdrawalState"]:
        """Converts JSON data to the appropriate :class:`RevenueWithdrawalState` object, i.e. takes
        care of selecting the correct subclass.

        Args:
            data (dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with this object.

        Returns:
            The Telegram object.

        """
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: dict[str, type[RevenueWithdrawalState]] = {
            cls.PENDING: RevenueWithdrawalStatePending,
            cls.SUCCEEDED: RevenueWithdrawalStateSucceeded,
            cls.FAILED: RevenueWithdrawalStateFailed,
        }

        if cls is RevenueWithdrawalState and data.get("type") in _class_mapping:
            return _class_mapping[data.pop("type")].de_json(data=data, bot=bot)

        return super().de_json(data=data, bot=bot)


class RevenueWithdrawalStatePending(RevenueWithdrawalState):
    """The withdrawal is in progress.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.PENDING`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=RevenueWithdrawalState.PENDING, api_kwargs=api_kwargs)
        self._freeze()


class RevenueWithdrawalStateSucceeded(RevenueWithdrawalState):
    """The withdrawal succeeded.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`date` are equal.

    .. versionadded:: 21.4

    Args:
        date (:obj:`datetime.datetime`): Date the withdrawal was completed as a datetime object.
        url (:obj:`str`): An HTTPS URL that can be used to see transaction details.

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.SUCCEEDED`.
        date (:obj:`datetime.datetime`): Date the withdrawal was completed as a datetime object.
        url (:obj:`str`): An HTTPS URL that can be used to see transaction details.
    """

    __slots__ = ("date", "url")

    def __init__(
        self,
        date: dtm.datetime,
        url: str,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(type=RevenueWithdrawalState.SUCCEEDED, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.date: dtm.datetime = date
            self.url: str = url
            self._id_attrs = (
                self.type,
                self.date,
            )

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["RevenueWithdrawalStateSucceeded"]:
        """See :meth:`telegram.RevenueWithdrawalState.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)
        data["date"] = from_timestamp(data.get("date", None), tzinfo=loc_tzinfo)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class RevenueWithdrawalStateFailed(RevenueWithdrawalState):
    """The withdrawal failed and the transaction was refunded.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.FAILED`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=RevenueWithdrawalState.FAILED, api_kwargs=api_kwargs)
        self._freeze()


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
            :tg-const:`~telegram.constants.StarTransactions.NANOSTAR_VALUE` shares of Telegram
            Stars received by the affiliate; from
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MIN_AMOUNT` to
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MAX_AMOUNT`;
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
            :tg-const:`~telegram.constants.StarTransactions.NANOSTAR_VALUE` shares of Telegram
            Stars received by the affiliate; from
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MIN_AMOUNT` to
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MAX_AMOUNT`;
            can be negative for refunds
    """

    __slots__ = (
        "affiliate_chat",
        "affiliate_user",
        "amount",
        "commission_per_mille",
        "nanostar_amount",
    )

    def __init__(
        self,
        commission_per_mille: int,
        amount: int,
        affiliate_user: Optional["User"] = None,
        affiliate_chat: Optional["Chat"] = None,
        nanostar_amount: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.affiliate_user: Optional[User] = affiliate_user
        self.affiliate_chat: Optional[Chat] = affiliate_chat
        self.commission_per_mille: int = commission_per_mille
        self.amount: int = amount
        self.nanostar_amount: Optional[int] = nanostar_amount

        self._id_attrs = (
            self.affiliate_user,
            self.affiliate_chat,
            self.commission_per_mille,
            self.amount,
            self.nanostar_amount,
        )
        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["AffiliateInfo"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["affiliate_user"] = User.de_json(data.get("affiliate_user"), bot)
        data["affiliate_chat"] = Chat.de_json(data.get("affiliate_chat"), bot)

        return super().de_json(data=data, bot=bot)


class TransactionPartner(TelegramObject):
    """This object describes the source of a transaction, or its recipient for outgoing
    transactions. Currently, it can be one of:

    * :class:`TransactionPartnerUser`
    * :class:`TransactionPartnerAffiliateProgram`
    * :class:`TransactionPartnerFragment`
    * :class:`TransactionPartnerTelegramAds`
    * :class:`TransactionPartnerTelegramApi`
    * :class:`TransactionPartnerOther`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): The type of the transaction partner.

    Attributes:
        type (:obj:`str`): The type of the transaction partner.
    """

    __slots__ = ("type",)

    AFFILIATE_PROGRAM: Final[str] = constants.TransactionPartnerType.AFFILIATE_PROGRAM
    """:const:`telegram.constants.TransactionPartnerType.AFFILIATE_PROGRAM`

    .. versionadded:: 21.9
    """
    FRAGMENT: Final[str] = constants.TransactionPartnerType.FRAGMENT
    """:const:`telegram.constants.TransactionPartnerType.FRAGMENT`"""
    OTHER: Final[str] = constants.TransactionPartnerType.OTHER
    """:const:`telegram.constants.TransactionPartnerType.OTHER`"""
    TELEGRAM_ADS: Final[str] = constants.TransactionPartnerType.TELEGRAM_ADS
    """:const:`telegram.constants.TransactionPartnerType.TELEGRAM_ADS`"""
    TELEGRAM_API: Final[str] = constants.TransactionPartnerType.TELEGRAM_API
    """:const:`telegram.constants.TransactionPartnerType.TELEGRAM_API`"""
    USER: Final[str] = constants.TransactionPartnerType.USER
    """:const:`telegram.constants.TransactionPartnerType.USER`"""

    def __init__(self, type: str, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.TransactionPartnerType, type, type)

        self._id_attrs = (self.type,)
        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["TransactionPartner"]:
        """Converts JSON data to the appropriate :class:`TransactionPartner` object, i.e. takes
        care of selecting the correct subclass.

        Args:
            data (dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with this object.

        Returns:
            The Telegram object.

        """
        data = cls._parse_data(data)

        if data is None:
            return None

        if not data and cls is TransactionPartner:
            return None

        _class_mapping: dict[str, type[TransactionPartner]] = {
            cls.AFFILIATE_PROGRAM: TransactionPartnerAffiliateProgram,
            cls.FRAGMENT: TransactionPartnerFragment,
            cls.USER: TransactionPartnerUser,
            cls.TELEGRAM_ADS: TransactionPartnerTelegramAds,
            cls.TELEGRAM_API: TransactionPartnerTelegramApi,
            cls.OTHER: TransactionPartnerOther,
        }

        if cls is TransactionPartner and data.get("type") in _class_mapping:
            return _class_mapping[data.pop("type")].de_json(data=data, bot=bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = ("commission_per_mille", "sponsor_user")

    def __init__(
        self,
        commission_per_mille: int,
        sponsor_user: Optional["User"] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(type=TransactionPartner.AFFILIATE_PROGRAM, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.sponsor_user: Optional[User] = sponsor_user
            self.commission_per_mille: int = commission_per_mille
            self._id_attrs = (
                self.type,
                self.commission_per_mille,
            )

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["TransactionPartnerAffiliateProgram"]:
        """See :meth:`telegram.TransactionPartner.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["sponsor_user"] = User.de_json(data.get("sponsor_user"), bot)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


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

    __slots__ = ("withdrawal_state",)

    def __init__(
        self,
        withdrawal_state: Optional["RevenueWithdrawalState"] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(type=TransactionPartner.FRAGMENT, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.withdrawal_state: Optional[RevenueWithdrawalState] = withdrawal_state

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["TransactionPartnerFragment"]:
        """See :meth:`telegram.TransactionPartner.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["withdrawal_state"] = RevenueWithdrawalState.de_json(
            data.get("withdrawal_state"), bot
        )

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class TransactionPartnerUser(TransactionPartner):
    """Describes a transaction with a user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` are equal.

    .. versionadded:: 21.4

    Args:
        user (:class:`telegram.User`): Information about the user.
        affiliate (:class:`telegram.AffiliateInfo`, optional): Information about the affiliate that
            received a commission via this transaction

            .. versionadded:: 21.9
        invoice_payload (:obj:`str`, optional): Bot-specified invoice payload.
        subscription_period (:class:`datetime.timedelta`, optional): The duration of the paid
            subscription

            .. versionadded:: 21.8
        paid_media (Sequence[:class:`telegram.PaidMedia`], optional): Information about the paid
            media bought by the user.

            .. versionadded:: 21.5
        paid_media_payload (:obj:`str`, optional): Bot-specified paid media payload.

            .. versionadded:: 21.6
        gift (:class:`telegram.Gift`, optional): The gift sent to the user by the bot

            .. versionadded:: 21.8

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.USER`.
        user (:class:`telegram.User`): Information about the user.
        affiliate (:class:`telegram.AffiliateInfo`): Optional. Information about the affiliate that
            received a commission via this transaction

            .. versionadded:: 21.9
        invoice_payload (:obj:`str`): Optional. Bot-specified invoice payload.
        subscription_period (:class:`datetime.timedelta`): Optional. The duration of the paid
            subscription

            .. versionadded:: 21.8
        paid_media (tuple[:class:`telegram.PaidMedia`]): Optional. Information about the paid
            media bought by the user.

            .. versionadded:: 21.5
        paid_media_payload (:obj:`str`): Optional. Bot-specified paid media payload.

            .. versionadded:: 21.6
        gift (:class:`telegram.Gift`): Optional. The gift sent to the user by the bot

            .. versionadded:: 21.8

    """

    __slots__ = (
        "affiliate",
        "gift",
        "invoice_payload",
        "paid_media",
        "paid_media_payload",
        "subscription_period",
        "user",
    )

    def __init__(
        self,
        user: "User",
        invoice_payload: Optional[str] = None,
        paid_media: Optional[Sequence[PaidMedia]] = None,
        paid_media_payload: Optional[str] = None,
        subscription_period: Optional[dtm.timedelta] = None,
        gift: Optional[Gift] = None,
        affiliate: Optional[AffiliateInfo] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(type=TransactionPartner.USER, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.user: User = user
            self.affiliate: Optional[AffiliateInfo] = affiliate
            self.invoice_payload: Optional[str] = invoice_payload
            self.paid_media: Optional[tuple[PaidMedia, ...]] = parse_sequence_arg(paid_media)
            self.paid_media_payload: Optional[str] = paid_media_payload
            self.subscription_period: Optional[dtm.timedelta] = subscription_period
            self.gift: Optional[Gift] = gift

            self._id_attrs = (
                self.type,
                self.user,
            )

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["TransactionPartnerUser"]:
        """See :meth:`telegram.TransactionPartner.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.get("user"), bot)
        data["affiliate"] = AffiliateInfo.de_json(data.get("affiliate"), bot)
        data["paid_media"] = PaidMedia.de_list(data.get("paid_media"), bot=bot)
        data["subscription_period"] = (
            dtm.timedelta(seconds=sp)
            if (sp := data.get("subscription_period")) is not None
            else None
        )
        data["gift"] = Gift.de_json(data.get("gift"), bot)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class TransactionPartnerOther(TransactionPartner):
    """Describes a transaction with an unknown partner.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.OTHER`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=TransactionPartner.OTHER, api_kwargs=api_kwargs)
        self._freeze()


class TransactionPartnerTelegramAds(TransactionPartner):
    """Describes a withdrawal transaction to the Telegram Ads platform.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.TELEGRAM_ADS`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=TransactionPartner.TELEGRAM_ADS, api_kwargs=api_kwargs)
        self._freeze()


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

    __slots__ = ("request_count",)

    def __init__(self, request_count: int, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=TransactionPartner.TELEGRAM_API, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.request_count: int = request_count
            self._id_attrs = (self.request_count,)


class StarTransaction(TelegramObject):
    """Describes a Telegram Star transaction.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id`, :attr:`source`, and :attr:`receiver` are equal.

    .. versionadded:: 21.4

    Args:
        id (:obj:`str`): Unique identifier of the transaction. Coincides with the identifer
            of the original transaction for refund transactions.
            Coincides with :attr:`SuccessfulPayment.telegram_payment_charge_id` for
            successful incoming payments from users.
        amount (:obj:`int`): Integer amount of Telegram Stars transferred by the transaction.
        nanostar_amount (:obj:`int`, optional): The number of
            :tg-const:`~telegram.constants.StarTransactions.NANOSTAR_VALUE` shares of Telegram
            Stars transferred by the transaction; from 0 to
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MAX_AMOUNT`

            .. versionadded:: 21.9
        date (:obj:`datetime.datetime`): Date the transaction was created as a datetime object.
        source (:class:`telegram.TransactionPartner`, optional): Source of an incoming transaction
            (e.g., a user purchasing goods or services, Fragment refunding a failed withdrawal).
            Only for incoming transactions.
        receiver (:class:`telegram.TransactionPartner`, optional): Receiver of an outgoing
            transaction (e.g., a user for a purchase refund, Fragment for a withdrawal). Only for
            outgoing transactions.

    Attributes:
        id (:obj:`str`): Unique identifier of the transaction. Coincides with the identifer
            of the original transaction for refund transactions.
            Coincides with :attr:`SuccessfulPayment.telegram_payment_charge_id` for
            successful incoming payments from users.
        amount (:obj:`int`): Integer amount of Telegram Stars transferred by the transaction.
        nanostar_amount (:obj:`int`): Optional. The number of
            :tg-const:`~telegram.constants.StarTransactions.NANOSTAR_VALUE` shares of Telegram
            Stars transferred by the transaction; from 0 to
            :tg-const:`~telegram.constants.StarTransactionsLimit.NANOSTAR_MAX_AMOUNT`

            .. versionadded:: 21.9
        date (:obj:`datetime.datetime`): Date the transaction was created as a datetime object.
        source (:class:`telegram.TransactionPartner`): Optional. Source of an incoming transaction
            (e.g., a user purchasing goods or services, Fragment refunding a failed withdrawal).
            Only for incoming transactions.
        receiver (:class:`telegram.TransactionPartner`): Optional. Receiver of an outgoing
            transaction (e.g., a user for a purchase refund, Fragment for a withdrawal). Only for
            outgoing transactions.
    """

    __slots__ = ("amount", "date", "id", "nanostar_amount", "receiver", "source")

    def __init__(
        self,
        id: str,
        amount: int,
        date: dtm.datetime,
        source: Optional[TransactionPartner] = None,
        receiver: Optional[TransactionPartner] = None,
        nanostar_amount: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.amount: int = amount
        self.date: dtm.datetime = date
        self.source: Optional[TransactionPartner] = source
        self.receiver: Optional[TransactionPartner] = receiver
        self.nanostar_amount: Optional[int] = nanostar_amount

        self._id_attrs = (
            self.id,
            self.source,
            self.receiver,
        )
        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["StarTransaction"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)
        data["date"] = from_timestamp(data.get("date", None), tzinfo=loc_tzinfo)

        data["source"] = TransactionPartner.de_json(data.get("source"), bot)
        data["receiver"] = TransactionPartner.de_json(data.get("receiver"), bot)

        return super().de_json(data=data, bot=bot)


class StarTransactions(TelegramObject):
    """
    Contains a list of Telegram Star transactions.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`transactions` are equal.

    .. versionadded:: 21.4

    Args:
        transactions (Sequence[:class:`telegram.StarTransaction`]): The list of transactions.

    Attributes:
        transactions (tuple[:class:`telegram.StarTransaction`]): The list of transactions.
    """

    __slots__ = ("transactions",)

    def __init__(
        self, transactions: Sequence[StarTransaction], *, api_kwargs: Optional[JSONDict] = None
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.transactions: tuple[StarTransaction, ...] = parse_sequence_arg(transactions)

        self._id_attrs = (self.transactions,)
        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["StarTransactions"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if data is None:
            return None

        data["transactions"] = StarTransaction.de_list(data.get("transactions"), bot)
        return super().de_json(data=data, bot=bot)
