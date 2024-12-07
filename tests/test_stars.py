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
from collections.abc import Sequence
from copy import deepcopy

import pytest

from telegram import (
    Chat,
    Dice,
    Gift,
    PaidMediaPhoto,
    PhotoSize,
    RevenueWithdrawalState,
    RevenueWithdrawalStateFailed,
    RevenueWithdrawalStatePending,
    RevenueWithdrawalStateSucceeded,
    StarTransaction,
    StarTransactions,
    Sticker,
    TelegramObject,
    TransactionPartner,
    TransactionPartnerFragment,
    TransactionPartnerOther,
    TransactionPartnerTelegramAds,
    TransactionPartnerTelegramApi,
    TransactionPartnerUser,
    User,
)
from telegram._payment.stars import AffiliateInfo, TransactionPartnerAffiliateProgram
from telegram._utils.datetime import UTC, from_timestamp, to_timestamp
from telegram.constants import RevenueWithdrawalStateType, TransactionPartnerType
from tests.auxil.slots import mro_slots


def withdrawal_state_succeeded():
    return RevenueWithdrawalStateSucceeded(
        date=datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
        url="url",
    )


@pytest.fixture
def withdrawal_state_failed():
    return RevenueWithdrawalStateFailed()


@pytest.fixture
def withdrawal_state_pending():
    return RevenueWithdrawalStatePending()


def transaction_partner_user():
    return TransactionPartnerUser(
        user=User(id=1, is_bot=False, first_name="first_name", username="username"),
        affiliate=AffiliateInfo(
            affiliate_user=User(id=2, is_bot=True, first_name="first_name", username="username"),
            affiliate_chat=Chat(id=3, type="private", title="title"),
            commission_per_mille=1,
            amount=2,
            nanostar_amount=3,
        ),
        invoice_payload="payload",
        paid_media=[
            PaidMediaPhoto(
                photo=[
                    PhotoSize(
                        file_id="file_id", width=1, height=1, file_unique_id="file_unique_id"
                    )
                ]
            )
        ],
        paid_media_payload="payload",
        subscription_period=datetime.timedelta(days=1),
        gift=Gift(
            id="some_id",
            sticker=Sticker(
                file_id="file_id",
                file_unique_id="file_unique_id",
                width=512,
                height=512,
                is_animated=False,
                is_video=False,
                type="regular",
            ),
            star_count=5,
            total_count=10,
            remaining_count=5,
        ),
    )


def transaction_partner_affiliate_program():
    return TransactionPartnerAffiliateProgram(
        sponsor_user=User(id=1, is_bot=True, first_name="first_name", username="username"),
        commission_per_mille=42,
    )


def transaction_partner_fragment():
    return TransactionPartnerFragment(
        withdrawal_state=withdrawal_state_succeeded(),
    )


def star_transaction():
    return StarTransaction(
        id="1",
        amount=1,
        nanostar_amount=365,
        date=to_timestamp(datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)),
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


