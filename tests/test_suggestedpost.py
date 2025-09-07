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
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import datetime as dtm

import pytest

from telegram import Dice
from telegram._chat import Chat
from telegram._message import Message
from telegram._payment.stars.staramount import StarAmount
from telegram._suggestedpost import (
    SuggestedPostApprovalFailed,
    SuggestedPostApproved,
    SuggestedPostDeclined,
    SuggestedPostInfo,
    SuggestedPostPaid,
    SuggestedPostParameters,
    SuggestedPostPrice,
    SuggestedPostRefunded,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import SuggestedPostInfoState
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def suggested_post_parameters():
    return SuggestedPostParameters(
        price=SuggestedPostParametersTestBase.price,
        send_date=SuggestedPostParametersTestBase.send_date,
    )


class SuggestedPostParametersTestBase:
    price = SuggestedPostPrice(currency="XTR", amount=100)
    send_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


class TestSuggestedPostParametersWithoutRequest(SuggestedPostParametersTestBase):
    def test_slot_behaviour(self, suggested_post_parameters):
        for attr in suggested_post_parameters.__slots__:
            assert getattr(suggested_post_parameters, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(suggested_post_parameters)) == len(
            set(mro_slots(suggested_post_parameters))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "price": self.price.to_dict(),
            "send_date": to_timestamp(self.send_date),
        }
        spp = SuggestedPostParameters.de_json(json_dict, offline_bot)
        assert spp.price == self.price
        assert spp.send_date == self.send_date
        assert spp.api_kwargs == {}

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "price": self.price.to_dict(),
            "send_date": to_timestamp(self.send_date),
        }

        spp_bot = SuggestedPostParameters.de_json(json_dict, offline_bot)
        spp_bot_raw = SuggestedPostParameters.de_json(json_dict, raw_bot)
        spp_bot_tz = SuggestedPostParameters.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        send_date_offset = spp_bot_tz.send_date.utcoffset()
        send_date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(
            spp_bot_tz.send_date.replace(tzinfo=None)
        )

        assert spp_bot.send_date.tzinfo == UTC
        assert spp_bot_raw.send_date.tzinfo == UTC
        assert send_date_offset_tz == send_date_offset

    def test_to_dict(self, suggested_post_parameters):
        spp_dict = suggested_post_parameters.to_dict()

        assert isinstance(spp_dict, dict)
        assert spp_dict["price"] == self.price.to_dict()
        assert spp_dict["send_date"] == to_timestamp(self.send_date)

    def test_equality(self, suggested_post_parameters):
        a = suggested_post_parameters
        b = SuggestedPostParameters(price=self.price, send_date=self.send_date)
        c = SuggestedPostParameters(
            price=self.price, send_date=self.send_date + dtm.timedelta(seconds=1)
        )
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_info():
    return SuggestedPostInfo(
        state=SuggestedPostInfoTestBase.state,
        price=SuggestedPostInfoTestBase.price,
        send_date=SuggestedPostInfoTestBase.send_date,
    )


class SuggestedPostInfoTestBase:
    state = SuggestedPostInfoState.PENDING
    price = SuggestedPostPrice(currency="XTR", amount=100)
    send_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


