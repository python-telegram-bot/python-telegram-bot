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
from copy import deepcopy

import pytest

from telegram import (
    Dice,
    RevenueWithdrawalState,
    RevenueWithdrawalStateFailed,
    RevenueWithdrawalStatePending,
    RevenueWithdrawalStateSucceeded,
    StarTransaction,
    StarTransactions,
    TransactionPartner,
    TransactionPartnerFragment,
    TransactionPartnerOther,
    TransactionPartnerTelegramAds,
    TransactionPartnerUser,
    User,
)
from telegram._utils.datetime import UTC, from_timestamp, to_timestamp
from telegram.constants import RevenueWithdrawalStateType, TransactionPartnerType
from tests.auxil.slots import mro_slots


def withdrawal_state_succeeded():
    return RevenueWithdrawalStateSucceeded(
        date=datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
        url="url",
    )


@pytest.fixture()
def withdrawal_state_failed():
    return RevenueWithdrawalStateFailed()


@pytest.fixture()
def withdrawal_state_pending():
    return RevenueWithdrawalStatePending()


def transaction_partner_user():
    return TransactionPartnerUser(
        user=User(id=1, is_bot=False, first_name="first_name", username="username"),
    )


@pytest.fixture()
def transaction_partner_other():
    return TransactionPartnerOther()


def transaction_partner_fragment():
    return TransactionPartnerFragment(
        withdrawal_state=withdrawal_state_succeeded(),
    )


def star_transaction():
    return StarTransaction(
        id="1",
        amount=1,
        date=to_timestamp(datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)),
        source=transaction_partner_user(),
        receiver=transaction_partner_fragment(),
    )


@pytest.fixture()
def star_transactions():
    return StarTransactions(
        transactions=[
            star_transaction(),
            star_transaction(),
        ]
    )


@pytest.fixture(
    scope="module",
    params=[
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.USER,
        TransactionPartner.TELEGRAM_ADS,
    ],
)
def tp_scope_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        TransactionPartnerFragment,
        TransactionPartnerOther,
        TransactionPartnerUser,
        TransactionPartnerTelegramAds,
    ],
    ids=[
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.USER,
        TransactionPartner.TELEGRAM_ADS,
    ],
)
def tp_scope_class(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        (TransactionPartnerFragment, TransactionPartner.FRAGMENT),
        (TransactionPartnerOther, TransactionPartner.OTHER),
        (TransactionPartnerUser, TransactionPartner.USER),
        (TransactionPartnerTelegramAds, TransactionPartner.TELEGRAM_ADS),
    ],
    ids=[
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.USER,
        TransactionPartner.TELEGRAM_ADS,
    ],
)
def tp_scope_class_and_type(request):
    return request.param


@pytest.fixture(scope="module")
def transaction_partner(tp_scope_class_and_type):
    # We use de_json here so that we don't have to worry about which class gets which arguments
    return tp_scope_class_and_type[0].de_json(
        {
            "type": tp_scope_class_and_type[1],
            "invoice_payload": TestTransactionPartnerBase.invoice_payload,
            "withdrawal_state": TestTransactionPartnerBase.withdrawal_state.to_dict(),
            "user": TestTransactionPartnerBase.user.to_dict(),
        },
        bot=None,
    )


@pytest.fixture(
    scope="module",
    params=[
        RevenueWithdrawalState.FAILED,
        RevenueWithdrawalState.SUCCEEDED,
        RevenueWithdrawalState.PENDING,
    ],
)
def rws_scope_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        RevenueWithdrawalStateFailed,
        RevenueWithdrawalStateSucceeded,
        RevenueWithdrawalStatePending,
    ],
    ids=[
        RevenueWithdrawalState.FAILED,
        RevenueWithdrawalState.SUCCEEDED,
        RevenueWithdrawalState.PENDING,
    ],
)
def rws_scope_class(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        (RevenueWithdrawalStateFailed, RevenueWithdrawalState.FAILED),
        (RevenueWithdrawalStateSucceeded, RevenueWithdrawalState.SUCCEEDED),
        (RevenueWithdrawalStatePending, RevenueWithdrawalState.PENDING),
    ],
    ids=[
        RevenueWithdrawalState.FAILED,
        RevenueWithdrawalState.SUCCEEDED,
        RevenueWithdrawalState.PENDING,
    ],
)
def rws_scope_class_and_type(request):
    return request.param


