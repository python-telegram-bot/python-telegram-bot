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

from telegram import (InlineKeyboardMarkup, InlineQueryResultAudio, InlineQueryResultArticle,
                      InlineKeyboardButton, InputTextMessageContent)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultArticle.type,
        'id': TestInlineQueryResultArticle.id,
        'title': TestInlineQueryResultArticle.title,
        'input_message_content': TestInlineQueryResultArticle.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultArticle.reply_markup.to_dict(),
        'url': TestInlineQueryResultArticle.url,
        'hide_url': TestInlineQueryResultArticle.hide_url,
        'description': TestInlineQueryResultArticle.description,
        'thumb_url': TestInlineQueryResultArticle.thumb_url,
        'thumb_height': TestInlineQueryResultArticle.thumb_height,
        'thumb_width': TestInlineQueryResultArticle.thumb_width
    }


@pytest.fixture(scope='class')
def inline_query_result_article():
    return InlineQueryResultArticle(type=TestInlineQueryResultArticle.type,
                                    id=TestInlineQueryResultArticle.id,
                                    title=TestInlineQueryResultArticle.title,
                                    input_message_content=TestInlineQueryResultArticle.input_message_content,
                                    reply_markup=TestInlineQueryResultArticle.reply_markup,
                                    url=TestInlineQueryResultArticle.url,
                                    hide_url=TestInlineQueryResultArticle.hide_url,
                                    description=TestInlineQueryResultArticle.description,
                                    thumb_url=TestInlineQueryResultArticle.thumb_url,
                                    thumb_height=TestInlineQueryResultArticle.thumb_height,
                                    thumb_width=TestInlineQueryResultArticle.thumb_width)


class TestInlineQueryResultArticle:
    """This object represents Tests for Telegram InlineQueryResultArticle."""

    id = 'id'
    type = 'article'
    title = 'title'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])
    url = 'url'
    hide_url = True
    description = 'description'
    thumb_url = 'thumb url'
    thumb_height = 10
    thumb_width = 15

    def test_article_de_json(self):
        article = InlineQueryResultArticle.de_json(json_dict, bot)

        assert article.type == self.type
        assert article.id == self.id
        assert article.title == self.title
        self.assertDictEqual(article.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert article.reply_markup.to_dict() == self.reply_markup.to_dict()
        assert article.url == self.url
        assert article.hide_url == self.hide_url
        assert article.description == self.description
        assert article.thumb_url == self.thumb_url
        assert article.thumb_height == self.thumb_height
        assert article.thumb_width == self.thumb_width

    def test_article_to_json(self):
        article = InlineQueryResultArticle.de_json(json_dict, bot)

        json.loads(article.to_json())

    def test_article_to_dict(self):
        article = InlineQueryResultArticle.de_json(json_dict, bot).to_dict()

        assert isinstance(article, dict)
        assert json_dict == article

    def test_equality(self):
        a = InlineQueryResultArticle(self.id, self.title, self.input_message_content)
        b = InlineQueryResultArticle(self.id, self.title, self.input_message_content)
        c = InlineQueryResultArticle(self.id, "", self.input_message_content)
        d = InlineQueryResultArticle("", self.title, self.input_message_content)
        e = InlineQueryResultAudio(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
