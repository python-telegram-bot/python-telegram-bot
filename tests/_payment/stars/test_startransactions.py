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
import datetime as dtm

import pytest

from telegram import (
    StarTransaction,
    StarTransactions,
    TransactionPartnerOther,
    TransactionPartnerUser,
    User,
)
from telegram._utils.datetime import UTC, from_timestamp, to_timestamp
from tests._payment.stars.test_stars import transaction_partner_fragment, transaction_partner_user
from tests.auxil.slots import mro_slots


def star_transaction():
    return StarTransaction(
        id="1",
        amount=1,
        nanostar_amount=365,
        date=to_timestamp(dtm.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)),
        source=transaction_partner_user(),
        receiver=transaction_partner_fragment(),
    )


@pytest.fixture
def star_transactions():
    return StarTransactions(
        transactions=[
            star_transaction(),
            star_transaction(),
        ]
    )


class StarTransactionTestBase:
    id = "2"
    amount = 2
    nanostar_amount = 365
    date = to_timestamp(dtm.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC))
    source = TransactionPartnerUser(
        user=User(
            id=2,
            is_bot=False,
            first_name="first_name",
        ),
    )
    receiver = TransactionPartnerOther()


class TestStarTransactionWithoutRequest(StarTransactionTestBase):
    def test_slot_behaviour(self):
        inst = star_transaction()
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "id": self.id,
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
            "date": self.date,
            "source": self.source.to_dict(),
            "receiver": self.receiver.to_dict(),
        }
        st = StarTransaction.de_json(json_dict, offline_bot)
        st_none = StarTransaction.de_json(None, offline_bot)
        assert st.api_kwargs == {}
        assert st.id == self.id
        assert st.amount == self.amount
        assert st.nanostar_amount == self.nanostar_amount
        assert st.date == from_timestamp(self.date)
        assert st.source == self.source
        assert st.receiver == self.receiver
        assert st_none is None

    def test_de_json_star_transaction_localization(self, tz_bot, offline_bot, raw_bot):
        json_dict = star_transaction().to_dict()
        st_raw = StarTransaction.de_json(json_dict, raw_bot)
        st_bot = StarTransaction.de_json(json_dict, offline_bot)
        st_tz = StarTransaction.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        st_offset = st_tz.date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(st_tz.date.replace(tzinfo=None))

        assert st_raw.date.tzinfo == UTC
        assert st_bot.date.tzinfo == UTC
        assert st_offset == tz_bot_offset

    def test_to_dict(self):
        st = star_transaction()
        expected_dict = {
            "id": "1",
            "amount": 1,
            "nanostar_amount": 365,
            "date": st.date,
            "source": st.source.to_dict(),
            "receiver": st.receiver.to_dict(),
        }
        assert st.to_dict() == expected_dict

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
            date=None,
            source=self.source,
            receiver=self.receiver,
        )
        c = StarTransaction(
            id="3",
            amount=3,
            date=to_timestamp(dtm.datetime.utcnow()),
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


class StarTransactionsTestBase:
    transactions = [star_transaction(), star_transaction()]


class TestStarTransactionsWithoutRequest(StarTransactionsTestBase):
    def test_slot_behaviour(self, star_transactions):
        inst = star_transactions
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "transactions": [t.to_dict() for t in self.transactions],
        }
        st = StarTransactions.de_json(json_dict, offline_bot)
        st_none = StarTransactions.de_json(None, offline_bot)
        assert st.api_kwargs == {}
        assert st.transactions == tuple(self.transactions)
        assert st_none is None

    def test_to_dict(self, star_transactions):
        expected_dict = {
            "transactions": [t.to_dict() for t in self.transactions],
        }
        assert star_transactions.to_dict() == expected_dict

    def test_equality(self):
        a = StarTransactions(
            transactions=self.transactions,
        )
        b = StarTransactions(
            transactions=self.transactions,
        )
        c = StarTransactions(
            transactions=[star_transaction()],
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)
