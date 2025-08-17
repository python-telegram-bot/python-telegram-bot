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

import pytest

from telegram import Dice, PaidMessagePriceChanged
from tests.auxil.slots import mro_slots


class PaidMessagePriceChangedTestBase:
    paid_message_star_count = 291


@pytest.fixture(scope="module")
def paid_message_price_changed():
    return PaidMessagePriceChanged(PaidMessagePriceChangedTestBase.paid_message_star_count)


class TestPaidMessagePriceChangedWithoutRequest(PaidMessagePriceChangedTestBase):
    def test_slot_behaviour(self, paid_message_price_changed):
        for attr in paid_message_price_changed.__slots__:
            assert getattr(paid_message_price_changed, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(paid_message_price_changed)) == len(
            set(mro_slots(paid_message_price_changed))
        ), "duplicate slot"

    def test_to_dict(self, paid_message_price_changed):
        pmpc_dict = paid_message_price_changed.to_dict()
        assert isinstance(pmpc_dict, dict)
        assert pmpc_dict["paid_message_star_count"] == self.paid_message_star_count

    def test_de_json(self, offline_bot):
        json_dict = {"paid_message_star_count": self.paid_message_star_count}
        pmpc = PaidMessagePriceChanged.de_json(json_dict, offline_bot)
        assert isinstance(pmpc, PaidMessagePriceChanged)
        assert pmpc.paid_message_star_count == self.paid_message_star_count
        assert pmpc.api_kwargs == {}

    def test_equality(self):
        pmpc1 = PaidMessagePriceChanged(self.paid_message_star_count)
        pmpc2 = PaidMessagePriceChanged(self.paid_message_star_count)
        pmpc3 = PaidMessagePriceChanged(3)
        dice = Dice(5, "emoji")

        assert pmpc1 == pmpc2
        assert hash(pmpc1) == hash(pmpc2)

        assert pmpc1 != pmpc3
        assert hash(pmpc1) != hash(pmpc3)

        assert pmpc1 != dice
        assert hash(pmpc1) != hash(dice)