@pytest.fixture(
    scope="module",
    params=[
        TransactionPartner.AFFILIATE_PROGRAM,
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.TELEGRAM_ADS,
        TransactionPartner.TELEGRAM_API,
        TransactionPartner.USER,
    ],
)
def tp_scope_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        TransactionPartnerAffiliateProgram,
        TransactionPartnerFragment,
        TransactionPartnerOther,
        TransactionPartnerTelegramAds,
        TransactionPartnerTelegramApi,
        TransactionPartnerUser,
    ],
    ids=[
        TransactionPartner.AFFILIATE_PROGRAM,
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.TELEGRAM_ADS,
        TransactionPartner.TELEGRAM_API,
        TransactionPartner.USER,
    ],
)
def tp_scope_class(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        (TransactionPartnerAffiliateProgram, TransactionPartner.AFFILIATE_PROGRAM),
        (TransactionPartnerFragment, TransactionPartner.FRAGMENT),
        (TransactionPartnerOther, TransactionPartner.OTHER),
        (TransactionPartnerTelegramAds, TransactionPartner.TELEGRAM_ADS),
        (TransactionPartnerTelegramApi, TransactionPartner.TELEGRAM_API),
        (TransactionPartnerUser, TransactionPartner.USER),
    ],
    ids=[
        TransactionPartner.AFFILIATE_PROGRAM,
        TransactionPartner.FRAGMENT,
        TransactionPartner.OTHER,
        TransactionPartner.TELEGRAM_ADS,
        TransactionPartner.TELEGRAM_API,
        TransactionPartner.USER,
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
            "invoice_payload": TransactionPartnerTestBase.invoice_payload,
            "withdrawal_state": TransactionPartnerTestBase.withdrawal_state.to_dict(),
            "user": TransactionPartnerTestBase.user.to_dict(),
            "affiliate": TransactionPartnerTestBase.affiliate.to_dict(),
            "request_count": TransactionPartnerTestBase.request_count,
            "sponsor_user": TransactionPartnerTestBase.sponsor_user.to_dict(),
            "commission_per_mille": TransactionPartnerTestBase.commission_per_mille,
            "gift": TransactionPartnerTestBase.gift.to_dict(),
            "paid_media": [m.to_dict() for m in TransactionPartnerTestBase.paid_media],
            "paid_media_payload": TransactionPartnerTestBase.paid_media_payload,
            "subscription_period": TransactionPartnerTestBase.subscription_period.total_seconds(),
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
            "date": to_timestamp(RevenueWithdrawalStateTestBase.date),
            "url": RevenueWithdrawalStateTestBase.url,
        },
        bot=None,
    )


class StarTransactionTestBase:
    id = "2"
    amount = 2
    nanostar_amount = 365
    date = to_timestamp(datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC))
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


class TransactionPartnerTestBase:
    withdrawal_state = withdrawal_state_succeeded()
    user = transaction_partner_user().user
    affiliate = transaction_partner_user().affiliate
    invoice_payload = "payload"
    request_count = 42
    sponsor_user = transaction_partner_affiliate_program().sponsor_user
    commission_per_mille = transaction_partner_affiliate_program().commission_per_mille
    gift = transaction_partner_user().gift
    paid_media = transaction_partner_user().paid_media
    paid_media_payload = transaction_partner_user().paid_media_payload
    subscription_period = transaction_partner_user().subscription_period


