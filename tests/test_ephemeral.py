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

from telegram import EphemeralMessageParameters
from tests.auxil.slots import mro_slots


@pytest.fixture
def ephemeral_message_parameters():
    return EphemeralMessageParameters(
        receiver_user_id=12345,
        callback_query_id="cq_123",
        replace_callback_query_message=True,
    )


class TestEphemeralMessageParametersWithoutRequest:
    def test_slot_behaviour(self, ephemeral_message_parameters):
        inst = ephemeral_message_parameters
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, ephemeral_message_parameters):
        json_dict = {
            "receiver_user_id": 12345,
            "callback_query_id": "cq_123",
            "replace_callback_query_message": True,
        }
        obj = EphemeralMessageParameters.de_json(json_dict, offline_bot)
        assert obj.api_kwargs == {}
        assert obj.receiver_user_id == 12345
        assert obj.callback_query_id == "cq_123"
        assert obj.replace_callback_query_message is True

    def test_to_dict(self, ephemeral_message_parameters):
        d = ephemeral_message_parameters.to_dict()
        assert d["receiver_user_id"] == 12345
        assert d["callback_query_id"] == "cq_123"
        assert d["replace_callback_query_message"] is True

    def test_equality(self, ephemeral_message_parameters):
        a = ephemeral_message_parameters
        b = EphemeralMessageParameters(
            receiver_user_id=12345,
            callback_query_id="cq_123",
            replace_callback_query_message=True,
        )
        c = EphemeralMessageParameters(receiver_user_id=54321)
        assert a == b
        assert a != c
        assert hash(a) == hash(b)
