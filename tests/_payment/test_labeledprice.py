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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import LabeledPrice, Location
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def labeled_price():
    return LabeledPrice(TestLabeledPriceBase.label, TestLabeledPriceBase.amount)


class TestLabeledPriceBase:
    label = "label"
    amount = 100


class TestLabeledPriceWithoutRequest(TestLabeledPriceBase):
    def test_slot_behaviour(self, labeled_price):
        inst = labeled_price
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, labeled_price):
        assert labeled_price.label == self.label
        assert labeled_price.amount == self.amount

    def test_to_dict(self, labeled_price):
        labeled_price_dict = labeled_price.to_dict()

        assert isinstance(labeled_price_dict, dict)
        assert labeled_price_dict["label"] == labeled_price.label
        assert labeled_price_dict["amount"] == labeled_price.amount

    def test_equality(self):
        a = LabeledPrice("label", 100)
        b = LabeledPrice("label", 100)
        c = LabeledPrice("Label", 101)
        d = Location(123, 456)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