class TestSuggestedPostInfoWithoutRequest(SuggestedPostInfoTestBase):
    def test_slot_behaviour(self, suggested_post_info):
        for attr in suggested_post_info.__slots__:
            assert getattr(suggested_post_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(suggested_post_info)) == len(set(mro_slots(suggested_post_info))), (
            "duplicate slot"
        )

    def test_type_enum_conversion(self):
        assert type(SuggestedPostInfo("pending").state) is SuggestedPostInfoState
        assert SuggestedPostInfo("unknown").state == "unknown"

    def test_de_json(self, offline_bot):
        json_dict = {
            "state": self.state,
            "price": self.price.to_dict(),
            "send_date": to_timestamp(self.send_date),
        }
        spi = SuggestedPostInfo.de_json(json_dict, offline_bot)
        assert spi.state == self.state
        assert spi.price == self.price
        assert spi.send_date == self.send_date
        assert spi.api_kwargs == {}

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "state": self.state,
            "price": self.price.to_dict(),
            "send_date": to_timestamp(self.send_date),
        }

        spi_bot = SuggestedPostInfo.de_json(json_dict, offline_bot)
        spi_bot_raw = SuggestedPostInfo.de_json(json_dict, raw_bot)
        spi_bot_tz = SuggestedPostInfo.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        send_date_offset = spi_bot_tz.send_date.utcoffset()
        send_date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(
            spi_bot_tz.send_date.replace(tzinfo=None)
        )

        assert spi_bot.send_date.tzinfo == UTC
        assert spi_bot_raw.send_date.tzinfo == UTC
        assert send_date_offset_tz == send_date_offset

    def test_to_dict(self, suggested_post_info):
        spi_dict = suggested_post_info.to_dict()

        assert isinstance(spi_dict, dict)
        assert spi_dict["state"] == self.state
        assert spi_dict["price"] == self.price.to_dict()
        assert spi_dict["send_date"] == to_timestamp(self.send_date)

    def test_equality(self, suggested_post_info):
        a = suggested_post_info
        b = SuggestedPostInfo(state=self.state, price=self.price)
        c = SuggestedPostInfo(state=SuggestedPostInfoState.DECLINED, price=self.price)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_price():
    return SuggestedPostPrice(
        currency=SuggestedPostPriceTestBase.currency,
        amount=SuggestedPostPriceTestBase.amount,
    )


class SuggestedPostPriceTestBase:
    currency = "XTR"
    amount = 100


class TestSuggestedPostPriceWithoutRequest(SuggestedPostPriceTestBase):
    def test_slot_behaviour(self, suggested_post_price):
        for attr in suggested_post_price.__slots__:
            assert getattr(suggested_post_price, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(suggested_post_price)) == len(set(mro_slots(suggested_post_price))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "currency": self.currency,
            "amount": self.amount,
        }
        spp = SuggestedPostPrice.de_json(json_dict, offline_bot)
        assert spp.currency == self.currency
        assert spp.amount == self.amount
        assert spp.api_kwargs == {}

    def test_to_dict(self, suggested_post_price):
        spp_dict = suggested_post_price.to_dict()

        assert isinstance(spp_dict, dict)
        assert spp_dict["currency"] == self.currency
        assert spp_dict["amount"] == self.amount

    def test_equality(self, suggested_post_price):
        a = suggested_post_price
        b = SuggestedPostPrice(currency=self.currency, amount=self.amount)
        c = SuggestedPostPrice(currency="TON", amount=self.amount)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_declined():
    return SuggestedPostDeclined(
        suggested_post_message=SuggestedPostDeclinedTestBase.suggested_post_message,
        comment=SuggestedPostDeclinedTestBase.comment,
    )


class SuggestedPostDeclinedTestBase:
    suggested_post_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="post this pls.")
    comment = "another time"


class TestSuggestedPostDeclinedWithoutRequest(SuggestedPostDeclinedTestBase):
    def test_slot_behaviour(self, suggested_post_declined):
        for attr in suggested_post_declined.__slots__:
            assert getattr(suggested_post_declined, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(suggested_post_declined)) == len(
            set(mro_slots(suggested_post_declined))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "suggested_post_message": self.suggested_post_message.to_dict(),
            "comment": self.comment,
        }
        spd = SuggestedPostDeclined.de_json(json_dict, offline_bot)
        assert spd.suggested_post_message == self.suggested_post_message
        assert spd.comment == self.comment
        assert spd.api_kwargs == {}

    def test_to_dict(self, suggested_post_declined):
        spd_dict = suggested_post_declined.to_dict()

        assert isinstance(spd_dict, dict)
        assert spd_dict["suggested_post_message"] == self.suggested_post_message.to_dict()
        assert spd_dict["comment"] == self.comment

    def test_equality(self, suggested_post_declined):
        a = suggested_post_declined
        b = SuggestedPostDeclined(
            suggested_post_message=self.suggested_post_message, comment=self.comment
        )
        c = SuggestedPostDeclined(suggested_post_message=self.suggested_post_message, comment="no")
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_paid():
    return SuggestedPostPaid(
        currency=SuggestedPostPaidTestBase.currency,
        suggested_post_message=SuggestedPostPaidTestBase.suggested_post_message,
        amount=SuggestedPostPaidTestBase.amount,
        star_amount=SuggestedPostPaidTestBase.star_amount,
    )


