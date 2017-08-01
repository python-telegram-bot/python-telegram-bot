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

from telegram import (InlineQueryResultMpeg4Gif, InlineKeyboardButton, InlineQueryResultArticle,
                      InlineKeyboardMarkup, InputTextMessageContent)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultMpeg4Gif.type,
        'id': TestInlineQueryResultMpeg4Gif.id,
        'mpeg4_url': TestInlineQueryResultMpeg4Gif.mpeg4_url,
        'mpeg4_width': TestInlineQueryResultMpeg4Gif.mpeg4_width,
        'mpeg4_height': TestInlineQueryResultMpeg4Gif.mpeg4_height,
        'mpeg4_duration': TestInlineQueryResultMpeg4Gif.mpeg4_duration,
        'thumb_url': TestInlineQueryResultMpeg4Gif.thumb_url,
        'title': TestInlineQueryResultMpeg4Gif.title,
        'caption': TestInlineQueryResultMpeg4Gif.caption,
        'input_message_content': TestInlineQueryResultMpeg4Gif.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultMpeg4Gif.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_mpeg4_gif():
    return InlineQueryResultMpeg4Gif(type=TestInlineQueryResultMpeg4Gif.type,
                                     id=TestInlineQueryResultMpeg4Gif.id,
                                     mpeg4_url=TestInlineQueryResultMpeg4Gif.mpeg4_url,
                                     mpeg4_width=TestInlineQueryResultMpeg4Gif.mpeg4_width,
                                     mpeg4_height=TestInlineQueryResultMpeg4Gif.mpeg4_height,
                                     mpeg4_duration=TestInlineQueryResultMpeg4Gif.mpeg4_duration,
                                     thumb_url=TestInlineQueryResultMpeg4Gif.thumb_url,
                                     title=TestInlineQueryResultMpeg4Gif.title,
                                     caption=TestInlineQueryResultMpeg4Gif.caption,
                                     input_message_content=TestInlineQueryResultMpeg4Gif.input_message_content,
                                     reply_markup=TestInlineQueryResultMpeg4Gif.reply_markup)


class TestInlineQueryResultMpeg4Gif:
    """This object represents Tests for Telegram InlineQueryResultMpeg4Gif."""

    id = 'id'
    type = 'mpeg4_gif'
    mpeg4_url = 'mpeg4 url'
    mpeg4_width = 10
    mpeg4_height = 15
    mpeg4_duration = 1
    thumb_url = 'thumb url'
    title = 'title'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_mpeg4_de_json(self):
        mpeg4 = InlineQueryResultMpeg4Gif.de_json(json_dict, bot)

        assert mpeg4.type == self.type
        assert mpeg4.id == self.id
        assert mpeg4.mpeg4_url == self.mpeg4_url
        assert mpeg4.mpeg4_width == self.mpeg4_width
        assert mpeg4.mpeg4_height == self.mpeg4_height
        assert mpeg4.mpeg4_duration == self.mpeg4_duration
        assert mpeg4.thumb_url == self.thumb_url
        assert mpeg4.title == self.title
        assert mpeg4.caption == self.caption
        self.assertDictEqual(mpeg4.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert mpeg4.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_mpeg4_to_json(self):
        mpeg4 = InlineQueryResultMpeg4Gif.de_json(json_dict, bot)

        json.loads(mpeg4.to_json())

    def test_mpeg4_to_dict(self):
        mpeg4 = InlineQueryResultMpeg4Gif.de_json(json_dict, bot).to_dict()

        assert isinstance(mpeg4, dict)
        assert json_dict == mpeg4

    def test_equality(self):
        a = InlineQueryResultMpeg4Gif(self.id, self.mpeg4_url, self.thumb_url)
        b = InlineQueryResultMpeg4Gif(self.id, self.mpeg4_url, self.thumb_url)
        c = InlineQueryResultMpeg4Gif(self.id, "", self.thumb_url)
        d = InlineQueryResultMpeg4Gif("", self.mpeg4_url, self.thumb_url)
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
