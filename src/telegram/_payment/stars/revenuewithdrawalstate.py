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
"""This module contains the classes for Telegram Stars Revenue Withdrawals."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class RevenueWithdrawalState(TelegramObject):
    """This object describes the state of a revenue withdrawal operation. Currently, it can be one
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

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "pending": "RevenueWithdrawalStatePending",
            "succeeded": "RevenueWithdrawalStateSucceeded",
            "failed": "RevenueWithdrawalStateFailed",
        },
    )

    PENDING: ClassVar[str] = constants.RevenueWithdrawalStateType.PENDING
    """:const:`telegram.constants.RevenueWithdrawalStateType.PENDING`"""
    SUCCEEDED: ClassVar[str] = constants.RevenueWithdrawalStateType.SUCCEEDED
    """:const:`telegram.constants.RevenueWithdrawalStateType.SUCCEEDED`"""
    FAILED: ClassVar[str] = constants.RevenueWithdrawalStateType.FAILED
    """:const:`telegram.constants.RevenueWithdrawalStateType.FAILED`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.RevenueWithdrawalStateType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class RevenueWithdrawalStatePending(RevenueWithdrawalState):
    """The withdrawal is in progress.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.PENDING`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=RevenueWithdrawalState.PENDING)


@tg_dataclass()
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

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=RevenueWithdrawalState.SUCCEEDED)

    date: dtm.datetime = tg_field(compare=True)
    url: str = tg_field()


@tg_dataclass()
class RevenueWithdrawalStateFailed(RevenueWithdrawalState):
    """The withdrawal failed and the transaction was refunded.

    .. versionadded:: 21.4

    Attributes:
        type (:obj:`str`): The type of the state, always
            :tg-const:`telegram.RevenueWithdrawalState.FAILED`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=RevenueWithdrawalState.FAILED)
