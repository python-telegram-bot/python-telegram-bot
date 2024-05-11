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
import warnings

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
from telegram._chat import _deprecated_attrs
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ReactionEmoji
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def chat_full_info(bot):
    chat = ChatFullInfo(
        TestChatInfoBase.id_,
        type=TestChatInfoBase.type_,
        accent_color_id=TestChatInfoBase.accent_color_id,
        max_reaction_count=TestChatInfoBase.max_reaction_count,
        title=TestChatInfoBase.title,
        username=TestChatInfoBase.username,
        sticker_set_name=TestChatInfoBase.sticker_set_name,
        can_set_sticker_set=TestChatInfoBase.can_set_sticker_set,
        permissions=TestChatInfoBase.permissions,
        slow_mode_delay=TestChatInfoBase.slow_mode_delay,
        bio=TestChatInfoBase.bio,
        linked_chat_id=TestChatInfoBase.linked_chat_id,
        location=TestChatInfoBase.location,
        has_private_forwards=True,
        has_protected_content=True,
        has_visible_history=True,
        join_to_send_messages=True,
        join_by_request=True,
        has_restricted_voice_and_video_messages=True,
        is_forum=True,
        active_usernames=TestChatInfoBase.active_usernames,
        emoji_status_custom_emoji_id=TestChatInfoBase.emoji_status_custom_emoji_id,
        emoji_status_expiration_date=TestChatInfoBase.emoji_status_expiration_date,
        has_aggressive_anti_spam_enabled=TestChatInfoBase.has_aggressive_anti_spam_enabled,
        has_hidden_members=TestChatInfoBase.has_hidden_members,
        available_reactions=TestChatInfoBase.available_reactions,
        background_custom_emoji_id=TestChatInfoBase.background_custom_emoji_id,
        profile_accent_color_id=TestChatInfoBase.profile_accent_color_id,
        profile_background_custom_emoji_id=TestChatInfoBase.profile_background_custom_emoji_id,
        unrestrict_boost_count=TestChatInfoBase.unrestrict_boost_count,
        custom_emoji_sticker_set_name=TestChatInfoBase.custom_emoji_sticker_set_name,
        business_intro=TestChatInfoBase.business_intro,
        business_location=TestChatInfoBase.business_location,
        business_opening_hours=TestChatInfoBase.business_opening_hours,
        birthdate=Birthdate(1, 1),
        personal_chat=TestChatInfoBase.personal_chat,
    )
    chat.set_bot(bot)
    chat._unfreeze()
    return chat


class TestChatInfoBase:
    id_ = -28767330
    max_reaction_count = 2
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
    has_visible_history = True
    has_private_forwards = True
    join_to_send_messages = True
    join_by_request = True
    has_restricted_voice_and_video_messages = True
    is_forum = True
    active_usernames = ["These", "Are", "Usernames!"]
    emoji_status_custom_emoji_id = "VeryUniqueCustomEmojiID"
    emoji_status_expiration_date = datetime.datetime.now(tz=UTC).replace(microsecond=0)
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


class TestChatWithoutRequest(TestChatInfoBase):
    def test_slot_behaviour(self, chat_full_info):
        cfi = chat_full_info
        for attr in cfi.__slots__:
            assert getattr(cfi, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(cfi)) == len(set(mro_slots(cfi))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "id": self.id_,
            "title": self.title,
            "type": self.type_,
            "accent_color_id": self.accent_color_id,
            "max_reaction_count": self.max_reaction_count,
            "username": self.username,
            "all_members_are_administrators": self.all_members_are_administrators,
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
        }
        cfi = ChatFullInfo.de_json(json_dict, bot)
        assert cfi.max_reaction_count == self.max_reaction_count

    def test_to_dict(self, chat_full_info):
        cfi = chat_full_info
        cfi_dict = cfi.to_dict()

        assert isinstance(cfi_dict, dict)
        assert cfi_dict["max_reaction_count"] == cfi.max_reaction_count

    def test_attr_access_no_warning(self, chat_full_info):
        cfi = chat_full_info
        for depr_attr in _deprecated_attrs:
            with warnings.catch_warnings():  # No warning should be raised
                warnings.simplefilter("error")
                getattr(cfi, depr_attr)

    def test_cfi_creation_no_warning(self, chat_full_info):
        cfi = chat_full_info
        with warnings.catch_warnings():
            dict = cfi.to_dict()
            ChatFullInfo(**dict)
