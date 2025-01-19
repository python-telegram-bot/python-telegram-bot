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
import datetime as dtm
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
from telegram.constants import ChatMemberStatus
from tests.auxil.slots import mro_slots


@pytest.fixture
def chat_member():
    return ChatMember(ChatMemberTestBase.user, ChatMemberTestBase.status)


class ChatMemberTestBase:
    status = ChatMemberStatus.MEMBER
    user = User(1, "test_user", is_bot=False)
    is_anonymous = True
    custom_title = "test_title"
    can_be_edited = True
    can_manage_chat = True
    can_delete_messages = True
    can_manage_video_chats = True
    can_restrict_members = True
    can_promote_members = True
    can_change_info = True
    can_invite_users = True
    can_post_messages = True
    can_edit_messages = True
    can_pin_messages = True
    can_post_stories = True
    can_edit_stories = True
    can_delete_stories = True
    can_manage_topics = True
    until_date = dtm.datetime.now(UTC).replace(microsecond=0)
    can_send_polls = True
    can_send_other_messages = True
    can_add_web_page_previews = True
    can_send_audios = True
    can_send_documents = True
    can_send_photos = True
    can_send_videos = True
    can_send_video_notes = True
    can_send_voice_notes = True
    can_send_messages = True
    is_member = True


class TestChatMemberWithoutRequest(ChatMemberTestBase):
    def test_slot_behaviour(self, chat_member):
        inst = chat_member
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_status_enum_conversion(self, chat_member):
        assert type(ChatMember(ChatMemberTestBase.user, "member").status) is ChatMemberStatus
        assert ChatMember(ChatMemberTestBase.user, "unknown").status == "unknown"

    def test_de_json(self, offline_bot):
        data = {"status": "unknown", "user": self.user.to_dict()}
        chat_member = ChatMember.de_json(data, offline_bot)
        assert chat_member.api_kwargs == {}
        assert chat_member.status == "unknown"
        assert chat_member.user == self.user

    @pytest.mark.parametrize(
        ("status", "subclass"),
        [
            ("administrator", ChatMemberAdministrator),
            ("kicked", ChatMemberBanned),
            ("left", ChatMemberLeft),
            ("member", ChatMemberMember),
            ("creator", ChatMemberOwner),
            ("restricted", ChatMemberRestricted),
        ],
    )
    def test_de_json_subclass(self, offline_bot, status, subclass):
        json_dict = {
            "status": status,
            "user": self.user.to_dict(),
            "is_anonymous": self.is_anonymous,
            "is_member": self.is_member,
            "until_date": to_timestamp(self.until_date),
            **{name: value for name, value in inspect.getmembers(self) if name.startswith("can_")},
        }
        chat_member = ChatMember.de_json(json_dict, offline_bot)

        assert type(chat_member) is subclass
        assert set(chat_member.api_kwargs.keys()) == set(json_dict.keys()) - set(
            subclass.__slots__
        ) - {"status", "user"}
        assert chat_member.user == self.user

    def test_to_dict(self, chat_member):
        assert chat_member.to_dict() == {
            "status": chat_member.status,
            "user": chat_member.user.to_dict(),
        }

    def test_equality(self, chat_member):
        a = chat_member
        b = ChatMember(self.user, self.status)
        c = ChatMember(self.user, "unknown")
        d = ChatMember(User(2, "test_bot", is_bot=True), self.status)
        e = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture
