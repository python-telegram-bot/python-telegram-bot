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
"""This module contains an object for testing a Direct Message Price."""

from typing import TYPE_CHECKING

import pytest

from telegram import DirectMessagePriceChanged, User
from tests.auxil.slots import mro_slots

if TYPE_CHECKING:
    from telegram._utils.types import JSONDict


@pytest.fixture
def direct_message_price_changed():
    return DirectMessagePriceChanged(
        are_direct_messages_enabled=DirectMessagePriceChangedTestBase.are_direct_messages_enabled,
        direct_message_star_count=DirectMessagePriceChangedTestBase.direct_message_star_count,
    )


class DirectMessagePriceChangedTestBase:
    are_direct_messages_enabled: bool = True
    direct_message_star_count: int = 100


class TestDirectMessagePriceChangedWithoutRequest(DirectMessagePriceChangedTestBase):
    def test_slot_behaviour(self, direct_message_price_changed):
        action = direct_message_price_changed
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict: JSONDict = {
            "are_direct_messages_enabled": self.are_direct_messages_enabled,
            "direct_message_star_count": self.direct_message_star_count,
        }
        dmpc = DirectMessagePriceChanged.de_json(json_dict, offline_bot)
        assert dmpc.api_kwargs == {}

        assert dmpc.are_direct_messages_enabled == self.are_direct_messages_enabled
        assert dmpc.direct_message_star_count == self.direct_message_star_count

    def test_to_dict(self, direct_message_price_changed):
        dmpc_dict = direct_message_price_changed.to_dict()
        assert dmpc_dict["are_direct_messages_enabled"] == self.are_direct_messages_enabled
        assert dmpc_dict["direct_message_star_count"] == self.direct_message_star_count

    def test_equality(self, direct_message_price_changed):
        dmpc1 = direct_message_price_changed
        dmpc2 = DirectMessagePriceChanged(
            are_direct_messages_enabled=self.are_direct_messages_enabled,
            direct_message_star_count=self.direct_message_star_count,
        )
        assert dmpc1 == dmpc2
        assert hash(dmpc1) == hash(dmpc2)

        dmpc3 = DirectMessagePriceChanged(
            are_direct_messages_enabled=False,
            direct_message_star_count=self.direct_message_star_count,
        )
        assert dmpc1 != dmpc3
        assert hash(dmpc1) != hash(dmpc3)

        not_a_dmpc = User(id=1, first_name="wrong", is_bot=False)
        assert dmpc1 != not_a_dmpc
        assert hash(dmpc1) != hash(not_a_dmpc)
