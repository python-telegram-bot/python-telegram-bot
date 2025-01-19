#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
    Dice,
    MenuButton,
    MenuButtonCommands,
    MenuButtonDefault,
    MenuButtonWebApp,
    WebAppInfo,
)
from telegram.constants import MenuButtonType
from tests.auxil.slots import mro_slots


@pytest.fixture
def menu_button():
    return MenuButton(MenuButtonTestBase.type)


class MenuButtonTestBase:
    type = MenuButtonType.DEFAULT
    text = "this is a test string"
    web_app = WebAppInfo(url="https://python-telegram-bot.org")


class TestMenuButtonWithoutRequest(MenuButtonTestBase):
    def test_slot_behaviour(self, menu_button):
        inst = menu_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, menu_button):
        assert type(MenuButton("default").type) is MenuButtonType
        assert MenuButton("unknown").type == "unknown"

    def test_de_json(self, offline_bot):
        data = {"type": "unknown"}
        transaction_partner = MenuButton.de_json(data, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "unknown"

    @pytest.mark.parametrize(
        ("mb_type", "subclass"),
        [
            ("commands", MenuButtonCommands),
            ("web_app", MenuButtonWebApp),
            ("default", MenuButtonDefault),
        ],
    )
    def test_de_json_subclass(self, offline_bot, mb_type, subclass):
        json_dict = {
            "type": mb_type,
            "web_app": self.web_app.to_dict(),
            "text": self.text,
        }
        mb = MenuButton.de_json(json_dict, offline_bot)

        assert type(mb) is subclass
        assert set(mb.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert mb.type == mb_type

    def test_to_dict(self, menu_button):
        assert menu_button.to_dict() == {"type": menu_button.type}

    def test_equality(self, menu_button):
        a = menu_button
        b = MenuButton(self.type)
        c = MenuButton("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def menu_button_commands():
    return MenuButtonCommands()


class TestMenuButtonCommandsWithoutRequest(MenuButtonTestBase):
    type = MenuButtonType.COMMANDS

    def test_slot_behaviour(self, menu_button_commands):
        inst = menu_button_commands
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = MenuButtonCommands.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "commands"

    def test_to_dict(self, menu_button_commands):
        assert menu_button_commands.to_dict() == {"type": menu_button_commands.type}

    def test_equality(self, menu_button_commands):
        a = menu_button_commands
        b = MenuButtonCommands()
        c = Dice(5, "test")
        d = MenuButtonDefault()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def menu_button_default():
    return MenuButtonDefault()


class TestMenuButtonDefaultWithoutRequest(MenuButtonTestBase):
    type = MenuButtonType.DEFAULT

    def test_slot_behaviour(self, menu_button_default):
        inst = menu_button_default
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        transaction_partner = MenuButtonDefault.de_json({}, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "default"

    def test_to_dict(self, menu_button_default):
        assert menu_button_default.to_dict() == {"type": menu_button_default.type}

    def test_equality(self, menu_button_default):
        a = menu_button_default
        b = MenuButtonDefault()
        c = Dice(5, "test")
        d = MenuButtonCommands()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def menu_button_web_app():
    return MenuButtonWebApp(
        web_app=TestMenuButtonWebAppWithoutRequest.web_app,
        text=TestMenuButtonWebAppWithoutRequest.text,
    )


class TestMenuButtonWebAppWithoutRequest(MenuButtonTestBase):
    type = MenuButtonType.WEB_APP

    def test_slot_behaviour(self, menu_button_web_app):
        inst = menu_button_web_app
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"web_app": self.web_app.to_dict(), "text": self.text}
        transaction_partner = MenuButtonWebApp.de_json(json_dict, offline_bot)
        assert transaction_partner.api_kwargs == {}
        assert transaction_partner.type == "web_app"
        assert transaction_partner.web_app == self.web_app
        assert transaction_partner.text == self.text

    def test_to_dict(self, menu_button_web_app):
        assert menu_button_web_app.to_dict() == {
            "type": menu_button_web_app.type,
            "web_app": menu_button_web_app.web_app.to_dict(),
            "text": menu_button_web_app.text,
        }

    def test_equality(self, menu_button_web_app):
        a = menu_button_web_app
        b = MenuButtonWebApp(web_app=self.web_app, text=self.text)
        c = MenuButtonWebApp(web_app=self.web_app, text="other text")
        d = MenuButtonWebApp(web_app=WebAppInfo(url="https://example.org"), text=self.text)
        e = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
