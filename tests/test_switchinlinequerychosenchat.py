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
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import SwitchInlineQueryChosenChat
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def switch_inline_query_chosen_chat():
    return SwitchInlineQueryChosenChat(
        query=TestSwitchInlineQueryChosenChatBase.query,
        allow_user_chats=TestSwitchInlineQueryChosenChatBase.allow_user_chats,
        allow_bot_chats=TestSwitchInlineQueryChosenChatBase.allow_bot_chats,
        allow_channel_chats=TestSwitchInlineQueryChosenChatBase.allow_channel_chats,
        allow_group_chats=TestSwitchInlineQueryChosenChatBase.allow_group_chats,
    )


class TestSwitchInlineQueryChosenChatBase:
    query = "query"
    allow_user_chats = True
    allow_bot_chats = True
    allow_channel_chats = False
    allow_group_chats = True


class TestSwitchInlineQueryChosenChat(TestSwitchInlineQueryChosenChatBase):
    def test_slot_behaviour(self, switch_inline_query_chosen_chat):
        inst = switch_inline_query_chosen_chat
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, switch_inline_query_chosen_chat):
        assert switch_inline_query_chosen_chat.query == self.query
        assert switch_inline_query_chosen_chat.allow_user_chats == self.allow_user_chats
        assert switch_inline_query_chosen_chat.allow_bot_chats == self.allow_bot_chats
        assert switch_inline_query_chosen_chat.allow_channel_chats == self.allow_channel_chats
        assert switch_inline_query_chosen_chat.allow_group_chats == self.allow_group_chats

    def test_to_dict(self, switch_inline_query_chosen_chat):
        siqcc = switch_inline_query_chosen_chat.to_dict()

        assert isinstance(siqcc, dict)
        assert siqcc["query"] == switch_inline_query_chosen_chat.query
        assert siqcc["allow_user_chats"] == switch_inline_query_chosen_chat.allow_user_chats
        assert siqcc["allow_bot_chats"] == switch_inline_query_chosen_chat.allow_bot_chats
        assert siqcc["allow_channel_chats"] == switch_inline_query_chosen_chat.allow_channel_chats
        assert siqcc["allow_group_chats"] == switch_inline_query_chosen_chat.allow_group_chats

    def test_equality(self):
        siqcc = SwitchInlineQueryChosenChat
        a = siqcc(self.query, self.allow_user_chats, self.allow_bot_chats)
        b = siqcc(self.query, self.allow_user_chats, self.allow_bot_chats)
        c = siqcc(self.query, self.allow_user_chats)
        d = siqcc("", self.allow_user_chats, self.allow_bot_chats)
        e = siqcc(self.query, self.allow_user_chats, self.allow_bot_chats, self.allow_group_chats)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
