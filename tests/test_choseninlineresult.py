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

from telegram import ChosenInlineResult, Location, User, Voice
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def user():
    user = User(1, "First name", False)
    user._unfreeze()
    return user


@pytest.fixture(scope="module")
def chosen_inline_result(user):
    return ChosenInlineResult(
        ChosenInlineResultTestBase.result_id, user, ChosenInlineResultTestBase.query
    )


class ChosenInlineResultTestBase:
    result_id = "result id"
    query = "query text"
    location = Location(-42.003, 34.004)
    inline_message_id = "a random id"


class TestChosenInlineResultWithoutRequest(ChosenInlineResultTestBase, DeserializationTestBase):
    de_json_class = ChosenInlineResult

    @pytest.fixture
    def de_json_dict(self, user):
        return {
            "result_id": self.result_id,
            "from": user.to_dict(),
            "query": self.query,
            "location": self.location.to_dict(),
            "inline_message_id": self.inline_message_id,
        }

    def test_slot_behaviour(self, chosen_inline_result):
        inst = chosen_inline_result
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict, user):
        result = ChosenInlineResult.de_json(de_json_dict, offline_bot)
        assert result.api_kwargs == {}

        assert result.result_id == self.result_id
        assert result.from_user == user
        assert result.query == self.query
        assert result.location == self.location
        assert result.inline_message_id == self.inline_message_id

    def test_to_dict(self, chosen_inline_result):
        chosen_inline_result_dict = chosen_inline_result.to_dict()

        assert isinstance(chosen_inline_result_dict, dict)
        assert chosen_inline_result_dict["result_id"] == chosen_inline_result.result_id
        assert chosen_inline_result_dict["from"] == chosen_inline_result.from_user.to_dict()
        assert chosen_inline_result_dict["query"] == chosen_inline_result.query

    def test_equality(self, user):
        a = ChosenInlineResult(self.result_id, user, "Query", "")
        b = ChosenInlineResult(self.result_id, user, "Query", "")
        c = ChosenInlineResult(self.result_id, user, "", "")
        d = ChosenInlineResult("", user, "Query", "")
        e = Voice(self.result_id, "unique_id", 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
