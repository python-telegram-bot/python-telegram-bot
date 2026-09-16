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

from telegram import (
    InputRichBlockParagraph,
    InputRichMessage,
    RichBlockParagraph,
    RichMessage,
    RichMessageButton,
    RichText,
    RichTextBold,
    RichTextCode,
    RichTextItalic,
    RichTextLink,
    RichTextPlain,
    RichTextSpoiler,
    RichTextStrikethrough,
    RichTextUnderline,
)
from tests.auxil.slots import mro_slots


class TestRichTextWithoutRequest:
    def test_plain_text(self, offline_bot):
        t = RichTextPlain(text="hello")
        assert t.text == "hello"
        assert t.to_dict() == "hello"
        obj = RichText.de_json("hello", offline_bot)
        assert isinstance(obj, RichTextPlain)
        assert obj.text == "hello"

    def test_bold_text(self, offline_bot):
        t = RichTextBold(text=RichTextPlain("bold text"))
        assert isinstance(t.text, RichTextPlain)
        assert t.to_dict() == {"type": "bold", "text": "bold text"}
        obj = RichText.de_json({"type": "bold", "text": "bold text"}, offline_bot)
        assert isinstance(obj, RichTextBold)
        assert obj.text == "bold text"

    def test_link_text(self, offline_bot):
        t = RichTextLink(text=RichTextPlain("link"), url="https://example.com")
        assert t.url == "https://example.com"
        assert t.to_dict() == {"type": "url", "text": "link", "url": "https://example.com"}
        obj = RichText.de_json({"type": "url", "text": "link", "url": "https://example.com"}, offline_bot)
        assert isinstance(obj, RichTextLink)
        assert obj.url == "https://example.com"


class TestRichBlockWithoutRequest:
    def test_rich_block_paragraph(self, offline_bot):
        block = RichBlockParagraph(text="Paragraph text")
        assert block.text == "Paragraph text"
        d = block.to_dict()
        assert d["text"] == "Paragraph text"
        assert d["type"] == "paragraph"

    def test_input_rich_block_paragraph(self, offline_bot):
        block = InputRichBlockParagraph(text="Input paragraph text")
        assert block.text == "Input paragraph text"
        d = block.to_dict()
        assert d["text"] == "Input paragraph text"
        assert d["type"] == "paragraph"


class TestRichMessageWithoutRequest:
    def test_rich_message_button(self, offline_bot):
        btn = RichMessageButton(text="Click me", url="https://example.com")
        assert btn.text == "Click me"
        assert btn.url == "https://example.com"
        d = btn.to_dict()
        assert d["text"] == "Click me"
        assert d["url"] == "https://example.com"
        obj = RichMessageButton.de_json(d, offline_bot)
        assert obj.text == "Click me"
        assert obj.url == "https://example.com"

    def test_rich_message(self, offline_bot):
        msg = RichMessage(
            blocks=[RichBlockParagraph(text="Hello rich world")],
        )
        assert len(msg.blocks) == 1
        d = msg.to_dict()
        assert len(d["blocks"]) == 1
        assert d["blocks"][0]["type"] == "paragraph"
        obj = RichMessage.de_json(d, offline_bot)
        assert isinstance(obj, RichMessage)
        assert len(obj.blocks) == 1
        assert isinstance(obj.blocks[0], RichBlockParagraph)

    def test_input_rich_message(self, offline_bot):
        msg = InputRichMessage(
            blocks=[InputRichBlockParagraph(text="Hello rich input")],
        )
        assert len(msg.blocks) == 1
        d = msg.to_dict()
        assert len(d["blocks"]) == 1
        assert d["blocks"][0]["type"] == "paragraph"
