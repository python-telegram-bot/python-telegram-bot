#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

from telegram import SentWebAppMessage
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def sent_web_app_message():
    return SentWebAppMessage(inline_message_id=TestSentWebAppMessageBase.inline_message_id)


class TestSentWebAppMessageBase:
    inline_message_id = "123"


class TestSentWebAppMessageWithoutRequest(TestSentWebAppMessageBase):
    def test_slot_behaviour(self, sent_web_app_message):
        inst = sent_web_app_message
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, sent_web_app_message):
        sent_web_app_message_dict = sent_web_app_message.to_dict()

        assert isinstance(sent_web_app_message_dict, dict)
        assert sent_web_app_message_dict["inline_message_id"] == self.inline_message_id

    def test_de_json(self, bot):
        data = {"inline_message_id": self.inline_message_id}
        m = SentWebAppMessage.de_json(data, None)
        assert m.api_kwargs == {}
        assert m.inline_message_id == self.inline_message_id

    def test_equality(self):
        a = SentWebAppMessage(self.inline_message_id)
        b = SentWebAppMessage(self.inline_message_id)
        c = SentWebAppMessage("")
        d = SentWebAppMessage("not_inline_message_id")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
