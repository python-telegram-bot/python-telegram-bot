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
"""This module contains the TestDirectMessagesTopic class."""

import pytest

from telegram import DirectMessagesTopic, User
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def direct_messages_topic(offline_bot):
    dmt = DirectMessagesTopic(
        topic_id=DirectMessagesTopicTestBase.topic_id,
        user=DirectMessagesTopicTestBase.user,
    )
    dmt.set_bot(offline_bot)
    dmt._unfreeze()
    return dmt


class DirectMessagesTopicTestBase:
    topic_id = 12345
    user = User(id=67890, is_bot=False, first_name="Test")


class TestDirectMessagesTopicWithoutRequest(DirectMessagesTopicTestBase):
    def test_slot_behaviour(self, direct_messages_topic):
        cfi = direct_messages_topic
        for attr in cfi.__slots__:
            assert getattr(cfi, attr, "err") != "err", f"got extra slot '{attr}'"

        assert len(mro_slots(cfi)) == len(set(mro_slots(cfi))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "topic_id": self.topic_id,
            "user": self.user.to_dict(),
        }

        dmt = DirectMessagesTopic.de_json(json_dict, offline_bot)
        assert dmt.topic_id == self.topic_id
        assert dmt.user == self.user
        assert dmt.api_kwargs == {}

    def test_to_dict(self, direct_messages_topic):
        dmt = direct_messages_topic
        dmt_dict = dmt.to_dict()

        assert isinstance(dmt_dict, dict)
        assert dmt_dict["topic_id"] == dmt.topic_id
        assert dmt_dict["user"] == dmt.user.to_dict()

    def test_equality(self, direct_messages_topic):
        dmt_1 = direct_messages_topic
        dmt_2 = DirectMessagesTopic(
            topic_id=dmt_1.topic_id,
            user=dmt_1.user,
        )
        assert dmt_1 == dmt_2
        assert hash(dmt_1) == hash(dmt_2)

        random = User(id=99999, is_bot=False, first_name="Random")
        assert random != dmt_2
        assert hash(random) != hash(dmt_2)

        dmt_3 = DirectMessagesTopic(
            topic_id=8371,
            user=dmt_1.user,
        )
        assert dmt_1 != dmt_3
        assert hash(dmt_1) != hash(dmt_3)
