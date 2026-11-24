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
# along with this program. If not, see [http://www.gnu.org/licenses/].
import datetime as dtm

import pytest

from telegram import Chat, InaccessibleMessage, MaybeInaccessibleMessage, Message
from telegram._utils.datetime import to_timestamp
from telegram.constants import ZERO_DATE
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="class")
def maybe_inaccessible_message():
    return MaybeInaccessibleMessage(
        MaybeInaccessibleMessageTestBase.chat,
        MaybeInaccessibleMessageTestBase.message_id,
        MaybeInaccessibleMessageTestBase.date,
    )


class MaybeInaccessibleMessageTestBase:
    chat = Chat(1, "title")
    message_id = 123
    date = dtm.datetime.now(dtm.UTC).replace(microsecond=0)


class TestMaybeInaccessibleMessageWithoutRequest(
    MaybeInaccessibleMessageTestBase, DeserializationTestBase
):
    de_json_class = MaybeInaccessibleMessage

    @pytest.fixture
    def de_json_dict(self):
        return {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": to_timestamp(self.date),
        }

    def test_slot_behaviour(self, maybe_inaccessible_message):
        for attr in maybe_inaccessible_message.__slots__:
            assert getattr(maybe_inaccessible_message, attr, "err") != "err", (
                f"got extra slot '{attr}'"
            )
        assert len(mro_slots(maybe_inaccessible_message)) == len(
            set(mro_slots(maybe_inaccessible_message))
        ), "duplicate slot"

    def test_to_dict(self, maybe_inaccessible_message):
        maybe_inaccessible_message_dict = maybe_inaccessible_message.to_dict()

        assert isinstance(maybe_inaccessible_message_dict, dict)
        assert maybe_inaccessible_message_dict["chat"] == self.chat.to_dict()
        assert maybe_inaccessible_message_dict["message_id"] == self.message_id
        assert maybe_inaccessible_message_dict["date"] == to_timestamp(self.date)

    def test_de_json(self, offline_bot, de_json_dict):
        # MaybeInaccessibleMessage.de_json never returns the base class: a message with a date
        # is a Message, see test_de_json_zero_date for the inaccessible ones
        maybe_inaccessible_message = MaybeInaccessibleMessage.de_json(de_json_dict, offline_bot)
        assert type(maybe_inaccessible_message) is Message
        assert maybe_inaccessible_message.api_kwargs == {}

        assert maybe_inaccessible_message.chat == self.chat
        assert maybe_inaccessible_message.message_id == self.message_id
        assert maybe_inaccessible_message.date == self.date

    def test_de_json_zero_date(self, offline_bot):
        json_dict = {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": 0,
        }

        maybe_inaccessible_message = MaybeInaccessibleMessage.de_json(json_dict, offline_bot)
        assert type(maybe_inaccessible_message) is InaccessibleMessage
        assert maybe_inaccessible_message.date == ZERO_DATE
        assert maybe_inaccessible_message.date is ZERO_DATE

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "InaccessibleMessage has no `date` argument, so the `date` sent by Telegram ends up "
            "in `api_kwargs`"
        ),
    )
    def test_de_json_zero_date_api_kwargs(self, offline_bot, de_json_dict):
        json_dict = de_json_dict | {"date": 0}
        maybe_inaccessible_message = MaybeInaccessibleMessage.de_json(json_dict, offline_bot)
        assert maybe_inaccessible_message.api_kwargs == {}

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


@pytest.fixture(scope="class")
def inaccessible_message():
    return InaccessibleMessage(
        InaccessibleMessageTestBase.chat,
        InaccessibleMessageTestBase.message_id,
    )


class InaccessibleMessageTestBase:
    chat = Chat(1, "title")
    message_id = 123


class TestInaccessibleMessageWithoutRequest(InaccessibleMessageTestBase, DeserializationTestBase):
    de_json_class = InaccessibleMessage

    @pytest.fixture
    def de_json_dict(self):
        # Telegram also sends `"date": 0`, see TestMaybeInaccessibleMessageWithoutRequest
        return {"chat": self.chat.to_dict(), "message_id": self.message_id}

    def test_slot_behaviour(self, inaccessible_message):
        inst = inaccessible_message
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot, de_json_dict):
        inaccessible_message = InaccessibleMessage.de_json(de_json_dict, offline_bot)
        assert type(inaccessible_message) is InaccessibleMessage
        assert inaccessible_message.api_kwargs == {}

        assert inaccessible_message.chat == self.chat
        assert inaccessible_message.message_id == self.message_id
        assert inaccessible_message.date is ZERO_DATE
        assert not inaccessible_message.is_accessible

    def test_to_dict(self, inaccessible_message):
        assert inaccessible_message.to_dict() == {
            "chat": self.chat.to_dict(),
            "message_id": self.message_id,
            "date": 0,
        }

    def test_equality(self, inaccessible_message):
        a = inaccessible_message
        b = InaccessibleMessage(self.chat, self.message_id)
        c = InaccessibleMessage(self.chat, self.message_id + 1)
        d = InaccessibleMessage(Chat(2, "title"), self.message_id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
