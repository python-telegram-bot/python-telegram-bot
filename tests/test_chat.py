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

import pytest

from telegram import Bot, Chat, ChatLocation, ChatPermissions, Location, User
from telegram.constants import ChatAction, ChatType
from telegram.helpers import escape_markdown
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat(bot):
    chat = Chat(
        TestChatBase.id_,
        title=TestChatBase.title,
        type=TestChatBase.type_,
        username=TestChatBase.username,
        sticker_set_name=TestChatBase.sticker_set_name,
        can_set_sticker_set=TestChatBase.can_set_sticker_set,
        permissions=TestChatBase.permissions,
        slow_mode_delay=TestChatBase.slow_mode_delay,
        bio=TestChatBase.bio,
        linked_chat_id=TestChatBase.linked_chat_id,
        location=TestChatBase.location,
        has_private_forwards=True,
        has_protected_content=True,
        join_to_send_messages=True,
        join_by_request=True,
        has_restricted_voice_and_video_messages=True,
        is_forum=True,
        active_usernames=TestChatBase.active_usernames,
        emoji_status_custom_emoji_id=TestChatBase.emoji_status_custom_emoji_id,
        has_aggressive_anti_spam_enabled=TestChatBase.has_aggressive_anti_spam_enabled,
        has_hidden_members=TestChatBase.has_hidden_members,
    )
    chat.set_bot(bot)
    chat._unfreeze()
    return chat


class TestChatBase:
    id_ = -28767330
    title = "ToledosPalaceBot - Group"
    type_ = "group"
    username = "username"
    all_members_are_administrators = False
    sticker_set_name = "stickers"
    can_set_sticker_set = False
    permissions = ChatPermissions(
        can_send_messages=True,
        can_change_info=False,
        can_invite_users=True,
    )
    slow_mode_delay = 30
    bio = "I'm a Barbie Girl in a Barbie World"
    linked_chat_id = 11880
    location = ChatLocation(Location(123, 456), "Barbie World")
    has_protected_content = True
    has_private_forwards = True
    join_to_send_messages = True
    join_by_request = True
    has_restricted_voice_and_video_messages = True
    is_forum = True
    active_usernames = ["These", "Are", "Usernames!"]
    emoji_status_custom_emoji_id = "VeryUniqueCustomEmojiID"
    has_aggressive_anti_spam_enabled = True
    has_hidden_members = True


