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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import datetime as dtm

import pytest

from telegram import InputLocationMessageContent, Location
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_location_message_content():
    return InputLocationMessageContent(
        InputLocationMessageContentTestBase.latitude,
        InputLocationMessageContentTestBase.longitude,
        live_period=InputLocationMessageContentTestBase.live_period,
        horizontal_accuracy=InputLocationMessageContentTestBase.horizontal_accuracy,
        heading=InputLocationMessageContentTestBase.heading,
        proximity_alert_radius=InputLocationMessageContentTestBase.proximity_alert_radius,
    )


class InputLocationMessageContentTestBase:
    latitude = -23.691288
    longitude = -46.788279
    live_period = dtm.timedelta(seconds=80)
    horizontal_accuracy = 50.5
    heading = 90
    proximity_alert_radius = 999


class TestInputLocationMessageContentWithoutRequest(InputLocationMessageContentTestBase):
    def test_slot_behaviour(self, input_location_message_content):
        inst = input_location_message_content
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, input_location_message_content):
        assert input_location_message_content.longitude == self.longitude
        assert input_location_message_content.latitude == self.latitude
        assert input_location_message_content._live_period == self.live_period
        assert input_location_message_content.horizontal_accuracy == self.horizontal_accuracy
        assert input_location_message_content.heading == self.heading
        assert input_location_message_content.proximity_alert_radius == self.proximity_alert_radius

    def test_to_dict(self, input_location_message_content):
        input_location_message_content_dict = input_location_message_content.to_dict()

        assert isinstance(input_location_message_content_dict, dict)
        assert (
            input_location_message_content_dict["latitude"]
            == input_location_message_content.latitude
        )
        assert (
            input_location_message_content_dict["longitude"]
            == input_location_message_content.longitude
        )
        assert input_location_message_content_dict["live_period"] == int(
            self.live_period.total_seconds()
        )
        assert isinstance(input_location_message_content_dict["live_period"], int)
        assert (
            input_location_message_content_dict["horizontal_accuracy"]
            == input_location_message_content.horizontal_accuracy
        )
        assert (
            input_location_message_content_dict["heading"]
            == input_location_message_content.heading
        )
        assert (
            input_location_message_content_dict["proximity_alert_radius"]
            == input_location_message_content.proximity_alert_radius
        )

    def test_time_period_properties(self, PTB_TIMEDELTA, input_location_message_content):
        live_period = input_location_message_content.live_period

        if PTB_TIMEDELTA:
            assert live_period == self.live_period
            assert isinstance(live_period, dtm.timedelta)
        else:
            assert live_period == int(self.live_period.total_seconds())
            assert isinstance(live_period, int)

    def test_time_period_int_deprecated(
        self, recwarn, PTB_TIMEDELTA, input_location_message_content
    ):
        input_location_message_content.live_period

        if PTB_TIMEDELTA:
            assert len(recwarn) == 0
        else:
            assert len(recwarn) == 1
            assert "`live_period` will be of type `datetime.timedelta`" in str(recwarn[0].message)
            assert recwarn[0].category is PTBDeprecationWarning

    def test_equality(self):
        a = InputLocationMessageContent(123, 456, 70)
        b = InputLocationMessageContent(123, 456, 90)
        c = InputLocationMessageContent(123, 457, 70)
        d = Location(123, 456)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
