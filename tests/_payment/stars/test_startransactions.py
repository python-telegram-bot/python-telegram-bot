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
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


def star_transaction_factory():
    return StarTransaction(
        id=StarTransactionTestBase.id,
        amount=StarTransactionTestBase.amount,
        nanostar_amount=StarTransactionTestBase.nanostar_amount,
        date=from_timestamp(StarTransactionTestBase.date),
        source=StarTransactionTestBase.source,
        receiver=StarTransactionTestBase.receiver,
    )


@pytest.fixture
def star_transaction():
    return star_transaction_factory()


@pytest.fixture
def star_transactions():
    return StarTransactions(
        transactions=[
            star_transaction_factory(),
            star_transaction_factory(),
        ]
    )


class StarTransactionTestBase:
    id = "2"
    amount = 2
    nanostar_amount = 365
    date = to_timestamp(dtm.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC))
    source = TransactionPartnerUser(
        transaction_type="premium_purchase",
        user=User(
            id=2,
            is_bot=False,
            first_name="first_name",
        ),
    )
    receiver = TransactionPartnerOther()


class TestStarTransactionWithoutRequest(StarTransactionTestBase, DeserializationTestBase):
    de_json_class = StarTransaction

    @pytest.fixture
    def de_json_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
            "date": self.date,
            "source": self.source.to_dict(),
            "receiver": self.receiver.to_dict(),
        }

    def test_slot_behaviour(self, star_transaction):
        inst = star_transaction
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        st = StarTransaction.de_json(de_json_dict, offline_bot)
        assert st.api_kwargs == {}
        assert st.id == self.id
        assert st.amount == self.amount
        assert st.nanostar_amount == self.nanostar_amount
        assert st.date == from_timestamp(self.date)
        assert st.source == self.source
        assert st.receiver == self.receiver

    def test_to_dict(self, star_transaction):
        expected_dict = {
            "id": self.id,
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
            "date": self.date,
            "source": self.source.to_dict(),
            "receiver": self.receiver.to_dict(),
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
            date=None,
            source=self.source,
            receiver=self.receiver,
        )
        c = StarTransaction(
            id="3",
            amount=3,
            date=to_timestamp(dtm.datetime.now(dtm.UTC).replace(tzinfo=None)),
            source=TransactionPartnerUser(
                transaction_type="other_type",
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
    transactions = [star_transaction_factory(), star_transaction_factory()]


class TestStarTransactionsWithoutRequest(StarTransactionsTestBase, DeserializationTestBase):
    de_json_class = StarTransactions

    @pytest.fixture
    def de_json_dict(self):
        return {
            "transactions": [t.to_dict() for t in self.transactions],
        }

    def test_slot_behaviour(self, star_transactions):
        inst = star_transactions
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        st = StarTransactions.de_json(de_json_dict, offline_bot)
        assert st.api_kwargs == {}
        assert st.transactions == tuple(self.transactions)

    def test_to_dict(self, star_transactions):
        expected_dict = {
            "transactions": [t.to_dict() for t in self.transactions],
        }
        assert star_transactions.to_dict() == expected_dict

    def test_equality(self, star_transaction):
        a = StarTransactions(
            transactions=self.transactions,
        )
        b = StarTransactions(
            transactions=self.transactions,
        )
        c = StarTransactions(
            transactions=[star_transaction],
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)
