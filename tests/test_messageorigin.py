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
import datetime as dtm
import inspect
from copy import deepcopy

import pytest

from telegram import (
    Chat,
    Dice,
    MessageOrigin,
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    MessageOriginUser,
    User,
)
from telegram._utils.datetime import to_timestamp
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots

ignored = ["self", "api_kwargs"]


class MODefaults:
    date: dtm.datetime = to_timestamp(dtm.datetime.now(dtm.UTC).replace(tzinfo=None))
    chat = Chat(1, Chat.CHANNEL)
    message_id = 123
    author_signautre = "PTB"
    sender_chat = Chat(1, Chat.CHANNEL)
    sender_user_name = "PTB"
    sender_user = User(1, "user", False)


def message_origin_channel():
    return MessageOriginChannel(
        MODefaults.date, MODefaults.chat, MODefaults.message_id, MODefaults.author_signautre
    )


def message_origin_chat():
    return MessageOriginChat(
        MODefaults.date,
        MODefaults.sender_chat,
        MODefaults.author_signautre,
    )


def message_origin_hidden_user():
    return MessageOriginHiddenUser(MODefaults.date, MODefaults.sender_user_name)


def message_origin_user():
    return MessageOriginUser(MODefaults.date, MODefaults.sender_user)


def make_json_dict(instance: MessageOrigin, include_optional_args: bool = False) -> dict:
    """Used to make the json dict which we use for testing de_json. Similar to iter_args()"""
    json_dict = {"type": instance.type}
    sig = inspect.signature(instance.__class__.__init__)

    for param in sig.parameters.values():
        if param.name in ignored:  # ignore irrelevant params
            continue

        val = getattr(instance, param.name)
        # Compulsory args-
        if param.default is inspect.Parameter.empty:
            if hasattr(val, "to_dict"):  # convert the user object or any future ones to dict.
                val = val.to_dict()
            json_dict[param.name] = val

        # If we want to test all args (for de_json)-
        elif param.default is not inspect.Parameter.empty and include_optional_args:
            json_dict[param.name] = val
    return json_dict


@pytest.fixture
def message_origin_type(request):
    return request.param()


@pytest.mark.parametrize(
    "message_origin_type",
    [
        message_origin_channel,
        message_origin_chat,
        message_origin_hidden_user,
        message_origin_user,
    ],
    indirect=True,
)
class TestMessageOriginTypesWithoutRequest:
    def test_slot_behaviour(self, message_origin_type):
        inst = message_origin_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_invalid_type(self, message_origin_type, offline_bot):
        json_dict = {"type": "invalid", "date": MODefaults.date}
        message_origin_type = MessageOrigin.de_json(json_dict, offline_bot)

        assert type(message_origin_type) is MessageOrigin
        assert message_origin_type.type == "invalid"

    def test_de_json_subclass(self, message_origin_type, offline_bot, chat_id):
        """This makes sure that e.g. MessageOriginChat(data, offline_bot) never returns a
        MessageOriginUser instance."""
        cls = message_origin_type.__class__
        json_dict = make_json_dict(message_origin_type, True)
        assert type(cls.de_json(json_dict, offline_bot)) is cls

    def test_to_dict(self, message_origin_type):
        message_origin_dict = message_origin_type.to_dict()

        assert isinstance(message_origin_dict, dict)
        assert message_origin_dict["type"] == message_origin_type.type
        assert message_origin_dict["date"] == message_origin_type.date

        for slot in message_origin_type.__slots__:  # additional verification for the optional args
            if slot in ("chat", "sender_chat", "sender_user"):
                assert (getattr(message_origin_type, slot)).to_dict() == message_origin_dict[slot]
                continue
            assert getattr(message_origin_type, slot) == message_origin_dict[slot]

    def test_equality(self, message_origin_type):
        a = MessageOrigin(type="type", date=MODefaults.date)
        b = MessageOrigin(type="type", date=MODefaults.date)
        c = message_origin_type
        d = deepcopy(message_origin_type)
        e = Dice(4, "emoji")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)


class TestMessageOriginWithoutRequest(DeserializationTestBase):
    de_json_class = MessageOrigin

    @pytest.fixture
    def de_json_dict(self):
        # An unknown type, so that MessageOrigin.de_json does not dispatch to a subclass
        return {"type": "unknown", "date": MODefaults.date}

    def test_de_json(self, offline_bot, de_json_dict):
        message_origin = MessageOrigin.de_json(de_json_dict, offline_bot)
        assert type(message_origin) is MessageOrigin
        assert message_origin.api_kwargs == {}

        assert message_origin.type == "unknown"
        assert to_timestamp(message_origin.date) == MODefaults.date


class TestMessageOriginUserWithoutRequest(DeserializationTestBase):
    de_json_class = MessageOriginUser

    @pytest.fixture
    def de_json_dict(self):
        return {"date": MODefaults.date, "sender_user": MODefaults.sender_user.to_dict()}

    def test_de_json(self, offline_bot, de_json_dict):
        message_origin = MessageOriginUser.de_json(de_json_dict, offline_bot)
        assert type(message_origin) is MessageOriginUser
        assert message_origin.api_kwargs == {}

        assert message_origin.type == MessageOrigin.USER
        assert to_timestamp(message_origin.date) == MODefaults.date
        assert message_origin.sender_user == MODefaults.sender_user


class TestMessageOriginHiddenUserWithoutRequest(DeserializationTestBase):
    de_json_class = MessageOriginHiddenUser

    @pytest.fixture
    def de_json_dict(self):
        return {"date": MODefaults.date, "sender_user_name": MODefaults.sender_user_name}

    def test_de_json(self, offline_bot, de_json_dict):
        message_origin = MessageOriginHiddenUser.de_json(de_json_dict, offline_bot)
        assert type(message_origin) is MessageOriginHiddenUser
        assert message_origin.api_kwargs == {}

        assert message_origin.type == MessageOrigin.HIDDEN_USER
        assert to_timestamp(message_origin.date) == MODefaults.date
        assert message_origin.sender_user_name == MODefaults.sender_user_name


class TestMessageOriginChatWithoutRequest(DeserializationTestBase):
    de_json_class = MessageOriginChat

    @pytest.fixture
    def de_json_dict(self):
        return {
            "date": MODefaults.date,
            "sender_chat": MODefaults.sender_chat.to_dict(),
            "author_signature": MODefaults.author_signautre,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        message_origin = MessageOriginChat.de_json(de_json_dict, offline_bot)
        assert type(message_origin) is MessageOriginChat
        assert message_origin.api_kwargs == {}

        assert message_origin.type == MessageOrigin.CHAT
        assert to_timestamp(message_origin.date) == MODefaults.date
        assert message_origin.sender_chat == MODefaults.sender_chat
        assert message_origin.author_signature == MODefaults.author_signautre


class TestMessageOriginChannelWithoutRequest(DeserializationTestBase):
    de_json_class = MessageOriginChannel

    @pytest.fixture
    def de_json_dict(self):
        return {
            "date": MODefaults.date,
            "chat": MODefaults.chat.to_dict(),
            "message_id": MODefaults.message_id,
            "author_signature": MODefaults.author_signautre,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        message_origin = MessageOriginChannel.de_json(de_json_dict, offline_bot)
        assert type(message_origin) is MessageOriginChannel
        assert message_origin.api_kwargs == {}

        assert message_origin.type == MessageOrigin.CHANNEL
        assert to_timestamp(message_origin.date) == MODefaults.date
        assert message_origin.chat == MODefaults.chat
        assert message_origin.message_id == MODefaults.message_id
        assert message_origin.author_signature == MODefaults.author_signautre
