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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultDocument,
                      InlineKeyboardMarkup, InlineQueryResultArticle)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'id': TestInlineQueryResultDocument.id,
        'type': TestInlineQueryResultDocument.type,
        'document_url': TestInlineQueryResultDocument.document_url,
        'title': TestInlineQueryResultDocument.title,
        'caption': TestInlineQueryResultDocument.caption,
        'mime_type': TestInlineQueryResultDocument.mime_type,
        'description': TestInlineQueryResultDocument.description,
        'thumb_url': TestInlineQueryResultDocument.thumb_url,
        'thumb_width': TestInlineQueryResultDocument.thumb_width,
        'thumb_height': TestInlineQueryResultDocument.thumb_height,
        'input_message_content': TestInlineQueryResultDocument.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultDocument.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_document():
    return InlineQueryResultDocument(id=TestInlineQueryResultDocument.id,
                                     type=TestInlineQueryResultDocument.type,
                                     document_url=TestInlineQueryResultDocument.document_url,
                                     title=TestInlineQueryResultDocument.title,
                                     caption=TestInlineQueryResultDocument.caption,
                                     mime_type=TestInlineQueryResultDocument.mime_type,
                                     description=TestInlineQueryResultDocument.description,
                                     thumb_url=TestInlineQueryResultDocument.thumb_url,
                                     thumb_width=TestInlineQueryResultDocument.thumb_width,
                                     thumb_height=TestInlineQueryResultDocument.thumb_height,
                                     input_message_content=TestInlineQueryResultDocument.input_message_content,
                                     reply_markup=TestInlineQueryResultDocument.reply_markup)


class TestInlineQueryResultDocument:
    """This object represents Tests for Telegram InlineQueryResultDocument."""

    id = 'id'
    type = 'document'
    document_url = 'document url'
    title = 'title'
    caption = 'caption'
    mime_type = 'mime type'
    description = 'description'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_document_de_json(self):
        document = InlineQueryResultDocument.de_json(json_dict, bot)

        assert document.id == self.id
        assert document.type == self.type
        assert document.document_url == self.document_url
        assert document.title == self.title
        assert document.caption == self.caption
        assert document.mime_type == self.mime_type
        assert document.description == self.description
        assert document.thumb_url == self.thumb_url
        assert document.thumb_width == self.thumb_width
        assert document.thumb_height == self.thumb_height
        self.assertDictEqual(document.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert document.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_document_to_json(self):
        document = InlineQueryResultDocument.de_json(json_dict, bot)

        json.loads(document.to_json())

    def test_document_to_dict(self):
        document = InlineQueryResultDocument.de_json(json_dict, bot).to_dict()

        assert isinstance(document, dict)
        assert json_dict == document

    def test_equality(self):
        a = InlineQueryResultDocument(self.id, self.document_url, self.title,
                                      self.mime_type)
        b = InlineQueryResultDocument(self.id, self.document_url, self.title,
                                      self.mime_type)
        c = InlineQueryResultDocument(self.id, "", self.title, self.mime_type)
        d = InlineQueryResultDocument("", self.document_url, self.title, self.mime_type)
        e = InlineQueryResultArticle(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