@pytest.fixture(scope="module")
def revenue_withdrawal_state(rws_scope_class_and_type):
    # We use de_json here so that we don't have to worry about which class gets which arguments
    return rws_scope_class_and_type[0].de_json(
        {
            "type": rws_scope_class_and_type[1],
            "date": to_timestamp(TestRevenueWithdrawalStateBase.date),
            "url": TestRevenueWithdrawalStateBase.url,
        },
        bot=None,
    )


class TestStarTransactionBase:
    id = "2"
    amount = 2
    date = to_timestamp(datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC))
    source = TransactionPartnerUser(
        user=User(
            id=2,
            is_bot=False,
            first_name="first_name",
        ),
    )
    receiver = TransactionPartnerOther()


class TestStarTransactionWithoutRequest(TestStarTransactionBase):
    def test_slot_behaviour(self):
        inst = star_transaction()
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
        st_none = StarTransaction.de_json(None, bot)
        assert st.api_kwargs == {}
        assert st.id == self.id
        assert st.amount == self.amount
        assert st.date == from_timestamp(self.date)
        assert st.source == self.source
        assert st.receiver == self.receiver
        assert st_none is None

    def test_de_json_star_transaction_localization(self, tz_bot, bot, raw_bot):
        json_dict = star_transaction().to_dict()
        st_raw = StarTransaction.de_json(json_dict, raw_bot)
        st_bot = StarTransaction.de_json(json_dict, bot)
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


class TestStarTransactionsBase:
    transactions = [star_transaction(), star_transaction()]


class TestStarTransactionsWithoutRequest(TestStarTransactionsBase):
    def test_slot_behaviour(self, star_transactions):
        inst = star_transactions
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "transactions": [t.to_dict() for t in self.transactions],
        }
        st = StarTransactions.de_json(json_dict, bot)
        st_none = StarTransactions.de_json(None, bot)
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


class TestTransactionPartnerBase:
    withdrawal_state = withdrawal_state_succeeded()
    user = transaction_partner_user().user
    invoice_payload = "payload"


class TestTransactionPartnerWithoutRequest(TestTransactionPartnerBase):
    def test_slot_behaviour(self, transaction_partner):
        inst = transaction_partner
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, tp_scope_class_and_type):
        cls = tp_scope_class_and_type[0]
        type_ = tp_scope_class_and_type[1]

        json_dict = {
            "type": type_,
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
        }
        tp = TransactionPartner.de_json(json_dict, bot)
        assert set(tp.api_kwargs.keys()) == {"user", "withdrawal_state", "invoice_payload"} - set(
            cls.__slots__
        )

        assert isinstance(tp, TransactionPartner)
        assert type(tp) is cls
        assert tp.type == type_
        if "withdrawal_state" in cls.__slots__:
            assert tp.withdrawal_state == self.withdrawal_state
        if "user" in cls.__slots__:
            assert tp.user == self.user
            assert tp.invoice_payload == self.invoice_payload

        assert cls.de_json(None, bot) is None
        assert TransactionPartner.de_json({}, bot) is None

    def test_de_json_invalid_type(self, bot):
        json_dict = {
            "type": "invalid",
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
        }
        tp = TransactionPartner.de_json(json_dict, bot)
        assert tp.api_kwargs == {
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
            "invoice_payload": self.invoice_payload,
        }

        assert type(tp) is TransactionPartner
        assert tp.type == "invalid"

    def test_de_json_subclass(self, tp_scope_class, bot):
        """This makes sure that e.g. TransactionPartnerUser(data) never returns a
        TransactionPartnerFragment instance."""
        json_dict = {
            "type": "invalid",
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
        }
        assert type(tp_scope_class.de_json(json_dict, bot)) is tp_scope_class

    def test_to_dict(self, transaction_partner):
        tp_dict = transaction_partner.to_dict()

        assert isinstance(tp_dict, dict)
        assert tp_dict["type"] == transaction_partner.type
        if hasattr(transaction_partner, "user"):
            assert tp_dict["user"] == transaction_partner.user.to_dict()
            assert tp_dict["invoice_payload"] == transaction_partner.invoice_payload
        if hasattr(transaction_partner, "withdrawal_state"):
            assert tp_dict["withdrawal_state"] == transaction_partner.withdrawal_state.to_dict()

    def test_type_enum_conversion(self):
        assert type(TransactionPartner("other").type) is TransactionPartnerType
        assert TransactionPartner("unknown").type == "unknown"

    def test_equality(self, transaction_partner, bot):
        a = TransactionPartner("base_type")
        b = TransactionPartner("base_type")
        c = transaction_partner
        d = deepcopy(transaction_partner)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        if hasattr(c, "user"):
            json_dict = c.to_dict()
            json_dict["user"] = User(2, "something", True).to_dict()
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)


