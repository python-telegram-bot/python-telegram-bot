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

import pytest

from telegram import (
    Birthdate,
    BusinessIntro,
    BusinessLocation,
    BusinessOpeningHours,
    BusinessOpeningHoursInterval,
    Chat,
    ChatFullInfo,
    ChatLocation,
    ChatPermissions,
    Location,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ReactionEmoji
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat_full_info(bot):
    chat = ChatFullInfo(
        ChatFullInfoTestBase.id_,
        type=ChatFullInfoTestBase.type_,
        accent_color_id=ChatFullInfoTestBase.accent_color_id,
        max_reaction_count=ChatFullInfoTestBase.max_reaction_count,
        title=ChatFullInfoTestBase.title,
        username=ChatFullInfoTestBase.username,
        sticker_set_name=ChatFullInfoTestBase.sticker_set_name,
        can_set_sticker_set=ChatFullInfoTestBase.can_set_sticker_set,
        permissions=ChatFullInfoTestBase.permissions,
        slow_mode_delay=ChatFullInfoTestBase.slow_mode_delay,
        bio=ChatFullInfoTestBase.bio,
        linked_chat_id=ChatFullInfoTestBase.linked_chat_id,
        location=ChatFullInfoTestBase.location,
        has_private_forwards=ChatFullInfoTestBase.has_private_forwards,
        has_protected_content=ChatFullInfoTestBase.has_protected_content,
        has_visible_history=ChatFullInfoTestBase.has_visible_history,
        join_to_send_messages=ChatFullInfoTestBase.join_to_send_messages,
        join_by_request=ChatFullInfoTestBase.join_by_request,
        has_restricted_voice_and_video_messages=(
            ChatFullInfoTestBase.has_restricted_voice_and_video_messages
        ),
        is_forum=ChatFullInfoTestBase.is_forum,
        active_usernames=ChatFullInfoTestBase.active_usernames,
        emoji_status_custom_emoji_id=ChatFullInfoTestBase.emoji_status_custom_emoji_id,
        emoji_status_expiration_date=ChatFullInfoTestBase.emoji_status_expiration_date,
        has_aggressive_anti_spam_enabled=ChatFullInfoTestBase.has_aggressive_anti_spam_enabled,
        has_hidden_members=ChatFullInfoTestBase.has_hidden_members,
        available_reactions=ChatFullInfoTestBase.available_reactions,
        background_custom_emoji_id=ChatFullInfoTestBase.background_custom_emoji_id,
        profile_accent_color_id=ChatFullInfoTestBase.profile_accent_color_id,
        profile_background_custom_emoji_id=ChatFullInfoTestBase.profile_background_custom_emoji_id,
        unrestrict_boost_count=ChatFullInfoTestBase.unrestrict_boost_count,
        custom_emoji_sticker_set_name=ChatFullInfoTestBase.custom_emoji_sticker_set_name,
        business_intro=ChatFullInfoTestBase.business_intro,
        business_location=ChatFullInfoTestBase.business_location,
        business_opening_hours=ChatFullInfoTestBase.business_opening_hours,
        birthdate=ChatFullInfoTestBase.birthdate,
        personal_chat=ChatFullInfoTestBase.personal_chat,
        first_name=ChatFullInfoTestBase.first_name,
        last_name=ChatFullInfoTestBase.last_name,
        can_send_paid_media=ChatFullInfoTestBase.can_send_paid_media,
    )
    chat.set_bot(bot)
    chat._unfreeze()
    return chat


# Shortcut methods are tested in test_chat.py.
class ChatFullInfoTestBase:
    id_ = -28767330
    max_reaction_count = 2
    title = "ToledosPalaceBot - Group"
    type_ = "group"
    username = "username"
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
    has_visible_history = True
    has_private_forwards = True
    join_to_send_messages = True
    join_by_request = True
    has_restricted_voice_and_video_messages = True
    is_forum = True
    active_usernames = ["These", "Are", "Usernames!"]
    emoji_status_custom_emoji_id = "VeryUniqueCustomEmojiID"
    emoji_status_expiration_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)
    has_aggressive_anti_spam_enabled = True
    has_hidden_members = True
    available_reactions = [
        ReactionTypeEmoji(ReactionEmoji.THUMBS_DOWN),
        ReactionTypeCustomEmoji("custom_emoji_id"),
    ]
    business_intro = BusinessIntro("Title", "Description", None)
    business_location = BusinessLocation("Address", Location(123, 456))
    business_opening_hours = BusinessOpeningHours(
        "Country/City",
        [BusinessOpeningHoursInterval(opening, opening + 60) for opening in (0, 24 * 60)],
    )
    accent_color_id = 1
    background_custom_emoji_id = "background_custom_emoji_id"
    profile_accent_color_id = 2
    profile_background_custom_emoji_id = "profile_background_custom_emoji_id"
    unrestrict_boost_count = 100
    custom_emoji_sticker_set_name = "custom_emoji_sticker_set_name"
    birthdate = Birthdate(1, 1)
    personal_chat = Chat(3, "private", "private")
    first_name = "first_name"
    last_name = "last_name"
    can_send_paid_media = True


