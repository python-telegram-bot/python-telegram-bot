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

from telegram import CallbackGame
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def callback_game():
    return CallbackGame()


class TestCallbackGameWithoutRequest(DeserializationTestBase):
    de_json_class = CallbackGame

    @pytest.fixture
    def de_json_dict(self):
        # CallbackGame is a placeholder without any fields
        return {}

    def test_slot_behaviour(self, callback_game):
        for attr in callback_game.__slots__:
            assert getattr(callback_game, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(callback_game)) == len(set(mro_slots(callback_game))), "same slot"

    def test_de_json(self, offline_bot, de_json_dict):
        callback_game = CallbackGame.de_json(de_json_dict, offline_bot)
        assert callback_game.api_kwargs == {}

        assert isinstance(callback_game, CallbackGame)
        assert callback_game.get_bot() is offline_bot

    def test_to_dict(self, callback_game):
        assert callback_game.to_dict() == {}