class TestChatWithoutRequest(TestChatBase):
    def test_slot_behaviour(self, chat):
        for attr in chat.__slots__:
            assert getattr(chat, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(chat)) == len(set(mro_slots(chat))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "id": self.id_,
            "title": self.title,
            "type": self.type_,
            "username": self.username,
            "all_members_are_administrators": self.all_members_are_administrators,
            "sticker_set_name": self.sticker_set_name,
            "can_set_sticker_set": self.can_set_sticker_set,
            "permissions": self.permissions.to_dict(),
            "slow_mode_delay": self.slow_mode_delay,
            "bio": self.bio,
            "has_protected_content": self.has_protected_content,
            "has_private_forwards": self.has_private_forwards,
            "linked_chat_id": self.linked_chat_id,
            "location": self.location.to_dict(),
            "join_to_send_messages": self.join_to_send_messages,
            "join_by_request": self.join_by_request,
            "has_restricted_voice_and_video_messages": (
                self.has_restricted_voice_and_video_messages
            ),
            "is_forum": self.is_forum,
            "active_usernames": self.active_usernames,
            "emoji_status_custom_emoji_id": self.emoji_status_custom_emoji_id,
            "has_aggressive_anti_spam_enabled": self.has_aggressive_anti_spam_enabled,
            "has_hidden_members": self.has_hidden_members,
        }
        chat = Chat.de_json(json_dict, bot)

        assert chat.id == self.id_
        assert chat.title == self.title
        assert chat.type == self.type_
        assert chat.username == self.username
        assert chat.sticker_set_name == self.sticker_set_name
        assert chat.can_set_sticker_set == self.can_set_sticker_set
        assert chat.permissions == self.permissions
        assert chat.slow_mode_delay == self.slow_mode_delay
        assert chat.bio == self.bio
        assert chat.has_protected_content == self.has_protected_content
        assert chat.has_private_forwards == self.has_private_forwards
        assert chat.linked_chat_id == self.linked_chat_id
        assert chat.location.location == self.location.location
        assert chat.location.address == self.location.address
        assert chat.join_to_send_messages == self.join_to_send_messages
        assert chat.join_by_request == self.join_by_request
        assert (
            chat.has_restricted_voice_and_video_messages
            == self.has_restricted_voice_and_video_messages
        )
        assert chat.api_kwargs == {
            "all_members_are_administrators": self.all_members_are_administrators
        }
        assert chat.is_forum == self.is_forum
        assert chat.active_usernames == tuple(self.active_usernames)
        assert chat.emoji_status_custom_emoji_id == self.emoji_status_custom_emoji_id
        assert chat.has_aggressive_anti_spam_enabled == self.has_aggressive_anti_spam_enabled
        assert chat.has_hidden_members == self.has_hidden_members

    def test_to_dict(self, chat):
        chat_dict = chat.to_dict()

        assert isinstance(chat_dict, dict)
        assert chat_dict["id"] == chat.id
        assert chat_dict["title"] == chat.title
        assert chat_dict["type"] == chat.type
        assert chat_dict["username"] == chat.username
        assert chat_dict["permissions"] == chat.permissions.to_dict()
        assert chat_dict["slow_mode_delay"] == chat.slow_mode_delay
        assert chat_dict["bio"] == chat.bio
        assert chat_dict["has_private_forwards"] == chat.has_private_forwards
        assert chat_dict["has_protected_content"] == chat.has_protected_content
        assert chat_dict["linked_chat_id"] == chat.linked_chat_id
        assert chat_dict["location"] == chat.location.to_dict()
        assert chat_dict["join_to_send_messages"] == chat.join_to_send_messages
        assert chat_dict["join_by_request"] == chat.join_by_request
        assert (
            chat_dict["has_restricted_voice_and_video_messages"]
            == chat.has_restricted_voice_and_video_messages
        )
        assert chat_dict["is_forum"] == chat.is_forum
        assert chat_dict["active_usernames"] == list(chat.active_usernames)
        assert chat_dict["emoji_status_custom_emoji_id"] == chat.emoji_status_custom_emoji_id
        assert (
            chat_dict["has_aggressive_anti_spam_enabled"] == chat.has_aggressive_anti_spam_enabled
        )
        assert chat_dict["has_hidden_members"] == chat.has_hidden_members

    def test_always_tuples_attributes(self):
        chat = Chat(
            id=123,
            title="title",
            type=Chat.PRIVATE,
        )
        assert isinstance(chat.active_usernames, tuple)
        assert chat.active_usernames == ()

    def test_enum_init(self):
        chat = Chat(id=1, type="foo")
        assert chat.type == "foo"
        chat = Chat(id=1, type="private")
        assert chat.type is ChatType.PRIVATE

    def test_equality(self):
        a = Chat(self.id_, self.title, self.type_)
        b = Chat(self.id_, self.title, self.type_)
        c = Chat(self.id_, "", "")
        d = Chat(0, self.title, self.type_)
        e = User(self.id_, "", False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    def test_link(self, chat):
        assert chat.link == f"https://t.me/{chat.username}"
        chat.username = None
        assert chat.link is None

    def test_full_name(self):
        chat = Chat(
            id=1, type=Chat.PRIVATE, first_name="first\u2022name", last_name="last\u2022name"
        )
        assert chat.full_name == "first\u2022name last\u2022name"
        chat = Chat(id=1, type=Chat.PRIVATE, first_name="first\u2022name")
        assert chat.full_name == "first\u2022name"
        chat = Chat(
            id=1,
            type=Chat.PRIVATE,
        )
        assert chat.full_name is None

    def test_effective_name(self):
        chat = Chat(id=1, type=Chat.PRIVATE, first_name="first\u2022name")
        assert chat.effective_name == "first\u2022name"
        chat = Chat(id=1, type=Chat.GROUP, title="group")
        assert chat.effective_name == "group"
        chat = Chat(id=1, type=Chat.GROUP, first_name="first\u2022name", title="group")
        assert chat.effective_name == "group"
        chat = Chat(id=1, type=Chat.GROUP)
        assert chat.effective_name is None

    async def test_send_action(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            id_ = kwargs["chat_id"] == chat.id
            action = kwargs["action"] == ChatAction.TYPING
            return id_ and action

        assert check_shortcut_signature(chat.send_action, Bot.send_chat_action, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_action, chat.get_bot(), "send_chat_action")
        assert await check_defaults_handling(chat.send_action, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_chat_action", make_assertion)
        assert await chat.send_action(action=ChatAction.TYPING)

    async def test_leave(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(Chat.leave, Bot.leave_chat, ["chat_id"], [])
        assert await check_shortcut_call(chat.leave, chat.get_bot(), "leave_chat")
        assert await check_defaults_handling(chat.leave, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "leave_chat", make_assertion)
        assert await chat.leave()

    async def test_get_administrators(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.get_administrators, Bot.get_chat_administrators, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.get_administrators, chat.get_bot(), "get_chat_administrators"
        )
        assert await check_defaults_handling(chat.get_administrators, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "get_chat_administrators", make_assertion)
        assert await chat.get_administrators()

    async def test_get_members_count(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.get_member_count, Bot.get_chat_member_count, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.get_member_count, chat.get_bot(), "get_chat_member_count"
        )
        assert await check_defaults_handling(chat.get_member_count, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "get_chat_member_count", make_assertion)
        assert await chat.get_member_count()

    async def test_get_member(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            return chat_id and user_id

        assert check_shortcut_signature(Chat.get_member, Bot.get_chat_member, ["chat_id"], [])
        assert await check_shortcut_call(chat.get_member, chat.get_bot(), "get_chat_member")
        assert await check_defaults_handling(chat.get_member, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "get_chat_member", make_assertion)
        assert await chat.get_member(user_id=42)

    async def test_ban_member(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            until = kwargs["until_date"] == 43
            return chat_id and user_id and until

        assert check_shortcut_signature(Chat.ban_member, Bot.ban_chat_member, ["chat_id"], [])
        assert await check_shortcut_call(chat.ban_member, chat.get_bot(), "ban_chat_member")
        assert await check_defaults_handling(chat.ban_member, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "ban_chat_member", make_assertion)
        assert await chat.ban_member(user_id=42, until_date=43)

    async def test_ban_sender_chat(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            sender_chat_id = kwargs["sender_chat_id"] == 42
            return chat_id and sender_chat_id

        assert check_shortcut_signature(
            Chat.ban_sender_chat, Bot.ban_chat_sender_chat, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.ban_sender_chat, chat.get_bot(), "ban_chat_sender_chat"
        )
        assert await check_defaults_handling(chat.ban_sender_chat, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "ban_chat_sender_chat", make_assertion)
        assert await chat.ban_sender_chat(42)

    async def test_ban_chat(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == 42
            sender_chat_id = kwargs["sender_chat_id"] == chat.id
            return chat_id and sender_chat_id

        assert check_shortcut_signature(
            Chat.ban_chat, Bot.ban_chat_sender_chat, ["sender_chat_id"], []
        )
        assert await check_shortcut_call(chat.ban_chat, chat.get_bot(), "ban_chat_sender_chat")
        assert await check_defaults_handling(chat.ban_chat, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "ban_chat_sender_chat", make_assertion)
        assert await chat.ban_chat(42)

    @pytest.mark.parametrize("only_if_banned", [True, False, None])
    async def test_unban_member(self, monkeypatch, chat, only_if_banned):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            o_i_b = kwargs.get("only_if_banned", None) == only_if_banned
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(Chat.unban_member, Bot.unban_chat_member, ["chat_id"], [])
        assert await check_shortcut_call(chat.unban_member, chat.get_bot(), "unban_chat_member")
        assert await check_defaults_handling(chat.unban_member, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unban_chat_member", make_assertion)
        assert await chat.unban_member(user_id=42, only_if_banned=only_if_banned)

    async def test_unban_sender_chat(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            sender_chat_id = kwargs["sender_chat_id"] == 42
            return chat_id and sender_chat_id

        assert check_shortcut_signature(
            Chat.unban_sender_chat, Bot.unban_chat_sender_chat, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.unban_sender_chat, chat.get_bot(), "unban_chat_sender_chat"
        )
        assert await check_defaults_handling(chat.unban_sender_chat, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unban_chat_sender_chat", make_assertion)
        assert await chat.unban_sender_chat(42)

    async def test_unban_chat(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == 42
            sender_chat_id = kwargs["sender_chat_id"] == chat.id
            return chat_id and sender_chat_id

        assert check_shortcut_signature(
            Chat.unban_chat, Bot.ban_chat_sender_chat, ["sender_chat_id"], []
        )
        assert await check_shortcut_call(chat.unban_chat, chat.get_bot(), "unban_chat_sender_chat")
        assert await check_defaults_handling(chat.unban_chat, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unban_chat_sender_chat", make_assertion)
        assert await chat.unban_chat(42)

    @pytest.mark.parametrize("is_anonymous", [True, False, None])
    async def test_promote_member(self, monkeypatch, chat, is_anonymous):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            o_i_b = kwargs.get("is_anonymous", None) == is_anonymous
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(
            Chat.promote_member, Bot.promote_chat_member, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.promote_member, chat.get_bot(), "promote_chat_member"
        )
        assert await check_defaults_handling(chat.promote_member, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "promote_chat_member", make_assertion)
        assert await chat.promote_member(user_id=42, is_anonymous=is_anonymous)

    async def test_restrict_member(self, monkeypatch, chat):
        permissions = ChatPermissions(True, False, True, False, True, False, True, False)

        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            o_i_b = kwargs.get("permissions", None) == permissions
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(
            Chat.restrict_member, Bot.restrict_chat_member, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.restrict_member, chat.get_bot(), "restrict_chat_member"
        )
        assert await check_defaults_handling(chat.restrict_member, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "restrict_chat_member", make_assertion)
        assert await chat.restrict_member(user_id=42, permissions=permissions)

    async def test_set_permissions(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            permissions = kwargs["permissions"] == self.permissions
            return chat_id and permissions

        assert check_shortcut_signature(
            Chat.set_permissions, Bot.set_chat_permissions, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.set_permissions, chat.get_bot(), "set_chat_permissions"
        )
        assert await check_defaults_handling(chat.set_permissions, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "set_chat_permissions", make_assertion)
        assert await chat.set_permissions(permissions=self.permissions)

    async def test_set_administrator_custom_title(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            user_id = kwargs["user_id"] == 42
            custom_title = kwargs["custom_title"] == "custom_title"
            return chat_id and user_id and custom_title

        monkeypatch.setattr("telegram.Bot.set_chat_administrator_custom_title", make_assertion)
        assert await chat.set_administrator_custom_title(user_id=42, custom_title="custom_title")

    async def test_set_photo(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            photo = kwargs["photo"] == "test_photo"
            return chat_id, photo

        assert check_shortcut_signature(Chat.set_photo, Bot.set_chat_photo, ["chat_id"], [])
        assert await check_shortcut_call(chat.set_photo, chat.get_bot(), "set_chat_photo")
        assert await check_defaults_handling(chat.set_photo, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "set_chat_photo", make_assertion)
        assert await chat.set_photo(photo="test_photo")

    async def test_delete_photo(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(Chat.delete_photo, Bot.delete_chat_photo, ["chat_id"], [])
        assert await check_shortcut_call(chat.delete_photo, chat.get_bot(), "delete_chat_photo")
        assert await check_defaults_handling(chat.delete_photo, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "delete_chat_photo", make_assertion)
        assert await chat.delete_photo()

    async def test_set_title(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            title = kwargs["title"] == "test_title"
            return chat_id, title

        assert check_shortcut_signature(Chat.set_title, Bot.set_chat_title, ["chat_id"], [])
        assert await check_shortcut_call(chat.set_title, chat.get_bot(), "set_chat_title")
        assert await check_defaults_handling(chat.set_title, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "set_chat_title", make_assertion)
        assert await chat.set_title(title="test_title")

    async def test_set_description(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            description = kwargs["description"] == "test_descripton"
            return chat_id, description

        assert check_shortcut_signature(
            Chat.set_description, Bot.set_chat_description, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.set_description, chat.get_bot(), "set_chat_description"
        )
        assert await check_defaults_handling(chat.set_description, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "set_chat_description", make_assertion)
        assert await chat.set_description(description="test_description")

    async def test_pin_message(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["message_id"] == 42

        assert check_shortcut_signature(Chat.pin_message, Bot.pin_chat_message, ["chat_id"], [])
        assert await check_shortcut_call(chat.pin_message, chat.get_bot(), "pin_chat_message")
        assert await check_defaults_handling(chat.pin_message, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "pin_chat_message", make_assertion)
        assert await chat.pin_message(message_id=42)

    async def test_unpin_message(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.unpin_message, Bot.unpin_chat_message, ["chat_id"], []
        )
        assert await check_shortcut_call(chat.unpin_message, chat.get_bot(), "unpin_chat_message")
        assert await check_defaults_handling(chat.unpin_message, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unpin_chat_message", make_assertion)
        assert await chat.unpin_message()

    async def test_unpin_all_messages(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.unpin_all_messages, Bot.unpin_all_chat_messages, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.unpin_all_messages, chat.get_bot(), "unpin_all_chat_messages"
        )
        assert await check_defaults_handling(chat.unpin_all_messages, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unpin_all_chat_messages", make_assertion)
        assert await chat.unpin_all_messages()

    async def test_instance_method_send_message(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["text"] == "test"

        assert check_shortcut_signature(Chat.send_message, Bot.send_message, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_message, chat.get_bot(), "send_message")
        assert await check_defaults_handling(chat.send_message, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_message", make_assertion)
        assert await chat.send_message(text="test")

    async def test_instance_method_send_media_group(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["media"] == "test_media_group"

        assert check_shortcut_signature(
            Chat.send_media_group, Bot.send_media_group, ["chat_id"], []
        )
        assert await check_shortcut_call(chat.send_media_group, chat.get_bot(), "send_media_group")
        assert await check_defaults_handling(chat.send_media_group, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_media_group", make_assertion)
        assert await chat.send_media_group(media="test_media_group")

    async def test_instance_method_send_photo(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["photo"] == "test_photo"

        assert check_shortcut_signature(Chat.send_photo, Bot.send_photo, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_photo, chat.get_bot(), "send_photo")
        assert await check_defaults_handling(chat.send_photo, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_photo", make_assertion)
        assert await chat.send_photo(photo="test_photo")

    async def test_instance_method_send_contact(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["phone_number"] == "test_contact"

        assert check_shortcut_signature(Chat.send_contact, Bot.send_contact, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_contact, chat.get_bot(), "send_contact")
        assert await check_defaults_handling(chat.send_contact, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_contact", make_assertion)
        assert await chat.send_contact(phone_number="test_contact")

    async def test_instance_method_send_audio(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["audio"] == "test_audio"

        assert check_shortcut_signature(Chat.send_audio, Bot.send_audio, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_audio, chat.get_bot(), "send_audio")
        assert await check_defaults_handling(chat.send_audio, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_audio", make_assertion)
        assert await chat.send_audio(audio="test_audio")

    async def test_instance_method_send_document(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["document"] == "test_document"

        assert check_shortcut_signature(Chat.send_document, Bot.send_document, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_document, chat.get_bot(), "send_document")
        assert await check_defaults_handling(chat.send_document, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_document", make_assertion)
        assert await chat.send_document(document="test_document")

    async def test_instance_method_send_dice(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["emoji"] == "test_dice"

        assert check_shortcut_signature(Chat.send_dice, Bot.send_dice, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_dice, chat.get_bot(), "send_dice")
        assert await check_defaults_handling(chat.send_dice, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_dice", make_assertion)
        assert await chat.send_dice(emoji="test_dice")

    async def test_instance_method_send_game(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["game_short_name"] == "test_game"

        assert check_shortcut_signature(Chat.send_game, Bot.send_game, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_game, chat.get_bot(), "send_game")
        assert await check_defaults_handling(chat.send_game, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_game", make_assertion)
        assert await chat.send_game(game_short_name="test_game")

    async def test_instance_method_send_invoice(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            title = kwargs["title"] == "title"
            description = kwargs["description"] == "description"
            payload = kwargs["payload"] == "payload"
            provider_token = kwargs["provider_token"] == "provider_token"
            currency = kwargs["currency"] == "currency"
            prices = kwargs["prices"] == "prices"
            args = title and description and payload and provider_token and currency and prices
            return kwargs["chat_id"] == chat.id and args

        assert check_shortcut_signature(Chat.send_invoice, Bot.send_invoice, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_invoice, chat.get_bot(), "send_invoice")
        assert await check_defaults_handling(chat.send_invoice, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_invoice", make_assertion)
        assert await chat.send_invoice(
            "title",
            "description",
            "payload",
            "provider_token",
            "currency",
            "prices",
        )

    async def test_instance_method_send_location(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["latitude"] == "test_location"

        assert check_shortcut_signature(Chat.send_location, Bot.send_location, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_location, chat.get_bot(), "send_location")
        assert await check_defaults_handling(chat.send_location, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_location", make_assertion)
        assert await chat.send_location(latitude="test_location")

    async def test_instance_method_send_sticker(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["sticker"] == "test_sticker"

        assert check_shortcut_signature(Chat.send_sticker, Bot.send_sticker, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_sticker, chat.get_bot(), "send_sticker")
        assert await check_defaults_handling(chat.send_sticker, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_sticker", make_assertion)
        assert await chat.send_sticker(sticker="test_sticker")

    async def test_instance_method_send_venue(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["title"] == "test_venue"

        assert check_shortcut_signature(Chat.send_venue, Bot.send_venue, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_venue, chat.get_bot(), "send_venue")
        assert await check_defaults_handling(chat.send_venue, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_venue", make_assertion)
        assert await chat.send_venue(title="test_venue")

    async def test_instance_method_send_video(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["video"] == "test_video"

        assert check_shortcut_signature(Chat.send_video, Bot.send_video, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_video, chat.get_bot(), "send_video")
        assert await check_defaults_handling(chat.send_video, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_video", make_assertion)
        assert await chat.send_video(video="test_video")

    async def test_instance_method_send_video_note(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["video_note"] == "test_video_note"

        assert check_shortcut_signature(Chat.send_video_note, Bot.send_video_note, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_video_note, chat.get_bot(), "send_video_note")
        assert await check_defaults_handling(chat.send_video_note, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_video_note", make_assertion)
        assert await chat.send_video_note(video_note="test_video_note")

    async def test_instance_method_send_voice(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["voice"] == "test_voice"

        assert check_shortcut_signature(Chat.send_voice, Bot.send_voice, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_voice, chat.get_bot(), "send_voice")
        assert await check_defaults_handling(chat.send_voice, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_voice", make_assertion)
        assert await chat.send_voice(voice="test_voice")

    async def test_instance_method_send_animation(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["animation"] == "test_animation"

        assert check_shortcut_signature(Chat.send_animation, Bot.send_animation, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_animation, chat.get_bot(), "send_animation")
        assert await check_defaults_handling(chat.send_animation, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_animation", make_assertion)
        assert await chat.send_animation(animation="test_animation")

    async def test_instance_method_send_poll(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["question"] == "test_poll"

        assert check_shortcut_signature(Chat.send_poll, Bot.send_poll, ["chat_id"], [])
        assert await check_shortcut_call(chat.send_poll, chat.get_bot(), "send_poll")
        assert await check_defaults_handling(chat.send_poll, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "send_poll", make_assertion)
        assert await chat.send_poll(question="test_poll", options=[1, 2])

    async def test_instance_method_send_copy(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            from_chat_id = kwargs["from_chat_id"] == "test_copy"
            message_id = kwargs["message_id"] == 42
            chat_id = kwargs["chat_id"] == chat.id
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.send_copy, Bot.copy_message, ["chat_id"], [])
        assert await check_shortcut_call(chat.copy_message, chat.get_bot(), "copy_message")
        assert await check_defaults_handling(chat.copy_message, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "copy_message", make_assertion)
        assert await chat.send_copy(from_chat_id="test_copy", message_id=42)

    async def test_instance_method_copy_message(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            from_chat_id = kwargs["from_chat_id"] == chat.id
            message_id = kwargs["message_id"] == 42
            chat_id = kwargs["chat_id"] == "test_copy"
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.copy_message, Bot.copy_message, ["from_chat_id"], [])
        assert await check_shortcut_call(chat.copy_message, chat.get_bot(), "copy_message")
        assert await check_defaults_handling(chat.copy_message, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "copy_message", make_assertion)
        assert await chat.copy_message(chat_id="test_copy", message_id=42)

    async def test_instance_method_forward_from(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            chat_id = kwargs["chat_id"] == chat.id
            message_id = kwargs["message_id"] == 42
            from_chat_id = kwargs["from_chat_id"] == "test_forward"
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.forward_from, Bot.forward_message, ["chat_id"], [])
        assert await check_shortcut_call(chat.forward_from, chat.get_bot(), "forward_message")
        assert await check_defaults_handling(chat.forward_from, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "forward_message", make_assertion)
        assert await chat.forward_from(from_chat_id="test_forward", message_id=42)

    async def test_instance_method_forward_to(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            from_chat_id = kwargs["from_chat_id"] == chat.id
            message_id = kwargs["message_id"] == 42
            chat_id = kwargs["chat_id"] == "test_forward"
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.forward_to, Bot.forward_message, ["from_chat_id"], [])
        assert await check_shortcut_call(chat.forward_to, chat.get_bot(), "forward_message")
        assert await check_defaults_handling(chat.forward_to, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "forward_message", make_assertion)
        assert await chat.forward_to(chat_id="test_forward", message_id=42)

    async def test_export_invite_link(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.export_invite_link, Bot.export_chat_invite_link, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.export_invite_link, chat.get_bot(), "export_chat_invite_link"
        )
        assert await check_defaults_handling(chat.export_invite_link, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "export_chat_invite_link", make_assertion)
        assert await chat.export_invite_link()

    async def test_create_invite_link(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.create_invite_link, Bot.create_chat_invite_link, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.create_invite_link, chat.get_bot(), "create_chat_invite_link"
        )
        assert await check_defaults_handling(chat.create_invite_link, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "create_chat_invite_link", make_assertion)
        assert await chat.create_invite_link()

    async def test_edit_invite_link(self, monkeypatch, chat):
        link = "ThisIsALink"

        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["invite_link"] == link

        assert check_shortcut_signature(
            Chat.edit_invite_link, Bot.edit_chat_invite_link, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.edit_invite_link, chat.get_bot(), "edit_chat_invite_link"
        )
        assert await check_defaults_handling(chat.edit_invite_link, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "edit_chat_invite_link", make_assertion)
        assert await chat.edit_invite_link(invite_link=link)

    async def test_revoke_invite_link(self, monkeypatch, chat):
        link = "ThisIsALink"

        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["invite_link"] == link

        assert check_shortcut_signature(
            Chat.revoke_invite_link, Bot.revoke_chat_invite_link, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.revoke_invite_link, chat.get_bot(), "revoke_chat_invite_link"
        )
        assert await check_defaults_handling(chat.revoke_invite_link, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "revoke_chat_invite_link", make_assertion)
        assert await chat.revoke_invite_link(invite_link=link)

    async def test_instance_method_get_menu_button(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.get_menu_button, Bot.get_chat_menu_button, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.get_menu_button,
            chat.get_bot(),
            "get_chat_menu_button",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.get_menu_button, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "get_chat_menu_button", make_assertion)
        assert await chat.get_menu_button()

    async def test_instance_method_set_menu_button(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["menu_button"] == "menu_button"

        assert check_shortcut_signature(
            Chat.set_menu_button, Bot.set_chat_menu_button, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.set_menu_button,
            chat.get_bot(),
            "set_chat_menu_button",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.set_menu_button, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "set_chat_menu_button", make_assertion)
        assert await chat.set_menu_button(menu_button="menu_button")

    async def test_approve_join_request(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["user_id"] == 42

        assert check_shortcut_signature(
            Chat.approve_join_request, Bot.approve_chat_join_request, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.approve_join_request, chat.get_bot(), "approve_chat_join_request"
        )
        assert await check_defaults_handling(chat.approve_join_request, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "approve_chat_join_request", make_assertion)
        assert await chat.approve_join_request(user_id=42)

    async def test_decline_join_request(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["user_id"] == 42

        assert check_shortcut_signature(
            Chat.decline_join_request, Bot.decline_chat_join_request, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.decline_join_request, chat.get_bot(), "decline_chat_join_request"
        )
        assert await check_defaults_handling(chat.decline_join_request, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "decline_chat_join_request", make_assertion)
        assert await chat.decline_join_request(user_id=42)

    async def test_create_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == chat.id
                and kwargs["name"] == "New Name"
                and kwargs["icon_color"] == 0x6FB9F0
                and kwargs["icon_custom_emoji_id"] == "12345"
            )

        assert check_shortcut_signature(
            Chat.create_forum_topic, Bot.create_forum_topic, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.create_forum_topic,
            chat.get_bot(),
            "create_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.create_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "create_forum_topic", make_assertion)
        assert await chat.create_forum_topic(
            name="New Name", icon_color=0x6FB9F0, icon_custom_emoji_id="12345"
        )

    async def test_edit_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return (
                kwargs["chat_id"] == chat.id
                and kwargs["message_thread_id"] == 42
                and kwargs["name"] == "New Name"
                and kwargs["icon_custom_emoji_id"] == "12345"
            )

        assert check_shortcut_signature(
            Chat.edit_forum_topic, Bot.edit_forum_topic, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.edit_forum_topic, chat.get_bot(), "edit_forum_topic", shortcut_kwargs=["chat_id"]
        )
        assert await check_defaults_handling(chat.edit_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "edit_forum_topic", make_assertion)
        assert await chat.edit_forum_topic(
            message_thread_id=42, name="New Name", icon_custom_emoji_id="12345"
        )

    async def test_close_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["message_thread_id"] == 42

        assert check_shortcut_signature(
            Chat.close_forum_topic, Bot.close_forum_topic, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.close_forum_topic,
            chat.get_bot(),
            "close_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.close_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "close_forum_topic", make_assertion)
        assert await chat.close_forum_topic(message_thread_id=42)

    async def test_reopen_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["message_thread_id"] == 42

        assert check_shortcut_signature(
            Chat.reopen_forum_topic, Bot.reopen_forum_topic, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.reopen_forum_topic,
            chat.get_bot(),
            "reopen_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.reopen_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "reopen_forum_topic", make_assertion)
        assert await chat.reopen_forum_topic(message_thread_id=42)

    async def test_delete_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["message_thread_id"] == 42

        assert check_shortcut_signature(
            Chat.delete_forum_topic, Bot.delete_forum_topic, ["chat_id"], []
        )
        assert await check_shortcut_call(
            chat.delete_forum_topic,
            chat.get_bot(),
            "delete_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.delete_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "delete_forum_topic", make_assertion)
        assert await chat.delete_forum_topic(message_thread_id=42)

    async def test_unpin_all_forum_topic_messages(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["message_thread_id"] == 42

        assert check_shortcut_signature(
            Chat.unpin_all_forum_topic_messages,
            Bot.unpin_all_forum_topic_messages,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.unpin_all_forum_topic_messages,
            chat.get_bot(),
            "unpin_all_forum_topic_messages",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.unpin_all_forum_topic_messages, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unpin_all_forum_topic_messages", make_assertion)
        assert await chat.unpin_all_forum_topic_messages(message_thread_id=42)

    async def test_edit_general_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id and kwargs["name"] == "WhatAName"

        assert check_shortcut_signature(
            Chat.edit_general_forum_topic,
            Bot.edit_general_forum_topic,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.edit_general_forum_topic,
            chat.get_bot(),
            "edit_general_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.edit_general_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "edit_general_forum_topic", make_assertion)
        assert await chat.edit_general_forum_topic(name="WhatAName")

    async def test_close_general_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.close_general_forum_topic,
            Bot.close_general_forum_topic,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.close_general_forum_topic,
            chat.get_bot(),
            "close_general_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.close_general_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "close_general_forum_topic", make_assertion)
        assert await chat.close_general_forum_topic()

    async def test_reopen_general_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.reopen_general_forum_topic,
            Bot.reopen_general_forum_topic,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.reopen_general_forum_topic,
            chat.get_bot(),
            "reopen_general_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.reopen_general_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "reopen_general_forum_topic", make_assertion)
        assert await chat.reopen_general_forum_topic()

    async def test_hide_general_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.hide_general_forum_topic,
            Bot.hide_general_forum_topic,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.hide_general_forum_topic,
            chat.get_bot(),
            "hide_general_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.hide_general_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "hide_general_forum_topic", make_assertion)
        assert await chat.hide_general_forum_topic()

    async def test_unhide_general_forum_topic(self, monkeypatch, chat):
        async def make_assertion(*_, **kwargs):
            return kwargs["chat_id"] == chat.id

        assert check_shortcut_signature(
            Chat.unhide_general_forum_topic,
            Bot.unhide_general_forum_topic,
            ["chat_id"],
            [],
        )
        assert await check_shortcut_call(
            chat.unhide_general_forum_topic,
            chat.get_bot(),
            "unhide_general_forum_topic",
            shortcut_kwargs=["chat_id"],
        )
        assert await check_defaults_handling(chat.unhide_general_forum_topic, chat.get_bot())

        monkeypatch.setattr(chat.get_bot(), "unhide_general_forum_topic", make_assertion)
        assert await chat.unhide_general_forum_topic()

    def test_mention_html(self):
        chat = Chat(id=1, type="foo")
        with pytest.raises(TypeError, match="Can not create a mention to a private group chat"):
            chat.mention_html()

        expected = '<a href="tg://user?id={}">{}</a>'
        chat = Chat(
            id=1, type=Chat.PRIVATE, first_name="first\u2022name", last_name="last\u2022name"
        )
        assert chat.mention_html("the_name*\u2022") == expected.format(chat.id, "the_name*\u2022")
        assert chat.mention_html() == expected.format(chat.id, chat.full_name)
        chat = Chat(id=1, type=Chat.PRIVATE, last_name="last\u2022name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a private chat without first name"
        ):
            chat.mention_html()

        expected = '<a href="https://t.me/{}">{}</a>'
        chat = Chat(id=1, type="foo", username="user\u2022name", title="\u2022title")
        assert chat.mention_html("the_name*\u2022") == expected.format(
            chat.username, "the_name*\u2022"
        )
        assert chat.mention_html() == expected.format(chat.username, chat.title)
        chat = Chat(id=1, type="foo", username="user\u2022name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a public chat without title"
        ):
            chat.mention_html()

    def test_mention_markdown(self):
        chat = Chat(id=1, type="foo")
        with pytest.raises(TypeError, match="Can not create a mention to a private group chat"):
            chat.mention_markdown()

        expected = "[{}](tg://user?id={})"
        chat = Chat(
            id=1, type=Chat.PRIVATE, first_name="first\u2022name", last_name="last\u2022name"
        )
        assert chat.mention_markdown("the_name*\u2022") == expected.format(
            "the_name*\u2022", chat.id
        )
        assert chat.mention_markdown() == expected.format(chat.full_name, chat.id)
        chat = Chat(id=1, type=Chat.PRIVATE, last_name="last\u2022name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a private chat without first name"
        ):
            chat.mention_markdown()

        expected = "[{}](https://t.me/{})"
        chat = Chat(id=1, type="foo", username="user\u2022name", title="\u2022title")
        assert chat.mention_markdown("the_name*\u2022") == expected.format(
            "the_name*\u2022", chat.username
        )
        assert chat.mention_markdown() == expected.format(chat.title, chat.username)
        chat = Chat(id=1, type="foo", username="user\u2022name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a public chat without title"
        ):
            chat.mention_markdown()

    def test_mention_markdown_v2(self):
        chat = Chat(id=1, type="foo")
        with pytest.raises(TypeError, match="Can not create a mention to a private group chat"):
            chat.mention_markdown_v2()

        expected = "[{}](tg://user?id={})"
        chat = Chat(id=1, type=Chat.PRIVATE, first_name="first{name", last_name="last_name")
        assert chat.mention_markdown_v2("the{name>\u2022") == expected.format(
            "the\\{name\\>\u2022", chat.id
        )
        assert chat.mention_markdown_v2() == expected.format(
            escape_markdown(chat.full_name, version=2), chat.id
        )
        chat = Chat(id=1, type=Chat.PRIVATE, last_name="last_name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a private chat without first name"
        ):
            chat.mention_markdown_v2()

        expected = "[{}](https://t.me/{})"
        chat = Chat(id=1, type="foo", username="user{name", title="{title")
        assert chat.mention_markdown_v2("the{name>\u2022") == expected.format(
            "the\\{name\\>\u2022", chat.username
        )
        assert chat.mention_markdown_v2() == expected.format(
            escape_markdown(chat.title, version=2), chat.username
        )
        chat = Chat(id=1, type="foo", username="user\u2022name")
        with pytest.raises(
            TypeError, match="Can not create a mention to a public chat without title"
        ):
            chat.mention_markdown_v2()