class TestRevenueWithdrawalStateBase:
    date = datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
    url = "url"


class TestRevenueWithdrawalStateWithoutRequest(TestRevenueWithdrawalStateBase):
    def test_slot_behaviour(self, revenue_withdrawal_state):
        inst = revenue_withdrawal_state
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, rws_scope_class_and_type):
        cls = rws_scope_class_and_type[0]
        type_ = rws_scope_class_and_type[1]

        json_dict = {
            "type": type_,
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        rws = RevenueWithdrawalState.de_json(json_dict, bot)
        assert set(rws.api_kwargs.keys()) == {"date", "url"} - set(cls.__slots__)

        assert isinstance(rws, RevenueWithdrawalState)
        assert type(rws) is cls
        assert rws.type == type_
        if "date" in cls.__slots__:
            assert rws.date == self.date
        if "url" in cls.__slots__:
            assert rws.url == self.url

        assert cls.de_json(None, bot) is None
        assert RevenueWithdrawalState.de_json({}, bot) is None

    def test_de_json_invalid_type(self, bot):
        json_dict = {
            "type": "invalid",
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        rws = RevenueWithdrawalState.de_json(json_dict, bot)
        assert rws.api_kwargs == {
            "date": to_timestamp(self.date),
            "url": self.url,
        }

        assert type(rws) is RevenueWithdrawalState
        assert rws.type == "invalid"

    def test_de_json_subclass(self, rws_scope_class, bot):
        """This makes sure that e.g. RevenueWithdrawalState(data) never returns a
        RevenueWithdrawalStateFailed instance."""
        json_dict = {
            "type": "invalid",
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        assert type(rws_scope_class.de_json(json_dict, bot)) is rws_scope_class

    def test_to_dict(self, revenue_withdrawal_state):
        rws_dict = revenue_withdrawal_state.to_dict()

        assert isinstance(rws_dict, dict)
        assert rws_dict["type"] == revenue_withdrawal_state.type
        if hasattr(revenue_withdrawal_state, "date"):
            assert rws_dict["date"] == to_timestamp(revenue_withdrawal_state.date)
        if hasattr(revenue_withdrawal_state, "url"):
            assert rws_dict["url"] == revenue_withdrawal_state.url

    def test_type_enum_conversion(self):
        assert type(RevenueWithdrawalState("failed").type) is RevenueWithdrawalStateType
        assert RevenueWithdrawalState("unknown").type == "unknown"

    def test_equality(self, revenue_withdrawal_state, bot):
        a = RevenueWithdrawalState("base_type")
        b = RevenueWithdrawalState("base_type")
        c = revenue_withdrawal_state
        d = deepcopy(revenue_withdrawal_state)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        if hasattr(c, "url"):
            json_dict = c.to_dict()
            json_dict["url"] = "something"
            f = c.__class__.de_json(json_dict, bot)

            assert c == f
            assert hash(c) == hash(f)

        if hasattr(c, "date"):
            json_dict = c.to_dict()
            json_dict["date"] = to_timestamp(datetime.datetime.utcnow())
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)