class SuggestedPostPaidTestBase:
    suggested_post_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="post this pls.")
    currency = "XTR"
    amount = 100
    star_amount = StarAmount(100)


class TestSuggestedPostPaidWithoutRequest(SuggestedPostPaidTestBase):
    def test_slot_behaviour(self, suggested_post_paid):
        for attr in suggested_post_paid.__slots__:
            assert getattr(suggested_post_paid, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(suggested_post_paid)) == len(set(mro_slots(suggested_post_paid))), (
            "duplicate slot"
        )

    def test_de_json(self, offline_bot):
        json_dict = {
            "suggested_post_message": self.suggested_post_message.to_dict(),
            "currency": self.currency,
            "amount": self.amount,
            "star_amount": self.star_amount.to_dict(),
        }
        spp = SuggestedPostPaid.de_json(json_dict, offline_bot)
        assert spp.suggested_post_message == self.suggested_post_message
        assert spp.currency == self.currency
        assert spp.amount == self.amount
        assert spp.star_amount == self.star_amount
        assert spp.api_kwargs == {}

    def test_to_dict(self, suggested_post_paid):
        spp_dict = suggested_post_paid.to_dict()

        assert isinstance(spp_dict, dict)
        assert spp_dict["suggested_post_message"] == self.suggested_post_message.to_dict()
        assert spp_dict["currency"] == self.currency
        assert spp_dict["amount"] == self.amount
        assert spp_dict["star_amount"] == self.star_amount.to_dict()

    def test_equality(self, suggested_post_paid):
        a = suggested_post_paid
        b = SuggestedPostPaid(
            suggested_post_message=self.suggested_post_message,
            currency=self.currency,
            amount=self.amount,
            star_amount=self.star_amount,
        )
        c = SuggestedPostPaid(
            suggested_post_message=self.suggested_post_message,
            currency=self.currency,
            amount=self.amount - 1,
            star_amount=StarAmount(self.amount - 1),
        )
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_refunded():
    return SuggestedPostRefunded(
        reason=SuggestedPostRefundedTestBase.reason,
        suggested_post_message=SuggestedPostRefundedTestBase.suggested_post_message,
    )


class SuggestedPostRefundedTestBase:
    reason = "post_deleted"
    suggested_post_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="post this pls.")


class TestSuggestedPostRefundedWithoutRequest(SuggestedPostRefundedTestBase):
    def test_slot_behaviour(self, suggested_post_refunded):
        for attr in suggested_post_refunded.__slots__:
            assert getattr(suggested_post_refunded, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(suggested_post_refunded)) == len(
            set(mro_slots(suggested_post_refunded))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "suggested_post_message": self.suggested_post_message.to_dict(),
            "reason": self.reason,
        }
        spr = SuggestedPostRefunded.de_json(json_dict, offline_bot)
        assert spr.suggested_post_message == self.suggested_post_message
        assert spr.reason == self.reason
        assert spr.api_kwargs == {}

    def test_to_dict(self, suggested_post_refunded):
        spr_dict = suggested_post_refunded.to_dict()

        assert isinstance(spr_dict, dict)
        assert spr_dict["suggested_post_message"] == self.suggested_post_message.to_dict()
        assert spr_dict["reason"] == self.reason

    def test_equality(self, suggested_post_refunded):
        a = suggested_post_refunded
        b = SuggestedPostRefunded(
            suggested_post_message=self.suggested_post_message, reason=self.reason
        )
        c = SuggestedPostRefunded(
            suggested_post_message=self.suggested_post_message, reason="payment_refunded"
        )
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_approved():
    return SuggestedPostApproved(
        send_date=SuggestedPostApprovedTestBase.send_date,
        suggested_post_message=SuggestedPostApprovedTestBase.suggested_post_message,
        price=SuggestedPostApprovedTestBase.price,
    )


class SuggestedPostApprovedTestBase:
    send_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)
    suggested_post_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="post this pls.")
    price = SuggestedPostPrice(currency="XTR", amount=100)


