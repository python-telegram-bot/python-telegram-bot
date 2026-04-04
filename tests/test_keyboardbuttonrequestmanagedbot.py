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

from telegram import KeyboardButtonRequestManagedBot
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def keyboard_button_request_managed_bot():
    return KeyboardButtonRequestManagedBot(
        KeyboardButtonRequestManagedBotTestBase.request_id,
        KeyboardButtonRequestManagedBotTestBase.suggested_name,
        KeyboardButtonRequestManagedBotTestBase.suggested_username,
    )


class KeyboardButtonRequestManagedBotTestBase:
    request_id = 4
    suggested_name = "suggested_name"
    suggested_username = "username"


class TestKeyboardButtonRequestManagedBotWithoutRequest(KeyboardButtonRequestManagedBotTestBase):
    def test_slot_behaviour(self, keyboard_button_request_managed_bot):
        inst = keyboard_button_request_managed_bot
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "request_id": self.request_id,
            "suggested_name": self.suggested_name,
            "suggested_username": self.suggested_username,
        }
        keyboard_button_request_managed_bot = KeyboardButtonRequestManagedBot.de_json(
            json_dict, offline_bot
        )
        assert keyboard_button_request_managed_bot.api_kwargs == {}
        assert keyboard_button_request_managed_bot.request_id == self.request_id
        assert keyboard_button_request_managed_bot.suggested_name == self.suggested_name
        assert keyboard_button_request_managed_bot.suggested_username == self.suggested_username

    def test_to_dict(self):
        keyboard_button_request_managed_bot = KeyboardButtonRequestManagedBot(
            self.request_id,
            self.suggested_name,
            self.suggested_username,
        )
        keyboard_button_request_managed_bot_dict = keyboard_button_request_managed_bot.to_dict()
        assert (
            keyboard_button_request_managed_bot_dict["request_id"]
            == keyboard_button_request_managed_bot.request_id
        )
        assert (
            keyboard_button_request_managed_bot_dict["suggested_name"]
            == keyboard_button_request_managed_bot.suggested_name
        )
        assert (
            keyboard_button_request_managed_bot_dict["suggested_username"]
            == keyboard_button_request_managed_bot.suggested_username
        )

    def test_equality(self):
        a = KeyboardButtonRequestManagedBot(
            self.request_id, self.suggested_name, self.suggested_username
        )
        b = KeyboardButtonRequestManagedBot(
            self.request_id, self.suggested_name, self.suggested_username
        )
        c = KeyboardButtonRequestManagedBot(1, self.suggested_name, self.suggested_username)
        d = "not a KeyboardButtonRequestManagedBot"

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
