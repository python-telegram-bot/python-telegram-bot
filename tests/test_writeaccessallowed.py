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

from telegram import WriteAccessAllowed
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


class TestWriteAccessAllowed(DeserializationTestBase):
    de_json_class = WriteAccessAllowed
    web_app_name = "web_app_name"
    from_request = True
    from_attachment_menu = False

    @pytest.fixture
    def de_json_dict(self):
        return {
            "web_app_name": self.web_app_name,
            "from_request": self.from_request,
            "from_attachment_menu": self.from_attachment_menu,
        }

    def test_slot_behaviour(self):
        action = WriteAccessAllowed()
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        action = WriteAccessAllowed.de_json(de_json_dict, offline_bot)
        assert action.api_kwargs == {}
        assert isinstance(action, WriteAccessAllowed)

        assert action.web_app_name == self.web_app_name
        assert action.from_request == self.from_request
        assert action.from_attachment_menu == self.from_attachment_menu

    def test_to_dict(self):
        action = WriteAccessAllowed()
        action_dict = action.to_dict()
        assert action_dict == {}

    def test_equality(self):
        a = WriteAccessAllowed()
        b = WriteAccessAllowed()
        c = WriteAccessAllowed(web_app_name="foo")
        d = WriteAccessAllowed(web_app_name="foo")
        e = WriteAccessAllowed(web_app_name="bar")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)
