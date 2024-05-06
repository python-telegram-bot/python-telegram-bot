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
import asyncio

import pytest

from telegram import Location, ReplyParameters, Venue
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.request import RequestData
from tests.auxil.build_messages import make_message
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def venue():
    return Venue(
        TestVenueBase.location,
        TestVenueBase.title,
        TestVenueBase.address,
        foursquare_id=TestVenueBase.foursquare_id,
        foursquare_type=TestVenueBase.foursquare_type,
        google_place_id=TestVenueBase.google_place_id,
        google_place_type=TestVenueBase.google_place_type,
    )


class TestVenueBase:
    location = Location(longitude=-46.788279, latitude=-23.691288)
    title = "title"
    address = "address"
    foursquare_id = "foursquare id"
    foursquare_type = "foursquare type"
    google_place_id = "google place id"
    google_place_type = "google place type"


class TestVenueWithoutRequest(TestVenueBase):
    def test_slot_behaviour(self, venue):
        for attr in venue.__slots__:
            assert getattr(venue, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(venue)) == len(set(mro_slots(venue))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "location": self.location.to_dict(),
            "title": self.title,
            "address": self.address,
            "foursquare_id": self.foursquare_id,
            "foursquare_type": self.foursquare_type,
            "google_place_id": self.google_place_id,
            "google_place_type": self.google_place_type,
        }
        venue = Venue.de_json(json_dict, bot)
        assert venue.api_kwargs == {}

        assert venue.location == self.location
        assert venue.title == self.title
        assert venue.address == self.address
        assert venue.foursquare_id == self.foursquare_id
        assert venue.foursquare_type == self.foursquare_type
        assert venue.google_place_id == self.google_place_id
        assert venue.google_place_type == self.google_place_type

    def test_to_dict(self, venue):
        venue_dict = venue.to_dict()

        assert isinstance(venue_dict, dict)
        assert venue_dict["location"] == venue.location.to_dict()
        assert venue_dict["title"] == venue.title
        assert venue_dict["address"] == venue.address
        assert venue_dict["foursquare_id"] == venue.foursquare_id
        assert venue_dict["foursquare_type"] == venue.foursquare_type
        assert venue_dict["google_place_id"] == venue.google_place_id
        assert venue_dict["google_place_type"] == venue.google_place_type

    def test_equality(self):
        a = Venue(Location(0, 0), self.title, self.address)
        b = Venue(Location(0, 0), self.title, self.address)
        c = Venue(Location(0, 0), self.title, "")
        d = Venue(Location(0, 1), self.title, self.address)
        d2 = Venue(Location(0, 0), "", self.address)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)

    async def test_send_venue_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match="Either venue or latitude, longitude, address and"):
            await bot.send_venue(chat_id=chat_id)

    async def test_send_venue_mutually_exclusive(self, bot, chat_id, venue):
        with pytest.raises(ValueError, match="Not both"):
            await bot.send_venue(
                chat_id=chat_id,
                latitude=1,
                longitude=1,
                address="address",
                title="title",
                venue=venue,
            )

    async def test_send_with_venue(self, monkeypatch, bot, chat_id, venue):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            return (
                data["longitude"] == str(self.location.longitude)
                and data["latitude"] == str(self.location.latitude)
                and data["title"] == self.title
                and data["address"] == self.address
                and data["foursquare_id"] == self.foursquare_id
                and data["foursquare_type"] == self.foursquare_type
                and data["google_place_id"] == self.google_place_id
                and data["google_place_type"] == self.google_place_type
            )

        monkeypatch.setattr(bot.request, "post", make_assertion)
        message = await bot.send_venue(chat_id, venue=venue)
        assert message

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_venue_default_quote_parse_mode(
        self, default_bot, chat_id, venue, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_venue(
            chat_id, venue=venue, reply_parameters=ReplyParameters(**kwargs)
        )


class TestVenueWithRequest(TestVenueBase):
    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_venue_default_allow_sending_without_reply(
        self, default_bot, chat_id, venue, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_venue(
                chat_id,
                venue=venue,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_venue(
                chat_id, venue=venue, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to be replied not found"):
                await default_bot.send_venue(
                    chat_id, venue=venue, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_venue_default_protect_content(self, default_bot, chat_id, venue):
        tasks = asyncio.gather(
            default_bot.send_venue(chat_id, venue=venue),
            default_bot.send_venue(chat_id, venue=venue, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content
