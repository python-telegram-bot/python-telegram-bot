#!/usr/bin/env python
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

from telegram import Bot, Chat, Story
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def story(bot):
    story = Story(StoryTestBase.chat, StoryTestBase.id)
    story.set_bot(bot)
    return story


class StoryTestBase:
    chat = Chat(1, "")
    id = 0


class TestStoryWithoutRequest(StoryTestBase):
    def test_slot_behaviour(self, story):
        for attr in story.__slots__:
            assert getattr(story, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(story)) == len(set(mro_slots(story))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"chat": self.chat.to_dict(), "id": self.id}
        story = Story.de_json(json_dict, offline_bot)
        assert story.api_kwargs == {}
        assert story.chat == self.chat
        assert story.id == self.id
        assert isinstance(story, Story)

    def test_to_dict(self, story):
        story_dict = story.to_dict()
        assert story_dict["chat"] == self.chat.to_dict()
        assert story_dict["id"] == self.id

    def test_equality(self):
        a = Story(Chat(1, ""), 0)
        b = Story(Chat(1, ""), 0)
        c = Story(Chat(1, ""), 1)
        d = Story(Chat(2, ""), 0)
        e = Chat(1, "")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_instance_method_repost(self, monkeypatch, story):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["from_chat_id"] == story.chat.id
            story_id = kwargs["from_story_id"] == story.id
            return chat_id and story_id

        assert check_shortcut_signature(
            Story.repost,
            Bot.repost_story,
            [
                "from_chat_id",
                "from_story_id",
            ],
            additional_kwargs=[],
        )
        assert await check_shortcut_call(
            story.repost,
            story.get_bot(),
            "repost_story",
            shortcut_kwargs=["from_chat_id", "from_story_id"],
        )
        assert await check_defaults_handling(story.repost, story.get_bot())

        monkeypatch.setattr(story.get_bot(), "repost_story", make_assertion)
        assert await story.repost(
            business_connection_id="bcid",
            active_period=3600,
        )
