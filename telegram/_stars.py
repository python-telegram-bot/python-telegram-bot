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

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Final, Optional, Sequence, Type

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._user import User
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

    .. versionadded:: NEXT.VERSION

    Args:
        type (:obj:`str`): The type of the state.

    Attributes:
        type (:obj:`str`): The type of the state.
    """

    __slots__ = ("type",)

    PENDING: Final[str] = constants.RevenueWithdrawalStateType.PENDING
    """:const:`telegram.constants.RevenueWithdrawalState.PENDING`"""
    SUCCEEDED: Final[str] = constants.RevenueWithdrawalStateType.SUCCEEDED
    """:const:`telegram.constants.RevenueWithdrawalState.SUCCEEDED`"""
    FAILED: Final[str] = constants.RevenueWithdrawalStateType.FAILED
    """:const:`telegram.constants.RevenueWithdrawalState.FAILED`"""

    def __init__(self, type: str, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = type

        self._id_attrs = (self.type,)
        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["RevenueWithdrawalState"]:
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: Dict[str, Type[RevenueWithdrawalState]] = {
            cls.PENDING: RevenueWithdrawalStatePending,
            cls.SUCCEEDED: RevenueWithdrawalStateSucceeded,
            cls.FAILED: RevenueWithdrawalStateFailed,
        }

        if cls is RevenueWithdrawalState and data.get("type") in _class_mapping:
            return _class_mapping[data.pop("type")].de_json(data=data, bot=bot)

        return super().de_json(data=data, bot=bot)


class RevenueWithdrawalStatePending(RevenueWithdrawalState):
    """The withdrawal is in progress.

    .. versionadded:: NEXT.VERSION

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.PENDING`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=RevenueWithdrawalState.PENDING, api_kwargs=api_kwargs)


class RevenueWithdrawalStateSucceeded(RevenueWithdrawalState):
    """The withdrawal succeeded.

    .. versionadded:: NEXT.VERSION

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
        date: datetime,
        url: str,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(type=RevenueWithdrawalState.SUCCEEDED, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.date: datetime = date
            self.url: str = url

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: "Bot"
    ) -> Optional["RevenueWithdrawalStateSucceeded"]:
        data = cls._parse_data(data)

        if not data:
            return None

        if "date" in data:
            # Get the local timezone from the bot if it has defaults
            loc_tzinfo = extract_tzinfo_from_defaults(bot)
            data["date"] = from_timestamp(data["date"], tzinfo=loc_tzinfo)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class RevenueWithdrawalStateFailed(RevenueWithdrawalState):
    """The withdrawal failed and the transaction was refunded.

    .. verisonadded:: NEXT.VERSION

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.FAILED`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=RevenueWithdrawalState.FAILED, api_kwargs=api_kwargs)


