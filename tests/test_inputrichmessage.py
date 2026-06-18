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

from telegram import InputRichMessage, InputRichMessageContent
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_rich_message():
    return InputRichMessage(
        html=InputRichMessageTestBase.html,
        is_rtl=InputRichMessageTestBase.is_rtl,
        skip_entity_detection=InputRichMessageTestBase.skip_entity_detection,
    )


class InputRichMessageTestBase:
    html = "<h3>Report</h3><blockquote>Body</blockquote>"
    markdown = "# Report\n\n> Body"
    is_rtl = True
    skip_entity_detection = True


class TestInputRichMessageWithoutRequest(InputRichMessageTestBase):
    def test_slot_behaviour(self, input_rich_message):
        a = input_rich_message
        for attr in a.__slots__:
            assert getattr(a, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(a)) == len(set(mro_slots(a))), "duplicate slot"

    def test_to_dict(self, input_rich_message):
        input_rich_message_dict = input_rich_message.to_dict()

        assert isinstance(input_rich_message_dict, dict)
        assert input_rich_message_dict["html"] == self.html
        assert input_rich_message_dict["is_rtl"] == self.is_rtl
        assert input_rich_message_dict["skip_entity_detection"] == self.skip_entity_detection
        # Unset fields are omitted
        assert "markdown" not in input_rich_message_dict

    def test_de_json(self):
        input_rich_message_dict = {
            "markdown": self.markdown,
            "is_rtl": self.is_rtl,
            "skip_entity_detection": self.skip_entity_detection,
        }

        input_rich_message = InputRichMessage.de_json(input_rich_message_dict, bot=None)
        assert input_rich_message.api_kwargs == {}

        assert input_rich_message.markdown == self.markdown
        assert input_rich_message.html is None
        assert input_rich_message.is_rtl == self.is_rtl
        assert input_rich_message.skip_entity_detection == self.skip_entity_detection

    def test_equality(self):
        a = InputRichMessage(html=self.html, is_rtl=self.is_rtl)
        b = InputRichMessage(html=self.html, is_rtl=self.is_rtl)
        c = InputRichMessage(html=self.html)
        d = InputRichMessage(markdown=self.markdown)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestInputRichMessageContentWithoutRequest(InputRichMessageTestBase):
    def test_slot_behaviour(self, input_rich_message):
        inst = InputRichMessageContent(rich_message=input_rich_message)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"

    def test_to_dict(self, input_rich_message):
        inst = InputRichMessageContent(rich_message=input_rich_message)
        assert inst.to_dict() == {"rich_message": input_rich_message.to_dict()}

    def test_equality(self):
        rich_message = InputRichMessage(markdown=self.markdown)
        a = InputRichMessageContent(rich_message=rich_message)
        b = InputRichMessageContent(rich_message=rich_message)
        c = InputRichMessageContent(rich_message=InputRichMessage(html=self.html))

        assert a == b
        assert hash(a) == hash(b)
        assert a != c
        assert hash(a) != hash(c)