class TestTransactionPartnerWithoutRequest(TransactionPartnerTestBase):
    def test_slot_behaviour(self, transaction_partner):
        inst = transaction_partner
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, tp_scope_class_and_type):
        cls = tp_scope_class_and_type[0]
        type_ = tp_scope_class_and_type[1]

        json_dict = {
            "type": type_,
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
            "affiliate": self.affiliate.to_dict(),
            "request_count": self.request_count,
            "sponsor_user": self.sponsor_user.to_dict(),
            "commission_per_mille": self.commission_per_mille,
        }
        tp = TransactionPartner.de_json(json_dict, offline_bot)
        assert set(tp.api_kwargs.keys()) == {
            "user",
            "affiliate",
            "withdrawal_state",
            "invoice_payload",
            "request_count",
            "sponsor_user",
            "commission_per_mille",
        } - set(cls.__slots__)

        assert isinstance(tp, TransactionPartner)
        assert type(tp) is cls
        assert tp.type == type_
        for key in json_dict:
            if key in cls.__slots__:
                assert getattr(tp, key) == getattr(self, key)

        assert cls.de_json(None, offline_bot) is None
        assert TransactionPartner.de_json({}, offline_bot) is None

    def test_de_json_invalid_type(self, offline_bot):
        json_dict = {
            "type": "invalid",
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
            "affiliate": self.affiliate.to_dict(),
            "request_count": self.request_count,
            "sponsor_user": self.sponsor_user.to_dict(),
            "commission_per_mille": self.commission_per_mille,
        }
        tp = TransactionPartner.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
            "affiliate": self.affiliate.to_dict(),
            "invoice_payload": self.invoice_payload,
            "request_count": self.request_count,
            "sponsor_user": self.sponsor_user.to_dict(),
            "commission_per_mille": self.commission_per_mille,
        }

        assert type(tp) is TransactionPartner
        assert tp.type == "invalid"

    def test_de_json_subclass(self, tp_scope_class, offline_bot):
        """This makes sure that e.g. TransactionPartnerUser(data) never returns a
        TransactionPartnerFragment instance."""
        json_dict = {
            "type": "invalid",
            "invoice_payload": self.invoice_payload,
            "withdrawal_state": self.withdrawal_state.to_dict(),
            "user": self.user.to_dict(),
            "affiliate": self.affiliate.to_dict(),
            "request_count": self.request_count,
            "commission_per_mille": self.commission_per_mille,
        }
        assert type(tp_scope_class.de_json(json_dict, offline_bot)) is tp_scope_class

    def test_to_dict(self, transaction_partner):
        tp_dict = transaction_partner.to_dict()

        assert isinstance(tp_dict, dict)
        assert tp_dict["type"] == transaction_partner.type
        for attr in transaction_partner.__slots__:
            attribute = getattr(transaction_partner, attr)
            if isinstance(attribute, TelegramObject):
                assert tp_dict[attr] == attribute.to_dict()
            elif not isinstance(attribute, str) and isinstance(attribute, Sequence):
                assert tp_dict[attr] == [a.to_dict() for a in attribute]
            elif isinstance(attribute, datetime.timedelta):
                assert tp_dict[attr] == attribute.total_seconds()
            else:
                assert tp_dict[attr] == attribute

    def test_type_enum_conversion(self):
        assert type(TransactionPartner("other").type) is TransactionPartnerType
        assert TransactionPartner("unknown").type == "unknown"

    def test_equality(self, transaction_partner, offline_bot):
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
            f = c.__class__.de_json(json_dict, offline_bot)

            assert c != f
            assert hash(c) != hash(f)

        if hasattr(c, "request_count"):
            json_dict = c.to_dict()
            json_dict["request_count"] = 1
            f = c.__class__.de_json(json_dict, offline_bot)

            assert c != f
            assert hash(c) != hash(f)


class TestTransactionPartnerUserWithoutRequest(TransactionPartnerTestBase):
    def test_de_json_required(self, offline_bot):
        json_dict = {
            "user": transaction_partner_user().user.to_dict(),
        }
        tp = TransactionPartnerUser.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.user == transaction_partner_user().user

        # This test is here mainly to check that the below cases work
        assert tp.subscription_period is None
        assert tp.gift is None


class RevenueWithdrawalStateTestBase:
    date = datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
    url = "url"