class TransactionPartner(TelegramObject):
    """This object describes the source of a transaction, or its recipient for outgoing
    transactions. Currently, it can be one of:

    * :class:`TransactionPartnerFragment`
    * :class:`TransactionPartnerUser`
    * :class:`TransactionPartnerOther`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        type (:obj:`str`): The type of the transaction partner.

    Attributes:
        type (:obj:`str`): The type of the transaction partner.
    """

    __slots__ = ("type",)

    FRAGMENT: Final[str] = constants.TransactionPartnerType.FRAGMENT
    """:const:`telegram.constants.TransactionPartnerType.FRAGMENT`"""
    USER: Final[str] = constants.TransactionPartnerType.USER
    """:const:`telegram.constants.TransactionPartnerType.USER`"""
    OTHER: Final[str] = constants.TransactionPartnerType.OTHER
    """:const:`telegram.constants.TransactionPartnerType.OTHER`"""

    def __init__(self, type: str, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = type

        self._id_attrs = (self.type,)
        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["TransactionPartner"]:
        print(data)
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: Dict[str, Type[TransactionPartner]] = {
            cls.FRAGMENT: TransactionPartnerFragment,
            cls.USER: TransactionPartnerUser,
            cls.OTHER: TransactionPartnerOther,
        }

        if cls is TransactionPartner and data.get("type") in _class_mapping:
            return _class_mapping[data.get("type")].de_json(data=data, bot=bot)

        return super().de_json(data=data, bot=bot)


class TransactionPartnerFragment(TransactionPartner):
    """Describes a withdrawal transaction with Fragment.

    .. versionadded:: NEXT.VERSION

    Args:
        withdrawal_state (:obj:`telegram.RevenueWithdrawalState`, optional): State of the
            transaction if the transaction is outgoing.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.FRAGMENT`.
        withdrawal_state (:obj:`telegram.RevenueWithdrawalState`): Optional. State of the
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
        cls, data: Optional[JSONDict], bot: "Bot"
    ) -> Optional["TransactionPartnerFragment"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data["withdrawal_state"] = RevenueWithdrawalState.de_json(
            data.get("withdrawal_state"), bot
        )

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class TransactionPartnerUser(TransactionPartner):
    """Describes a transaction with a user.

    .. versionadded:: NEXT.VERSION

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.USER`.
        user (:class:`telegram.User`): Information about the user.
    """

    __slots__ = ("user",)

    def __init__(self, user: "User", *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=TransactionPartner.USER, api_kwargs=api_kwargs)

        with self._unfrozen():
            self.user: User = user

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["TransactionPartnerUser"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.get("user"), bot)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class TransactionPartnerOther(TransactionPartner):
    """Describes a transaction with an unknown partner.

    .. versionadded:: NEXT.VERSION

    Attributes:
        type (:obj:`str`): The type of the transaction partner,
            always :tg-const:`telegram.TransactionPartner.OTHER`.
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: Optional[JSONDict] = None) -> None:
        super().__init__(type=TransactionPartner.OTHER, api_kwargs=api_kwargs)


class StarTransaction(TelegramObject):
    """Describes a Telegram Star transaction.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id`, :attr:`amount`, and :attr:`date` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        id (:obj:`str`): Unique identifier of the transaction. Coincides with the identifer
            of the original transaction for refund transactions.
            Coincides with :attr:`SuccessfulPayment.telegram_payment_charge_id` for
            successful incoming payments from users.
        amount (:obj:`int`): Number of Telegram Stars transferred by the transaction.
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
        amount (:obj:`int`): Number of Telegram Stars transferred by the transaction.
        date (:obj:`datetime.datetime`): Date the transaction was created as a datetime object.
        source (:class:`telegram.TransactionPartner`): Optional. Source of an incoming transaction
            (e.g., a user purchasing goods or services, Fragment refunding a failed withdrawal).
            Only for incoming transactions.
        receiver (:class:`telegram.TransactionPartner`): Optional. Receiver of an outgoing
            transaction (e.g., a user for a purchase refund, Fragment for a withdrawal). Only for
            outgoing transactions.
    """

    __slots__ = ("amount", "date", "id", "receiver", "source")

    def __init__(
        self,
        id: str,
        amount: int,
        date: datetime,
        source: Optional[TransactionPartner] = None,
        receiver: Optional[TransactionPartner] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.amount: int = amount
        self.date: datetime = date
        self.source: Optional[TransactionPartner] = source
        self.receiver: Optional[TransactionPartner] = receiver

        self._id_attrs = (
            self.id,
            self.amount,
            self.date,
        )

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["StarTransaction"]:
        data = cls._parse_data(data)

        if not data:
            return None

        if "date" in data:
            # Get the local timezone from the bot if it has defaults
            loc_tzinfo = extract_tzinfo_from_defaults(bot)
            data["date"] = from_timestamp(data["date"], tzinfo=loc_tzinfo)

        data["source"] = TransactionPartner.de_json(data.get("source"), bot)
        data["receiver"] = TransactionPartner.de_json(data.get("receiver"), bot)

        return super().de_json(data=data, bot=bot)  # type: ignore[return-value]


class StarTransactions(TelegramObject):
    """
    Contains a list of Telegram Star transactions.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`transactions` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        transactions (Sequence[:class:`telegram.StarTransaction`]): The list of transactions.

    Attributes:
        transactions (Sequence[:class:`telegram.StarTransaction`]): The list of transactions.
    """

    __slots__ = ("transactions",)

    def __init__(
        self, transactions: Sequence[StarTransaction], *, api_kwargs: Optional[JSONDict] = None
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.transactions: Sequence[StarTransaction] = transactions

        self._id_attrs = (self.transactions,)
        self._freeze()
