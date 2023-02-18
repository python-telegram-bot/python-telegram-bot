#!/usr/bin/env python
#
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
import pytest

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultGame,
    InlineQueryResultVoice,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_game():
    return InlineQueryResultGame(
        TestInlineQueryResultGameBase.id_,
        TestInlineQueryResultGameBase.game_short_name,
        reply_markup=TestInlineQueryResultGameBase.reply_markup,
    )


class TestInlineQueryResultGameBase:
    id_ = "id"
    type_ = "game"
    game_short_name = "game short name"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultGameWithoutRequest(TestInlineQueryResultGameBase):
    def test_slot_behaviour(self, inline_query_result_game):
        inst = inline_query_result_game
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_game):
        assert inline_query_result_game.type == self.type_
        assert inline_query_result_game.id == self.id_
        assert inline_query_result_game.game_short_name == self.game_short_name
        assert inline_query_result_game.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_game):
        inline_query_result_game_dict = inline_query_result_game.to_dict()

        assert isinstance(inline_query_result_game_dict, dict)
        assert inline_query_result_game_dict["type"] == inline_query_result_game.type
        assert inline_query_result_game_dict["id"] == inline_query_result_game.id
        assert (
            inline_query_result_game_dict["game_short_name"]
            == inline_query_result_game.game_short_name
        )
        assert (
            inline_query_result_game_dict["reply_markup"]
            == inline_query_result_game.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultGame(self.id_, self.game_short_name)
        b = InlineQueryResultGame(self.id_, self.game_short_name)
        c = InlineQueryResultGame(self.id_, "")
        d = InlineQueryResultGame("", self.game_short_name)
        e = InlineQueryResultVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
