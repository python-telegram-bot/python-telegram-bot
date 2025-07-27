#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
# along with this program. If not, see [http://www.gnu.org/licenses/].


import pytest

from telegram._dice import Dice
from telegram._reaction import ReactionTypeEmoji
from telegram._storyarea import (
    LocationAddress,
    StoryArea,
    StoryAreaPosition,
    StoryAreaType,
    StoryAreaTypeLink,
    StoryAreaTypeLocation,
    StoryAreaTypeSuggestedReaction,
    StoryAreaTypeUniqueGift,
    StoryAreaTypeWeather,
)
from telegram.constants import StoryAreaTypeType
from tests.auxil.slots import mro_slots


@pytest.fixture
def story_area_position():
    return StoryAreaPosition(
        x_percentage=StoryAreaPositionTestBase.x_percentage,
        y_percentage=StoryAreaPositionTestBase.y_percentage,
        width_percentage=StoryAreaPositionTestBase.width_percentage,
        height_percentage=StoryAreaPositionTestBase.height_percentage,
        rotation_angle=StoryAreaPositionTestBase.rotation_angle,
        corner_radius_percentage=StoryAreaPositionTestBase.corner_radius_percentage,
    )


class StoryAreaPositionTestBase:
    x_percentage = 50.0
    y_percentage = 10.0
    width_percentage = 15
    height_percentage = 15
    rotation_angle = 0.0
    corner_radius_percentage = 8.0


class TestStoryAreaPositionWithoutRequest(StoryAreaPositionTestBase):
    def test_slot_behaviour(self, story_area_position):
        inst = story_area_position
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_position):
        assert story_area_position.x_percentage == self.x_percentage
        assert story_area_position.y_percentage == self.y_percentage
        assert story_area_position.width_percentage == self.width_percentage
        assert story_area_position.height_percentage == self.height_percentage
        assert story_area_position.rotation_angle == self.rotation_angle
        assert story_area_position.corner_radius_percentage == self.corner_radius_percentage

    def test_to_dict(self, story_area_position):
        json_dict = story_area_position.to_dict()
        assert json_dict["x_percentage"] == self.x_percentage
        assert json_dict["y_percentage"] == self.y_percentage
        assert json_dict["width_percentage"] == self.width_percentage
        assert json_dict["height_percentage"] == self.height_percentage
        assert json_dict["rotation_angle"] == self.rotation_angle
        assert json_dict["corner_radius_percentage"] == self.corner_radius_percentage

    def test_equality(self, story_area_position):
        a = story_area_position
        b = StoryAreaPosition(
            self.x_percentage,
            self.y_percentage,
            self.width_percentage,
            self.height_percentage,
            self.rotation_angle,
            self.corner_radius_percentage,
        )
        c = StoryAreaPosition(
            self.x_percentage + 10.0,
            self.y_percentage,
            self.width_percentage,
            self.height_percentage,
            self.rotation_angle,
            self.corner_radius_percentage,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def location_address():
    return LocationAddress(
        country_code=LocationAddressTestBase.country_code,
        state=LocationAddressTestBase.state,
        city=LocationAddressTestBase.city,
        street=LocationAddressTestBase.street,
    )


class LocationAddressTestBase:
    country_code = "CC"
    state = "State"
    city = "City"
    street = "12 downtown"


class TestLocationAddressWithoutRequest(LocationAddressTestBase):
    def test_slot_behaviour(self, location_address):
        inst = location_address
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, location_address):
        assert location_address.country_code == self.country_code
        assert location_address.state == self.state
        assert location_address.city == self.city
        assert location_address.street == self.street

    def test_to_dict(self, location_address):
        json_dict = location_address.to_dict()
        assert json_dict["country_code"] == self.country_code
        assert json_dict["state"] == self.state
        assert json_dict["city"] == self.city
        assert json_dict["street"] == self.street

    def test_equality(self, location_address):
        a = location_address
        b = LocationAddress(self.country_code, self.state, self.city, self.street)
        c = LocationAddress("some_other_code", self.state, self.city, self.street)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area():
    return StoryArea(
        position=StoryAreaTestBase.position,
        type=StoryAreaTestBase.type,
    )


