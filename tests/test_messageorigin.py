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
import datetime
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
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots

ignored = ["self", "api_kwargs"]


class MODefaults:
    date: datetime.datetime = to_timestamp(datetime.datetime.utcnow())
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


def iter_args(
    instance: MessageOrigin, de_json_inst: MessageOrigin, include_optional: bool = False
):
    """
    We accept both the regular instance and de_json created instance and iterate over them for
    easy one line testing later one.
    """
    yield instance.type, de_json_inst.type  # yield this here cause it's not available in sig.

    sig = inspect.signature(instance.__class__.__init__)
    for param in sig.parameters.values():
        if param.name in ignored:
            continue
        inst_at, json_at = getattr(instance, param.name), getattr(de_json_inst, param.name)
        if isinstance(json_at, datetime.datetime):  # Convert datetime to int
            json_at = to_timestamp(json_at)
        if (
            param.default is not inspect.Parameter.empty and include_optional
        ) or param.default is inspect.Parameter.empty:
            yield inst_at, json_at


@pytest.fixture()
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

    def test_de_json_required_args(self, bot, message_origin_type):
        cls = message_origin_type.__class__
        assert cls.de_json({}, bot) is None

        json_dict = make_json_dict(message_origin_type)
        const_message_origin = MessageOrigin.de_json(json_dict, bot)
        assert const_message_origin.api_kwargs == {}

        assert isinstance(const_message_origin, MessageOrigin)
        assert isinstance(const_message_origin, cls)
        for msg_origin_type_at, const_msg_origin_at in iter_args(
            message_origin_type, const_message_origin
        ):
            assert msg_origin_type_at == const_msg_origin_at

    def test_de_json_all_args(self, bot, message_origin_type):
        json_dict = make_json_dict(message_origin_type, include_optional_args=True)
        const_message_origin = MessageOrigin.de_json(json_dict, bot)

        assert const_message_origin.api_kwargs == {}

        assert isinstance(const_message_origin, MessageOrigin)
        assert isinstance(const_message_origin, message_origin_type.__class__)
        for msg_origin_type_at, const_msg_origin_at in iter_args(
            message_origin_type, const_message_origin, True
        ):
            assert msg_origin_type_at == const_msg_origin_at

    def test_de_json_messageorigin_localization(self, message_origin_type, tz_bot, bot, raw_bot):
        json_dict = make_json_dict(message_origin_type, include_optional_args=True)
        msgorigin_raw = MessageOrigin.de_json(json_dict, raw_bot)
        msgorigin_bot = MessageOrigin.de_json(json_dict, bot)
        msgorigin_tz = MessageOrigin.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        msgorigin_offset = msgorigin_tz.date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(msgorigin_tz.date.replace(tzinfo=None))

        assert msgorigin_raw.date.tzinfo == UTC
        assert msgorigin_bot.date.tzinfo == UTC
        assert msgorigin_offset == tz_bot_offset

    def test_de_json_invalid_type(self, message_origin_type, bot):
        json_dict = {"type": "invalid", "date": MODefaults.date}
        message_origin_type = MessageOrigin.de_json(json_dict, bot)

        assert type(message_origin_type) is MessageOrigin
        assert message_origin_type.type == "invalid"

    def test_de_json_subclass(self, message_origin_type, bot, chat_id):
        """This makes sure that e.g. MessageOriginChat(data, bot) never returns a
        MessageOriginUser instance."""
        cls = message_origin_type.__class__
        json_dict = make_json_dict(message_origin_type, True)
        assert type(cls.de_json(json_dict, bot)) is cls

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
