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
# along with this program. If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import SentGuestMessage
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def sent_guest_message():
    return SentGuestMessage(inline_message_id=SentGuestMessageTestBase.inline_message_id)


class SentGuestMessageTestBase:
    inline_message_id = "123"


class TestSentGuestMessageWithoutRequest(SentGuestMessageTestBase):
    def test_slot_behaviour(self, sent_guest_message):
        inst = sent_guest_message
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, sent_guest_message):
        sent_guest_message_dict = sent_guest_message.to_dict()

        assert isinstance(sent_guest_message_dict, dict)
        assert sent_guest_message_dict["inline_message_id"] == self.inline_message_id

    def test_de_json(self, offline_bot):
        data = {"inline_message_id": self.inline_message_id}
        m = SentGuestMessage.de_json(data, None)
        assert m.api_kwargs == {}
        assert m.inline_message_id == self.inline_message_id

    def test_equality(self):
        a = SentGuestMessage(self.inline_message_id)
        b = SentGuestMessage(self.inline_message_id)
        c = SentGuestMessage("not_inline_message_id")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
