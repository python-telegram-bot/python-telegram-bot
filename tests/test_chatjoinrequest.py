#!/usr/bin/env python
#
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
import datetime

import pytest

from telegram import Bot, Chat, ChatInviteLink, ChatJoinRequest, User
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def time():
    return datetime.datetime.now(tz=UTC)


@pytest.fixture(scope="module")
def chat_join_request(bot, time):
    cjr = ChatJoinRequest(
        chat=TestChatJoinRequestBase.chat,
        from_user=TestChatJoinRequestBase.from_user,
        date=time,
        bio=TestChatJoinRequestBase.bio,
        invite_link=TestChatJoinRequestBase.invite_link,
        user_chat_id=TestChatJoinRequestBase.from_user.id,
    )
    cjr.set_bot(bot)
    return cjr


class TestChatJoinRequestBase:
    chat = Chat(1, Chat.SUPERGROUP)
    from_user = User(2, "first_name", False)
    bio = "bio"
    invite_link = ChatInviteLink(
        "https://invite.link",
        User(42, "creator", False),
        creates_join_request=False,
        name="InviteLink",
        is_revoked=False,
        is_primary=False,
    )


class TestChatJoinRequestWithoutRequest(TestChatJoinRequestBase):
    def test_slot_behaviour(self, chat_join_request):
        inst = chat_join_request
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, time):
        json_dict = {
            "chat": self.chat.to_dict(),
            "from": self.from_user.to_dict(),
            "date": to_timestamp(time),
            "user_chat_id": self.from_user.id,
        }
        chat_join_request = ChatJoinRequest.de_json(json_dict, bot)
        assert chat_join_request.api_kwargs == {}

        assert chat_join_request.chat == self.chat
        assert chat_join_request.from_user == self.from_user
        assert abs(chat_join_request.date - time) < datetime.timedelta(seconds=1)
        assert to_timestamp(chat_join_request.date) == to_timestamp(time)
        assert chat_join_request.user_chat_id == self.from_user.id

        json_dict.update({"bio": self.bio, "invite_link": self.invite_link.to_dict()})
        chat_join_request = ChatJoinRequest.de_json(json_dict, bot)
        assert chat_join_request.api_kwargs == {}

        assert chat_join_request.chat == self.chat
        assert chat_join_request.from_user == self.from_user
        assert abs(chat_join_request.date - time) < datetime.timedelta(seconds=1)
        assert to_timestamp(chat_join_request.date) == to_timestamp(time)
        assert chat_join_request.user_chat_id == self.from_user.id
        assert chat_join_request.bio == self.bio
        assert chat_join_request.invite_link == self.invite_link

    def test_to_dict(self, chat_join_request, time):
        chat_join_request_dict = chat_join_request.to_dict()

        assert isinstance(chat_join_request_dict, dict)
        assert chat_join_request_dict["chat"] == chat_join_request.chat.to_dict()
        assert chat_join_request_dict["from"] == chat_join_request.from_user.to_dict()
        assert chat_join_request_dict["date"] == to_timestamp(chat_join_request.date)
        assert chat_join_request_dict["bio"] == chat_join_request.bio
        assert chat_join_request_dict["invite_link"] == chat_join_request.invite_link.to_dict()
        assert chat_join_request_dict["user_chat_id"] == self.from_user.id

    def test_equality(self, chat_join_request, time):
        a = chat_join_request
        b = ChatJoinRequest(self.chat, self.from_user, time, self.from_user.id)
        c = ChatJoinRequest(self.chat, self.from_user, time, self.from_user.id, bio="bio")
        d = ChatJoinRequest(
            self.chat, self.from_user, time + datetime.timedelta(1), self.from_user.id
        )
        e = ChatJoinRequest(self.chat, User(-1, "last_name", True), time, -1)
        f = User(456, "", False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)

    async def test_approve(self, monkeypatch, chat_join_request):
        async def make_assertion(*_, **kwargs):
            chat_id_test = kwargs["chat_id"] == chat_join_request.chat.id
            user_id_test = kwargs["user_id"] == chat_join_request.from_user.id

            return chat_id_test and user_id_test

        assert check_shortcut_signature(
            ChatJoinRequest.approve, Bot.approve_chat_join_request, ["chat_id", "user_id"], []
        )
        assert await check_shortcut_call(
            chat_join_request.approve, chat_join_request.get_bot(), "approve_chat_join_request"
        )
        assert await check_defaults_handling(
            chat_join_request.approve, chat_join_request.get_bot()
        )

        monkeypatch.setattr(
            chat_join_request.get_bot(), "approve_chat_join_request", make_assertion
        )
        assert await chat_join_request.approve()

    async def test_decline(self, monkeypatch, chat_join_request):
        async def make_assertion(*_, **kwargs):
            chat_id_test = kwargs["chat_id"] == chat_join_request.chat.id
            user_id_test = kwargs["user_id"] == chat_join_request.from_user.id

            return chat_id_test and user_id_test

        assert check_shortcut_signature(
            ChatJoinRequest.decline, Bot.decline_chat_join_request, ["chat_id", "user_id"], []
        )
        assert await check_shortcut_call(
            chat_join_request.decline, chat_join_request.get_bot(), "decline_chat_join_request"
        )
        assert await check_defaults_handling(
            chat_join_request.decline, chat_join_request.get_bot()
        )

        monkeypatch.setattr(
            chat_join_request.get_bot(), "decline_chat_join_request", make_assertion
        )
        assert await chat_join_request.decline()
