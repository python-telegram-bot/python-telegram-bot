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
from datetime import datetime

import pytest

from telegram import BusinessConnection, BusinessMessagesDeleted, Chat, User
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


class TestBusinessBase:
    id_ = "123"
    user = User(123, "test_user", False)
    user_chat_id = 123
    date = datetime.now(tz=UTC).replace(microsecond=0)
    can_reply = True
    is_enabled = True
    message_ids = (123, 321)
    business_connection_id = "123"
    chat = Chat(123, "test_chat")


@pytest.fixture(scope="module")
def business_connection():
    return BusinessConnection(
        TestBusinessBase.id_,
        TestBusinessBase.user,
        TestBusinessBase.user_chat_id,
        TestBusinessBase.date,
        TestBusinessBase.can_reply,
        TestBusinessBase.is_enabled,
    )


@pytest.fixture(scope="module")
def business_messages_deleted():
    return BusinessMessagesDeleted(
        TestBusinessBase.business_connection_id,
        TestBusinessBase.chat,
        TestBusinessBase.message_ids,
    )


class TestBusinessConnectionWithoutRequest(TestBusinessBase):
    def test_slots(self, business_connection):
        bc = business_connection
        for attr in bc.__slots__:
            assert getattr(bc, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bc)) == len(set(mro_slots(bc))), "duplicate slot"

    def test_de_json(self):
        json_dict = {
            "id": self.id_,
            "user": self.user.to_dict(),
            "user_chat_id": self.user_chat_id,
            "date": to_timestamp(self.date),
            "can_reply": self.can_reply,
            "is_enabled": self.is_enabled,
        }
        bc = BusinessConnection.de_json(json_dict, None)
        assert bc.id == self.id_
        assert bc.user == self.user
        assert bc.user_chat_id == self.user_chat_id
        assert bc.date == self.date
        assert bc.can_reply == self.can_reply
        assert bc.is_enabled == self.is_enabled
        assert bc.api_kwargs == {}
        assert isinstance(bc, BusinessConnection)

    def test_de_json_localization(self, bot, raw_bot, tz_bot):
        json_dict = {
            "id": self.id_,
            "user": self.user.to_dict(),
            "user_chat_id": self.user_chat_id,
            "date": to_timestamp(self.date),
            "can_reply": self.can_reply,
            "is_enabled": self.is_enabled,
        }
        chat_bot = BusinessConnection.de_json(json_dict, bot)
        chat_bot_raw = BusinessConnection.de_json(json_dict, raw_bot)
        chat_bot_tz = BusinessConnection.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        date_offset = chat_bot_tz.date.utcoffset()
        date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(chat_bot_tz.date.replace(tzinfo=None))

        assert chat_bot.date.tzinfo == UTC
        assert chat_bot_raw.date.tzinfo == UTC
        assert date_offset_tz == date_offset

    def test_to_dict(self, business_connection):
        bc_dict = business_connection.to_dict()
        assert isinstance(bc_dict, dict)
        assert bc_dict["id"] == self.id_
        assert bc_dict["user"] == self.user.to_dict()
        assert bc_dict["user_chat_id"] == self.user_chat_id
        assert bc_dict["date"] == to_timestamp(self.date)
        assert bc_dict["can_reply"] == self.can_reply
        assert bc_dict["is_enabled"] == self.is_enabled

    def test_equality(self):
        bc1 = BusinessConnection(
            self.id_, self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )
        bc2 = BusinessConnection(
            self.id_, self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )
        bc3 = BusinessConnection(
            "321", self.user, self.user_chat_id, self.date, self.can_reply, self.is_enabled
        )

        assert bc1 == bc2
        assert hash(bc1) == hash(bc2)

        assert bc1 != bc3
        assert hash(bc1) != hash(bc3)


class TestBusinessMessagesDeleted(TestBusinessBase):
    def test_slots(self, business_messages_deleted):
        bmd = business_messages_deleted
        for attr in bmd.__slots__:
            assert getattr(bmd, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(bmd)) == len(set(mro_slots(bmd))), "duplicate slot"

    def test_to_dict(self, business_messages_deleted):
        bmd_dict = business_messages_deleted.to_dict()
        assert isinstance(bmd_dict, dict)
        assert bmd_dict["message_ids"] == list(self.message_ids)
        assert bmd_dict["business_connection_id"] == self.business_connection_id
        assert bmd_dict["chat"] == self.chat.to_dict()

    def test_de_json(self):
        json_dict = {
            "business_connection_id": self.business_connection_id,
            "chat": self.chat.to_dict(),
            "message_ids": self.message_ids,
        }
        bmd = BusinessMessagesDeleted.de_json(json_dict, None)
        assert bmd.business_connection_id == self.business_connection_id
        assert bmd.chat == self.chat
        assert bmd.message_ids == self.message_ids
        assert bmd.api_kwargs == {}
        assert isinstance(bmd, BusinessMessagesDeleted)

    def test_equality(self):
        bmd1 = BusinessMessagesDeleted(self.business_connection_id, self.chat, self.message_ids)
        bmd2 = BusinessMessagesDeleted(self.business_connection_id, self.chat, self.message_ids)
        bmd3 = BusinessMessagesDeleted("1", Chat(4, "random"), [321, 123])

        assert bmd1 == bmd2
        assert hash(bmd1) == hash(bmd2)

        assert bmd1 != bmd3
        assert hash(bmd1) != hash(bmd3)
