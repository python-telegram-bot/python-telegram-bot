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
    CallbackGame,
    InlineKeyboardButton,
    LoginUrl,
    SwitchInlineQueryChosenChat,
    WebAppInfo,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_keyboard_button():
    return InlineKeyboardButton(
        TestInlineKeyboardButtonBase.text,
        url=TestInlineKeyboardButtonBase.url,
        callback_data=TestInlineKeyboardButtonBase.callback_data,
        switch_inline_query=TestInlineKeyboardButtonBase.switch_inline_query,
        switch_inline_query_current_chat=(
            TestInlineKeyboardButtonBase.switch_inline_query_current_chat
        ),
        callback_game=TestInlineKeyboardButtonBase.callback_game,
        pay=TestInlineKeyboardButtonBase.pay,
        login_url=TestInlineKeyboardButtonBase.login_url,
        web_app=TestInlineKeyboardButtonBase.web_app,
        switch_inline_query_chosen_chat=(
            TestInlineKeyboardButtonBase.switch_inline_query_chosen_chat
        ),
    )


class TestInlineKeyboardButtonBase:
    text = "text"
    url = "url"
    callback_data = "callback data"
    switch_inline_query = "switch_inline_query"
    switch_inline_query_current_chat = "switch_inline_query_current_chat"
    callback_game = CallbackGame()
    pay = True
    login_url = LoginUrl("http://google.com")
    web_app = WebAppInfo(url="https://example.com")
    switch_inline_query_chosen_chat = SwitchInlineQueryChosenChat("a_bot", True, False, True, True)


class TestInlineKeyboardButtonWithoutRequest(TestInlineKeyboardButtonBase):
    def test_slot_behaviour(self, inline_keyboard_button):
        inst = inline_keyboard_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_keyboard_button):
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query
        assert (
            inline_keyboard_button.switch_inline_query_current_chat
            == self.switch_inline_query_current_chat
        )
        assert isinstance(inline_keyboard_button.callback_game, CallbackGame)
        assert inline_keyboard_button.pay == self.pay
        assert inline_keyboard_button.login_url == self.login_url
        assert inline_keyboard_button.web_app == self.web_app
        assert (
            inline_keyboard_button.switch_inline_query_chosen_chat
            == self.switch_inline_query_chosen_chat
        )

    def test_to_dict(self, inline_keyboard_button):
        inline_keyboard_button_dict = inline_keyboard_button.to_dict()

        assert isinstance(inline_keyboard_button_dict, dict)
        assert inline_keyboard_button_dict["text"] == inline_keyboard_button.text
        assert inline_keyboard_button_dict["url"] == inline_keyboard_button.url
        assert inline_keyboard_button_dict["callback_data"] == inline_keyboard_button.callback_data
        assert (
            inline_keyboard_button_dict["switch_inline_query"]
            == inline_keyboard_button.switch_inline_query
        )
        assert (
            inline_keyboard_button_dict["switch_inline_query_current_chat"]
            == inline_keyboard_button.switch_inline_query_current_chat
        )
        assert (
            inline_keyboard_button_dict["callback_game"]
            == inline_keyboard_button.callback_game.to_dict()
        )
        assert inline_keyboard_button_dict["pay"] == inline_keyboard_button.pay
        assert (
            inline_keyboard_button_dict["login_url"] == inline_keyboard_button.login_url.to_dict()
        )
        assert inline_keyboard_button_dict["web_app"] == inline_keyboard_button.web_app.to_dict()
        assert (
            inline_keyboard_button_dict["switch_inline_query_chosen_chat"]
            == inline_keyboard_button.switch_inline_query_chosen_chat.to_dict()
        )

    def test_de_json(self, bot):
        json_dict = {
            "text": self.text,
            "url": self.url,
            "callback_data": self.callback_data,
            "switch_inline_query": self.switch_inline_query,
            "switch_inline_query_current_chat": self.switch_inline_query_current_chat,
            "callback_game": self.callback_game.to_dict(),
            "web_app": self.web_app.to_dict(),
            "login_url": self.login_url.to_dict(),
            "pay": self.pay,
            "switch_inline_query_chosen_chat": self.switch_inline_query_chosen_chat.to_dict(),
        }

        inline_keyboard_button = InlineKeyboardButton.de_json(json_dict, None)
        assert inline_keyboard_button.api_kwargs == {}
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query
        assert (
            inline_keyboard_button.switch_inline_query_current_chat
            == self.switch_inline_query_current_chat
        )
        # CallbackGame has empty _id_attrs, so just test if the class is created.
        assert isinstance(inline_keyboard_button.callback_game, CallbackGame)
        assert inline_keyboard_button.pay == self.pay
        assert inline_keyboard_button.login_url == self.login_url
        assert inline_keyboard_button.web_app == self.web_app
        assert (
            inline_keyboard_button.switch_inline_query_chosen_chat
            == self.switch_inline_query_chosen_chat
        )

        none = InlineKeyboardButton.de_json({}, bot)
        assert none is None

    def test_equality(self):
        a = InlineKeyboardButton("text", callback_data="data")
        b = InlineKeyboardButton("text", callback_data="data")
        c = InlineKeyboardButton("texts", callback_data="data")
        d = InlineKeyboardButton("text", callback_data="info")
        e = InlineKeyboardButton("text", url="http://google.com")
        f = InlineKeyboardButton("text", web_app=WebAppInfo(url="https://ptb.org"))
        g = LoginUrl("http://google.com")

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

    @pytest.mark.parametrize("callback_data", ["foo", 1, ("da", "ta"), object()])
    def test_update_callback_data(self, callback_data):
        button = InlineKeyboardButton(text="test", callback_data="data")
        button_b = InlineKeyboardButton(text="test", callback_data="data")

        assert button == button_b
        assert hash(button) == hash(button_b)

        button.update_callback_data(callback_data)
        assert button.callback_data is callback_data
        assert button != button_b
        assert hash(button) != hash(button_b)

        button_b.update_callback_data(callback_data)
        assert button_b.callback_data is callback_data
        assert button == button_b
        assert hash(button) == hash(button_b)

        button.update_callback_data({})
        assert button.callback_data == {}
        with pytest.raises(TypeError, match="unhashable"):
            hash(button)