def chat_member_administrator():
    return ChatMemberAdministrator(
        TestChatMemberAdministratorWithoutRequest.user,
        TestChatMemberAdministratorWithoutRequest.can_be_edited,
        TestChatMemberAdministratorWithoutRequest.can_change_info,
        TestChatMemberAdministratorWithoutRequest.can_delete_messages,
        TestChatMemberAdministratorWithoutRequest.can_delete_stories,
        TestChatMemberAdministratorWithoutRequest.can_edit_messages,
        TestChatMemberAdministratorWithoutRequest.can_edit_stories,
        TestChatMemberAdministratorWithoutRequest.can_invite_users,
        TestChatMemberAdministratorWithoutRequest.can_manage_chat,
        TestChatMemberAdministratorWithoutRequest.can_manage_topics,
        TestChatMemberAdministratorWithoutRequest.can_manage_video_chats,
        TestChatMemberAdministratorWithoutRequest.can_pin_messages,
        TestChatMemberAdministratorWithoutRequest.can_post_messages,
        TestChatMemberAdministratorWithoutRequest.can_post_stories,
        TestChatMemberAdministratorWithoutRequest.can_promote_members,
        TestChatMemberAdministratorWithoutRequest.can_restrict_members,
        TestChatMemberAdministratorWithoutRequest.custom_title,
        TestChatMemberAdministratorWithoutRequest.is_anonymous,
    )


class TestChatMemberAdministratorWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.ADMINISTRATOR

    def test_slot_behaviour(self, chat_member_administrator):
        inst = chat_member_administrator
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {
            "user": self.user.to_dict(),
            "can_be_edited": self.can_be_edited,
            "can_change_info": self.can_change_info,
            "can_delete_messages": self.can_delete_messages,
            "can_delete_stories": self.can_delete_stories,
            "can_edit_messages": self.can_edit_messages,
            "can_edit_stories": self.can_edit_stories,
            "can_invite_users": self.can_invite_users,
            "can_manage_chat": self.can_manage_chat,
            "can_manage_topics": self.can_manage_topics,
            "can_manage_video_chats": self.can_manage_video_chats,
            "can_pin_messages": self.can_pin_messages,
            "can_post_messages": self.can_post_messages,
            "can_post_stories": self.can_post_stories,
            "can_promote_members": self.can_promote_members,
            "can_restrict_members": self.can_restrict_members,
            "custom_title": self.custom_title,
            "is_anonymous": self.is_anonymous,
        }
        chat_member = ChatMemberAdministrator.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberAdministrator
        assert chat_member.api_kwargs == {}

        assert chat_member.user == self.user
        assert chat_member.can_be_edited == self.can_be_edited
        assert chat_member.can_change_info == self.can_change_info
        assert chat_member.can_delete_messages == self.can_delete_messages
        assert chat_member.can_delete_stories == self.can_delete_stories
        assert chat_member.can_edit_messages == self.can_edit_messages
        assert chat_member.can_edit_stories == self.can_edit_stories
        assert chat_member.can_invite_users == self.can_invite_users
        assert chat_member.can_manage_chat == self.can_manage_chat
        assert chat_member.can_manage_topics == self.can_manage_topics
        assert chat_member.can_manage_video_chats == self.can_manage_video_chats
        assert chat_member.can_pin_messages == self.can_pin_messages
        assert chat_member.can_post_messages == self.can_post_messages
        assert chat_member.can_post_stories == self.can_post_stories
        assert chat_member.can_promote_members == self.can_promote_members
        assert chat_member.can_restrict_members == self.can_restrict_members
        assert chat_member.custom_title == self.custom_title
        assert chat_member.is_anonymous == self.is_anonymous

    def test_to_dict(self, chat_member_administrator):
        assert chat_member_administrator.to_dict() == {
            "status": chat_member_administrator.status,
            "user": chat_member_administrator.user.to_dict(),
            "can_be_edited": chat_member_administrator.can_be_edited,
            "can_change_info": chat_member_administrator.can_change_info,
            "can_delete_messages": chat_member_administrator.can_delete_messages,
            "can_delete_stories": chat_member_administrator.can_delete_stories,
            "can_edit_messages": chat_member_administrator.can_edit_messages,
            "can_edit_stories": chat_member_administrator.can_edit_stories,
            "can_invite_users": chat_member_administrator.can_invite_users,
            "can_manage_chat": chat_member_administrator.can_manage_chat,
            "can_manage_topics": chat_member_administrator.can_manage_topics,
            "can_manage_video_chats": chat_member_administrator.can_manage_video_chats,
            "can_pin_messages": chat_member_administrator.can_pin_messages,
            "can_post_messages": chat_member_administrator.can_post_messages,
            "can_post_stories": chat_member_administrator.can_post_stories,
            "can_promote_members": chat_member_administrator.can_promote_members,
            "can_restrict_members": chat_member_administrator.can_restrict_members,
            "custom_title": chat_member_administrator.custom_title,
            "is_anonymous": chat_member_administrator.is_anonymous,
        }

    def test_equality(self, chat_member_administrator):
        a = chat_member_administrator
        b = ChatMemberAdministrator(
            User(1, "test_user", is_bot=False),
            True,
            True,
            True,
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
        c = ChatMemberAdministrator(
            User(1, "test_user", is_bot=False),
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_member_banned():
    return ChatMemberBanned(
        TestChatMemberBannedWithoutRequest.user,
        TestChatMemberBannedWithoutRequest.until_date,
    )


class TestChatMemberBannedWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.BANNED

    def test_slot_behaviour(self, chat_member_banned):
        inst = chat_member_banned
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {
            "user": self.user.to_dict(),
            "until_date": to_timestamp(self.until_date),
        }
        chat_member = ChatMemberBanned.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberBanned
        assert chat_member.api_kwargs == {}

        assert chat_member.user == self.user
        assert chat_member.until_date == self.until_date

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot):
        json_dict = {
            "user": self.user.to_dict(),
            "until_date": to_timestamp(self.until_date),
        }

        cmb_raw = ChatMemberBanned.de_json(json_dict, raw_bot)
        cmb_bot = ChatMemberBanned.de_json(json_dict, offline_bot)
        cmb_bot_tz = ChatMemberBanned.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        cmb_bot_tz_offset = cmb_bot_tz.until_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            cmb_bot_tz.until_date.replace(tzinfo=None)
        )

        assert cmb_raw.until_date.tzinfo == UTC
        assert cmb_bot.until_date.tzinfo == UTC
        assert cmb_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, chat_member_banned):
        assert chat_member_banned.to_dict() == {
            "status": chat_member_banned.status,
            "user": chat_member_banned.user.to_dict(),
            "until_date": to_timestamp(chat_member_banned.until_date),
        }

    def test_equality(self, chat_member_banned):
        a = chat_member_banned
        b = ChatMemberBanned(
            User(1, "test_user", is_bot=False), dtm.datetime.now(UTC).replace(microsecond=0)
        )
        c = ChatMemberBanned(
            User(2, "test_bot", is_bot=True), dtm.datetime.now(UTC).replace(microsecond=0)
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_member_left():
    return ChatMemberLeft(TestChatMemberLeftWithoutRequest.user)


class TestChatMemberLeftWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.LEFT

    def test_slot_behaviour(self, chat_member_left):
        inst = chat_member_left
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {"user": self.user.to_dict()}
        chat_member = ChatMemberLeft.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberLeft
        assert chat_member.api_kwargs == {}

        assert chat_member.user == self.user

    def test_to_dict(self, chat_member_left):
        assert chat_member_left.to_dict() == {
            "status": chat_member_left.status,
            "user": chat_member_left.user.to_dict(),
        }

    def test_equality(self, chat_member_left):
        a = chat_member_left
        b = ChatMemberLeft(User(1, "test_user", is_bot=False))
        c = ChatMemberLeft(User(2, "test_bot", is_bot=True))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_member_member():
    return ChatMemberMember(TestChatMemberMemberWithoutRequest.user)


class TestChatMemberMemberWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.MEMBER

    def test_slot_behaviour(self, chat_member_member):
        inst = chat_member_member
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {"user": self.user.to_dict(), "until_date": to_timestamp(self.until_date)}
        chat_member = ChatMemberMember.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberMember
        assert chat_member.api_kwargs == {}

        assert chat_member.user == self.user
        assert chat_member.until_date == self.until_date

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot):
        json_dict = {
            "user": self.user.to_dict(),
            "until_date": to_timestamp(self.until_date),
        }

        cmm_raw = ChatMemberMember.de_json(json_dict, raw_bot)
        cmm_bot = ChatMemberMember.de_json(json_dict, offline_bot)
        cmm_bot_tz = ChatMemberMember.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        cmm_bot_tz_offset = cmm_bot_tz.until_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            cmm_bot_tz.until_date.replace(tzinfo=None)
        )

        assert cmm_raw.until_date.tzinfo == UTC
        assert cmm_bot.until_date.tzinfo == UTC
        assert cmm_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, chat_member_member):
        assert chat_member_member.to_dict() == {
            "status": chat_member_member.status,
            "user": chat_member_member.user.to_dict(),
        }

    def test_equality(self, chat_member_member):
        a = chat_member_member
        b = ChatMemberMember(User(1, "test_user", is_bot=False))
        c = ChatMemberMember(User(2, "test_bot", is_bot=True))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_member_owner():
    return ChatMemberOwner(
        TestChatMemberOwnerWithoutRequest.user,
        TestChatMemberOwnerWithoutRequest.is_anonymous,
        TestChatMemberOwnerWithoutRequest.custom_title,
    )


class TestChatMemberOwnerWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.OWNER

    def test_slot_behaviour(self, chat_member_owner):
        inst = chat_member_owner
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {
            "user": self.user.to_dict(),
            "is_anonymous": self.is_anonymous,
            "custom_title": self.custom_title,
        }
        chat_member = ChatMemberOwner.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberOwner
        assert chat_member.api_kwargs == {}

        assert chat_member.user == self.user
        assert chat_member.is_anonymous == self.is_anonymous
        assert chat_member.custom_title == self.custom_title

    def test_to_dict(self, chat_member_owner):
        assert chat_member_owner.to_dict() == {
            "status": chat_member_owner.status,
            "user": chat_member_owner.user.to_dict(),
            "is_anonymous": chat_member_owner.is_anonymous,
            "custom_title": chat_member_owner.custom_title,
        }

    def test_equality(self, chat_member_owner):
        a = chat_member_owner
        b = ChatMemberOwner(User(1, "test_user", is_bot=False), True, "test_title")
        c = ChatMemberOwner(User(1, "test_user", is_bot=False), False, "test_title")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_member_restricted():
    return ChatMemberRestricted(
        user=TestChatMemberRestrictedWithoutRequest.user,
        can_add_web_page_previews=TestChatMemberRestrictedWithoutRequest.can_add_web_page_previews,
        can_change_info=TestChatMemberRestrictedWithoutRequest.can_change_info,
        can_invite_users=TestChatMemberRestrictedWithoutRequest.can_invite_users,
        can_manage_topics=TestChatMemberRestrictedWithoutRequest.can_manage_topics,
        can_pin_messages=TestChatMemberRestrictedWithoutRequest.can_pin_messages,
        can_send_audios=TestChatMemberRestrictedWithoutRequest.can_send_audios,
        can_send_documents=TestChatMemberRestrictedWithoutRequest.can_send_documents,
        can_send_messages=TestChatMemberRestrictedWithoutRequest.can_send_messages,
        can_send_other_messages=TestChatMemberRestrictedWithoutRequest.can_send_other_messages,
        can_send_photos=TestChatMemberRestrictedWithoutRequest.can_send_photos,
        can_send_polls=TestChatMemberRestrictedWithoutRequest.can_send_polls,
        can_send_video_notes=TestChatMemberRestrictedWithoutRequest.can_send_video_notes,
        can_send_videos=TestChatMemberRestrictedWithoutRequest.can_send_videos,
        can_send_voice_notes=TestChatMemberRestrictedWithoutRequest.can_send_voice_notes,
        is_member=TestChatMemberRestrictedWithoutRequest.is_member,
        until_date=TestChatMemberRestrictedWithoutRequest.until_date,
    )


