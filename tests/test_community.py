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

from telegram import Community, CommunityChatJoined
from tests.auxil.slots import mro_slots


@pytest.fixture
def community():
    return Community(
        id=12345,
        name="Test Community",
    )


@pytest.fixture
def community_chat_joined(community):
    return CommunityChatJoined(
        community=community,
    )


class TestCommunityWithoutRequest:
    def test_slot_behaviour(self, community):
        inst = community
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, community):
        json_dict = {
            "id": 12345,
            "name": "Test Community",
        }
        obj = Community.de_json(json_dict, offline_bot)
        assert obj.api_kwargs == {}
        assert obj.id == 12345
        assert obj.name == "Test Community"

    def test_to_dict(self, community):
        d = community.to_dict()
        assert d["id"] == 12345
        assert d["name"] == "Test Community"

    def test_equality(self, community):
        a = community
        b = Community(id=12345, name="Test Community")
        c = Community(id=54321, name="Test Community")
        assert a == b
        assert a != c
        assert hash(a) == hash(b)


class TestCommunityChatJoinedWithoutRequest:
    def test_slot_behaviour(self, community_chat_joined):
        inst = community_chat_joined
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, community_chat_joined):
        json_dict = {
            "community": {
                "id": 12345,
                "name": "Test Community",
            },
        }
        obj = CommunityChatJoined.de_json(json_dict, offline_bot)
        assert obj.api_kwargs == {}
        assert obj.community.id == 12345
        assert obj.community.name == "Test Community"

    def test_to_dict(self, community_chat_joined):
        d = community_chat_joined.to_dict()
        assert d["community"]["id"] == 12345
        assert d["community"]["name"] == "Test Community"

    def test_equality(self, community_chat_joined, community):
        a = community_chat_joined
        b = CommunityChatJoined(community=Community(id=12345, name="Test Community"))
        c = CommunityChatJoined(community=Community(id=54321, name="Test Community"))
        assert a == b
        assert a != c
        assert hash(a) == hash(b)
