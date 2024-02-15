#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

from telegram import ChatBoostAdded, VideoChatStarted
from tests.auxil.slots import mro_slots


class TestChatBoostAddedWithoutRequest:
    boost_count = 100

    def test_slot_behaviour(self):
        action = ChatBoostAdded(8)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        json_dict = {"boost_count": self.boost_count}
        chat_boost_added = ChatBoostAdded.de_json(json_dict, None)
        assert chat_boost_added.api_kwargs == {}

        assert chat_boost_added.boost_count == self.boost_count

    def test_to_dict(self):
        chat_boost_added = ChatBoostAdded(self.boost_count)
        chat_boost_added_dict = chat_boost_added.to_dict()

        assert isinstance(chat_boost_added_dict, dict)
        assert chat_boost_added_dict["boost_count"] == self.boost_count

    def test_equality(self):
        a = ChatBoostAdded(100)
        b = ChatBoostAdded(100)
        c = ChatBoostAdded(50)
        d = VideoChatStarted()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