class TestRevenueWithdrawalStateWithoutRequest(RevenueWithdrawalStateTestBase):
    def test_slot_behaviour(self, revenue_withdrawal_state):
        inst = revenue_withdrawal_state
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, rws_scope_class_and_type):
        cls = rws_scope_class_and_type[0]
        type_ = rws_scope_class_and_type[1]

        json_dict = {
            "type": type_,
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        rws = RevenueWithdrawalState.de_json(json_dict, offline_bot)
        assert set(rws.api_kwargs.keys()) == {"date", "url"} - set(cls.__slots__)

        assert isinstance(rws, RevenueWithdrawalState)
        assert type(rws) is cls
        assert rws.type == type_
        if "date" in cls.__slots__:
            assert rws.date == self.date
        if "url" in cls.__slots__:
            assert rws.url == self.url

        assert cls.de_json(None, offline_bot) is None
        assert RevenueWithdrawalState.de_json({}, offline_bot) is None

    def test_de_json_invalid_type(self, offline_bot):
        json_dict = {
            "type": "invalid",
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        rws = RevenueWithdrawalState.de_json(json_dict, offline_bot)
        assert rws.api_kwargs == {
            "date": to_timestamp(self.date),
            "url": self.url,
        }

        assert type(rws) is RevenueWithdrawalState
        assert rws.type == "invalid"

    def test_de_json_subclass(self, rws_scope_class, offline_bot):
        """This makes sure that e.g. RevenueWithdrawalState(data) never returns a
        RevenueWithdrawalStateFailed instance."""
        json_dict = {
            "type": "invalid",
            "date": to_timestamp(self.date),
            "url": self.url,
        }
        assert type(rws_scope_class.de_json(json_dict, offline_bot)) is rws_scope_class

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

    def test_equality(self, revenue_withdrawal_state, offline_bot):
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
            f = c.__class__.de_json(json_dict, offline_bot)

            assert c == f
            assert hash(c) == hash(f)

        if hasattr(c, "date"):
            json_dict = c.to_dict()
            json_dict["date"] = to_timestamp(datetime.datetime.utcnow())
            f = c.__class__.de_json(json_dict, offline_bot)

            assert c != f
            assert hash(c) != hash(f)


@pytest.fixture
def affiliate_info():
    return AffiliateInfo(
        affiliate_user=AffiliateInfoTestBase.affiliate_user,
        affiliate_chat=AffiliateInfoTestBase.affiliate_chat,
        commission_per_mille=AffiliateInfoTestBase.commission_per_mille,
        amount=AffiliateInfoTestBase.amount,
        nanostar_amount=AffiliateInfoTestBase.nanostar_amount,
    )


class AffiliateInfoTestBase:
    affiliate_user = User(id=1, is_bot=True, first_name="affiliate_user", username="username")
    affiliate_chat = Chat(id=2, type="private", title="affiliate_chat")
    commission_per_mille = 13
    amount = 14
    nanostar_amount = -42


class TestAffiliateInfoWithoutRequest(AffiliateInfoTestBase):
    def test_slot_behaviour(self, affiliate_info):
        inst = affiliate_info
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "affiliate_user": self.affiliate_user.to_dict(),
            "affiliate_chat": self.affiliate_chat.to_dict(),
            "commission_per_mille": self.commission_per_mille,
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
        }
        ai = AffiliateInfo.de_json(json_dict, offline_bot)
        assert ai.api_kwargs == {}
        assert ai.affiliate_user == self.affiliate_user
        assert ai.affiliate_chat == self.affiliate_chat
        assert ai.commission_per_mille == self.commission_per_mille
        assert ai.amount == self.amount
        assert ai.nanostar_amount == self.nanostar_amount

        assert AffiliateInfo.de_json(None, offline_bot) is None
        assert AffiliateInfo.de_json({}, offline_bot) is None

    def test_to_dict(self, affiliate_info):
        ai_dict = affiliate_info.to_dict()

        assert isinstance(ai_dict, dict)
        assert ai_dict["affiliate_user"] == affiliate_info.affiliate_user.to_dict()
        assert ai_dict["affiliate_chat"] == affiliate_info.affiliate_chat.to_dict()
        assert ai_dict["commission_per_mille"] == affiliate_info.commission_per_mille
        assert ai_dict["amount"] == affiliate_info.amount
        assert ai_dict["nanostar_amount"] == affiliate_info.nanostar_amount

    def test_equality(self, affiliate_info, offline_bot):
        a = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        b = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        c = AffiliateInfo(
            affiliate_user=User(id=3, is_bot=True, first_name="first_name", username="username"),
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        d = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=Chat(id=3, type="private", title="title"),
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        e = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=1,
            amount=self.amount,
            nanostar_amount=self.nanostar_amount,
        )
        f = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=1,
            nanostar_amount=self.nanostar_amount,
        )
        g = AffiliateInfo(
            affiliate_user=self.affiliate_user,
            affiliate_chat=self.affiliate_chat,
            commission_per_mille=self.commission_per_mille,
            amount=self.amount,
            nanostar_amount=1,
        )
        h = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)

        assert a != g
        assert hash(a) != hash(g)

        assert a != h
        assert hash(a) != hash(h)