class TestChatFullInfoWithoutRequest(ChatFullInfoTestBase):
    def test_slot_behaviour(self, chat_full_info):
        cfi = chat_full_info
        for attr in cfi.__slots__:
            assert getattr(cfi, attr, "err") != "err", f"got extra slot '{attr}'"

        assert len(mro_slots(cfi)) == len(set(mro_slots(cfi))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "id": self.id_,
            "title": self.title,
            "type": self.type_,
            "accent_color_id": self.accent_color_id,
            "max_reaction_count": self.max_reaction_count,
            "username": self.username,
            "sticker_set_name": self.sticker_set_name,
            "can_set_sticker_set": self.can_set_sticker_set,
            "permissions": self.permissions.to_dict(),
            "slow_mode_delay": self.slow_mode_delay,
            "bio": self.bio,
            "business_intro": self.business_intro.to_dict(),
            "business_location": self.business_location.to_dict(),
            "business_opening_hours": self.business_opening_hours.to_dict(),
            "has_protected_content": self.has_protected_content,
            "has_visible_history": self.has_visible_history,
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
            "emoji_status_expiration_date": to_timestamp(self.emoji_status_expiration_date),
            "has_aggressive_anti_spam_enabled": self.has_aggressive_anti_spam_enabled,
            "has_hidden_members": self.has_hidden_members,
            "available_reactions": [reaction.to_dict() for reaction in self.available_reactions],
            "background_custom_emoji_id": self.background_custom_emoji_id,
            "profile_accent_color_id": self.profile_accent_color_id,
            "profile_background_custom_emoji_id": self.profile_background_custom_emoji_id,
            "unrestrict_boost_count": self.unrestrict_boost_count,
            "custom_emoji_sticker_set_name": self.custom_emoji_sticker_set_name,
            "birthdate": self.birthdate.to_dict(),
            "personal_chat": self.personal_chat.to_dict(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "can_send_paid_media": self.can_send_paid_media,
        }
        cfi = ChatFullInfo.de_json(json_dict, offline_bot)
        assert cfi.id == self.id_
        assert cfi.title == self.title
        assert cfi.type == self.type_
        assert cfi.username == self.username
        assert cfi.sticker_set_name == self.sticker_set_name
        assert cfi.can_set_sticker_set == self.can_set_sticker_set
        assert cfi.permissions == self.permissions
        assert cfi.slow_mode_delay == self.slow_mode_delay
        assert cfi.bio == self.bio
        assert cfi.business_intro == self.business_intro
        assert cfi.business_location == self.business_location
        assert cfi.business_opening_hours == self.business_opening_hours
        assert cfi.has_protected_content == self.has_protected_content
        assert cfi.has_visible_history == self.has_visible_history
        assert cfi.has_private_forwards == self.has_private_forwards
        assert cfi.linked_chat_id == self.linked_chat_id
        assert cfi.location.location == self.location.location
        assert cfi.location.address == self.location.address
        assert cfi.join_to_send_messages == self.join_to_send_messages
        assert cfi.join_by_request == self.join_by_request
        assert (
            cfi.has_restricted_voice_and_video_messages
            == self.has_restricted_voice_and_video_messages
        )
        assert cfi.is_forum == self.is_forum
        assert cfi.active_usernames == tuple(self.active_usernames)
        assert cfi.emoji_status_custom_emoji_id == self.emoji_status_custom_emoji_id
        assert cfi.emoji_status_expiration_date == (self.emoji_status_expiration_date)
        assert cfi.has_aggressive_anti_spam_enabled == self.has_aggressive_anti_spam_enabled
        assert cfi.has_hidden_members == self.has_hidden_members
        assert cfi.available_reactions == tuple(self.available_reactions)
        assert cfi.accent_color_id == self.accent_color_id
        assert cfi.background_custom_emoji_id == self.background_custom_emoji_id
        assert cfi.profile_accent_color_id == self.profile_accent_color_id
        assert cfi.profile_background_custom_emoji_id == self.profile_background_custom_emoji_id
        assert cfi.unrestrict_boost_count == self.unrestrict_boost_count
        assert cfi.custom_emoji_sticker_set_name == self.custom_emoji_sticker_set_name
        assert cfi.birthdate == self.birthdate
        assert cfi.personal_chat == self.personal_chat
        assert cfi.first_name == self.first_name
        assert cfi.last_name == self.last_name
        assert cfi.max_reaction_count == self.max_reaction_count
        assert cfi.can_send_paid_media == self.can_send_paid_media

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "id": self.id_,
            "type": self.type_,
            "accent_color_id": self.accent_color_id,
            "max_reaction_count": self.max_reaction_count,
            "emoji_status_expiration_date": to_timestamp(self.emoji_status_expiration_date),
        }
        cfi_bot = ChatFullInfo.de_json(json_dict, offline_bot)
        cfi_bot_raw = ChatFullInfo.de_json(json_dict, raw_bot)
        cfi_bot_tz = ChatFullInfo.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        emoji_expire_offset = cfi_bot_tz.emoji_status_expiration_date.utcoffset()
        emoji_expire_offset_tz = tz_bot.defaults.tzinfo.utcoffset(
            cfi_bot_tz.emoji_status_expiration_date.replace(tzinfo=None)
        )

        assert cfi_bot.emoji_status_expiration_date.tzinfo == UTC
        assert cfi_bot_raw.emoji_status_expiration_date.tzinfo == UTC
        assert emoji_expire_offset_tz == emoji_expire_offset

    def test_to_dict(self, chat_full_info):
        cfi = chat_full_info
        cfi_dict = cfi.to_dict()

        assert isinstance(cfi_dict, dict)
        assert cfi_dict["id"] == cfi.id
        assert cfi_dict["title"] == cfi.title
        assert cfi_dict["type"] == cfi.type
        assert cfi_dict["username"] == cfi.username
        assert cfi_dict["permissions"] == cfi.permissions.to_dict()
        assert cfi_dict["slow_mode_delay"] == cfi.slow_mode_delay
        assert cfi_dict["bio"] == cfi.bio
        assert cfi_dict["business_intro"] == cfi.business_intro.to_dict()
        assert cfi_dict["business_location"] == cfi.business_location.to_dict()
        assert cfi_dict["business_opening_hours"] == cfi.business_opening_hours.to_dict()
        assert cfi_dict["has_private_forwards"] == cfi.has_private_forwards
        assert cfi_dict["has_protected_content"] == cfi.has_protected_content
        assert cfi_dict["has_visible_history"] == cfi.has_visible_history
        assert cfi_dict["linked_chat_id"] == cfi.linked_chat_id
        assert cfi_dict["location"] == cfi.location.to_dict()
        assert cfi_dict["join_to_send_messages"] == cfi.join_to_send_messages
        assert cfi_dict["join_by_request"] == cfi.join_by_request
        assert (
            cfi_dict["has_restricted_voice_and_video_messages"]
            == cfi.has_restricted_voice_and_video_messages
        )
        assert cfi_dict["is_forum"] == cfi.is_forum
        assert cfi_dict["active_usernames"] == list(cfi.active_usernames)
        assert cfi_dict["emoji_status_custom_emoji_id"] == cfi.emoji_status_custom_emoji_id
        assert cfi_dict["emoji_status_expiration_date"] == to_timestamp(
            cfi.emoji_status_expiration_date
        )
        assert cfi_dict["has_aggressive_anti_spam_enabled"] == cfi.has_aggressive_anti_spam_enabled
        assert cfi_dict["has_hidden_members"] == cfi.has_hidden_members
        assert cfi_dict["available_reactions"] == [
            reaction.to_dict() for reaction in cfi.available_reactions
        ]
        assert cfi_dict["accent_color_id"] == cfi.accent_color_id
        assert cfi_dict["background_custom_emoji_id"] == cfi.background_custom_emoji_id
        assert cfi_dict["profile_accent_color_id"] == cfi.profile_accent_color_id
        assert (
            cfi_dict["profile_background_custom_emoji_id"]
            == cfi.profile_background_custom_emoji_id
        )
        assert cfi_dict["custom_emoji_sticker_set_name"] == cfi.custom_emoji_sticker_set_name
        assert cfi_dict["unrestrict_boost_count"] == cfi.unrestrict_boost_count
        assert cfi_dict["birthdate"] == cfi.birthdate.to_dict()
        assert cfi_dict["personal_chat"] == cfi.personal_chat.to_dict()
        assert cfi_dict["first_name"] == cfi.first_name
        assert cfi_dict["last_name"] == cfi.last_name
        assert cfi_dict["can_send_paid_media"] == cfi.can_send_paid_media

        assert cfi_dict["max_reaction_count"] == cfi.max_reaction_count

    def test_always_tuples_attributes(self):
        cfi = ChatFullInfo(
            id=123,
            type=Chat.PRIVATE,
            accent_color_id=1,
            max_reaction_count=2,
        )
        assert isinstance(cfi.active_usernames, tuple)
        assert cfi.active_usernames == ()
