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
# pylint: disable=redefined-builtin
"""This module contains the classes for Telegram Stars transactions."""

import datetime as dtm
from collections.abc import Sequence

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict

from .transactionpartner import TransactionPartner


class StarTransaction(TelegramObject):
    """Describes a Telegram Star transaction.
    Note that if the buyer initiates a chargeback with the payment provider from whom they
    acquired Stars (e.g., Apple, Google) following this transaction, the refunded Stars will be
    deducted from the bot's balance. This is outside of Telegram's control.

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
            :tg-const:`~telegram.constants.Nanostar.VALUE` shares of Telegram
            Stars transferred by the transaction; from 0 to
            :tg-const:`~telegram.constants.NanostarLimit.MAX_AMOUNT`

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
            :tg-const:`~telegram.constants.Nanostar.VALUE` shares of Telegram
            Stars transferred by the transaction; from 0 to
            :tg-const:`~telegram.constants.NanostarLimit.MAX_AMOUNT`

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
        source: TransactionPartner | None = None,
        receiver: TransactionPartner | None = None,
        nanostar_amount: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.amount: int = amount
        self.date: dtm.datetime = date
        self.source: TransactionPartner | None = source
        self.receiver: TransactionPartner | None = receiver
        self.nanostar_amount: int | None = nanostar_amount

        self._id_attrs = (
            self.id,
            self.source,
            self.receiver,
        )
        self._freeze()


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
        self, transactions: Sequence[StarTransaction], *, api_kwargs: JSONDict | None = None
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.transactions: tuple[StarTransaction, ...] = parse_sequence_arg(transactions)

        self._id_attrs = (self.transactions,)
        self._freeze()
