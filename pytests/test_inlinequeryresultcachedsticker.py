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

from telegram import (InlineQueryResultCachedSticker, InputTextMessageContent, InlineQueryResultCachedVoice, InlineKeyboardMarkup, InlineKeyboardButton)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedSticker.type,
            'id': TestInlineQueryResultCachedSticker.id,
            'sticker_file_id': TestInlineQueryResultCachedSticker.sticker_file_id,
            'input_message_content': TestInlineQueryResultCachedSticker.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedSticker.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_sticker():
   return InlineQueryResultCachedSticker(type=TestInlineQueryResultCachedSticker.type, id=TestInlineQueryResultCachedSticker.id, sticker_file_id=TestInlineQueryResultCachedSticker.sticker_file_id, input_message_content=TestInlineQueryResultCachedSticker.input_message_content, reply_markup=TestInlineQueryResultCachedSticker.reply_markup)

class TestInlineQueryResultCachedSticker:
    """This object represents Tests for Telegram
    InlineQueryResultCachedSticker."""

    id = 'id'
    type = 'sticker'
    sticker_file_id = 'sticker file id'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_sticker_de_json(self):
        sticker = InlineQueryResultCachedSticker.de_json(json_dict, bot)

        assert sticker.type == self.type
        assert sticker.id == self.id
        assert sticker.sticker_file_id == self.sticker_file_id
        self.assertDictEqual(sticker.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert sticker.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_sticker_to_json(self):
        sticker = InlineQueryResultCachedSticker.de_json(json_dict, bot)

        json.loads(sticker.to_json())

    def test_sticker_to_dict(self):
        sticker = InlineQueryResultCachedSticker.de_json(json_dict,
                                                                  bot).to_dict()

        assert isinstance(sticker, dict)
        assert json_dict == sticker

    def test_equality(self):
        a = InlineQueryResultCachedSticker(self.id, self.sticker_file_id)
        b = InlineQueryResultCachedSticker(self.id, self.sticker_file_id)
        c = InlineQueryResultCachedSticker(self.id, "")
        d = InlineQueryResultCachedSticker("", self.sticker_file_id)
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


