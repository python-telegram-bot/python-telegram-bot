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
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    WebAppInfo,
)
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def keyboard_button():
    return KeyboardButton(
        TestKeyboardButtonBase.text,
        request_location=TestKeyboardButtonBase.request_location,
        request_contact=TestKeyboardButtonBase.request_contact,
        request_poll=TestKeyboardButtonBase.request_poll,
        web_app=TestKeyboardButtonBase.web_app,
        request_chat=TestKeyboardButtonBase.request_chat,
        request_user=TestKeyboardButtonBase.request_user,
    )


class TestKeyboardButtonBase:
    text = "text"
    request_location = True
    request_contact = True
    request_poll = KeyboardButtonPollType("quiz")
    web_app = WebAppInfo(url="https://example.com")
    request_chat = KeyboardButtonRequestChat(1, True)
    request_user = KeyboardButtonRequestUser(2)


class TestKeyboardButtonWithoutRequest(TestKeyboardButtonBase):
    def test_slot_behaviour(self, keyboard_button):
        inst = keyboard_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, keyboard_button):
        assert keyboard_button.text == self.text
        assert keyboard_button.request_location == self.request_location
        assert keyboard_button.request_contact == self.request_contact
        assert keyboard_button.request_poll == self.request_poll
        assert keyboard_button.web_app == self.web_app
        assert keyboard_button.request_chat == self.request_chat
        assert keyboard_button.request_user == self.request_user

    def test_to_dict(self, keyboard_button):
        keyboard_button_dict = keyboard_button.to_dict()

        assert isinstance(keyboard_button_dict, dict)
        assert keyboard_button_dict["text"] == keyboard_button.text
        assert keyboard_button_dict["request_location"] == keyboard_button.request_location
        assert keyboard_button_dict["request_contact"] == keyboard_button.request_contact
        assert keyboard_button_dict["request_poll"] == keyboard_button.request_poll.to_dict()
        assert keyboard_button_dict["web_app"] == keyboard_button.web_app.to_dict()
        assert keyboard_button_dict["request_chat"] == keyboard_button.request_chat.to_dict()
        assert keyboard_button_dict["request_user"] == keyboard_button.request_user.to_dict()

    def test_de_json(self, bot):
        json_dict = {
            "text": self.text,
            "request_location": self.request_location,
            "request_contact": self.request_contact,
            "request_poll": self.request_poll.to_dict(),
            "web_app": self.web_app.to_dict(),
            "request_chat": self.request_chat.to_dict(),
            "request_user": self.request_user.to_dict(),
        }

        inline_keyboard_button = KeyboardButton.de_json(json_dict, None)
        assert inline_keyboard_button.api_kwargs == {}
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.request_location == self.request_location
        assert inline_keyboard_button.request_contact == self.request_contact
        assert inline_keyboard_button.request_poll == self.request_poll
        assert inline_keyboard_button.web_app == self.web_app
        assert inline_keyboard_button.request_chat == self.request_chat
        assert inline_keyboard_button.request_user == self.request_user

        none = KeyboardButton.de_json({}, None)
        assert none is None

    def test_equality(self):
        a = KeyboardButton("test", request_contact=True)
        b = KeyboardButton("test", request_contact=True)
        c = KeyboardButton("Test", request_location=True)
        d = KeyboardButton("Test", web_app=WebAppInfo(url="https://ptb.org"))
        e = InlineKeyboardButton("test", callback_data="test")
        f = KeyboardButton(
            "test",
            request_contact=True,
            request_chat=KeyboardButtonRequestChat(1, False),
            request_user=KeyboardButtonRequestUser(2),
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        # we expect this to be true since we don't compare these in V20
        assert a == f
        assert hash(a) == hash(f)

    def test_equality_warning(self, recwarn, keyboard_button):
        recwarn.clear()
        assert keyboard_button == keyboard_button

        assert str(recwarn[0].message) == (
            "In v21, granular media settings will be considered as well when comparing"
            " ChatPermissions instances."
        )
        assert recwarn[0].category is PTBDeprecationWarning
        assert recwarn[0].filename == __file__, "wrong stacklevel"
