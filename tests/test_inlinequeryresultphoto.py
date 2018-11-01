#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import (InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultPhoto, InlineQueryResultVoice)


@pytest.fixture(scope='class')
def inline_query_result_photo():
    return InlineQueryResultPhoto(
        TestInlineQueryResultPhoto.id,
        TestInlineQueryResultPhoto.photo_url,
        TestInlineQueryResultPhoto.thumb_url,
        photo_width=TestInlineQueryResultPhoto.photo_width,
        photo_height=TestInlineQueryResultPhoto.photo_height,
        title=TestInlineQueryResultPhoto.title,
        description=TestInlineQueryResultPhoto.description,
        caption=TestInlineQueryResultPhoto.caption,
        parse_mode=TestInlineQueryResultPhoto.parse_mode,
        input_message_content=TestInlineQueryResultPhoto.input_message_content,
        reply_markup=TestInlineQueryResultPhoto.reply_markup)


class TestInlineQueryResultPhoto(object):
    id = 'id'
    type = 'photo'
    photo_url = 'photo url'
    photo_width = 10
    photo_height = 15
    thumb_url = 'thumb url'
    title = 'title'
    description = 'description'
    caption = 'caption'
    parse_mode = 'HTML'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_photo):
        assert inline_query_result_photo.type == self.type
        assert inline_query_result_photo.id == self.id
        assert inline_query_result_photo.photo_url == self.photo_url
        assert inline_query_result_photo.photo_width == self.photo_width
        assert inline_query_result_photo.photo_height == self.photo_height
        assert inline_query_result_photo.thumb_url == self.thumb_url
        assert inline_query_result_photo.title == self.title
        assert inline_query_result_photo.description == self.description
        assert inline_query_result_photo.caption == self.caption
        assert inline_query_result_photo.parse_mode == self.parse_mode
        assert (inline_query_result_photo.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_photo.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_photo):
        inline_query_result_photo_dict = inline_query_result_photo.to_dict()

        assert isinstance(inline_query_result_photo_dict, dict)
        assert inline_query_result_photo_dict['type'] == inline_query_result_photo.type
        assert inline_query_result_photo_dict['id'] == inline_query_result_photo.id
        assert inline_query_result_photo_dict['photo_url'] == inline_query_result_photo.photo_url
        assert (inline_query_result_photo_dict['photo_width']
                == inline_query_result_photo.photo_width)
        assert (inline_query_result_photo_dict['photo_height']
                == inline_query_result_photo.photo_height)
        assert inline_query_result_photo_dict['thumb_url'] == inline_query_result_photo.thumb_url
        assert inline_query_result_photo_dict['title'] == inline_query_result_photo.title
        assert (inline_query_result_photo_dict['description']
                == inline_query_result_photo.description)
        assert inline_query_result_photo_dict['caption'] == inline_query_result_photo.caption
        assert inline_query_result_photo_dict['parse_mode'] == inline_query_result_photo.parse_mode
        assert (inline_query_result_photo_dict['input_message_content']
                == inline_query_result_photo.input_message_content.to_dict())
        assert (inline_query_result_photo_dict['reply_markup']
                == inline_query_result_photo.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultPhoto(self.id, self.photo_url, self.thumb_url)
        b = InlineQueryResultPhoto(self.id, self.photo_url, self.thumb_url)
        c = InlineQueryResultPhoto(self.id, '', self.thumb_url)
        d = InlineQueryResultPhoto('', self.photo_url, self.thumb_url)
        e = InlineQueryResultVoice(self.id, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
