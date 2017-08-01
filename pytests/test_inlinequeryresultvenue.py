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

from telegram import (InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton,
                      InlineQueryResultVenue, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'id': TestInlineQueryResultVenue.id,
        'type': TestInlineQueryResultVenue.type,
        'latitude': TestInlineQueryResultVenue.latitude,
        'longitude': TestInlineQueryResultVenue.longitude,
        'title': TestInlineQueryResultVenue.title,
        'address': TestInlineQueryResultVenue._address,
        'foursquare_id': TestInlineQueryResultVenue.foursquare_id,
        'thumb_url': TestInlineQueryResultVenue.thumb_url,
        'thumb_width': TestInlineQueryResultVenue.thumb_width,
        'thumb_height': TestInlineQueryResultVenue.thumb_height,
        'input_message_content': TestInlineQueryResultVenue.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultVenue.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_venue():
    return InlineQueryResultVenue(id=TestInlineQueryResultVenue.id,
                                  type=TestInlineQueryResultVenue.type,
                                  latitude=TestInlineQueryResultVenue.latitude,
                                  longitude=TestInlineQueryResultVenue.longitude,
                                  title=TestInlineQueryResultVenue.title,
                                  address=TestInlineQueryResultVenue._address,
                                  foursquare_id=TestInlineQueryResultVenue.foursquare_id,
                                  thumb_url=TestInlineQueryResultVenue.thumb_url,
                                  thumb_width=TestInlineQueryResultVenue.thumb_width,
                                  thumb_height=TestInlineQueryResultVenue.thumb_height,
                                  input_message_content=TestInlineQueryResultVenue.input_message_content,
                                  reply_markup=TestInlineQueryResultVenue.reply_markup)


class TestInlineQueryResultVenue:
    """This object represents Tests for Telegram InlineQueryResultVenue."""

    id = 'id'
    type = 'venue'
    latitude = 'latitude'
    longitude = 'longitude'
    title = 'title'
    _address = 'address'  # nose binds address for testing
    foursquare_id = 'foursquare id'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_venue_de_json(self):
        venue = InlineQueryResultVenue.de_json(json_dict, bot)

        assert venue.id == self.id
        assert venue.type == self.type
        assert venue.latitude == self.latitude
        assert venue.longitude == self.longitude
        assert venue.title == self.title
        assert venue.address == self._address
        assert venue.foursquare_id == self.foursquare_id
        assert venue.thumb_url == self.thumb_url
        assert venue.thumb_width == self.thumb_width
        assert venue.thumb_height == self.thumb_height
        self.assertDictEqual(venue.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert venue.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_venue_to_json(self):
        venue = InlineQueryResultVenue.de_json(json_dict, bot)

        json.loads(venue.to_json())

    def test_venue_to_dict(self):
        venue = InlineQueryResultVenue.de_json(json_dict, bot).to_dict()

        assert isinstance(venue, dict)
        assert json_dict == venue

    def test_equality(self):
        a = InlineQueryResultVenue(self.id, self.longitude, self.latitude, self.title,
                                   self._address)
        b = InlineQueryResultVenue(self.id, self.longitude, self.latitude, self.title,
                                   self._address)
        c = InlineQueryResultVenue(self.id, "", self.latitude, self.title, self._address)
        d = InlineQueryResultVenue("", self.longitude, self.latitude, self.title,
                                   self._address)
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
