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

from telegram import BotCommand, CopyTextButton
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def copy_text_button():
    return CopyTextButton(text=CopyTextButtonTestBase.text)


class CopyTextButtonTestBase:
    text = "This is some text"


class TestCopyTextButtonWithoutRequest(CopyTextButtonTestBase):
    def test_slot_behaviour(self, copy_text_button):
        for attr in copy_text_button.__slots__:
            assert getattr(copy_text_button, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(copy_text_button)) == len(
            set(mro_slots(copy_text_button))
        ), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"text": self.text}
        copy_text_button = CopyTextButton.de_json(json_dict, offline_bot)
        assert copy_text_button.api_kwargs == {}

        assert copy_text_button.text == self.text

    def test_to_dict(self, copy_text_button):
        copy_text_button_dict = copy_text_button.to_dict()

        assert isinstance(copy_text_button_dict, dict)
        assert copy_text_button_dict["text"] == copy_text_button.text

    def test_equality(self):
        a = CopyTextButton(self.text)
        b = CopyTextButton(self.text)
        c = CopyTextButton("text")
        d = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
