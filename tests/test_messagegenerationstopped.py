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

from telegram import Chat, MessageGenerationStopped
from tests.auxil.slots import mro_slots


@pytest.fixture
def message_generation_stopped():
    return MessageGenerationStopped(
        chat=Chat(id=123, type=Chat.PRIVATE),
        draft_id=456,
        message_thread_id=789,
    )


class TestMessageGenerationStoppedWithoutRequest:
    def test_slot_behaviour(self, message_generation_stopped):
        inst = message_generation_stopped
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, message_generation_stopped):
        json_dict = {
            "chat": {
                "id": 123,
                "type": "private",
            },
            "draft_id": 456,
            "message_thread_id": 789,
        }
        obj = MessageGenerationStopped.de_json(json_dict, offline_bot)
        assert obj.api_kwargs == {}
        assert obj.chat.id == 123
        assert obj.draft_id == 456
        assert obj.message_thread_id == 789

    def test_to_dict(self, message_generation_stopped):
        d = message_generation_stopped.to_dict()
        assert d["chat"]["id"] == 123
        assert d["draft_id"] == 456
        assert d["message_thread_id"] == 789

    def test_equality(self, message_generation_stopped):
        a = message_generation_stopped
        b = MessageGenerationStopped(
            chat=Chat(id=123, type=Chat.PRIVATE),
            draft_id=456,
            message_thread_id=789,
        )
        c = MessageGenerationStopped(
            chat=Chat(id=999, type=Chat.PRIVATE),
            draft_id=456,
        )
        assert a == b
        assert a != c
        assert hash(a) == hash(b)
