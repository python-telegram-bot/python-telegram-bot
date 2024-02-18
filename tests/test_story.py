#!/usr/bin/env python
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

from telegram import Story
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def story():
    return Story()


class TestStoryWithoutRequest:
    def test_slot_behaviour(self):
        story = Story()
        for attr in story.__slots__:
            assert getattr(story, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(story)) == len(set(mro_slots(story))), "duplicate slot"

    def test_de_json(self):
        story = Story.de_json({}, None)
        assert story.api_kwargs == {}
        assert isinstance(story, Story)

    def test_to_dict(self):
        story = Story()
        story_dict = story.to_dict()
        assert story_dict == {}
