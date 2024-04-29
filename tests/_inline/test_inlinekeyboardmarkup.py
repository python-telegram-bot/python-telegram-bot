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

from telegram import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_keyboard_markup():
    return InlineKeyboardMarkup(TestInlineKeyboardMarkupBase.inline_keyboard)


class TestInlineKeyboardMarkupBase:
    inline_keyboard = [
        [
            InlineKeyboardButton(text="button1", callback_data="data1"),
            InlineKeyboardButton(text="button2", callback_data="data2"),
        ]
    ]


class TestInlineKeyboardMarkupWithoutRequest(TestInlineKeyboardMarkupBase):
    def test_slot_behaviour(self, inline_keyboard_markup):
        inst = inline_keyboard_markup
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, inline_keyboard_markup):
        inline_keyboard_markup_dict = inline_keyboard_markup.to_dict()

        assert isinstance(inline_keyboard_markup_dict, dict)
        assert inline_keyboard_markup_dict["inline_keyboard"] == [
            [self.inline_keyboard[0][0].to_dict(), self.inline_keyboard[0][1].to_dict()]
        ]

    def test_de_json(self):
        json_dict = {
            "inline_keyboard": [
                [
                    {"text": "start", "url": "http://google.com"},
                    {"text": "next", "callback_data": "abcd"},
                ],
                [{"text": "Cancel", "callback_data": "Cancel"}],
            ]
        }
        inline_keyboard_markup = InlineKeyboardMarkup.de_json(json_dict, None)
        assert inline_keyboard_markup.api_kwargs == {}

        assert isinstance(inline_keyboard_markup, InlineKeyboardMarkup)
        keyboard = inline_keyboard_markup.inline_keyboard
        assert len(keyboard) == 2
        assert len(keyboard[0]) == 2
        assert len(keyboard[1]) == 1

        assert isinstance(keyboard[0][0], InlineKeyboardButton)
        assert isinstance(keyboard[0][1], InlineKeyboardButton)
        assert isinstance(keyboard[1][0], InlineKeyboardButton)

        assert keyboard[0][0].text == "start"
        assert keyboard[0][0].url == "http://google.com"

    def test_equality(self):
        a = InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(label, callback_data="data")
                for label in ["button1", "button2", "button3"]
            ]
        )
        b = InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(label, callback_data="data")
                for label in ["button1", "button2", "button3"]
            ]
        )
        c = InlineKeyboardMarkup.from_column(
            [InlineKeyboardButton(label, callback_data="data") for label in ["button1", "button2"]]
        )
        d = InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(label, callback_data=label)
                for label in ["button1", "button2", "button3"]
            ]
        )
        e = InlineKeyboardMarkup.from_column(
            [InlineKeyboardButton(label, url=label) for label in ["button1", "button2", "button3"]]
        )
        f = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(label, callback_data="data")
                    for label in ["button1", "button2"]
                ],
                [
                    InlineKeyboardButton(label, callback_data="data")
                    for label in ["button1", "button2"]
                ],
                [
                    InlineKeyboardButton(label, callback_data="data")
                    for label in ["button1", "button2"]
                ],
            ]
        )
        g = ReplyKeyboardMarkup.from_column(["button1", "button2", "button3"])

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)

        assert a != g
        assert hash(a) != hash(g)

    def test_from_button(self):
        inline_keyboard_markup = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="button1", callback_data="data1")
        ).inline_keyboard
        assert len(inline_keyboard_markup) == 1
        assert len(inline_keyboard_markup[0]) == 1

    def test_from_row(self):
        inline_keyboard_markup = InlineKeyboardMarkup.from_row(
            [
                InlineKeyboardButton(text="button1", callback_data="data1"),
                InlineKeyboardButton(text="button1", callback_data="data1"),
            ]
        ).inline_keyboard
        assert len(inline_keyboard_markup) == 1
        assert len(inline_keyboard_markup[0]) == 2

    def test_from_column(self):
        inline_keyboard_markup = InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(text="button1", callback_data="data1"),
                InlineKeyboardButton(text="button1", callback_data="data1"),
            ]
        ).inline_keyboard
        assert len(inline_keyboard_markup) == 2
        assert len(inline_keyboard_markup[0]) == 1
        assert len(inline_keyboard_markup[1]) == 1

    def test_expected_values(self, inline_keyboard_markup):
        assert inline_keyboard_markup.inline_keyboard == tuple(
            tuple(row) for row in self.inline_keyboard
        )

    def test_wrong_keyboard_inputs(self):
        with pytest.raises(ValueError, match="should be a sequence of sequences"):
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("b1", "1")], InlineKeyboardButton("b2", "2")]
            )
        with pytest.raises(ValueError, match="should be a sequence of sequences"):
            InlineKeyboardMarkup("strings_are_not_allowed")
        with pytest.raises(ValueError, match="should be a sequence of sequences"):
            InlineKeyboardMarkup(["strings_are_not_allowed_in_the_rows_either"])
        with pytest.raises(ValueError, match="should be a sequence of sequences"):
            InlineKeyboardMarkup(InlineKeyboardButton("b1", "1"))
        with pytest.raises(ValueError, match="should be a sequence of sequences"):
            InlineKeyboardMarkup([[[InlineKeyboardButton("only_2d_array_is_allowed", "1")]]])

    async def test_expected_values_empty_switch(self, inline_keyboard_markup, bot, monkeypatch):
        async def make_assertion(
            url,
            data,
            reply_to_message_id=None,
            disable_notification=None,
            reply_markup=None,
            timeout=None,
            **kwargs,
        ):
            if reply_markup is not None:
                markups = (
                    InlineKeyboardMarkup,
                    ReplyKeyboardMarkup,
                    ForceReply,
                    ReplyKeyboardRemove,
                )
                if isinstance(reply_markup, markups):
                    data["reply_markup"] = reply_markup.to_dict()
                else:
                    data["reply_markup"] = reply_markup

            assert bool("'switch_inline_query': ''" in str(data["reply_markup"]))
            assert bool("'switch_inline_query_current_chat': ''" in str(data["reply_markup"]))

        inline_keyboard_markup.inline_keyboard[0][0]._unfreeze()
        inline_keyboard_markup.inline_keyboard[0][0].callback_data = None
        inline_keyboard_markup.inline_keyboard[0][0].switch_inline_query = ""
        inline_keyboard_markup.inline_keyboard[0][1]._unfreeze()
        inline_keyboard_markup.inline_keyboard[0][1].callback_data = None
        inline_keyboard_markup.inline_keyboard[0][1].switch_inline_query_current_chat = ""

        monkeypatch.setattr(bot, "_send_message", make_assertion)
        await bot.send_message(123, "test", reply_markup=inline_keyboard_markup)


class TestInlineKeyborardMarkupWithRequest(TestInlineKeyboardMarkupBase):
    async def test_send_message_with_inline_keyboard_markup(
        self, bot, chat_id, inline_keyboard_markup
    ):
        message = await bot.send_message(
            chat_id, "Testing InlineKeyboardMarkup", reply_markup=inline_keyboard_markup
        )

        assert message.text == "Testing InlineKeyboardMarkup"
