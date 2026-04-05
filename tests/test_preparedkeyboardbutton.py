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

from telegram import PreparedKeyboardButton
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def prepared_keyboard_button():
    return PreparedKeyboardButton(PreparedKeyboardButtonTestBase.id)


class PreparedKeyboardButtonTestBase:
    id = 4


class TestPreparedKeyboardButtonWithoutRequest(PreparedKeyboardButtonTestBase):
    def test_slot_behaviour(self, prepared_keyboard_button):
        inst = prepared_keyboard_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "id": self.id,
        }
        prepared_keyboard_button = PreparedKeyboardButton.de_json(json_dict, offline_bot)
        assert prepared_keyboard_button.api_kwargs == {}
        assert prepared_keyboard_button.id == self.id

    def test_to_dict(self, prepared_keyboard_button):
        prepared_keyboard_button_dict = prepared_keyboard_button.to_dict()
        assert prepared_keyboard_button_dict["id"] == self.id

    def test_equality(self):
        a = PreparedKeyboardButton(self.id)
        b = PreparedKeyboardButton(self.id)
        c = PreparedKeyboardButton(self.id + 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)
