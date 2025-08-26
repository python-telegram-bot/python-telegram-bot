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
from telegram._suggestedpost import SuggestedPostParameters, SuggestedPostPrice
from telegram._utils.datetime import UTC, to_timestamp
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
