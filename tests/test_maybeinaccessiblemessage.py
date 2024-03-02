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
# along with this program. If not, see [http://www.gnu.org/licenses/].
import datetime as dtm

import pytest

from telegram import Chat, MaybeInaccessibleMessage
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ZERO_DATE
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="class")
def maybe_inaccessible_message():
    return MaybeInaccessibleMessage(
        TestMaybeInaccessibleMessageBase.chat,
        TestMaybeInaccessibleMessageBase.message_id,
        TestMaybeInaccessibleMessageBase.date,
    )


class TestMaybeInaccessibleMessageBase:
    chat = Chat(1, "title")
    message_id = 123
    date = dtm.datetime.now(dtm.timezone.utc).replace(microsecond=0)


class TestMaybeInaccessibleMessageWithoutRequest(TestMaybeInaccessibleMessageBase):
    def test_slot_behaviour(self, maybe_inaccessible_message):
        for attr in maybe_inaccessible_message.__slots__:
            assert (
                getattr(maybe_inaccessible_message, attr, "err") != "err"
            ), f"got extra slot '{attr}'"
        assert len(mro_slots(maybe_inaccessible_message)) == len(
            set(mro_slots(maybe_inaccessible_message))
        ), "duplicate slot"

    def test_to_dict(self, maybe_inaccessible_message):
        maybe_inaccessible_message_dict = maybe_inaccessible_message.to_dict()

        assert isinstance(maybe_inaccessible_message_dict, dict)
        assert maybe_inaccessible_message_dict["chat"] == self.chat.to_dict()
        assert maybe_inaccessible_message_dict["message_id"] == self.message_id
        assert maybe_inaccessible_message_dict["date"] == to_timestamp(self.date)

    def test_de_json(self, bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
        }
        maybe_inaccessible_message = MaybeInaccessibleMessage.de_json(json_dict, bot)
        assert maybe_inaccessible_message.api_kwargs == {}

        assert maybe_inaccessible_message.chat == self.chat
        assert maybe_inaccessible_message.message_id == self.message_id
        assert maybe_inaccessible_message.date == self.date

    def test_de_json_localization(self, tz_bot, bot, raw_bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
        }

        maybe_inaccessible_message_raw = MaybeInaccessibleMessage.de_json(json_dict, raw_bot)
        maybe_inaccessible_message_bot = MaybeInaccessibleMessage.de_json(json_dict, bot)
        maybe_inaccessible_message_bot_tz = MaybeInaccessibleMessage.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        maybe_inaccessible_message_bot_tz_offset = (
            maybe_inaccessible_message_bot_tz.date.utcoffset()
        )
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            maybe_inaccessible_message_bot_tz.date.replace(tzinfo=None)
        )

        assert maybe_inaccessible_message_raw.date.tzinfo == UTC
        assert maybe_inaccessible_message_bot.date.tzinfo == UTC
        assert maybe_inaccessible_message_bot_tz_offset == tz_bot_offset

    def test_de_json_zero_date(self, bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": 0,
        }

        maybe_inaccessible_message = MaybeInaccessibleMessage.de_json(json_dict, bot)
        assert maybe_inaccessible_message.date == ZERO_DATE
        assert maybe_inaccessible_message.date is ZERO_DATE

    def test_is_accessible(self):
        assert MaybeInaccessibleMessage(self.chat, self.message_id, self.date).is_accessible
        assert not MaybeInaccessibleMessage(self.chat, self.message_id, ZERO_DATE).is_accessible

    def test_equality(self, maybe_inaccessible_message):
        a = maybe_inaccessible_message
        b = MaybeInaccessibleMessage(
            self.chat, self.message_id, self.date + dtm.timedelta(seconds=1)
        )
        c = MaybeInaccessibleMessage(self.chat, self.message_id + 1, self.date)
        d = MaybeInaccessibleMessage(Chat(2, "title"), self.message_id, self.date)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)
        assert a is not c

        assert a != d
        assert hash(a) != hash(d)
        assert a is not d
