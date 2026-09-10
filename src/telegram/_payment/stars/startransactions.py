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
"""This module contains the classes for Telegram Stars transactions."""

import datetime as dtm

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field

from .transactionpartner import TransactionPartner


@tg_dataclass()
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

    # Required
    id: str = tg_field(compare=True)
    amount: int = tg_field()
    date: dtm.datetime = tg_field()
    # Optional
    source: TransactionPartner | None = tg_field(compare=True, default=None)
    receiver: TransactionPartner | None = tg_field(compare=True, default=None)
    nanostar_amount: int | None = tg_field(default=None)


@tg_dataclass()
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

    transactions: tuple[StarTransaction, ...] = tg_field(
        compare=True, converter=parse_sequence_arg
    )
