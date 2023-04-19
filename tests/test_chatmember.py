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
from copy import deepcopy

import pytest

from telegram import (
    ChatMember,
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
    Dice,
    User,
)
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.slots import mro_slots

ignored = ["self", "api_kwargs"]


class CMDefaults:
    user = User(1, "First name", False)
    custom_title: str = "PTB"
    is_anonymous: bool = True
    until_date: datetime.datetime = to_timestamp(datetime.datetime.utcnow())
    can_be_edited: bool = False
    can_change_info: bool = True
    can_post_messages: bool = True
    can_edit_messages: bool = True
    can_delete_messages: bool = True
    can_invite_users: bool = True
    can_restrict_members: bool = True
    can_pin_messages: bool = True
    can_promote_members: bool = True
    can_send_messages: bool = True
    can_send_media_messages: bool = True
    can_send_polls: bool = True
    can_send_other_messages: bool = True
    can_add_web_page_previews: bool = True
    is_member: bool = True
    can_manage_chat: bool = True
    can_manage_video_chats: bool = True
    can_manage_topics: bool = True
    can_send_audios: bool = True
    can_send_documents: bool = True
    can_send_photos: bool = True
    can_send_videos: bool = True
    can_send_video_notes: bool = True
    can_send_voice_notes: bool = True


def chat_member_owner():
    return ChatMemberOwner(CMDefaults.user, CMDefaults.is_anonymous, CMDefaults.custom_title)


def chat_member_administrator():
    return ChatMemberAdministrator(
        CMDefaults.user,
        CMDefaults.can_be_edited,
        CMDefaults.is_anonymous,
        CMDefaults.can_manage_chat,
        CMDefaults.can_delete_messages,
        CMDefaults.can_manage_video_chats,
        CMDefaults.can_restrict_members,
        CMDefaults.can_promote_members,
        CMDefaults.can_change_info,
        CMDefaults.can_invite_users,
        CMDefaults.can_post_messages,
        CMDefaults.can_edit_messages,
        CMDefaults.can_pin_messages,
        CMDefaults.can_manage_topics,
        CMDefaults.custom_title,
    )


def chat_member_member():
    return ChatMemberMember(CMDefaults.user)


def chat_member_restricted():
    return ChatMemberRestricted(
        CMDefaults.user,
        CMDefaults.is_member,
        CMDefaults.can_change_info,
        CMDefaults.can_invite_users,
        CMDefaults.can_pin_messages,
        CMDefaults.can_send_messages,
        CMDefaults.can_send_media_messages,
        CMDefaults.can_send_polls,
        CMDefaults.can_send_other_messages,
        CMDefaults.can_add_web_page_previews,
        CMDefaults.can_manage_topics,
        CMDefaults.until_date,
        CMDefaults.can_send_audios,
        CMDefaults.can_send_documents,
        CMDefaults.can_send_photos,
        CMDefaults.can_send_videos,
        CMDefaults.can_send_video_notes,
        CMDefaults.can_send_voice_notes,
    )


def chat_member_left():
    return ChatMemberLeft(CMDefaults.user)


def chat_member_banned():
    return ChatMemberBanned(CMDefaults.user, CMDefaults.until_date)


def make_json_dict(instance: ChatMember, include_optional_args: bool = False) -> dict:
    """Used to make the json dict which we use for testing de_json. Similar to iter_args()"""
    json_dict = {"status": instance.status}
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


def iter_args(instance: ChatMember, de_json_inst: ChatMember, include_optional: bool = False):
    """
    We accept both the regular instance and de_json created instance and iterate over them for
    easy one line testing later one.
    """
    yield instance.status, de_json_inst.status  # yield this here cause it's not available in sig.

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
def chat_member_type(request):
    return request.param()


@pytest.mark.parametrize(
    "chat_member_type",
    [
        chat_member_owner,
        chat_member_administrator,
        chat_member_member,
        chat_member_restricted,
        chat_member_left,
        chat_member_banned,
    ],
    indirect=True,
)
class TestChatMemberTypesWithoutRequest:
    def test_slot_behaviour(self, chat_member_type):
        inst = chat_member_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_required_args(self, bot, chat_member_type):
        cls = chat_member_type.__class__
        assert cls.de_json({}, bot) is None

        json_dict = make_json_dict(chat_member_type)
        const_chat_member = ChatMember.de_json(json_dict, bot)
        assert const_chat_member.api_kwargs == {}

        assert isinstance(const_chat_member, ChatMember)
        assert isinstance(const_chat_member, cls)
        for chat_mem_type_at, const_chat_mem_at in iter_args(chat_member_type, const_chat_member):
            assert chat_mem_type_at == const_chat_mem_at

    def test_de_json_all_args(self, bot, chat_member_type):
        json_dict = make_json_dict(chat_member_type, include_optional_args=True)
        const_chat_member = ChatMember.de_json(json_dict, bot)
        assert const_chat_member.api_kwargs == {}

        assert isinstance(const_chat_member, ChatMember)
        assert isinstance(const_chat_member, chat_member_type.__class__)
        for c_mem_type_at, const_c_mem_at in iter_args(chat_member_type, const_chat_member, True):
            assert c_mem_type_at == const_c_mem_at

    def test_de_json_chatmemberbanned_localization(self, chat_member_type, tz_bot, bot, raw_bot):
        # We only test two classes because the other three don't have datetimes in them.
        if isinstance(chat_member_type, (ChatMemberBanned, ChatMemberRestricted)):
            json_dict = make_json_dict(chat_member_type, include_optional_args=True)
            chatmember_raw = ChatMember.de_json(json_dict, raw_bot)
            chatmember_bot = ChatMember.de_json(json_dict, bot)
            chatmember_tz = ChatMember.de_json(json_dict, tz_bot)

            # comparing utcoffsets because comparing timezones is unpredicatable
            chatmember_offset = chatmember_tz.until_date.utcoffset()
            tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
                chatmember_tz.until_date.replace(tzinfo=None)
            )

            assert chatmember_raw.until_date.tzinfo == UTC
            assert chatmember_bot.until_date.tzinfo == UTC
            assert chatmember_offset == tz_bot_offset

    def test_de_json_invalid_status(self, chat_member_type, bot):
        json_dict = {"status": "invalid", "user": CMDefaults.user.to_dict()}
        chat_member_type = ChatMember.de_json(json_dict, bot)

        assert type(chat_member_type) is ChatMember
        assert chat_member_type.status == "invalid"

    def test_de_json_subclass(self, chat_member_type, bot, chat_id):
        """This makes sure that e.g. ChatMemberAdministrator(data, bot) never returns a
        ChatMemberBanned instance."""
        cls = chat_member_type.__class__
        json_dict = make_json_dict(chat_member_type, True)
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, chat_member_type):
        chat_member_dict = chat_member_type.to_dict()

        assert isinstance(chat_member_dict, dict)
        assert chat_member_dict["status"] == chat_member_type.status
        assert chat_member_dict["user"] == chat_member_type.user.to_dict()

        for slot in chat_member_type.__slots__:  # additional verification for the optional args
            assert getattr(chat_member_type, slot) == chat_member_dict[slot]

    def test_equality(self, chat_member_type):
        a = ChatMember(status="status", user=CMDefaults.user)
        b = ChatMember(status="status", user=CMDefaults.user)
        c = chat_member_type
        d = deepcopy(chat_member_type)
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
