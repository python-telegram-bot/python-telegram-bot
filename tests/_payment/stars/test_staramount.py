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

import pytest

from telegram import StarAmount
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def star_amount():
    return StarAmount(
        amount=StarTransactionTestBase.amount,
        nanostar_amount=StarTransactionTestBase.nanostar_amount,
    )


class StarTransactionTestBase:
    amount = 100
    nanostar_amount = 356


class TestStarAmountWithoutRequest(StarTransactionTestBase):
    def test_slot_behaviour(self, star_amount):
        inst = star_amount
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
        }
        st = StarAmount.de_json(json_dict, offline_bot)
        assert st.api_kwargs == {}
        assert st.amount == self.amount
        assert st.nanostar_amount == self.nanostar_amount

    def test_to_dict(self, star_amount):
        expected_dict = {
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
        }
        assert star_amount.to_dict() == expected_dict

    def test_equality(self, star_amount):
        a = star_amount
        b = StarAmount(amount=self.amount, nanostar_amount=self.nanostar_amount)
        c = StarAmount(amount=99, nanostar_amount=99)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)
