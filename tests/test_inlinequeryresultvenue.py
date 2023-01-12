#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
    InlineQueryResultVenue,
    InlineQueryResultVoice,
    InputTextMessageContent,
)


@pytest.fixture(scope="module")
def inline_query_result_venue():
    return InlineQueryResultVenue(
        Space.id_,
        Space.latitude,
        Space.longitude,
        Space.title,
        Space.address,
        foursquare_id=Space.foursquare_id,
        foursquare_type=Space.foursquare_type,
        thumb_url=Space.thumb_url,
        thumb_width=Space.thumb_width,
        thumb_height=Space.thumb_height,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
        google_place_id=Space.google_place_id,
        google_place_type=Space.google_place_type,
    )


class Space:
    id_ = "id"
    type_ = "venue"
    latitude = "latitude"
    longitude = "longitude"
    title = "title"
    address = "address"
    foursquare_id = "foursquare id"
    foursquare_type = "foursquare type"
    google_place_id = "google place id"
    google_place_type = "google place type"
    thumb_url = "thumb url"
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultVenueWithoutRequest:
    def test_slot_behaviour(self, inline_query_result_venue, mro_slots):
        inst = inline_query_result_venue
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_venue):
        assert inline_query_result_venue.id == Space.id_
        assert inline_query_result_venue.type == Space.type_
        assert inline_query_result_venue.latitude == Space.latitude
        assert inline_query_result_venue.longitude == Space.longitude
        assert inline_query_result_venue.title == Space.title
        assert inline_query_result_venue.address == Space.address
        assert inline_query_result_venue.foursquare_id == Space.foursquare_id
        assert inline_query_result_venue.foursquare_type == Space.foursquare_type
        assert inline_query_result_venue.google_place_id == Space.google_place_id
        assert inline_query_result_venue.google_place_type == Space.google_place_type
        assert inline_query_result_venue.thumb_url == Space.thumb_url
        assert inline_query_result_venue.thumb_width == Space.thumb_width
        assert inline_query_result_venue.thumb_height == Space.thumb_height
        assert (
            inline_query_result_venue.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_venue.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_venue):
        inline_query_result_venue_dict = inline_query_result_venue.to_dict()

        assert isinstance(inline_query_result_venue_dict, dict)
        assert inline_query_result_venue_dict["id"] == inline_query_result_venue.id
        assert inline_query_result_venue_dict["type"] == inline_query_result_venue.type
        assert inline_query_result_venue_dict["latitude"] == inline_query_result_venue.latitude
        assert inline_query_result_venue_dict["longitude"] == inline_query_result_venue.longitude
        assert inline_query_result_venue_dict["title"] == inline_query_result_venue.title
        assert inline_query_result_venue_dict["address"] == inline_query_result_venue.address
        assert (
            inline_query_result_venue_dict["foursquare_id"]
            == inline_query_result_venue.foursquare_id
        )
        assert (
            inline_query_result_venue_dict["foursquare_type"]
            == inline_query_result_venue.foursquare_type
        )
        assert (
            inline_query_result_venue_dict["google_place_id"]
            == inline_query_result_venue.google_place_id
        )
        assert (
            inline_query_result_venue_dict["google_place_type"]
            == inline_query_result_venue.google_place_type
        )
        assert inline_query_result_venue_dict["thumb_url"] == inline_query_result_venue.thumb_url
        assert (
            inline_query_result_venue_dict["thumb_width"] == inline_query_result_venue.thumb_width
        )
        assert (
            inline_query_result_venue_dict["thumb_height"]
            == inline_query_result_venue.thumb_height
        )
        assert (
            inline_query_result_venue_dict["input_message_content"]
            == inline_query_result_venue.input_message_content.to_dict()
        )
        assert (
            inline_query_result_venue_dict["reply_markup"]
            == inline_query_result_venue.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultVenue(
            Space.id_, Space.longitude, Space.latitude, Space.title, Space.address
        )
        b = InlineQueryResultVenue(
            Space.id_, Space.longitude, Space.latitude, Space.title, Space.address
        )
        c = InlineQueryResultVenue(Space.id_, "", Space.latitude, Space.title, Space.address)
        d = InlineQueryResultVenue("", Space.longitude, Space.latitude, Space.title, Space.address)
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
