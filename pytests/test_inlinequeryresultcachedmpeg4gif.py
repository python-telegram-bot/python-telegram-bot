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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultCachedMpeg4Gif, InlineQueryResultCachedVoice, InlineKeyboardMarkup)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedMpeg4Gif.type,
            'id': TestInlineQueryResultCachedMpeg4Gif.id,
            'mpeg4_file_id': TestInlineQueryResultCachedMpeg4Gif.mpeg4_file_id,
            'title': TestInlineQueryResultCachedMpeg4Gif.title,
            'caption': TestInlineQueryResultCachedMpeg4Gif.caption,
            'input_message_content': TestInlineQueryResultCachedMpeg4Gif.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedMpeg4Gif.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_mpeg4_gif():
   return InlineQueryResultCachedMpeg4Gif(type=TestInlineQueryResultCachedMpeg4Gif.type, id=TestInlineQueryResultCachedMpeg4Gif.id, mpeg4_file_id=TestInlineQueryResultCachedMpeg4Gif.mpeg4_file_id, title=TestInlineQueryResultCachedMpeg4Gif.title, caption=TestInlineQueryResultCachedMpeg4Gif.caption, input_message_content=TestInlineQueryResultCachedMpeg4Gif.input_message_content, reply_markup=TestInlineQueryResultCachedMpeg4Gif.reply_markup)

class TestInlineQueryResultCachedMpeg4Gif:
    """This object represents Tests for Telegram
    InlineQueryResultCachedMpeg4Gif."""

    id = 'id'
    type = 'mpeg4_gif'
    mpeg4_file_id = 'mpeg4 file id'
    title = 'title'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_mpeg4_de_json(self):
        mpeg4 = InlineQueryResultCachedMpeg4Gif.de_json(json_dict, bot)

        assert mpeg4.type == self.type
        assert mpeg4.id == self.id
        assert mpeg4.mpeg4_file_id == self.mpeg4_file_id
        assert mpeg4.title == self.title
        assert mpeg4.caption == self.caption
        self.assertDictEqual(mpeg4.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert mpeg4.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_mpeg4_to_json(self):
        mpeg4 = InlineQueryResultCachedMpeg4Gif.de_json(json_dict, bot)

        json.loads(mpeg4.to_json())

    def test_mpeg4_to_dict(self):
        mpeg4 = InlineQueryResultCachedMpeg4Gif.de_json(json_dict,
                                                                 bot).to_dict()

        assert isinstance(mpeg4, dict)
        assert json_dict == mpeg4

    def test_equality(self):
        a = InlineQueryResultCachedMpeg4Gif(self.id, self.mpeg4_file_id)
        b = InlineQueryResultCachedMpeg4Gif(self.id, self.mpeg4_file_id)
        c = InlineQueryResultCachedMpeg4Gif(self.id, "")
        d = InlineQueryResultCachedMpeg4Gif("", self.mpeg4_file_id)
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


