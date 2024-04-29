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

from telegram import InlineQueryResultsButton, WebAppInfo
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_results_button():
    return InlineQueryResultsButton(
        text=TestInlineQueryResultsButtonBase.text,
        start_parameter=TestInlineQueryResultsButtonBase.start_parameter,
        web_app=TestInlineQueryResultsButtonBase.web_app,
    )


class TestInlineQueryResultsButtonBase:
    text = "text"
    start_parameter = "start_parameter"
    web_app = WebAppInfo(url="https://python-telegram-bot.org")


class TestInlineQueryResultsButtonWithoutRequest(TestInlineQueryResultsButtonBase):
    def test_slot_behaviour(self, inline_query_results_button):
        inst = inline_query_results_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, inline_query_results_button):
        inline_query_results_button_dict = inline_query_results_button.to_dict()
        assert isinstance(inline_query_results_button_dict, dict)
        assert inline_query_results_button_dict["text"] == self.text
        assert inline_query_results_button_dict["start_parameter"] == self.start_parameter
        assert inline_query_results_button_dict["web_app"] == self.web_app.to_dict()

    def test_de_json(self, bot):
        assert InlineQueryResultsButton.de_json(None, bot) is None
        assert InlineQueryResultsButton.de_json({}, bot) is None

        json_dict = {
            "text": self.text,
            "start_parameter": self.start_parameter,
            "web_app": self.web_app.to_dict(),
        }
        inline_query_results_button = InlineQueryResultsButton.de_json(json_dict, bot)

        assert inline_query_results_button.text == self.text
        assert inline_query_results_button.start_parameter == self.start_parameter
        assert inline_query_results_button.web_app == self.web_app

    def test_equality(self):
        a = InlineQueryResultsButton(self.text, self.start_parameter, self.web_app)
        b = InlineQueryResultsButton(self.text, self.start_parameter, self.web_app)
        c = InlineQueryResultsButton(self.text, "", self.web_app)
        d = InlineQueryResultsButton(self.text, self.start_parameter, None)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
