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
    InlineKeyboardMarkup,
    InlineQueryResultDocument,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_document():
    return InlineQueryResultDocument(
        Space.id_,
        Space.document_url,
        Space.title,
        Space.mime_type,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        description=Space.description,
        thumb_url=Space.thumb_url,
        thumb_width=Space.thumb_width,
        thumb_height=Space.thumb_height,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "document"
    document_url = "document url"
    title = "title"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    mime_type = "mime type"
    description = "description"
    thumb_url = "thumb url"
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultDocumentWithoutRequest:
    def test_slot_behaviour(self, inline_query_result_document, mro_slots):
        inst = inline_query_result_document
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_document):
        assert inline_query_result_document.id == Space.id_
        assert inline_query_result_document.type == Space.type_
        assert inline_query_result_document.document_url == Space.document_url
        assert inline_query_result_document.title == Space.title
        assert inline_query_result_document.caption == Space.caption
        assert inline_query_result_document.parse_mode == Space.parse_mode
        assert inline_query_result_document.caption_entities == tuple(Space.caption_entities)
        assert inline_query_result_document.mime_type == Space.mime_type
        assert inline_query_result_document.description == Space.description
        assert inline_query_result_document.thumb_url == Space.thumb_url
        assert inline_query_result_document.thumb_width == Space.thumb_width
        assert inline_query_result_document.thumb_height == Space.thumb_height
        assert (
            inline_query_result_document.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_document.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultDocument(
            Space.id_, Space.document_url, Space.title, Space.mime_type
        )
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
            inline_query_result_document_dict["thumb_url"]
            == inline_query_result_document.thumb_url
        )
        assert (
            inline_query_result_document_dict["thumb_width"]
            == inline_query_result_document.thumb_width
        )
        assert (
            inline_query_result_document_dict["thumb_height"]
            == inline_query_result_document.thumb_height
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
        a = InlineQueryResultDocument(Space.id_, Space.document_url, Space.title, Space.mime_type)
        b = InlineQueryResultDocument(Space.id_, Space.document_url, Space.title, Space.mime_type)
        c = InlineQueryResultDocument(Space.id_, "", Space.title, Space.mime_type)
        d = InlineQueryResultDocument("", Space.document_url, Space.title, Space.mime_type)
        e = InlineQueryResultVoice(Space.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
