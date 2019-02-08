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

from telegram import (InputTextMessageContent, InlineQueryResultLocation, InlineKeyboardButton,
                      InlineQueryResultVoice, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def inline_query_result_location():
    return InlineQueryResultLocation(
        TestInlineQueryResultLocation.id,
        TestInlineQueryResultLocation.latitude,
        TestInlineQueryResultLocation.longitude,
        TestInlineQueryResultLocation.title,
        live_period=TestInlineQueryResultLocation.live_period,
        thumb_url=TestInlineQueryResultLocation.thumb_url,
        thumb_width=TestInlineQueryResultLocation.thumb_width,
        thumb_height=TestInlineQueryResultLocation.thumb_height,
        input_message_content=TestInlineQueryResultLocation.input_message_content,
        reply_markup=TestInlineQueryResultLocation.reply_markup)


class TestInlineQueryResultLocation(object):
    id = 'id'
    type = 'location'
    latitude = 0.0
    longitude = 1.0
    title = 'title'
    live_period = 70
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_location):
        assert inline_query_result_location.id == self.id
        assert inline_query_result_location.type == self.type
        assert inline_query_result_location.latitude == self.latitude
        assert inline_query_result_location.longitude == self.longitude
        assert inline_query_result_location.title == self.title
        assert inline_query_result_location.live_period == self.live_period
        assert inline_query_result_location.thumb_url == self.thumb_url
        assert inline_query_result_location.thumb_width == self.thumb_width
        assert inline_query_result_location.thumb_height == self.thumb_height
        assert (inline_query_result_location.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_location.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_location):
        inline_query_result_location_dict = inline_query_result_location.to_dict()

        assert isinstance(inline_query_result_location_dict, dict)
        assert inline_query_result_location_dict['id'] == inline_query_result_location.id
        assert inline_query_result_location_dict['type'] == inline_query_result_location.type
        assert (inline_query_result_location_dict['latitude']
                == inline_query_result_location.latitude)
        assert (inline_query_result_location_dict['longitude']
                == inline_query_result_location.longitude)
        assert inline_query_result_location_dict['title'] == inline_query_result_location.title
        assert (inline_query_result_location_dict['live_period']
                == inline_query_result_location.live_period)
        assert (inline_query_result_location_dict['thumb_url']
                == inline_query_result_location.thumb_url)
        assert (inline_query_result_location_dict['thumb_width']
                == inline_query_result_location.thumb_width)
        assert (inline_query_result_location_dict['thumb_height']
                == inline_query_result_location.thumb_height)
        assert (inline_query_result_location_dict['input_message_content']
                == inline_query_result_location.input_message_content.to_dict())
        assert (inline_query_result_location_dict['reply_markup']
                == inline_query_result_location.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultLocation(self.id, self.longitude, self.latitude, self.title)
        b = InlineQueryResultLocation(self.id, self.longitude, self.latitude, self.title)
        c = InlineQueryResultLocation(self.id, 0, self.latitude, self.title)
        d = InlineQueryResultLocation('', self.longitude, self.latitude, self.title)
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
