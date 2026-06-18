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

from telegram import Dice, InputRichMessage, InputRichMessageContent
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_rich_message():
    return InputRichMessage(
        html=InputRichMessageTestBase.html,
        is_rtl=InputRichMessageTestBase.is_rtl,
        skip_entity_detection=InputRichMessageTestBase.skip_entity_detection,
    )


class InputRichMessageTestBase:
    html = "<b>bold</b>"
    markdown = "**bold**"
    is_rtl = True
    skip_entity_detection = False


class TestInputRichMessageWithoutRequest(InputRichMessageTestBase):
    def test_slot_behaviour(self, input_rich_message):
        for attr in input_rich_message.__slots__:
            assert getattr(input_rich_message, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(input_rich_message)) == len(set(mro_slots(input_rich_message))), (
            "duplicate slot"
        )

    def test_expected_values(self, input_rich_message):
        assert input_rich_message.html == self.html
        assert input_rich_message.markdown is None
        assert input_rich_message.is_rtl == self.is_rtl
        assert input_rich_message.skip_entity_detection == self.skip_entity_detection

    def test_to_dict(self, input_rich_message):
        irm_dict = input_rich_message.to_dict()

        assert isinstance(irm_dict, dict)
        assert irm_dict["html"] == self.html
        assert irm_dict["is_rtl"] == self.is_rtl
        assert irm_dict["skip_entity_detection"] == self.skip_entity_detection
        assert "markdown" not in irm_dict

    def test_equality(self, input_rich_message):
        a = input_rich_message
        b = InputRichMessage(html=self.html, is_rtl=False)
        c = InputRichMessage(markdown=self.markdown)
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def input_rich_message_content(input_rich_message):
    return InputRichMessageContent(input_rich_message)


class TestInputRichMessageContentWithoutRequest:
    def test_slot_behaviour(self, input_rich_message_content):
        for attr in input_rich_message_content.__slots__:
            assert getattr(input_rich_message_content, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(input_rich_message_content)) == len(
            set(mro_slots(input_rich_message_content))
        ), "duplicate slot"

    def test_expected_values(self, input_rich_message_content, input_rich_message):
        assert input_rich_message_content.rich_message == input_rich_message

    def test_to_dict(self, input_rich_message_content, input_rich_message):
        irmc_dict = input_rich_message_content.to_dict()

        assert isinstance(irmc_dict, dict)
        assert irmc_dict["rich_message"] == input_rich_message.to_dict()

    def test_equality(self, input_rich_message_content, input_rich_message):
        a = input_rich_message_content
        b = InputRichMessageContent(InputRichMessage(html=input_rich_message.html))
        c = InputRichMessageContent(InputRichMessage(markdown="**other**"))
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
