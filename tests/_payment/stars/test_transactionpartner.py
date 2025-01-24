#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
    AffiliateInfo,
    Gift,
    PaidMediaVideo,
    RevenueWithdrawalStatePending,
    Sticker,
    TransactionPartner,
    TransactionPartnerAffiliateProgram,
    TransactionPartnerFragment,
    TransactionPartnerOther,
    TransactionPartnerTelegramAds,
    TransactionPartnerTelegramApi,
    TransactionPartnerUser,
    User,
    Video,
)
from telegram.constants import TransactionPartnerType
from tests.auxil.slots import mro_slots


@pytest.fixture
def transaction_partner():
    return TransactionPartner(TransactionPartnerTestBase.type)


class TransactionPartnerTestBase:
    type = TransactionPartnerType.AFFILIATE_PROGRAM
    commission_per_mille = 42
    sponsor_user = User(
        id=1,
        is_bot=False,
        first_name="sponsor",
        last_name="user",
    )
    withdrawal_state = RevenueWithdrawalStatePending()
    user = User(
        id=2,
        is_bot=False,
        first_name="user",
        last_name="user",
    )
    invoice_payload = "invoice_payload"
    paid_media = (
        PaidMediaVideo(
            video=Video(
                file_id="file_id",
                file_unique_id="file_unique_id",
                width=10,
                height=10,
                duration=10,
            )
        ),
    )
    paid_media_payload = "paid_media_payload"
    subscription_period = dtm.timedelta(days=1)
    gift = Gift(
        id="gift_id",
        sticker=Sticker(
            file_id="file_id",
            file_unique_id="file_unique_id",
            width=10,
            height=10,
            is_animated=False,
            is_video=False,
            type="type",
        ),
        total_count=42,
        remaining_count=42,
        star_count=42,
    )
    affiliate = AffiliateInfo(
        commission_per_mille=42,
        amount=42,
    )
    request_count = 42


class TestTransactionPartnerWithoutRequest(TransactionPartnerTestBase):
    def test_slot_behaviour(self, transaction_partner):
        inst = transaction_partner
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, transaction_partner):
        assert type(TransactionPartner("affiliate_program").type) is TransactionPartnerType
        assert TransactionPartner("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        data = {"type": "unknown"}
        transaction_partner = TransactionPartner.de_json(data, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "unknown"

    @pytest.mark.parametrize(
        ("tp_type", "subclass"),
        [
            ("affiliate_program", TransactionPartnerAffiliateProgram),
            ("fragment", TransactionPartnerFragment),
            ("user", TransactionPartnerUser),
            ("telegram_ads", TransactionPartnerTelegramAds),
            ("telegram_api", TransactionPartnerTelegramApi),
            ("other", TransactionPartnerOther),
        ],
    )
    def test_subclass(self, offline_bot, tp_type, subclass):
        json_dict = {
            "type": tp_type,
            "commission_per_mille": self.commission_per_mille,
            "user": self.user.to_dict(),
            "request_count": self.request_count,
        }
        tp = TransactionPartner.de_json(json_dict, offline_bot)

        assert type(tp) is subclass
        assert set(tp.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert tp.type == tp_type

    def test_to_dict(self, transaction_partner):
        data = transaction_partner.to_dict()
        assert data == {"type": self.type}

    def test_equality(self, transaction_partner):
        a = transaction_partner
        b = TransactionPartner(self.type)
        c = TransactionPartner("unknown")
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_affiliate_program():
    return TransactionPartnerAffiliateProgram(
        commission_per_mille=TransactionPartnerTestBase.commission_per_mille,
        sponsor_user=TransactionPartnerTestBase.sponsor_user,
    )


class TestTransactionPartnerAffiliateProgramWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.AFFILIATE_PROGRAM

    def test_slot_behaviour(self, transaction_partner_affiliate_program):
        inst = transaction_partner_affiliate_program
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "commission_per_mille": self.commission_per_mille,
            "sponsor_user": self.sponsor_user.to_dict(),
        }
        tp = TransactionPartnerAffiliateProgram.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "affiliate_program"
        assert tp.commission_per_mille == self.commission_per_mille
        assert tp.sponsor_user == self.sponsor_user

    def test_to_dict(self, transaction_partner_affiliate_program):
        json_dict = transaction_partner_affiliate_program.to_dict()
        assert json_dict["type"] == self.type
        assert json_dict["commission_per_mille"] == self.commission_per_mille
        assert json_dict["sponsor_user"] == self.sponsor_user.to_dict()

    def test_equality(self, transaction_partner_affiliate_program):
        a = transaction_partner_affiliate_program
        b = TransactionPartnerAffiliateProgram(
            commission_per_mille=self.commission_per_mille,
        )
        c = TransactionPartnerAffiliateProgram(
            commission_per_mille=0,
        )
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_fragment():
    return TransactionPartnerFragment(
        withdrawal_state=TransactionPartnerTestBase.withdrawal_state,
    )


class TestTransactionPartnerFragmentWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.FRAGMENT

    def test_slot_behaviour(self, transaction_partner_fragment):
        inst = transaction_partner_fragment
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"withdrawal_state": self.withdrawal_state.to_dict()}
        tp = TransactionPartnerFragment.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "fragment"
        assert tp.withdrawal_state == self.withdrawal_state

    def test_to_dict(self, transaction_partner_fragment):
        json_dict = transaction_partner_fragment.to_dict()
        assert json_dict["type"] == self.type
        assert json_dict["withdrawal_state"] == self.withdrawal_state.to_dict()

    def test_equality(self, transaction_partner_fragment):
        a = transaction_partner_fragment
        b = TransactionPartnerFragment(withdrawal_state=self.withdrawal_state)
        c = TransactionPartnerFragment(withdrawal_state=None)
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_user():
    return TransactionPartnerUser(
        user=TransactionPartnerTestBase.user,
        invoice_payload=TransactionPartnerTestBase.invoice_payload,
        paid_media=TransactionPartnerTestBase.paid_media,
        paid_media_payload=TransactionPartnerTestBase.paid_media_payload,
        subscription_period=TransactionPartnerTestBase.subscription_period,
    )


class TestTransactionPartnerUserWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.USER

    def test_slot_behaviour(self, transaction_partner_user):
        inst = transaction_partner_user
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "user": self.user.to_dict(),
            "invoice_payload": self.invoice_payload,
            "paid_media": [pm.to_dict() for pm in self.paid_media],
            "paid_media_payload": self.paid_media_payload,
            "subscription_period": self.subscription_period.total_seconds(),
        }
        tp = TransactionPartnerUser.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "user"
        assert tp.user == self.user
        assert tp.invoice_payload == self.invoice_payload
        assert tp.paid_media == self.paid_media
        assert tp.paid_media_payload == self.paid_media_payload
        assert tp.subscription_period == self.subscription_period

    def test_to_dict(self, transaction_partner_user):
        json_dict = transaction_partner_user.to_dict()
        assert json_dict["type"] == self.type
        assert json_dict["user"] == self.user.to_dict()
        assert json_dict["invoice_payload"] == self.invoice_payload
        assert json_dict["paid_media"] == [pm.to_dict() for pm in self.paid_media]
        assert json_dict["paid_media_payload"] == self.paid_media_payload
        assert json_dict["subscription_period"] == self.subscription_period.total_seconds()

    def test_equality(self, transaction_partner_user):
        a = transaction_partner_user
        b = TransactionPartnerUser(
            user=self.user,
        )
        c = TransactionPartnerUser(
            user=User(id=1, is_bot=False, first_name="user", last_name="user"),
        )
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_other():
    return TransactionPartnerOther()


class TestTransactionPartnerOtherWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.OTHER

    def test_slot_behaviour(self, transaction_partner_other):
        inst = transaction_partner_other
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {}
        tp = TransactionPartnerOther.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "other"

    def test_to_dict(self, transaction_partner_other):
        json_dict = transaction_partner_other.to_dict()
        assert json_dict == {"type": self.type}

    def test_equality(self, transaction_partner_other):
        a = transaction_partner_other
        b = TransactionPartnerOther()
        c = TransactionPartnerOther()
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_telegram_ads():
    return TransactionPartnerTelegramAds()


class TestTransactionPartnerTelegramAdsWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.TELEGRAM_ADS

    def test_slot_behaviour(self, transaction_partner_telegram_ads):
        inst = transaction_partner_telegram_ads
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {}
        tp = TransactionPartnerTelegramAds.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "telegram_ads"

    def test_to_dict(self, transaction_partner_telegram_ads):
        json_dict = transaction_partner_telegram_ads.to_dict()
        assert json_dict == {"type": self.type}

    def test_equality(self, transaction_partner_telegram_ads):
        a = transaction_partner_telegram_ads
        b = TransactionPartnerTelegramAds()
        c = TransactionPartnerTelegramAds()
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def transaction_partner_telegram_api():
    return TransactionPartnerTelegramApi(
        request_count=TransactionPartnerTestBase.request_count,
    )


class TestTransactionPartnerTelegramApiWithoutRequest(TransactionPartnerTestBase):
    type = TransactionPartnerType.TELEGRAM_API

    def test_slot_behaviour(self, transaction_partner_telegram_api):
        inst = transaction_partner_telegram_api
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"request_count": self.request_count}
        tp = TransactionPartnerTelegramApi.de_json(json_dict, offline_bot)
        assert tp.api_kwargs == {}
        assert tp.type == "telegram_api"
        assert tp.request_count == self.request_count

    def test_to_dict(self, transaction_partner_telegram_api):
        json_dict = transaction_partner_telegram_api.to_dict()
        assert json_dict["type"] == self.type
        assert json_dict["request_count"] == self.request_count

    def test_equality(self, transaction_partner_telegram_api):
        a = transaction_partner_telegram_api
        b = TransactionPartnerTelegramApi(
            request_count=self.request_count,
        )
        c = TransactionPartnerTelegramApi(
            request_count=0,
        )
        d = User(id=1, is_bot=False, first_name="user", last_name="user")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
