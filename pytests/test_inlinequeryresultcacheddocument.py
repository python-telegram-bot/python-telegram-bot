#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import (InlineKeyboardButton, InlineQueryResultCachedDocument, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultCachedVoice)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'id': TestInlineQueryResultCachedDocument.id,
            'type': TestInlineQueryResultCachedDocument.type,
            'document_file_id': TestInlineQueryResultCachedDocument.document_file_id,
            'title': TestInlineQueryResultCachedDocument.title,
            'caption': TestInlineQueryResultCachedDocument.caption,
            'description': TestInlineQueryResultCachedDocument.description,
            'input_message_content': TestInlineQueryResultCachedDocument.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedDocument.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_document():
   return InlineQueryResultCachedDocument(id=TestInlineQueryResultCachedDocument.id, type=TestInlineQueryResultCachedDocument.type, document_file_id=TestInlineQueryResultCachedDocument.document_file_id, title=TestInlineQueryResultCachedDocument.title, caption=TestInlineQueryResultCachedDocument.caption, description=TestInlineQueryResultCachedDocument.description, input_message_content=TestInlineQueryResultCachedDocument.input_message_content, reply_markup=TestInlineQueryResultCachedDocument.reply_markup)

class TestInlineQueryResultCachedDocument:
    """This object represents Tests for Telegram
    InlineQueryResultCachedDocument."""

    id = 'id'
    type = 'document'
    document_file_id = 'document file id'
    title = 'title'
    caption = 'caption'
    description = 'description'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    def test_document_de_json(self):
        document = InlineQueryResultCachedDocument.de_json(json_dict, bot)

        assert document.id == self.id
        assert document.type == self.type
        assert document.document_file_id == self.document_file_id
        assert document.title == self.title
        assert document.caption == self.caption
        assert document.description == self.description
        self.assertDictEqual(document.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert document.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_document_to_json(self):
        document = InlineQueryResultCachedDocument.de_json(json_dict, bot)

        json.loads(document.to_json())

    def test_document_to_dict(self):
        document = InlineQueryResultCachedDocument.de_json(json_dict,
                                                                    bot).to_dict()

        assert isinstance(document, dict)
        assert json_dict == document

    def test_equality(self):
        a = InlineQueryResultCachedDocument(self.id, self.title, self.document_file_id)
        b = InlineQueryResultCachedDocument(self.id, self.title, self.document_file_id)
        c = InlineQueryResultCachedDocument(self.id, self.title, "")
        d = InlineQueryResultCachedDocument("", self.title, self.document_file_id)
        e = InlineQueryResultCachedVoice(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


