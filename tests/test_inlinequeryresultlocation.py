#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultLocation,
    InlineQueryResultVoice,
    InputTextMessageContent,
)


@pytest.fixture(scope="module")
def inline_query_result_location():
    return InlineQueryResultLocation(
        Space.id_,
        Space.latitude,
        Space.longitude,
        Space.title,
        live_period=Space.live_period,
        thumb_url=Space.thumb_url,
        thumb_width=Space.thumb_width,
        thumb_height=Space.thumb_height,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
        horizontal_accuracy=Space.horizontal_accuracy,
        heading=Space.heading,
        proximity_alert_radius=Space.proximity_alert_radius,
    )


class Space:
    id_ = "id"
    type_ = "location"
    latitude = 0.0
    longitude = 1.0
    title = "title"
    horizontal_accuracy = 999
    live_period = 70
    heading = 90
    proximity_alert_radius = 1000
    thumb_url = "thumb url"
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultLocationNoReq:
    def test_slot_behaviour(self, inline_query_result_location, mro_slots):
        inst = inline_query_result_location
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_location):
        assert inline_query_result_location.id == Space.id_
        assert inline_query_result_location.type == Space.type_
        assert inline_query_result_location.latitude == Space.latitude
        assert inline_query_result_location.longitude == Space.longitude
        assert inline_query_result_location.title == Space.title
        assert inline_query_result_location.live_period == Space.live_period
        assert inline_query_result_location.thumb_url == Space.thumb_url
        assert inline_query_result_location.thumb_width == Space.thumb_width
        assert inline_query_result_location.thumb_height == Space.thumb_height
        assert (
            inline_query_result_location.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_location.reply_markup.to_dict() == Space.reply_markup.to_dict()
        assert inline_query_result_location.heading == Space.heading
        assert inline_query_result_location.horizontal_accuracy == Space.horizontal_accuracy
        assert inline_query_result_location.proximity_alert_radius == Space.proximity_alert_radius

    def test_to_dict(self, inline_query_result_location):
        inline_query_result_location_dict = inline_query_result_location.to_dict()

        assert isinstance(inline_query_result_location_dict, dict)
        assert inline_query_result_location_dict["id"] == inline_query_result_location.id
        assert inline_query_result_location_dict["type"] == inline_query_result_location.type
        assert (
            inline_query_result_location_dict["latitude"] == inline_query_result_location.latitude
        )
        assert (
            inline_query_result_location_dict["longitude"]
            == inline_query_result_location.longitude
        )
        assert inline_query_result_location_dict["title"] == inline_query_result_location.title
        assert (
            inline_query_result_location_dict["live_period"]
            == inline_query_result_location.live_period
        )
        assert (
            inline_query_result_location_dict["thumb_url"]
            == inline_query_result_location.thumb_url
        )
        assert (
            inline_query_result_location_dict["thumb_width"]
            == inline_query_result_location.thumb_width
        )
        assert (
            inline_query_result_location_dict["thumb_height"]
            == inline_query_result_location.thumb_height
        )
        assert (
            inline_query_result_location_dict["input_message_content"]
            == inline_query_result_location.input_message_content.to_dict()
        )
        assert (
            inline_query_result_location_dict["reply_markup"]
            == inline_query_result_location.reply_markup.to_dict()
        )
        assert (
            inline_query_result_location_dict["horizontal_accuracy"]
            == inline_query_result_location.horizontal_accuracy
        )
        assert inline_query_result_location_dict["heading"] == inline_query_result_location.heading
        assert (
            inline_query_result_location_dict["proximity_alert_radius"]
            == inline_query_result_location.proximity_alert_radius
        )

    def test_equality(self):
        a = InlineQueryResultLocation(Space.id_, Space.longitude, Space.latitude, Space.title)
        b = InlineQueryResultLocation(Space.id_, Space.longitude, Space.latitude, Space.title)
        c = InlineQueryResultLocation(Space.id_, 0, Space.latitude, Space.title)
        d = InlineQueryResultLocation("", Space.longitude, Space.latitude, Space.title)
        e = InlineQueryResultVoice(Space.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
