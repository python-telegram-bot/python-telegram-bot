#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
    InlineQueryResultCachedDocument,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputTextMessageContent,
    InlineQueryResultCachedVoice,
    MessageEntity,
)


@pytest.fixture(scope='class')
def inline_query_result_cached_document():
    return InlineQueryResultCachedDocument(
        TestInlineQueryResultCachedDocument.id_,
        TestInlineQueryResultCachedDocument.title,
        TestInlineQueryResultCachedDocument.document_file_id,
        caption=TestInlineQueryResultCachedDocument.caption,
        parse_mode=TestInlineQueryResultCachedDocument.parse_mode,
        caption_entities=TestInlineQueryResultCachedDocument.caption_entities,
        description=TestInlineQueryResultCachedDocument.description,
        input_message_content=TestInlineQueryResultCachedDocument.input_message_content,
        reply_markup=TestInlineQueryResultCachedDocument.reply_markup,
    )


class TestInlineQueryResultCachedDocument:
    id_ = 'id'
    type_ = 'document'
    document_file_id = 'document file id'
    title = 'title'
    caption = 'caption'
    parse_mode = 'Markdown'
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    description = 'description'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_slot_behaviour(self, inline_query_result_cached_document, mro_slots, recwarn):
        inst = inline_query_result_cached_document
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.id = 'should give warning', self.id_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, inline_query_result_cached_document):
        assert inline_query_result_cached_document.id == self.id_
        assert inline_query_result_cached_document.type == self.type_
        assert inline_query_result_cached_document.document_file_id == self.document_file_id
        assert inline_query_result_cached_document.title == self.title
        assert inline_query_result_cached_document.caption == self.caption
        assert inline_query_result_cached_document.parse_mode == self.parse_mode
        assert inline_query_result_cached_document.caption_entities == self.caption_entities
        assert inline_query_result_cached_document.description == self.description
        assert (
            inline_query_result_cached_document.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_document.reply_markup.to_dict()
            == self.reply_markup.to_dict()
        )

    def test_to_dict(self, inline_query_result_cached_document):
        inline_query_result_cached_document_dict = inline_query_result_cached_document.to_dict()

        assert isinstance(inline_query_result_cached_document_dict, dict)
        assert (
            inline_query_result_cached_document_dict['id']
            == inline_query_result_cached_document.id
        )
        assert (
            inline_query_result_cached_document_dict['type']
            == inline_query_result_cached_document.type
        )
        assert (
            inline_query_result_cached_document_dict['document_file_id']
            == inline_query_result_cached_document.document_file_id
        )
        assert (
            inline_query_result_cached_document_dict['title']
            == inline_query_result_cached_document.title
        )
        assert (
            inline_query_result_cached_document_dict['caption']
            == inline_query_result_cached_document.caption
        )
        assert (
            inline_query_result_cached_document_dict['parse_mode']
            == inline_query_result_cached_document.parse_mode
        )
        assert inline_query_result_cached_document_dict['caption_entities'] == [
            ce.to_dict() for ce in inline_query_result_cached_document.caption_entities
        ]
        assert (
            inline_query_result_cached_document_dict['description']
            == inline_query_result_cached_document.description
        )
        assert (
            inline_query_result_cached_document_dict['input_message_content']
            == inline_query_result_cached_document.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_document_dict['reply_markup']
            == inline_query_result_cached_document.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultCachedDocument(self.id_, self.title, self.document_file_id)
        b = InlineQueryResultCachedDocument(self.id_, self.title, self.document_file_id)
        c = InlineQueryResultCachedDocument(self.id_, self.title, '')
        d = InlineQueryResultCachedDocument('', self.title, self.document_file_id)
        e = InlineQueryResultCachedVoice(self.id_, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
