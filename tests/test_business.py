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
from datetime import datetime

import pytest

from telegram import (
    BusinessConnection,
    BusinessIntro,
    BusinessLocation,
    BusinessMessagesDeleted,
    BusinessOpeningHours,
    BusinessOpeningHoursInterval,
    Chat,
    Location,
    Sticker,
    User,
)
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


class TestBusinessBase:
    id_ = "123"
    user = User(123, "test_user", False)
    user_chat_id = 123
    date = datetime.now(tz=UTC).replace(microsecond=0)
    can_reply = True
    is_enabled = True
    message_ids = (123, 321)
    business_connection_id = "123"
    chat = Chat(123, "test_chat")
    title = "Business Title"
    message = "Business description"
    sticker = Sticker("sticker_id", "unique_id", 50, 50, True, False, Sticker.REGULAR)
    address = "address"
    location = Location(-23.691288, 46.788279)
    opening_minute = 0
    closing_minute = 60
    time_zone_name = "Country/City"
    opening_hours = [
        BusinessOpeningHoursInterval(opening, opening + 60) for opening in (0, 24 * 60)
    ]


@pytest.fixture(scope="module")
def business_connection():
    return BusinessConnection(
        TestBusinessBase.id_,
        TestBusinessBase.user,
        TestBusinessBase.user_chat_id,
        TestBusinessBase.date,
        TestBusinessBase.can_reply,
        TestBusinessBase.is_enabled,
    )


@pytest.fixture(scope="module")
def business_messages_deleted():
    return BusinessMessagesDeleted(
        TestBusinessBase.business_connection_id,
        TestBusinessBase.chat,
        TestBusinessBase.message_ids,
    )


@pytest.fixture(scope="module")
def business_intro():
    return BusinessIntro(
        TestBusinessBase.title,
        TestBusinessBase.message,
        TestBusinessBase.sticker,
    )


@pytest.fixture(scope="module")
def business_location():
    return BusinessLocation(
        TestBusinessBase.address,
        TestBusinessBase.location,
    )


@pytest.fixture(scope="module")
def business_opening_hours_interval():
    return BusinessOpeningHoursInterval(
        TestBusinessBase.opening_minute,
        TestBusinessBase.closing_minute,
    )


@pytest.fixture(scope="module")
def business_opening_hours():
    return BusinessOpeningHours(
        TestBusinessBase.time_zone_name,
        TestBusinessBase.opening_hours,
    )


class TestBusinessConnectionWithoutRequest(TestBusinessBase):
    def test_slots(self, business_connection):
        bc = business_connection
        for attr in bc.__slots__:
            assert getattr(bc, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bc)) == len(set(mro_slots(bc))), "duplicate slot"

    def test_de_json(self):
        json_dict = {
            "id": self.id_,
            "user": self.user.to_dict(),
            "user_chat_id": self.user_chat_id,
            "date": to_timestamp(self.date),
            "can_reply": self.can_reply,
            "is_enabled": self.is_enabled,
        }
        bc = BusinessConnection.de_json(json_dict, None)
        assert bc.id == self.id_
        assert bc.user == self.user
        assert bc.user_chat_id == self.user_chat_id
        assert bc.date == self.date
        assert bc.can_reply == self.can_reply
        assert bc.is_enabled == self.is_enabled
        assert bc.api_kwargs == {}
        assert isinstance(bc, BusinessConnection)

    def test_de_json_localization(self, bot, raw_bot, tz_bot):
        json_dict = {
            "id": self.id_,
            "user": self.user.to_dict(),
            "user_chat_id": self.user_chat_id,
            "date": to_timestamp(self.date),
            "can_reply": self.can_reply,
            "is_enabled": self.is_enabled,
        }
        chat_bot = BusinessConnection.de_json(json_dict, bot)
        chat_bot_raw = BusinessConnection.de_json(json_dict, raw_bot)
        chat_bot_tz = BusinessConnection.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        date_offset = chat_bot_tz.date.utcoffset()
        date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(chat_bot_tz.date.replace(tzinfo=None))

        assert chat_bot.date.tzinfo == UTC
        assert chat_bot_raw.date.tzinfo == UTC
        assert date_offset_tz == date_offset

    def test_to_dict(self, business_connection):
        bc_dict = business_connection.to_dict()
        assert isinstance(bc_dict, dict)
        assert bc_dict["id"] == self.id_
        assert bc_dict["user"] == self.user.to_dict()
        assert bc_dict["user_chat_id"] == self.user_chat_id
        assert bc_dict["date"] == to_timestamp(self.date)
        assert bc_dict["can_reply"] == self.can_reply
        assert bc_dict["is_enabled"] == self.is_enabled

    def test_equality(self):
        bc1 = BusinessConnection(
            self.id_, self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )
        bc2 = BusinessConnection(
            self.id_, self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )
        bc3 = BusinessConnection(
            "321", self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )

        assert bc1 == bc2
        assert hash(bc1) == hash(bc2)

        assert bc1 != bc3
        assert hash(bc1) != hash(bc3)


