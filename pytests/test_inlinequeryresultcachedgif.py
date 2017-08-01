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

from telegram import (InlineKeyboardMarkup, InlineQueryResultCachedVoice, InlineKeyboardButton, InputTextMessageContent, InlineQueryResultCachedGif)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedGif.type,
            'id': TestInlineQueryResultCachedGif.id,
            'gif_file_id': TestInlineQueryResultCachedGif.gif_file_id,
            'title': TestInlineQueryResultCachedGif.title,
            'caption': TestInlineQueryResultCachedGif.caption,
            'input_message_content': TestInlineQueryResultCachedGif.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedGif.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_gif():
   return InlineQueryResultCachedGif(type=TestInlineQueryResultCachedGif.type, id=TestInlineQueryResultCachedGif.id, gif_file_id=TestInlineQueryResultCachedGif.gif_file_id, title=TestInlineQueryResultCachedGif.title, caption=TestInlineQueryResultCachedGif.caption, input_message_content=TestInlineQueryResultCachedGif.input_message_content, reply_markup=TestInlineQueryResultCachedGif.reply_markup)

class TestInlineQueryResultCachedGif:
    """This object represents Tests for Telegram InlineQueryResultCachedGif."""

    id = 'id'
    type = 'gif'
    gif_file_id = 'gif file id'
    title = 'title'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_gif_de_json(self):
        gif = InlineQueryResultCachedGif.de_json(json_dict, bot)

        assert gif.type == self.type
        assert gif.id == self.id
        assert gif.gif_file_id == self.gif_file_id
        assert gif.title == self.title
        assert gif.caption == self.caption
        self.assertDictEqual(gif.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert gif.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_gif_to_json(self):
        gif = InlineQueryResultCachedGif.de_json(json_dict, bot)

        json.loads(gif.to_json())

    def test_gif_to_dict(self):
        gif = InlineQueryResultCachedGif.de_json(json_dict, bot).to_dict()

        assert isinstance(gif, dict)
        assert json_dict == gif

    def test_equality(self):
        a = InlineQueryResultCachedGif(self.id, self.gif_file_id)
        b = InlineQueryResultCachedGif(self.id, self.gif_file_id)
        c = InlineQueryResultCachedGif(self.id, "")
        d = InlineQueryResultCachedGif("", self.gif_file_id)
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


