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
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultDocument,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_document():
    return InlineQueryResultDocument(
        TestInlineQueryResultDocumentBase.id_,
        TestInlineQueryResultDocumentBase.document_url,
        TestInlineQueryResultDocumentBase.title,
        TestInlineQueryResultDocumentBase.mime_type,
        caption=TestInlineQueryResultDocumentBase.caption,
        parse_mode=TestInlineQueryResultDocumentBase.parse_mode,
        caption_entities=TestInlineQueryResultDocumentBase.caption_entities,
        description=TestInlineQueryResultDocumentBase.description,
        thumbnail_url=TestInlineQueryResultDocumentBase.thumbnail_url,
        thumbnail_width=TestInlineQueryResultDocumentBase.thumbnail_width,
        thumbnail_height=TestInlineQueryResultDocumentBase.thumbnail_height,
        input_message_content=TestInlineQueryResultDocumentBase.input_message_content,
        reply_markup=TestInlineQueryResultDocumentBase.reply_markup,
    )


class TestInlineQueryResultDocumentBase:
    id_ = "id"
    type_ = "document"
    document_url = "document url"
    title = "title"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    mime_type = "mime type"
    description = "description"
    thumbnail_url = "thumb url"
    thumbnail_width = 10
    thumbnail_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultDocumentWithoutRequest(TestInlineQueryResultDocumentBase):
    def test_slot_behaviour(self, inline_query_result_document):
        inst = inline_query_result_document
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_document):
        assert inline_query_result_document.id == self.id_
        assert inline_query_result_document.type == self.type_
        assert inline_query_result_document.document_url == self.document_url
        assert inline_query_result_document.title == self.title
        assert inline_query_result_document.caption == self.caption
        assert inline_query_result_document.parse_mode == self.parse_mode
        assert inline_query_result_document.caption_entities == tuple(self.caption_entities)
        assert inline_query_result_document.mime_type == self.mime_type
        assert inline_query_result_document.description == self.description
        assert inline_query_result_document.thumbnail_url == self.thumbnail_url
        assert inline_query_result_document.thumbnail_width == self.thumbnail_width
        assert inline_query_result_document.thumbnail_height == self.thumbnail_height
        assert (
            inline_query_result_document.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_document.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultDocument(self.id_, self.document_url, self.title, self.mime_type)
        assert result.caption_entities == ()

    def test_to_dict(self, inline_query_result_document):
        inline_query_result_document_dict = inline_query_result_document.to_dict()

        assert isinstance(inline_query_result_document_dict, dict)
        assert inline_query_result_document_dict["id"] == inline_query_result_document.id
        assert inline_query_result_document_dict["type"] == inline_query_result_document.type
        assert (
            inline_query_result_document_dict["document_url"]
            == inline_query_result_document.document_url
        )
        assert inline_query_result_document_dict["title"] == inline_query_result_document.title
        assert inline_query_result_document_dict["caption"] == inline_query_result_document.caption
        assert (
            inline_query_result_document_dict["parse_mode"]
            == inline_query_result_document.parse_mode
        )
        assert inline_query_result_document_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_document.caption_entities
        ]
        assert (
            inline_query_result_document_dict["mime_type"]
            == inline_query_result_document.mime_type
        )
        assert (
            inline_query_result_document_dict["description"]
            == inline_query_result_document.description
        )
        assert (
            inline_query_result_document_dict["thumbnail_url"]
            == inline_query_result_document.thumbnail_url
        )
        assert (
            inline_query_result_document_dict["thumbnail_width"]
            == inline_query_result_document.thumbnail_width
        )
        assert (
            inline_query_result_document_dict["thumbnail_height"]
            == inline_query_result_document.thumbnail_height
        )
        assert (
            inline_query_result_document_dict["input_message_content"]
            == inline_query_result_document.input_message_content.to_dict()
        )
        assert (
            inline_query_result_document_dict["reply_markup"]
            == inline_query_result_document.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultDocument(self.id_, self.document_url, self.title, self.mime_type)
        b = InlineQueryResultDocument(self.id_, self.document_url, self.title, self.mime_type)
        c = InlineQueryResultDocument(self.id_, "", self.title, self.mime_type)
        d = InlineQueryResultDocument("", self.document_url, self.title, self.mime_type)
        e = InlineQueryResultVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
