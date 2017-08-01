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

from telegram import (InlineQueryResultCachedVoice, InlineKeyboardButton, InputTextMessageContent, InlineKeyboardMarkup, InlineQueryResultCachedPhoto)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedPhoto.type,
            'id': TestInlineQueryResultCachedPhoto.id,
            'photo_file_id': TestInlineQueryResultCachedPhoto.photo_file_id,
            'title': TestInlineQueryResultCachedPhoto.title,
            'description': TestInlineQueryResultCachedPhoto.description,
            'caption': TestInlineQueryResultCachedPhoto.caption,
            'input_message_content': TestInlineQueryResultCachedPhoto.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedPhoto.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_photo():
   return InlineQueryResultCachedPhoto(type=TestInlineQueryResultCachedPhoto.type, id=TestInlineQueryResultCachedPhoto.id, photo_file_id=TestInlineQueryResultCachedPhoto.photo_file_id, title=TestInlineQueryResultCachedPhoto.title, description=TestInlineQueryResultCachedPhoto.description, caption=TestInlineQueryResultCachedPhoto.caption, input_message_content=TestInlineQueryResultCachedPhoto.input_message_content, reply_markup=TestInlineQueryResultCachedPhoto.reply_markup)

class TestInlineQueryResultCachedPhoto:
    """This object represents Tests for Telegram
    InlineQueryResultCachedPhoto."""

    id = 'id'
    type = 'photo'
    photo_file_id = 'photo file id'
    title = 'title'
    description = 'description'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_photo_de_json(self):
        photo = InlineQueryResultCachedPhoto.de_json(json_dict, bot)

        assert photo.type == self.type
        assert photo.id == self.id
        assert photo.photo_file_id == self.photo_file_id
        assert photo.title == self.title
        assert photo.description == self.description
        assert photo.caption == self.caption
        self.assertDictEqual(photo.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert photo.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_photo_to_json(self):
        photo = InlineQueryResultCachedPhoto.de_json(json_dict, bot)

        json.loads(photo.to_json())

    def test_photo_to_dict(self):
        photo = InlineQueryResultCachedPhoto.de_json(json_dict, bot).to_dict()

        assert isinstance(photo, dict)
        assert json_dict == photo

    def test_equality(self):
        a = InlineQueryResultCachedPhoto(self.id, self.photo_file_id)
        b = InlineQueryResultCachedPhoto(self.id, self.photo_file_id)
        c = InlineQueryResultCachedPhoto(self.id, "")
        d = InlineQueryResultCachedPhoto("", self.photo_file_id)
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