class TestSuggestedPostApprovedWithoutRequest(SuggestedPostApprovedTestBase):
    def test_slot_behaviour(self, suggested_post_approved):
        for attr in suggested_post_approved.__slots__:
            assert getattr(suggested_post_approved, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(suggested_post_approved)) == len(
            set(mro_slots(suggested_post_approved))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "send_date": to_timestamp(self.send_date),
            "suggested_post_message": self.suggested_post_message.to_dict(),
            "price": self.price.to_dict(),
        }
        spa = SuggestedPostApproved.de_json(json_dict, offline_bot)
        assert spa.send_date == self.send_date
        assert spa.suggested_post_message == self.suggested_post_message
        assert spa.price == self.price
        assert spa.api_kwargs == {}

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "send_date": to_timestamp(self.send_date),
            "suggested_post_message": self.suggested_post_message.to_dict(),
            "price": self.price.to_dict(),
        }

        spa_bot = SuggestedPostApproved.de_json(json_dict, offline_bot)
        spa_bot_raw = SuggestedPostApproved.de_json(json_dict, raw_bot)
        spi_bot_tz = SuggestedPostApproved.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        send_date_offset = spi_bot_tz.send_date.utcoffset()
        send_date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(
            spi_bot_tz.send_date.replace(tzinfo=None)
        )

        assert spa_bot.send_date.tzinfo == UTC
        assert spa_bot_raw.send_date.tzinfo == UTC
        assert send_date_offset_tz == send_date_offset

    def test_to_dict(self, suggested_post_approved):
        spa_dict = suggested_post_approved.to_dict()

        assert isinstance(spa_dict, dict)
        assert spa_dict["send_date"] == to_timestamp(self.send_date)
        assert spa_dict["suggested_post_message"] == self.suggested_post_message.to_dict()
        assert spa_dict["price"] == self.price.to_dict()

    def test_equality(self, suggested_post_approved):
        a = suggested_post_approved
        b = SuggestedPostApproved(
            send_date=self.send_date,
            suggested_post_message=self.suggested_post_message,
            price=self.price,
        )
        c = SuggestedPostApproved(
            send_date=self.send_date,
            suggested_post_message=self.suggested_post_message,
            price=SuggestedPostPrice(currency="XTR", amount=self.price.amount - 1),
        )
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def suggested_post_approval_failed():
    return SuggestedPostApprovalFailed(
        price=SuggestedPostApprovalFailedTestBase.price,
        suggested_post_message=SuggestedPostApprovalFailedTestBase.suggested_post_message,
    )


class SuggestedPostApprovalFailedTestBase:
    price = SuggestedPostPrice(currency="XTR", amount=100)
    suggested_post_message = Message(1, dtm.datetime.now(), Chat(1, ""), text="post this pls.")


class TestSuggestedPostApprovalFailedWithoutRequest(SuggestedPostApprovalFailedTestBase):
    def test_slot_behaviour(self, suggested_post_approval_failed):
        for attr in suggested_post_approval_failed.__slots__:
            assert getattr(suggested_post_approval_failed, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(suggested_post_approval_failed)) == len(
            set(mro_slots(suggested_post_approval_failed))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "price": self.price.to_dict(),
            "suggested_post_message": self.suggested_post_message.to_dict(),
        }
        spaf = SuggestedPostApprovalFailed.de_json(json_dict, offline_bot)
        assert spaf.price == self.price
        assert spaf.suggested_post_message == self.suggested_post_message
        assert spaf.api_kwargs == {}

    def test_to_dict(self, suggested_post_approval_failed):
        spaf_dict = suggested_post_approval_failed.to_dict()

        assert isinstance(spaf_dict, dict)
        assert spaf_dict["price"] == self.price.to_dict()
        assert spaf_dict["suggested_post_message"] == self.suggested_post_message.to_dict()

    def test_equality(self, suggested_post_approval_failed):
        a = suggested_post_approval_failed
        b = SuggestedPostApprovalFailed(
            price=self.price,
            suggested_post_message=self.suggested_post_message,
        )
        c = SuggestedPostApprovalFailed(
            price=SuggestedPostPrice(currency="XTR", amount=self.price.amount - 1),
            suggested_post_message=self.suggested_post_message,
        )
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != e
        assert hash(a) != hash(e)
