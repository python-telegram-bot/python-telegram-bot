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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import DisabledButton
from tests.auxil.slots import mro_slots


@pytest.fixture
def disabled_button():
    return DisabledButton()


class TestDisabledButtonWithoutRequest:
    def test_slot_behaviour(self, disabled_button):
        inst = disabled_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, disabled_button):
        json_dict = {}
        obj = DisabledButton.de_json(json_dict, offline_bot)
        assert obj.api_kwargs == {}

    def test_to_dict(self, disabled_button):
        d = disabled_button.to_dict()
        assert d == {}

    def test_equality(self, disabled_button):
        a = disabled_button
        b = DisabledButton()
        assert a == b
        assert hash(a) == hash(b)
