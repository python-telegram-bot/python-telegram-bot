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

from telegram import InputTextMessageContent, LinkPreviewOptions, MessageEntity
from telegram.constants import ParseMode
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_text_message_content():
    return InputTextMessageContent(
        TestInputTextMessageContentBase.message_text,
        parse_mode=TestInputTextMessageContentBase.parse_mode,
        entities=TestInputTextMessageContentBase.entities,
        link_preview_options=TestInputTextMessageContentBase.link_preview_options,
    )


class TestInputTextMessageContentBase:
    message_text = "*message text*"
    parse_mode = ParseMode.MARKDOWN
    entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    disable_web_page_preview = False
    link_preview_options = LinkPreviewOptions(False, url="https://python-telegram-bot.org")


class TestInputTextMessageContentWithoutRequest(TestInputTextMessageContentBase):
    def test_slot_behaviour(self, input_text_message_content):
        inst = input_text_message_content
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_text_message_content):
        assert input_text_message_content.parse_mode == self.parse_mode
        assert input_text_message_content.message_text == self.message_text
        assert input_text_message_content.entities == tuple(self.entities)
        assert input_text_message_content.link_preview_options == self.link_preview_options

    def test_entities_always_tuple(self):
        input_text_message_content = InputTextMessageContent("text")
        assert input_text_message_content.entities == ()

    def test_to_dict(self, input_text_message_content):
        input_text_message_content_dict = input_text_message_content.to_dict()

        assert isinstance(input_text_message_content_dict, dict)
        assert (
            input_text_message_content_dict["message_text"]
            == input_text_message_content.message_text
        )
        assert (
            input_text_message_content_dict["parse_mode"] == input_text_message_content.parse_mode
        )
        assert input_text_message_content_dict["entities"] == [
            ce.to_dict() for ce in input_text_message_content.entities
        ]
        assert (
            input_text_message_content_dict["link_preview_options"]
            == input_text_message_content.link_preview_options.to_dict()
        )

    def test_equality(self):
        a = InputTextMessageContent("text")
        b = InputTextMessageContent("text", parse_mode=ParseMode.HTML)
        c = InputTextMessageContent("label")
        d = ParseMode.HTML

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

    def test_mutually_exclusive(self):
        with pytest.raises(ValueError, match="`link_preview_options` are mutually exclusive"):
            InputTextMessageContent(
                "text", disable_web_page_preview=True, link_preview_options=LinkPreviewOptions()
            )

    def test_disable_web_page_preview_deprecation(self):
        itmc = InputTextMessageContent("text", disable_web_page_preview=True)
        assert itmc.link_preview_options.is_disabled is True
