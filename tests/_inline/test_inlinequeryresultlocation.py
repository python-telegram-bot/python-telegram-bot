#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_location():
    return InlineQueryResultLocation(
        TestInlineQueryResultLocationBase.id_,
        TestInlineQueryResultLocationBase.latitude,
        TestInlineQueryResultLocationBase.longitude,
        TestInlineQueryResultLocationBase.title,
        live_period=TestInlineQueryResultLocationBase.live_period,
        thumbnail_url=TestInlineQueryResultLocationBase.thumbnail_url,
        thumbnail_width=TestInlineQueryResultLocationBase.thumbnail_width,
        thumbnail_height=TestInlineQueryResultLocationBase.thumbnail_height,
        input_message_content=TestInlineQueryResultLocationBase.input_message_content,
        reply_markup=TestInlineQueryResultLocationBase.reply_markup,
        horizontal_accuracy=TestInlineQueryResultLocationBase.horizontal_accuracy,
        heading=TestInlineQueryResultLocationBase.heading,
        proximity_alert_radius=TestInlineQueryResultLocationBase.proximity_alert_radius,
    )


class TestInlineQueryResultLocationBase:
    id_ = "id"
    type_ = "location"
    latitude = 0.0
    longitude = 1.0
    title = "title"
    horizontal_accuracy = 999
    live_period = 70
    heading = 90
    proximity_alert_radius = 1000
    thumbnail_url = "thumb url"
    thumbnail_width = 10
    thumbnail_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultLocationWithoutRequest(TestInlineQueryResultLocationBase):
    def test_slot_behaviour(self, inline_query_result_location):
        inst = inline_query_result_location
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_location):
        assert inline_query_result_location.id == self.id_
        assert inline_query_result_location.type == self.type_
        assert inline_query_result_location.latitude == self.latitude
        assert inline_query_result_location.longitude == self.longitude
        assert inline_query_result_location.title == self.title
        assert inline_query_result_location.live_period == self.live_period
        assert inline_query_result_location.thumbnail_url == self.thumbnail_url
        assert inline_query_result_location.thumbnail_width == self.thumbnail_width
        assert inline_query_result_location.thumbnail_height == self.thumbnail_height
        assert (
            inline_query_result_location.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_location.reply_markup.to_dict() == self.reply_markup.to_dict()
        assert inline_query_result_location.heading == self.heading
        assert inline_query_result_location.horizontal_accuracy == self.horizontal_accuracy
        assert inline_query_result_location.proximity_alert_radius == self.proximity_alert_radius

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
            inline_query_result_location_dict["thumbnail_url"]
            == inline_query_result_location.thumbnail_url
        )
        assert (
            inline_query_result_location_dict["thumbnail_width"]
            == inline_query_result_location.thumbnail_width
        )
        assert (
            inline_query_result_location_dict["thumbnail_height"]
            == inline_query_result_location.thumbnail_height
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
        a = InlineQueryResultLocation(self.id_, self.longitude, self.latitude, self.title)
        b = InlineQueryResultLocation(self.id_, self.longitude, self.latitude, self.title)
        c = InlineQueryResultLocation(self.id_, 0, self.latitude, self.title)
        d = InlineQueryResultLocation("", self.longitude, self.latitude, self.title)
        e = InlineQueryResultVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
