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
import inspect

import pytest

from telegram import (
    Chat,
    ChatInviteLink,
    ChatMember,
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberOwner,
    ChatMemberUpdated,
    User,
)
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def user():
    return User(1, "First name", False)


@pytest.fixture(scope="module")
def chat():
    return Chat(1, Chat.SUPERGROUP, "Chat")


@pytest.fixture(scope="module")
def old_chat_member(user):
    return ChatMember(user, TestChatMemberUpdatedBase.old_status)


@pytest.fixture(scope="module")
def new_chat_member(user):
    return ChatMemberAdministrator(
        user,
        TestChatMemberUpdatedBase.new_status,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    )


@pytest.fixture(scope="module")
def time():
    return datetime.datetime.now(tz=UTC)


@pytest.fixture(scope="module")
def invite_link(user):
    return ChatInviteLink("link", user, False, True, True)


@pytest.fixture(scope="module")
def chat_member_updated(user, chat, old_chat_member, new_chat_member, invite_link, time):
    return ChatMemberUpdated(chat, user, time, old_chat_member, new_chat_member, invite_link)


class TestChatMemberUpdatedBase:
    old_status = ChatMember.MEMBER
    new_status = ChatMember.ADMINISTRATOR


class TestChatMemberUpdatedWithoutRequest(TestChatMemberUpdatedBase):
    def test_slot_behaviour(self, chat_member_updated):
        action = chat_member_updated
        for attr in action.__slots__:
            assert getattr(action, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"

    def test_de_json_required_args(self, bot, user, chat, old_chat_member, new_chat_member, time):
        json_dict = {
            "chat": chat.to_dict(),
            "from": user.to_dict(),
            "date": to_timestamp(time),
            "old_chat_member": old_chat_member.to_dict(),
            "new_chat_member": new_chat_member.to_dict(),
        }

        chat_member_updated = ChatMemberUpdated.de_json(json_dict, bot)
        assert chat_member_updated.api_kwargs == {}

        assert chat_member_updated.chat == chat
        assert chat_member_updated.from_user == user
        assert abs(chat_member_updated.date - time) < datetime.timedelta(seconds=1)
        assert to_timestamp(chat_member_updated.date) == to_timestamp(time)
        assert chat_member_updated.old_chat_member == old_chat_member
        assert chat_member_updated.new_chat_member == new_chat_member
        assert chat_member_updated.invite_link is None

    def test_de_json_all_args(
        self, bot, user, time, invite_link, chat, old_chat_member, new_chat_member
    ):
        json_dict = {
            "chat": chat.to_dict(),
            "from": user.to_dict(),
            "date": to_timestamp(time),
            "old_chat_member": old_chat_member.to_dict(),
            "new_chat_member": new_chat_member.to_dict(),
            "invite_link": invite_link.to_dict(),
        }

        chat_member_updated = ChatMemberUpdated.de_json(json_dict, bot)
        assert chat_member_updated.api_kwargs == {}

        assert chat_member_updated.chat == chat
        assert chat_member_updated.from_user == user
        assert abs(chat_member_updated.date - time) < datetime.timedelta(seconds=1)
        assert to_timestamp(chat_member_updated.date) == to_timestamp(time)
        assert chat_member_updated.old_chat_member == old_chat_member
        assert chat_member_updated.new_chat_member == new_chat_member
        assert chat_member_updated.invite_link == invite_link

    def test_to_dict(self, chat_member_updated):
        chat_member_updated_dict = chat_member_updated.to_dict()
        assert isinstance(chat_member_updated_dict, dict)
        assert chat_member_updated_dict["chat"] == chat_member_updated.chat.to_dict()
        assert chat_member_updated_dict["from"] == chat_member_updated.from_user.to_dict()
        assert chat_member_updated_dict["date"] == to_timestamp(chat_member_updated.date)
        assert (
            chat_member_updated_dict["old_chat_member"]
            == chat_member_updated.old_chat_member.to_dict()
        )
        assert (
            chat_member_updated_dict["new_chat_member"]
            == chat_member_updated.new_chat_member.to_dict()
        )
        assert chat_member_updated_dict["invite_link"] == chat_member_updated.invite_link.to_dict()

    def test_equality(self, time, old_chat_member, new_chat_member, invite_link):
        a = ChatMemberUpdated(
            Chat(1, "chat"),
            User(1, "", False),
            time,
            old_chat_member,
            new_chat_member,
            invite_link,
        )
        b = ChatMemberUpdated(
            Chat(1, "chat"), User(1, "", False), time, old_chat_member, new_chat_member
        )
        # wrong date
        c = ChatMemberUpdated(
            Chat(1, "chat"),
            User(1, "", False),
            time + datetime.timedelta(hours=1),
            old_chat_member,
            new_chat_member,
        )
        # wrong chat & form_user
        d = ChatMemberUpdated(
            Chat(42, "wrong_chat"),
            User(42, "wrong_user", False),
            time,
            old_chat_member,
            new_chat_member,
        )
        # wrong old_chat_member
        e = ChatMemberUpdated(
            Chat(1, "chat"),
            User(1, "", False),
            time,
            ChatMember(User(1, "", False), ChatMember.OWNER),
            new_chat_member,
        )
        # wrong new_chat_member
        f = ChatMemberUpdated(
            Chat(1, "chat"),
            User(1, "", False),
            time,
            old_chat_member,
            ChatMember(User(1, "", False), ChatMember.OWNER),
        )
        # wrong type
        g = ChatMember(User(1, "", False), ChatMember.OWNER)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        for other in [c, d, e, f, g]:
            assert a != other
            assert hash(a) != hash(other)

    def test_difference_required(self, user, chat):
        old_chat_member = ChatMember(user, "old_status")
        new_chat_member = ChatMember(user, "new_status")
        chat_member_updated = ChatMemberUpdated(
            chat, user, datetime.datetime.utcnow(), old_chat_member, new_chat_member
        )
        assert chat_member_updated.difference() == {"status": ("old_status", "new_status")}

        # We deliberately change an optional argument here to make sure that comparison doesn't
        # just happens by id/required args
        new_user = User(1, "First name", False, last_name="last name")
        new_chat_member = ChatMember(new_user, "new_status")
        chat_member_updated = ChatMemberUpdated(
            chat, user, datetime.datetime.utcnow(), old_chat_member, new_chat_member
        )
        assert chat_member_updated.difference() == {
            "status": ("old_status", "new_status"),
            "user": (user, new_user),
        }

    @pytest.mark.parametrize(
        "optional_attribute",
        # This gives the names of all optional arguments of ChatMember
        [
            name
            for name, param in inspect.signature(ChatMemberAdministrator).parameters.items()
            if name not in ["self", "api_kwargs"] and param.default != inspect.Parameter.empty
        ],
    )
    def test_difference_optionals(self, optional_attribute, user, chat):
        # We test with ChatMemberAdministrator, since that's currently the only interesting class
        # with optional arguments
        old_value = "old_value"
        new_value = "new_value"
        trues = tuple(True for _ in range(9))
        old_chat_member = ChatMemberAdministrator(user, *trues, **{optional_attribute: old_value})
        new_chat_member = ChatMemberAdministrator(user, *trues, **{optional_attribute: new_value})
        chat_member_updated = ChatMemberUpdated(
            chat, user, datetime.datetime.utcnow(), old_chat_member, new_chat_member
        )
        assert chat_member_updated.difference() == {optional_attribute: (old_value, new_value)}

    def test_difference_different_classes(self, user, chat):
        old_chat_member = ChatMemberOwner(user=user, is_anonymous=False)
        new_chat_member = ChatMemberBanned(user=user, until_date=datetime.datetime(2021, 1, 1))
        chat_member_updated = ChatMemberUpdated(
            chat=chat,
            from_user=user,
            date=datetime.datetime.utcnow(),
            old_chat_member=old_chat_member,
            new_chat_member=new_chat_member,
        )
        diff = chat_member_updated.difference()
        assert diff.pop("is_anonymous") == (False, None)
        assert diff.pop("until_date") == (None, datetime.datetime(2021, 1, 1))
        assert diff.pop("status") == (ChatMember.OWNER, ChatMember.BANNED)
        assert diff == {}
