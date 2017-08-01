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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultGif,
                      InlineQueryResultArticle, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultGif.type,
        'id': TestInlineQueryResultGif.id,
        'gif_url': TestInlineQueryResultGif.gif_url,
        'gif_width': TestInlineQueryResultGif.gif_width,
        'gif_height': TestInlineQueryResultGif.gif_height,
        'gif_duration': TestInlineQueryResultGif.gif_duration,
        'thumb_url': TestInlineQueryResultGif.thumb_url,
        'title': TestInlineQueryResultGif.title,
        'caption': TestInlineQueryResultGif.caption,
        'input_message_content': TestInlineQueryResultGif.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultGif.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_gif():
    return InlineQueryResultGif(type=TestInlineQueryResultGif.type, id=TestInlineQueryResultGif.id,
                                gif_url=TestInlineQueryResultGif.gif_url,
                                gif_width=TestInlineQueryResultGif.gif_width,
                                gif_height=TestInlineQueryResultGif.gif_height,
                                gif_duration=TestInlineQueryResultGif.gif_duration,
                                thumb_url=TestInlineQueryResultGif.thumb_url,
                                title=TestInlineQueryResultGif.title,
                                caption=TestInlineQueryResultGif.caption,
                                input_message_content=TestInlineQueryResultGif.input_message_content,
                                reply_markup=TestInlineQueryResultGif.reply_markup)


class TestInlineQueryResultGif:
    """This object represents Tests for Telegram InlineQueryResultGif."""

    id = 'id'
    type = 'gif'
    gif_url = 'gif url'
    gif_width = 10
    gif_height = 15
    gif_duration = 1
    thumb_url = 'thumb url'
    title = 'title'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_gif_de_json(self):
        gif = InlineQueryResultGif.de_json(json_dict, bot)

        assert gif.type == self.type
        assert gif.id == self.id
        assert gif.gif_url == self.gif_url
        assert gif.gif_width == self.gif_width
        assert gif.gif_height == self.gif_height
        assert gif.gif_duration == self.gif_duration
        assert gif.thumb_url == self.thumb_url
        assert gif.title == self.title
        assert gif.caption == self.caption
        self.assertDictEqual(gif.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert gif.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_gif_to_json(self):
        gif = InlineQueryResultGif.de_json(json_dict, bot)

        json.loads(gif.to_json())

    def test_gif_to_dict(self):
        gif = InlineQueryResultGif.de_json(json_dict, bot).to_dict()

        assert isinstance(gif, dict)
        assert json_dict == gif

    def test_equality(self):
        a = InlineQueryResultGif(self.id, self.gif_url, self.thumb_url)
        b = InlineQueryResultGif(self.id, self.gif_url, self.thumb_url)
        c = InlineQueryResultGif(self.id, "", self.thumb_url)
        d = InlineQueryResultGif("", self.gif_url, self.thumb_url)
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
