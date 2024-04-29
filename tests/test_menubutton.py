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
from copy import deepcopy

import pytest

from telegram import (
    Dice,
    MenuButton,
    MenuButtonCommands,
    MenuButtonDefault,
    MenuButtonWebApp,
    WebAppInfo,
)
from telegram.constants import MenuButtonType
from tests.auxil.slots import mro_slots


@pytest.fixture(
    scope="module",
    params=[
        MenuButton.DEFAULT,
        MenuButton.WEB_APP,
        MenuButton.COMMANDS,
    ],
)
def scope_type(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        MenuButtonDefault,
        MenuButtonCommands,
        MenuButtonWebApp,
    ],
    ids=[
        MenuButton.DEFAULT,
        MenuButton.COMMANDS,
        MenuButton.WEB_APP,
    ],
)
def scope_class(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        (MenuButtonDefault, MenuButton.DEFAULT),
        (MenuButtonCommands, MenuButton.COMMANDS),
        (MenuButtonWebApp, MenuButton.WEB_APP),
    ],
    ids=[
        MenuButton.DEFAULT,
        MenuButton.COMMANDS,
        MenuButton.WEB_APP,
    ],
)
def scope_class_and_type(request):
    return request.param


@pytest.fixture(scope="module")
def menu_button(scope_class_and_type):
    # We use de_json here so that we don't have to worry about which class gets which arguments
    return scope_class_and_type[0].de_json(
        {
            "type": scope_class_and_type[1],
            "text": TestMenuButtonselfBase.text,
            "web_app": TestMenuButtonselfBase.web_app.to_dict(),
        },
        bot=None,
    )


class TestMenuButtonselfBase:
    text = "button_text"
    web_app = WebAppInfo(url="https://python-telegram-bot.org/web_app")


# All the scope types are very similar, so we test everything via parametrization
class TestMenuButtonWithoutRequest(TestMenuButtonselfBase):
    def test_slot_behaviour(self, menu_button):
        for attr in menu_button.__slots__:
            assert getattr(menu_button, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(menu_button)) == len(set(mro_slots(menu_button))), "duplicate slot"

    def test_de_json(self, bot, scope_class_and_type):
        cls = scope_class_and_type[0]
        type_ = scope_class_and_type[1]

        json_dict = {"type": type_, "text": self.text, "web_app": self.web_app.to_dict()}
        menu_button = MenuButton.de_json(json_dict, bot)
        assert set(menu_button.api_kwargs.keys()) == {"text", "web_app"} - set(cls.__slots__)

        assert isinstance(menu_button, MenuButton)
        assert type(menu_button) is cls
        assert menu_button.type == type_
        if "web_app" in cls.__slots__:
            assert menu_button.web_app == self.web_app
        if "text" in cls.__slots__:
            assert menu_button.text == self.text

        assert cls.de_json(None, bot) is None
        assert MenuButton.de_json({}, bot) is None

    def test_de_json_invalid_type(self, bot):
        json_dict = {"type": "invalid", "text": self.text, "web_app": self.web_app.to_dict()}
        menu_button = MenuButton.de_json(json_dict, bot)
        assert menu_button.api_kwargs == {"text": self.text, "web_app": self.web_app.to_dict()}

        assert type(menu_button) is MenuButton
        assert menu_button.type == "invalid"

    def test_de_json_subclass(self, scope_class, bot):
        """This makes sure that e.g. MenuButtonDefault(data) never returns a
        MenuButtonChat instance."""
        json_dict = {"type": "invalid", "text": self.text, "web_app": self.web_app.to_dict()}
        assert type(scope_class.de_json(json_dict, bot)) is scope_class

    def test_to_dict(self, menu_button):
        menu_button_dict = menu_button.to_dict()

        assert isinstance(menu_button_dict, dict)
        assert menu_button_dict["type"] == menu_button.type
        if hasattr(menu_button, "web_app"):
            assert menu_button_dict["web_app"] == menu_button.web_app.to_dict()
        if hasattr(menu_button, "text"):
            assert menu_button_dict["text"] == menu_button.text

    def test_type_enum_conversion(self):
        assert type(MenuButton("commands").type) is MenuButtonType
        assert MenuButton("unknown").type == "unknown"

    def test_equality(self, menu_button, bot):
        a = MenuButton("base_type")
        b = MenuButton("base_type")
        c = menu_button
        d = deepcopy(menu_button)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        if hasattr(c, "web_app"):
            json_dict = c.to_dict()
            json_dict["web_app"] = WebAppInfo("https://foo.bar/web_app").to_dict()
            f = c.__class__.de_json(json_dict, bot)

            assert c != f
            assert hash(c) != hash(f)

        if hasattr(c, "text"):
            json_dict = c.to_dict()
            json_dict["text"] = "other text"
            g = c.__class__.de_json(json_dict, bot)

            assert c != g
            assert hash(c) != hash(g)
