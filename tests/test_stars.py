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

import datetime

import pytest

from telegram import (
    RevenueWithdrawalStateFailed,
    RevenueWithdrawalStatePending,
    RevenueWithdrawalStateSucceeded,
    StarTransaction,
    TransactionPartnerFragment,
    TransactionPartnerOther,
    TransactionPartnerUser,
    User,
)
from telegram._utils.datetime import UTC, from_timestamp, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture()
def withdrawal_state_succeeded():
    return RevenueWithdrawalStateSucceeded(
        date=to_timestamp(datetime.datetime.utcnow()),
        url="url",
    )


@pytest.fixture()
def withdrawal_state_failed():
    return RevenueWithdrawalStateFailed()


@pytest.fixture()
def withdrawal_state_pending():
    return RevenueWithdrawalStatePending()


@pytest.fixture()
def transaction_partner_user():
    return TransactionPartnerUser(
        user=User(id=1, is_bot=False, first_name="first_name", username="username"),
    )


@pytest.fixture()
def transaction_partner_other():
    return TransactionPartnerOther()


@pytest.fixture()
def transaction_partner_fragment(withdrawal_state_succeeded):
    return TransactionPartnerFragment(
        withdrawal_state=withdrawal_state_succeeded,
    )


@pytest.fixture()
def star_transaction(transaction_partner_user, transaction_partner_fragment):
    return StarTransaction(
        id="1",
        amount=1,
        date=to_timestamp(datetime.datetime.utcnow()),
        source=transaction_partner_user,
        receiver=transaction_partner_fragment,
    )


class TestStarTransactionBase:
    id = "2"
    amount = 2
    date = to_timestamp(datetime.datetime.utcnow())
    source = TransactionPartnerUser(
        user=User(
            id=2,
            is_bot=False,
            first_name="first_name",
        ),
    )
    receiver = TransactionPartnerOther()


class TestStarTransactionWithoutRequest(TestStarTransactionBase):
    def test_slot_behaviour(self, star_transaction):
        inst = star_transaction
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "source": self.source.to_dict(),
            "receiver": self.receiver.to_dict(),
        }
        st = StarTransaction.de_json(json_dict, bot)
        assert st.id == self.id
        assert st.amount == self.amount
        assert st.date == from_timestamp(self.date)
        assert st.source == self.source
        assert st.receiver == self.receiver

    def test_de_json_star_transaction_localization(self, star_transaction, tz_bot, bot, raw_bot):
        json_dict = star_transaction.to_dict()
        st_raw = StarTransaction.de_json(json_dict, raw_bot)
        st_bot = StarTransaction.de_json(json_dict, bot)
        st_tz = StarTransaction.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        st_offset = st_tz.date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(st_tz.date.replace(tzinfo=None))

        assert st_raw.date.tzinfo == UTC
        assert st_bot.date.tzinfo == UTC
        assert st_offset == tz_bot_offset

    def test_to_dict(self, star_transaction):
        expected_dict = {
            "id": "1",
            "amount": 1,
            "date": star_transaction.date,
            "source": star_transaction.source.to_dict(),
            "receiver": star_transaction.receiver.to_dict(),
        }
        assert star_transaction.to_dict() == expected_dict

    def test_equality(self):
        a = StarTransaction(
            id=self.id,
            amount=self.amount,
            date=self.date,
            source=self.source,
            receiver=self.receiver,
        )
        b = StarTransaction(
            id=self.id,
            amount=self.amount,
            date=self.date,
            source=self.source,
            receiver=self.receiver,
        )
        c = StarTransaction(
            id="3",
            amount=3,
            date=to_timestamp(datetime.datetime.utcnow()),
            source=TransactionPartnerUser(
                user=User(
                    id=3,
                    is_bot=False,
                    first_name="first_name",
                ),
            ),
            receiver=TransactionPartnerOther(),
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)
