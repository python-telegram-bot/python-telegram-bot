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

from telegram import (InputTextMessageContent, InlineQueryResultLocation, InlineKeyboardButton,
                      InlineQueryResultArticle, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'id': TestInlineQueryResultLocation.id,
        'type': TestInlineQueryResultLocation.type,
        'latitude': TestInlineQueryResultLocation.latitude,
        'longitude': TestInlineQueryResultLocation.longitude,
        'title': TestInlineQueryResultLocation.title,
        'thumb_url': TestInlineQueryResultLocation.thumb_url,
        'thumb_width': TestInlineQueryResultLocation.thumb_width,
        'thumb_height': TestInlineQueryResultLocation.thumb_height,
        'input_message_content': TestInlineQueryResultLocation.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultLocation.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_location():
    return InlineQueryResultLocation(id=TestInlineQueryResultLocation.id,
                                     type=TestInlineQueryResultLocation.type,
                                     latitude=TestInlineQueryResultLocation.latitude,
                                     longitude=TestInlineQueryResultLocation.longitude,
                                     title=TestInlineQueryResultLocation.title,
                                     thumb_url=TestInlineQueryResultLocation.thumb_url,
                                     thumb_width=TestInlineQueryResultLocation.thumb_width,
                                     thumb_height=TestInlineQueryResultLocation.thumb_height,
                                     input_message_content=TestInlineQueryResultLocation.input_message_content,
                                     reply_markup=TestInlineQueryResultLocation.reply_markup)


class TestInlineQueryResultLocation:
    """This object represents Tests for Telegram InlineQueryResultLocation."""

    id = 'id'
    type = 'location'
    latitude = 0.0
    longitude = 0.0
    title = 'title'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_location_de_json(self):
        location = InlineQueryResultLocation.de_json(json_dict, bot)

        assert location.id == self.id
        assert location.type == self.type
        assert location.latitude == self.latitude
        assert location.longitude == self.longitude
        assert location.title == self.title
        assert location.thumb_url == self.thumb_url
        assert location.thumb_width == self.thumb_width
        assert location.thumb_height == self.thumb_height
        self.assertDictEqual(location.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert location.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_location_to_json(self):
        location = InlineQueryResultLocation.de_json(json_dict, bot)

        json.loads(location.to_json())

    def test_location_to_dict(self):
        location = InlineQueryResultLocation.de_json(json_dict, bot).to_dict()

        assert isinstance(location, dict)
        assert json_dict == location

    def test_equality(self):
        a = InlineQueryResultLocation(self.id, self.longitude, self.latitude, self.title)
        b = InlineQueryResultLocation(self.id, self.longitude, self.latitude, self.title)
        c = InlineQueryResultLocation(self.id, 0, self.latitude, self.title)
        d = InlineQueryResultLocation("", self.longitude, self.latitude, self.title)
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