class StoryAreaTestBase:
    position = StoryAreaPosition(
        x_percentage=50.0,
        y_percentage=10.0,
        width_percentage=15,
        height_percentage=15,
        rotation_angle=0.0,
        corner_radius_percentage=8.0,
    )
    type = StoryAreaTypeLink(url="some_url")


class TestStoryAreaWithoutRequest(StoryAreaTestBase):
    def test_slot_behaviour(self, story_area):
        inst = story_area
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area):
        assert story_area.position == self.position
        assert story_area.type == self.type

    def test_to_dict(self, story_area):
        json_dict = story_area.to_dict()
        assert json_dict["position"] == self.position.to_dict()
        assert json_dict["type"] == self.type.to_dict()

    def test_equality(self, story_area):
        a = story_area
        b = StoryArea(self.position, self.type)
        c = StoryArea(self.position, StoryAreaTypeLink(url="some_other_url"))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type():
    return StoryAreaType(type=StoryAreaTypeTestBase.type)


class StoryAreaTypeTestBase:
    type = StoryAreaTypeType.LOCATION
    latitude = 100.5
    longitude = 200.5
    address = LocationAddress(
        country_code="cc",
        state="State",
        city="City",
        street="12 downtown",
    )
    reaction_type = ReactionTypeEmoji(emoji="emoji")
    is_dark = False
    is_flipped = False
    url = "http_url"
    temperature = 35.0
    emoji = "emoji"
    background_color = 0xFF66CCFF
    name = "unique_gift_name"


class TestStoryAreaTypeWithoutRequest(StoryAreaTypeTestBase):
    def test_slot_behaviour(self, story_area_type):
        inst = story_area_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type):
        assert story_area_type.type == self.type

    def test_type_enum_conversion(self, story_area_type):
        assert type(StoryAreaType("location").type) is StoryAreaTypeType
        assert StoryAreaType("unknown").type == "unknown"

    def test_to_dict(self, story_area_type):
        assert story_area_type.to_dict() == {"type": self.type}

    def test_equality(self, story_area_type):
        a = story_area_type
        b = StoryAreaType(self.type)
        c = StoryAreaType("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type_location():
    return StoryAreaTypeLocation(
        latitude=TestStoryAreaTypeLocationWithoutRequest.latitude,
        longitude=TestStoryAreaTypeLocationWithoutRequest.longitude,
        address=TestStoryAreaTypeLocationWithoutRequest.address,
    )


class TestStoryAreaTypeLocationWithoutRequest(StoryAreaTypeTestBase):
    type = StoryAreaTypeType.LOCATION

    def test_slot_behaviour(self, story_area_type_location):
        inst = story_area_type_location
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type_location):
        assert story_area_type_location.type == self.type
        assert story_area_type_location.latitude == self.latitude
        assert story_area_type_location.longitude == self.longitude
        assert story_area_type_location.address == self.address

    def test_to_dict(self, story_area_type_location):
        json_dict = story_area_type_location.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["latitude"] == self.latitude
        assert json_dict["longitude"] == self.longitude
        assert json_dict["address"] == self.address.to_dict()

    def test_equality(self, story_area_type_location):
        a = story_area_type_location
        b = StoryAreaTypeLocation(self.latitude, self.longitude, self.address)
        c = StoryAreaTypeLocation(self.latitude + 0.5, self.longitude, self.address)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type_suggested_reaction():
    return StoryAreaTypeSuggestedReaction(
        reaction_type=TestStoryAreaTypeSuggestedReactionWithoutRequest.reaction_type,
        is_dark=TestStoryAreaTypeSuggestedReactionWithoutRequest.is_dark,
        is_flipped=TestStoryAreaTypeSuggestedReactionWithoutRequest.is_flipped,
    )


