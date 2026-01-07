#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from telegram import BotCommand, UserRating
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def user_rating():
    return UserRating(
        level=UserRatingTestBase.level,
        rating=UserRatingTestBase.rating,
        current_level_rating=UserRatingTestBase.current_level_rating,
        next_level_rating=UserRatingTestBase.next_level_rating,
    )


class UserRatingTestBase:
    level = 2
    rating = 120
    current_level_rating = 100
    next_level_rating = 180


class TestUserRatingWithoutRequest(UserRatingTestBase):
    def test_slot_behaviour(self, user_rating):
        for attr in user_rating.__slots__:
            assert getattr(user_rating, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(user_rating)) == len(set(mro_slots(user_rating))), "duplicate slot"

    def test_de_json_with_next(self, offline_bot):
        json_dict = {
            "level": self.level,
            "rating": self.rating,
            "current_level_rating": self.current_level_rating,
            "next_level_rating": self.next_level_rating,
        }
        ur = UserRating.de_json(json_dict, offline_bot)
        assert ur.api_kwargs == {}

        assert ur.level == self.level
        assert ur.rating == self.rating
        assert ur.current_level_rating == self.current_level_rating
        assert ur.next_level_rating == self.next_level_rating

    def test_de_json_no_optional(self, offline_bot):
        json_dict = {
            "level": self.level,
            "rating": self.rating,
            "current_level_rating": self.current_level_rating,
        }
        ur = UserRating.de_json(json_dict, offline_bot)
        assert ur.api_kwargs == {}

        assert ur.level == self.level
        assert ur.rating == self.rating
        assert ur.current_level_rating == self.current_level_rating
        assert ur.next_level_rating is None

    def test_to_dict(self, user_rating):
        ur_dict = user_rating.to_dict()

        assert isinstance(ur_dict, dict)
        assert ur_dict["level"] == user_rating.level
        assert ur_dict["rating"] == user_rating.rating
        assert ur_dict["current_level_rating"] == user_rating.current_level_rating
        assert ur_dict["next_level_rating"] == user_rating.next_level_rating

    def test_equality(self):
        a = UserRating(3, 200, 150, 300)
        b = UserRating(3, 200, 100, None)
        c = UserRating(3, 201, 150, 300)
        d = UserRating(4, 200, 150, 300)
        e = BotCommand("start", "description")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