class TestBusinessMessagesDeleted(TestBusinessBase):
    def test_slots(self, business_messages_deleted):
        bmd = business_messages_deleted
        for attr in bmd.__slots__:
            assert getattr(bmd, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bmd)) == len(set(mro_slots(bmd))), "duplicate slot"

    def test_to_dict(self, business_messages_deleted):
        bmd_dict = business_messages_deleted.to_dict()
        assert isinstance(bmd_dict, dict)
        assert bmd_dict["message_ids"] == list(self.message_ids)
        assert bmd_dict["business_connection_id"] == self.business_connection_id
        assert bmd_dict["chat"] == self.chat.to_dict()

    def test_de_json(self):
        json_dict = {
            "business_connection_id": self.business_connection_id,
            "chat": self.chat.to_dict(),
            "message_ids": self.message_ids,
        }
        bmd = BusinessMessagesDeleted.de_json(json_dict, None)
        assert bmd.business_connection_id == self.business_connection_id
        assert bmd.chat == self.chat
        assert bmd.message_ids == self.message_ids
        assert bmd.api_kwargs == {}
        assert isinstance(bmd, BusinessMessagesDeleted)

    def test_equality(self):
        bmd1 = BusinessMessagesDeleted(self.business_connection_id, self.chat, self.message_ids)
        bmd2 = BusinessMessagesDeleted(self.business_connection_id, self.chat, self.message_ids)
        bmd3 = BusinessMessagesDeleted("1", Chat(4, "random"), [321, 123])

        assert bmd1 == bmd2
        assert hash(bmd1) == hash(bmd2)

        assert bmd1 != bmd3
        assert hash(bmd1) != hash(bmd3)


class TestBusinessIntroWithoutRequest(TestBusinessBase):
    def test_slot_behaviour(self, business_intro):
        intro = business_intro
        for attr in intro.__slots__:
            assert getattr(intro, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(intro)) == len(set(mro_slots(intro))), "duplicate slot"

    def test_to_dict(self, business_intro):
        intro_dict = business_intro.to_dict()
        assert isinstance(intro_dict, dict)
        assert intro_dict["title"] == self.title
        assert intro_dict["message"] == self.message
        assert intro_dict["sticker"] == self.sticker.to_dict()

    def test_de_json(self):
        json_dict = {
            "title": self.title,
            "message": self.message,
            "sticker": self.sticker.to_dict(),
        }
        intro = BusinessIntro.de_json(json_dict, None)
        assert intro.title == self.title
        assert intro.message == self.message
        assert intro.sticker == self.sticker
        assert intro.api_kwargs == {}
        assert isinstance(intro, BusinessIntro)

    def test_equality(self):
        intro1 = BusinessIntro(self.title, self.message, self.sticker)
        intro2 = BusinessIntro(self.title, self.message, self.sticker)
        intro3 = BusinessIntro("Other Business", self.message, self.sticker)

        assert intro1 == intro2
        assert hash(intro1) == hash(intro2)
        assert intro1 is not intro2

        assert intro1 != intro3
        assert hash(intro1) != hash(intro3)


class TestBusinessLocationWithoutRequest(TestBusinessBase):
    def test_slot_behaviour(self, business_location):
        inst = business_location
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, business_location):
        blc_dict = business_location.to_dict()
        assert isinstance(blc_dict, dict)
        assert blc_dict["address"] == self.address
        assert blc_dict["location"] == self.location.to_dict()

    def test_de_json(self):
        json_dict = {
            "address": self.address,
            "location": self.location.to_dict(),
        }
        blc = BusinessLocation.de_json(json_dict, None)
        assert blc.address == self.address
        assert blc.location == self.location
        assert blc.api_kwargs == {}
        assert isinstance(blc, BusinessLocation)

    def test_equality(self):
        blc1 = BusinessLocation(self.address, self.location)
        blc2 = BusinessLocation(self.address, self.location)
        blc3 = BusinessLocation("Other Address", self.location)

        assert blc1 == blc2
        assert hash(blc1) == hash(blc2)
        assert blc1 is not blc2

        assert blc1 != blc3
        assert hash(blc1) != hash(blc3)


