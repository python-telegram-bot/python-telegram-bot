#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

from telegram import (
    User,
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def user1():
    return User(first_name="Misses Test", id=123, is_bot=False)


@pytest.fixture(scope="module")
def user2():
    return User(first_name="Mister Test", id=124, is_bot=False)


class TestVideoChatStartedWithoutRequest:
    def test_slot_behaviour(self):
        action = VideoChatStarted()
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        video_chat_started = VideoChatStarted.de_json({}, None)
        assert video_chat_started.api_kwargs == {}
        assert isinstance(video_chat_started, VideoChatStarted)

    def test_to_dict(self):
        video_chat_started = VideoChatStarted()
        video_chat_dict = video_chat_started.to_dict()
        assert video_chat_dict == {}


class TestVideoChatEndedWithoutRequest:
    duration = 100

    def test_slot_behaviour(self):
        action = VideoChatEnded(8)
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self):
        json_dict = {"duration": self.duration}
        video_chat_ended = VideoChatEnded.de_json(json_dict, None)
        assert video_chat_ended.api_kwargs == {}

        assert video_chat_ended.duration == self.duration

    def test_to_dict(self):
        video_chat_ended = VideoChatEnded(self.duration)
        video_chat_dict = video_chat_ended.to_dict()

        assert isinstance(video_chat_dict, dict)
        assert video_chat_dict["duration"] == self.duration

    def test_equality(self):
        a = VideoChatEnded(100)
        b = VideoChatEnded(100)
        c = VideoChatEnded(50)
        d = VideoChatStarted()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestVideoChatParticipantsInvitedWithoutRequest:
    def test_slot_behaviour(self, user1):
        action = VideoChatParticipantsInvited([user1])
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json(self, user1, user2, bot):
        json_data = {"users": [user1.to_dict(), user2.to_dict()]}
        video_chat_participants = VideoChatParticipantsInvited.de_json(json_data, bot)
        assert video_chat_participants.api_kwargs == {}

        assert isinstance(video_chat_participants.users, tuple)
        assert video_chat_participants.users[0] == user1
        assert video_chat_participants.users[1] == user2
        assert video_chat_participants.users[0].id == user1.id
        assert video_chat_participants.users[1].id == user2.id

    @pytest.mark.parametrize("use_users", [True, False])
    def test_to_dict(self, user1, user2, use_users):
        video_chat_participants = VideoChatParticipantsInvited([user1, user2] if use_users else ())
        video_chat_dict = video_chat_participants.to_dict()

        assert isinstance(video_chat_dict, dict)
        if use_users:
            assert video_chat_dict["users"] == [user1.to_dict(), user2.to_dict()]
            assert video_chat_dict["users"][0]["id"] == user1.id
            assert video_chat_dict["users"][1]["id"] == user2.id
        else:
            assert video_chat_dict == {}

    def test_equality(self, user1, user2):
        a = VideoChatParticipantsInvited([user1])
        b = VideoChatParticipantsInvited([user1])
        c = VideoChatParticipantsInvited([user1, user2])
        d = VideoChatParticipantsInvited([])
        e = VideoChatStarted()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


class TestVideoChatScheduledWithoutRequest:
    start_date = dtm.datetime.now(dtm.timezone.utc)

    def test_slot_behaviour(self):
        inst = VideoChatScheduled(self.start_date)
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self):
        assert VideoChatScheduled(self.start_date).start_date == self.start_date

    def test_de_json(self, bot):
        assert VideoChatScheduled.de_json({}, bot=bot) is None

        json_dict = {"start_date": to_timestamp(self.start_date)}
        video_chat_scheduled = VideoChatScheduled.de_json(json_dict, bot)
        assert video_chat_scheduled.api_kwargs == {}

        assert abs(video_chat_scheduled.start_date - self.start_date) < dtm.timedelta(seconds=1)

    def test_de_json_localization(self, tz_bot, bot, raw_bot):
        json_dict = {"start_date": to_timestamp(self.start_date)}

        videochat_raw = VideoChatScheduled.de_json(json_dict, raw_bot)
        videochat_bot = VideoChatScheduled.de_json(json_dict, bot)
        videochat_tz = VideoChatScheduled.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        videochat_offset = videochat_tz.start_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            videochat_tz.start_date.replace(tzinfo=None)
        )

        assert videochat_raw.start_date.tzinfo == UTC
        assert videochat_bot.start_date.tzinfo == UTC
        assert videochat_offset == tz_bot_offset

    def test_to_dict(self):
        video_chat_scheduled = VideoChatScheduled(self.start_date)
        video_chat_scheduled_dict = video_chat_scheduled.to_dict()

        assert isinstance(video_chat_scheduled_dict, dict)
        assert video_chat_scheduled_dict["start_date"] == to_timestamp(self.start_date)

    def test_equality(self):
        a = VideoChatScheduled(self.start_date)
        b = VideoChatScheduled(self.start_date)
        c = VideoChatScheduled(dtm.datetime.utcnow() + dtm.timedelta(seconds=5))
        d = VideoChatStarted()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
