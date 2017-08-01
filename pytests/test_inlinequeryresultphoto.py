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

from telegram import (InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultPhoto, InlineQueryResultArticle)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultPhoto.type,
        'id': TestInlineQueryResultPhoto.id,
        'photo_url': TestInlineQueryResultPhoto.photo_url,
        'photo_width': TestInlineQueryResultPhoto.photo_width,
        'photo_height': TestInlineQueryResultPhoto.photo_height,
        'thumb_url': TestInlineQueryResultPhoto.thumb_url,
        'title': TestInlineQueryResultPhoto.title,
        'description': TestInlineQueryResultPhoto.description,
        'caption': TestInlineQueryResultPhoto.caption,
        'input_message_content': TestInlineQueryResultPhoto.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultPhoto.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_photo():
    return InlineQueryResultPhoto(type=TestInlineQueryResultPhoto.type,
                                  id=TestInlineQueryResultPhoto.id,
                                  photo_url=TestInlineQueryResultPhoto.photo_url,
                                  photo_width=TestInlineQueryResultPhoto.photo_width,
                                  photo_height=TestInlineQueryResultPhoto.photo_height,
                                  thumb_url=TestInlineQueryResultPhoto.thumb_url,
                                  title=TestInlineQueryResultPhoto.title,
                                  description=TestInlineQueryResultPhoto.description,
                                  caption=TestInlineQueryResultPhoto.caption,
                                  input_message_content=TestInlineQueryResultPhoto.input_message_content,
                                  reply_markup=TestInlineQueryResultPhoto.reply_markup)


class TestInlineQueryResultPhoto:
    """This object represents Tests for Telegram InlineQueryResultPhoto."""

    id = 'id'
    type = 'photo'
    photo_url = 'photo url'
    photo_width = 10
    photo_height = 15
    thumb_url = 'thumb url'
    title = 'title'
    description = 'description'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_photo_de_json(self):
        photo = InlineQueryResultPhoto.de_json(json_dict, bot)

        assert photo.type == self.type
        assert photo.id == self.id
        assert photo.photo_url == self.photo_url
        assert photo.photo_width == self.photo_width
        assert photo.photo_height == self.photo_height
        assert photo.thumb_url == self.thumb_url
        assert photo.title == self.title
        assert photo.description == self.description
        assert photo.caption == self.caption
        self.assertDictEqual(photo.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert photo.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_photo_to_json(self):
        photo = InlineQueryResultPhoto.de_json(json_dict, bot)

        json.loads(photo.to_json())

    def test_photo_to_dict(self):
        photo = InlineQueryResultPhoto.de_json(json_dict, bot).to_dict()

        assert isinstance(photo, dict)
        assert json_dict == photo

    def test_equality(self):
        a = InlineQueryResultPhoto(self.id, self.photo_url, self.thumb_url)
        b = InlineQueryResultPhoto(self.id, self.photo_url, self.thumb_url)
        c = InlineQueryResultPhoto(self.id, "", self.thumb_url)
        d = InlineQueryResultPhoto("", self.photo_url, self.thumb_url)
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
