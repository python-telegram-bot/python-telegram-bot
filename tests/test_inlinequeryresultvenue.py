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

from telegram import (InlineQueryResultVoice, InputTextMessageContent, InlineKeyboardButton,
                      InlineQueryResultVenue, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def inline_query_result_venue():
    return InlineQueryResultVenue(
        TestInlineQueryResultVenue.id,
        TestInlineQueryResultVenue.latitude,
        TestInlineQueryResultVenue.longitude,
        TestInlineQueryResultVenue.title,
        TestInlineQueryResultVenue.address,
        foursquare_id=TestInlineQueryResultVenue.foursquare_id,
        foursquare_type=TestInlineQueryResultVenue.foursquare_type,
        thumb_url=TestInlineQueryResultVenue.thumb_url,
        thumb_width=TestInlineQueryResultVenue.thumb_width,
        thumb_height=TestInlineQueryResultVenue.thumb_height,
        input_message_content=TestInlineQueryResultVenue.input_message_content,
        reply_markup=TestInlineQueryResultVenue.reply_markup)


class TestInlineQueryResultVenue(object):
    id = 'id'
    type = 'venue'
    latitude = 'latitude'
    longitude = 'longitude'
    title = 'title'
    address = 'address'
    foursquare_id = 'foursquare id'
    foursquare_type = 'foursquare type'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_venue):
        assert inline_query_result_venue.id == self.id
        assert inline_query_result_venue.type == self.type
        assert inline_query_result_venue.latitude == self.latitude
        assert inline_query_result_venue.longitude == self.longitude
        assert inline_query_result_venue.title == self.title
        assert inline_query_result_venue.address == self.address
        assert inline_query_result_venue.foursquare_id == self.foursquare_id
        assert inline_query_result_venue.foursquare_type == self.foursquare_type
        assert inline_query_result_venue.thumb_url == self.thumb_url
        assert inline_query_result_venue.thumb_width == self.thumb_width
        assert inline_query_result_venue.thumb_height == self.thumb_height
        assert (inline_query_result_venue.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_venue.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_venue):
        inline_query_result_venue_dict = inline_query_result_venue.to_dict()

        assert isinstance(inline_query_result_venue_dict, dict)
        assert inline_query_result_venue_dict['id'] == inline_query_result_venue.id
        assert inline_query_result_venue_dict['type'] == inline_query_result_venue.type
        assert inline_query_result_venue_dict['latitude'] == inline_query_result_venue.latitude
        assert inline_query_result_venue_dict['longitude'] == inline_query_result_venue.longitude
        assert inline_query_result_venue_dict['title'] == inline_query_result_venue.title
        assert inline_query_result_venue_dict['address'] == inline_query_result_venue.address
        assert (inline_query_result_venue_dict['foursquare_id']
                == inline_query_result_venue.foursquare_id)
        assert (inline_query_result_venue_dict['foursquare_type']
                == inline_query_result_venue.foursquare_type)
        assert inline_query_result_venue_dict['thumb_url'] == inline_query_result_venue.thumb_url
        assert (inline_query_result_venue_dict['thumb_width']
                == inline_query_result_venue.thumb_width)
        assert (inline_query_result_venue_dict['thumb_height']
                == inline_query_result_venue.thumb_height)
        assert (inline_query_result_venue_dict['input_message_content']
                == inline_query_result_venue.input_message_content.to_dict())
        assert (inline_query_result_venue_dict['reply_markup']
                == inline_query_result_venue.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultVenue(self.id, self.longitude, self.latitude, self.title,
                                   self.address)
        b = InlineQueryResultVenue(self.id, self.longitude, self.latitude, self.title,
                                   self.address)
        c = InlineQueryResultVenue(self.id, '', self.latitude, self.title, self.address)
        d = InlineQueryResultVenue('', self.longitude, self.latitude, self.title,
                                   self.address)
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