class TestBusinessOpeningHoursIntervalWithoutRequest(TestBusinessBase):
    def test_slot_behaviour(self, business_opening_hours_interval):
        inst = business_opening_hours_interval
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, business_opening_hours_interval):
        bohi_dict = business_opening_hours_interval.to_dict()
        assert isinstance(bohi_dict, dict)
        assert bohi_dict["opening_minute"] == self.opening_minute
        assert bohi_dict["closing_minute"] == self.closing_minute

    def test_de_json(self):
        json_dict = {
            "opening_minute": self.opening_minute,
            "closing_minute": self.closing_minute,
        }
        bohi = BusinessOpeningHoursInterval.de_json(json_dict, None)
        assert bohi.opening_minute == self.opening_minute
        assert bohi.closing_minute == self.closing_minute
        assert bohi.api_kwargs == {}
        assert isinstance(bohi, BusinessOpeningHoursInterval)

    def test_equality(self):
        bohi1 = BusinessOpeningHoursInterval(self.opening_minute, self.closing_minute)
        bohi2 = BusinessOpeningHoursInterval(self.opening_minute, self.closing_minute)
        bohi3 = BusinessOpeningHoursInterval(61, 100)

        assert bohi1 == bohi2
        assert hash(bohi1) == hash(bohi2)
        assert bohi1 is not bohi2

        assert bohi1 != bohi3
        assert hash(bohi1) != hash(bohi3)

    @pytest.mark.parametrize(
        ("opening_minute", "expected"),
        [  # openings per docstring
            (8 * 60, (0, 8, 0)),
            (24 * 60, (1, 0, 0)),
            (6 * 24 * 60, (6, 0, 0)),
        ],
    )
    def test_opening_time(self, opening_minute, expected):
        bohi = BusinessOpeningHoursInterval(opening_minute, -0)

        opening_time = bohi.opening_time
        assert opening_time == expected

        cached = bohi.opening_time
        assert cached is opening_time

    @pytest.mark.parametrize(
        ("closing_minute", "expected"),
        [  # closings per docstring
            (20 * 60 + 30, (0, 20, 30)),
            (2 * 24 * 60 - 1, (1, 23, 59)),
            (7 * 24 * 60 - 2, (6, 23, 58)),
        ],
    )
    def test_closing_time(self, closing_minute, expected):
        bohi = BusinessOpeningHoursInterval(-0, closing_minute)

        closing_time = bohi.closing_time
        assert closing_time == expected

        cached = bohi.closing_time
        assert cached is closing_time


class TestBusinessOpeningHoursWithoutRequest(TestBusinessBase):
    def test_slot_behaviour(self, business_opening_hours):
        inst = business_opening_hours
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_to_dict(self, business_opening_hours):
        boh_dict = business_opening_hours.to_dict()
        assert isinstance(boh_dict, dict)
        assert boh_dict["time_zone_name"] == self.time_zone_name
        assert boh_dict["opening_hours"] == [opening.to_dict() for opening in self.opening_hours]

    def test_de_json(self):
        json_dict = {
            "time_zone_name": self.time_zone_name,
            "opening_hours": [opening.to_dict() for opening in self.opening_hours],
        }
        boh = BusinessOpeningHours.de_json(json_dict, None)
        assert boh.time_zone_name == self.time_zone_name
        assert boh.opening_hours == tuple(self.opening_hours)
        assert boh.api_kwargs == {}
        assert isinstance(boh, BusinessOpeningHours)

    def test_equality(self):
        boh1 = BusinessOpeningHours(self.time_zone_name, self.opening_hours)
        boh2 = BusinessOpeningHours(self.time_zone_name, self.opening_hours)
        boh3 = BusinessOpeningHours("Other/Timezone", self.opening_hours)

        assert boh1 == boh2
        assert hash(boh1) == hash(boh2)
        assert boh1 is not boh2

        assert boh1 != boh3
        assert hash(boh1) != hash(boh3)
