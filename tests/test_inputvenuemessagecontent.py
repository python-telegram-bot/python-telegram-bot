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

from telegram import InputVenueMessageContent, Location
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_venue_message_content():
    return InputVenueMessageContent(
        TestInputVenueMessageContentBase.latitude,
        TestInputVenueMessageContentBase.longitude,
        TestInputVenueMessageContentBase.title,
        TestInputVenueMessageContentBase.address,
        foursquare_id=TestInputVenueMessageContentBase.foursquare_id,
        foursquare_type=TestInputVenueMessageContentBase.foursquare_type,
        google_place_id=TestInputVenueMessageContentBase.google_place_id,
        google_place_type=TestInputVenueMessageContentBase.google_place_type,
    )


class TestInputVenueMessageContentBase:
    latitude = 1.0
    longitude = 2.0
    title = "title"
    address = "address"
    foursquare_id = "foursquare id"
    foursquare_type = "foursquare type"
    google_place_id = "google place id"
    google_place_type = "google place type"


class TestInputVenueMessageContentWithoutRequest(TestInputVenueMessageContentBase):
    def test_slot_behaviour(self, input_venue_message_content):
        inst = input_venue_message_content
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_venue_message_content):
        assert input_venue_message_content.longitude == self.longitude
        assert input_venue_message_content.latitude == self.latitude
        assert input_venue_message_content.title == self.title
        assert input_venue_message_content.address == self.address
        assert input_venue_message_content.foursquare_id == self.foursquare_id
        assert input_venue_message_content.foursquare_type == self.foursquare_type
        assert input_venue_message_content.google_place_id == self.google_place_id
        assert input_venue_message_content.google_place_type == self.google_place_type

    def test_to_dict(self, input_venue_message_content):
        input_venue_message_content_dict = input_venue_message_content.to_dict()

        assert isinstance(input_venue_message_content_dict, dict)
        assert input_venue_message_content_dict["latitude"] == input_venue_message_content.latitude
        assert (
            input_venue_message_content_dict["longitude"] == input_venue_message_content.longitude
        )
        assert input_venue_message_content_dict["title"] == input_venue_message_content.title
        assert input_venue_message_content_dict["address"] == input_venue_message_content.address
        assert (
            input_venue_message_content_dict["foursquare_id"]
            == input_venue_message_content.foursquare_id
        )
        assert (
            input_venue_message_content_dict["foursquare_type"]
            == input_venue_message_content.foursquare_type
        )
        assert (
            input_venue_message_content_dict["google_place_id"]
            == input_venue_message_content.google_place_id
        )
        assert (
            input_venue_message_content_dict["google_place_type"]
            == input_venue_message_content.google_place_type
        )

    def test_equality(self):
        a = InputVenueMessageContent(123, 456, "title", "address")
        b = InputVenueMessageContent(123, 456, "title", "")
        c = InputVenueMessageContent(123, 456, "title", "address", foursquare_id=123)
        d = InputVenueMessageContent(456, 123, "title", "address", foursquare_id=123)
        e = Location(123, 456)

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