class TestChatMemberRestrictedWithoutRequest(ChatMemberTestBase):
    status = ChatMemberStatus.RESTRICTED

    def test_slot_behaviour(self, chat_member_restricted):
        inst = chat_member_restricted
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        data = {
            "user": self.user.to_dict(),
            "can_add_web_page_previews": self.can_add_web_page_previews,
            "can_change_info": self.can_change_info,
            "can_invite_users": self.can_invite_users,
            "can_manage_topics": self.can_manage_topics,
            "can_pin_messages": self.can_pin_messages,
            "can_send_audios": self.can_send_audios,
            "can_send_documents": self.can_send_documents,
            "can_send_messages": self.can_send_messages,
            "can_send_other_messages": self.can_send_other_messages,
            "can_send_photos": self.can_send_photos,
            "can_send_polls": self.can_send_polls,
            "can_send_video_notes": self.can_send_video_notes,
            "can_send_videos": self.can_send_videos,
            "can_send_voice_notes": self.can_send_voice_notes,
            "is_member": self.is_member,
            "until_date": to_timestamp(self.until_date),
            # legacy argument
            "can_send_media_messages": False,
        }
        chat_member = ChatMemberRestricted.de_json(data, offline_bot)

        assert type(chat_member) is ChatMemberRestricted
        assert chat_member.api_kwargs == {"can_send_media_messages": False}

        assert chat_member.user == self.user
        assert chat_member.can_add_web_page_previews == self.can_add_web_page_previews
        assert chat_member.can_change_info == self.can_change_info
        assert chat_member.can_invite_users == self.can_invite_users
        assert chat_member.can_manage_topics == self.can_manage_topics
        assert chat_member.can_pin_messages == self.can_pin_messages
        assert chat_member.can_send_audios == self.can_send_audios
        assert chat_member.can_send_documents == self.can_send_documents
        assert chat_member.can_send_messages == self.can_send_messages
        assert chat_member.can_send_other_messages == self.can_send_other_messages
        assert chat_member.can_send_photos == self.can_send_photos
        assert chat_member.can_send_polls == self.can_send_polls
        assert chat_member.can_send_video_notes == self.can_send_video_notes
        assert chat_member.can_send_videos == self.can_send_videos
        assert chat_member.can_send_voice_notes == self.can_send_voice_notes
        assert chat_member.is_member == self.is_member
        assert chat_member.until_date == self.until_date

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot, chat_member_restricted):
        json_dict = chat_member_restricted.to_dict()

        cmr_raw = ChatMemberRestricted.de_json(json_dict, raw_bot)
        cmr_bot = ChatMemberRestricted.de_json(json_dict, offline_bot)
        cmr_bot_tz = ChatMemberRestricted.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        cmr_bot_tz_offset = cmr_bot_tz.until_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            cmr_bot_tz.until_date.replace(tzinfo=None)
        )

        assert cmr_raw.until_date.tzinfo == UTC
        assert cmr_bot.until_date.tzinfo == UTC
        assert cmr_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, chat_member_restricted):
        assert chat_member_restricted.to_dict() == {
            "status": chat_member_restricted.status,
            "user": chat_member_restricted.user.to_dict(),
            "can_add_web_page_previews": chat_member_restricted.can_add_web_page_previews,
            "can_change_info": chat_member_restricted.can_change_info,
            "can_invite_users": chat_member_restricted.can_invite_users,
            "can_manage_topics": chat_member_restricted.can_manage_topics,
            "can_pin_messages": chat_member_restricted.can_pin_messages,
            "can_send_audios": chat_member_restricted.can_send_audios,
            "can_send_documents": chat_member_restricted.can_send_documents,
            "can_send_messages": chat_member_restricted.can_send_messages,
            "can_send_other_messages": chat_member_restricted.can_send_other_messages,
            "can_send_photos": chat_member_restricted.can_send_photos,
            "can_send_polls": chat_member_restricted.can_send_polls,
            "can_send_video_notes": chat_member_restricted.can_send_video_notes,
            "can_send_videos": chat_member_restricted.can_send_videos,
            "can_send_voice_notes": chat_member_restricted.can_send_voice_notes,
            "is_member": chat_member_restricted.is_member,
            "until_date": to_timestamp(chat_member_restricted.until_date),
        }

    def test_equality(self, chat_member_restricted):
        a = chat_member_restricted
        b = deepcopy(chat_member_restricted)
        c = ChatMemberRestricted(
            User(1, "test_user", is_bot=False),
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            self.until_date,
            False,
            False,
            False,
            False,
            False,
            False,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)