class TestStoryAreaTypeSuggestedReactionWithoutRequest(StoryAreaTypeTestBase):
    type = StoryAreaTypeType.SUGGESTED_REACTION

    def test_slot_behaviour(self, story_area_type_suggested_reaction):
        inst = story_area_type_suggested_reaction
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type_suggested_reaction):
        assert story_area_type_suggested_reaction.type == self.type
        assert story_area_type_suggested_reaction.reaction_type == self.reaction_type
        assert story_area_type_suggested_reaction.is_dark is self.is_dark
        assert story_area_type_suggested_reaction.is_flipped is self.is_flipped

    def test_to_dict(self, story_area_type_suggested_reaction):
        json_dict = story_area_type_suggested_reaction.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["reaction_type"] == self.reaction_type.to_dict()
        assert json_dict["is_dark"] is self.is_dark
        assert json_dict["is_flipped"] is self.is_flipped

    def test_equality(self, story_area_type_suggested_reaction):
        a = story_area_type_suggested_reaction
        b = StoryAreaTypeSuggestedReaction(self.reaction_type, self.is_dark, self.is_flipped)
        c = StoryAreaTypeSuggestedReaction(self.reaction_type, not self.is_dark, self.is_flipped)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type_link():
    return StoryAreaTypeLink(
        url=TestStoryAreaTypeLinkWithoutRequest.url,
    )


class TestStoryAreaTypeLinkWithoutRequest(StoryAreaTypeTestBase):
    type = StoryAreaTypeType.LINK

    def test_slot_behaviour(self, story_area_type_link):
        inst = story_area_type_link
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type_link):
        assert story_area_type_link.type == self.type
        assert story_area_type_link.url == self.url

    def test_to_dict(self, story_area_type_link):
        json_dict = story_area_type_link.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["url"] == self.url

    def test_equality(self, story_area_type_link):
        a = story_area_type_link
        b = StoryAreaTypeLink(self.url)
        c = StoryAreaTypeLink("other_http_url")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type_weather():
    return StoryAreaTypeWeather(
        temperature=TestStoryAreaTypeWeatherWithoutRequest.temperature,
        emoji=TestStoryAreaTypeWeatherWithoutRequest.emoji,
        background_color=TestStoryAreaTypeWeatherWithoutRequest.background_color,
    )


class TestStoryAreaTypeWeatherWithoutRequest(StoryAreaTypeTestBase):
    type = StoryAreaTypeType.WEATHER

    def test_slot_behaviour(self, story_area_type_weather):
        inst = story_area_type_weather
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type_weather):
        assert story_area_type_weather.type == self.type
        assert story_area_type_weather.temperature == self.temperature
        assert story_area_type_weather.emoji == self.emoji
        assert story_area_type_weather.background_color == self.background_color

    def test_to_dict(self, story_area_type_weather):
        json_dict = story_area_type_weather.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["temperature"] == self.temperature
        assert json_dict["emoji"] == self.emoji
        assert json_dict["background_color"] == self.background_color

    def test_equality(self, story_area_type_weather):
        a = story_area_type_weather
        b = StoryAreaTypeWeather(self.temperature, self.emoji, self.background_color)
        c = StoryAreaTypeWeather(self.temperature - 5.0, self.emoji, self.background_color)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def story_area_type_unique_gift():
    return StoryAreaTypeUniqueGift(
        name=TestStoryAreaTypeUniqueGiftWithoutRequest.name,
    )


class TestStoryAreaTypeUniqueGiftWithoutRequest(StoryAreaTypeTestBase):
    type = StoryAreaTypeType.UNIQUE_GIFT

    def test_slot_behaviour(self, story_area_type_unique_gift):
        inst = story_area_type_unique_gift
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, story_area_type_unique_gift):
        assert story_area_type_unique_gift.type == self.type
        assert story_area_type_unique_gift.name == self.name

    def test_to_dict(self, story_area_type_unique_gift):
        json_dict = story_area_type_unique_gift.to_dict()
        assert isinstance(json_dict, dict)
        assert json_dict["type"] == self.type
        assert json_dict["name"] == self.name

    def test_equality(self, story_area_type_unique_gift):
        a = story_area_type_unique_gift
        b = StoryAreaTypeUniqueGift(self.name)
        c = StoryAreaTypeUniqueGift("other_name")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
