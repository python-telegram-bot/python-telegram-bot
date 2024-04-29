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

from telegram import BotCommand, ProximityAlertTriggered, User
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def proximity_alert_triggered():
    return ProximityAlertTriggered(
        TestProximityAlertTriggeredBase.traveler,
        TestProximityAlertTriggeredBase.watcher,
        TestProximityAlertTriggeredBase.distance,
    )


class TestProximityAlertTriggeredBase:
    traveler = User(1, "foo", False)
    watcher = User(2, "bar", False)
    distance = 42


class TestProximityAlertTriggeredWithoutRequest(TestProximityAlertTriggeredBase):
    def test_slot_behaviour(self, proximity_alert_triggered):
        inst = proximity_alert_triggered
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "traveler": self.traveler.to_dict(),
            "watcher": self.watcher.to_dict(),
            "distance": self.distance,
        }
        proximity_alert_triggered = ProximityAlertTriggered.de_json(json_dict, bot)
        assert proximity_alert_triggered.api_kwargs == {}

        assert proximity_alert_triggered.traveler == self.traveler
        assert proximity_alert_triggered.traveler.first_name == self.traveler.first_name
        assert proximity_alert_triggered.watcher == self.watcher
        assert proximity_alert_triggered.watcher.first_name == self.watcher.first_name
        assert proximity_alert_triggered.distance == self.distance

    def test_to_dict(self, proximity_alert_triggered):
        proximity_alert_triggered_dict = proximity_alert_triggered.to_dict()

        assert isinstance(proximity_alert_triggered_dict, dict)
        assert (
            proximity_alert_triggered_dict["traveler"]
            == proximity_alert_triggered.traveler.to_dict()
        )
        assert (
            proximity_alert_triggered_dict["watcher"]
            == proximity_alert_triggered.watcher.to_dict()
        )
        assert proximity_alert_triggered_dict["distance"] == proximity_alert_triggered.distance

    def test_equality(self, proximity_alert_triggered):
        a = proximity_alert_triggered
        b = ProximityAlertTriggered(User(1, "John", False), User(2, "Doe", False), 42)
        c = ProximityAlertTriggered(User(3, "John", False), User(2, "Doe", False), 42)
        d = ProximityAlertTriggered(User(1, "John", False), User(3, "Doe", False), 42)
        e = ProximityAlertTriggered(User(1, "John", False), User(2, "Doe", False), 43)
        f = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)
