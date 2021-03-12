#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import VoiceChatStarted, VoiceChatEnded, VoiceChatParticipantsInvited, User


@pytest.fixture(scope='class')
def user1():
    return User(first_name='Misses Test', id=123, is_bot=False)


@pytest.fixture(scope='class')
def user2():
    return User(first_name='Mister Test', id=124, is_bot=False)


class TestVoiceChatStarted:
    def test_de_json(self):
        voice_chat_started = VoiceChatStarted.de_json({}, None)
        assert isinstance(voice_chat_started, VoiceChatStarted)

    def test_to_dict(self):
        voice_chat_started = VoiceChatStarted()
        voice_chat_dict = voice_chat_started.to_dict()
        assert voice_chat_dict == {}


class TestVoiceChatEnded:
    duration = 100

    def test_de_json(self):
        json_dict = {'duration': self.duration}
        voice_chat_ended = VoiceChatEnded.de_json(json_dict, None)

        assert voice_chat_ended.duration == self.duration

    def test_to_dict(self):
        voice_chat_ended = VoiceChatEnded(self.duration)
        voice_chat_dict = voice_chat_ended.to_dict()

        assert isinstance(voice_chat_dict, dict)
        assert voice_chat_dict["duration"] == self.duration

    def test_equality(self):
        a = VoiceChatEnded(100)
        b = VoiceChatEnded(100)
        c = VoiceChatEnded(50)
        d = VoiceChatEnded(25)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


class TestVoiceChatParticipantsInvited:
    def test_de_json(self, user1, user2, bot):
        json_data = {"users": [user1.to_dict(), user2.to_dict()]}
        voice_chat_participants = VoiceChatParticipantsInvited.de_json(json_data, bot)

        assert isinstance(voice_chat_participants.users, list)
        assert voice_chat_participants.users[0] == user1
        assert voice_chat_participants.users[1] == user2
        assert voice_chat_participants.users[0].id == user1.id
        assert voice_chat_participants.users[1].id == user2.id

    def test_to_dict(self, user1, user2):
        voice_chat_participants = VoiceChatParticipantsInvited([user1, user2])
        voice_chat_dict = voice_chat_participants.to_dict()

        assert isinstance(voice_chat_dict, dict)
        assert voice_chat_dict["users"] == [user1.to_dict(), user2.to_dict()]
        assert voice_chat_dict["users"][0]["id"] == user1.id
        assert voice_chat_dict["users"][1]["id"] == user2.id

    def test_equality(self, user1, user2):
        a = VoiceChatParticipantsInvited([user1])
        b = VoiceChatParticipantsInvited([user1])
        c = VoiceChatParticipantsInvited([user1, user2])
        d = VoiceChatParticipantsInvited([user2])

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
