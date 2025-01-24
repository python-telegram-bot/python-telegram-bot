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

from telegram import Birthdate
from tests.auxil.slots import mro_slots


class BirthdateTestBase:
    day = 1
    month = 1
    year = 2022


@pytest.fixture(scope="module")
def birthdate():
    return Birthdate(BirthdateTestBase.day, BirthdateTestBase.month, BirthdateTestBase.year)


class TestBirthdateWithoutRequest(BirthdateTestBase):
    def test_slot_behaviour(self, birthdate):
        for attr in birthdate.__slots__:
            assert getattr(birthdate, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(birthdate)) == len(set(mro_slots(birthdate))), "duplicate slot"

    def test_to_dict(self, birthdate):
        bd_dict = birthdate.to_dict()
        assert isinstance(bd_dict, dict)
        assert bd_dict["day"] == self.day
        assert bd_dict["month"] == self.month
        assert bd_dict["year"] == self.year

    def test_de_json(self, offline_bot):
        json_dict = {"day": self.day, "month": self.month, "year": self.year}
        bd = Birthdate.de_json(json_dict, offline_bot)
        assert isinstance(bd, Birthdate)
        assert bd.day == self.day
        assert bd.month == self.month
        assert bd.year == self.year

    def test_equality(self):
        bd1 = Birthdate(1, 1, 2022)
        bd2 = Birthdate(1, 1, 2022)
        bd3 = Birthdate(1, 1, 2023)
        bd4 = Birthdate(1, 2, 2022)

        assert bd1 == bd2
        assert hash(bd1) == hash(bd2)

        assert bd1 == bd3
        assert hash(bd1) == hash(bd3)

        assert bd1 != bd4
        assert hash(bd1) != hash(bd4)

    def test_to_date(self, birthdate):
        assert isinstance(birthdate.to_date(), dtm.date)
        assert birthdate.to_date() == dtm.date(self.year, self.month, self.day)
        new_bd = birthdate.to_date(2023)
        assert new_bd == dtm.date(2023, self.month, self.day)

    def test_to_date_no_year(self):
        bd = Birthdate(1, 1)
        with pytest.raises(ValueError, match="The `year` argument is required"):
            bd.to_date()
