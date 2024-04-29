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

from telegram import Location, ReplyParameters
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.request import RequestData
from tests.auxil.build_messages import make_message
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def location():
    return Location(
        latitude=TestLocationBase.latitude,
        longitude=TestLocationBase.longitude,
        horizontal_accuracy=TestLocationBase.horizontal_accuracy,
        live_period=TestLocationBase.live_period,
        heading=TestLocationBase.live_period,
        proximity_alert_radius=TestLocationBase.proximity_alert_radius,
    )


class TestLocationBase:
    latitude = -23.691288
    longitude = -46.788279
    horizontal_accuracy = 999
    live_period = 60
    heading = 90
    proximity_alert_radius = 50


class TestLocationWithoutRequest(TestLocationBase):
    def test_slot_behaviour(self, location):
        for attr in location.__slots__:
            assert getattr(location, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(location)) == len(set(mro_slots(location))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "horizontal_accuracy": self.horizontal_accuracy,
            "live_period": self.live_period,
            "heading": self.heading,
            "proximity_alert_radius": self.proximity_alert_radius,
        }
        location = Location.de_json(json_dict, bot)
        assert location.api_kwargs == {}

        assert location.latitude == self.latitude
        assert location.longitude == self.longitude
        assert location.horizontal_accuracy == self.horizontal_accuracy
        assert location.live_period == self.live_period
        assert location.heading == self.heading
        assert location.proximity_alert_radius == self.proximity_alert_radius

    def test_to_dict(self, location):
        location_dict = location.to_dict()

        assert location_dict["latitude"] == location.latitude
        assert location_dict["longitude"] == location.longitude
        assert location_dict["horizontal_accuracy"] == location.horizontal_accuracy
        assert location_dict["live_period"] == location.live_period
        assert location["heading"] == location.heading
        assert location["proximity_alert_radius"] == location.proximity_alert_radius

    def test_equality(self):
        a = Location(self.longitude, self.latitude)
        b = Location(self.longitude, self.latitude)
        d = Location(0, self.latitude)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

    async def test_send_location_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match="Either location or latitude and longitude"):
            await bot.send_location(chat_id=chat_id)

    async def test_edit_location_without_required(self, bot):
        with pytest.raises(ValueError, match="Either location or latitude and longitude"):
            await bot.edit_message_live_location(chat_id=2, message_id=3)

    async def test_send_location_with_all_args(self, bot, location):
        with pytest.raises(ValueError, match="Not both"):
            await bot.send_location(chat_id=1, latitude=2.5, longitude=4.6, location=location)

    async def test_edit_location_with_all_args(self, bot, location):
        with pytest.raises(ValueError, match="Not both"):
            await bot.edit_message_live_location(
                chat_id=1, message_id=7, latitude=2.5, longitude=4.6, location=location
            )

    # TODO: Needs improvement with in inline sent live location.
    async def test_edit_live_inline_message(self, monkeypatch, bot, location):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.json_parameters
            lat = data["latitude"] == str(location.latitude)
            lon = data["longitude"] == str(location.longitude)
            id_ = data["inline_message_id"] == "1234"
            ha = data["horizontal_accuracy"] == "50"
            heading = data["heading"] == "90"
            prox_alert = data["proximity_alert_radius"] == "1000"
            return lat and lon and id_ and ha and heading and prox_alert

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.edit_message_live_location(
            inline_message_id=1234,
            location=location,
            horizontal_accuracy=50,
            heading=90,
            proximity_alert_radius=1000,
        )

    # TODO: Needs improvement with in inline sent live location.
    async def test_stop_live_inline_message(self, monkeypatch, bot):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["inline_message_id"] == "1234"

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.stop_message_live_location(inline_message_id=1234)

    async def test_send_with_location(self, monkeypatch, bot, chat_id, location):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            lat = request_data.json_parameters["latitude"] == str(location.latitude)
            lon = request_data.json_parameters["longitude"] == str(location.longitude)
            return lat and lon

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_location(location=location, chat_id=chat_id)

    async def test_edit_live_location_with_location(self, monkeypatch, bot, location):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            lat = request_data.json_parameters["latitude"] == str(location.latitude)
            lon = request_data.json_parameters["longitude"] == str(location.longitude)
            return lat and lon

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.edit_message_live_location(None, None, location=location)

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_location_default_quote_parse_mode(
        self, default_bot, chat_id, location, custom, monkeypatch
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
        await default_bot.send_location(
            chat_id, location=location, reply_parameters=ReplyParameters(**kwargs)
        )


class TestLocationWithRequest:
    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_location_default_allow_sending_without_reply(
        self, default_bot, chat_id, location, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_location(
                chat_id,
                location=location,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_location(
                chat_id, location=location, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_location(
                    chat_id, location=location, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_location_default_protect_content(self, chat_id, default_bot, location):
        tasks = asyncio.gather(
            default_bot.send_location(chat_id, location=location),
            default_bot.send_location(chat_id, location=location, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    @pytest.mark.xfail()
    async def test_send_live_location(self, bot, chat_id):
        message = await bot.send_location(
            chat_id=chat_id,
            latitude=52.223880,
            longitude=5.166146,
            live_period=80,
            horizontal_accuracy=50,
            heading=90,
            proximity_alert_radius=1000,
            protect_content=True,
        )
        assert message.location
        assert pytest.approx(message.location.latitude, rel=1e-5) == 52.223880
        assert pytest.approx(message.location.longitude, rel=1e-5) == 5.166146
        assert message.location.live_period == 80
        assert message.location.horizontal_accuracy == 50
        assert message.location.heading == 90
        assert message.location.proximity_alert_radius == 1000
        assert message.has_protected_content

        message2 = await bot.edit_message_live_location(
            message.chat_id,
            message.message_id,
            latitude=52.223098,
            longitude=5.164306,
            horizontal_accuracy=30,
            heading=10,
            proximity_alert_radius=500,
        )

        assert pytest.approx(message2.location.latitude, rel=1e-5) == 52.223098
        assert pytest.approx(message2.location.longitude, rel=1e-5) == 5.164306
        assert message2.location.horizontal_accuracy == 30
        assert message2.location.heading == 10
        assert message2.location.proximity_alert_radius == 500

        await bot.stop_message_live_location(message.chat_id, message.message_id)
        with pytest.raises(BadRequest, match="Message can't be edited"):
            await bot.edit_message_live_location(
                message.chat_id, message.message_id, latitude=52.223880, longitude=5.164306
            )
