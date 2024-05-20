#!/usr/bin/env python
# pylint: disable=redefined-builtin
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
"""This module contains an object that represents a Telegram ChatFullInfo."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Sequence

from telegram._birthdate import Birthdate
from telegram._chat import Chat
from telegram._chatlocation import ChatLocation
from telegram._chatpermissions import ChatPermissions
from telegram._files.chatphoto import ChatPhoto
from telegram._reaction import ReactionType
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import BusinessIntro, BusinessLocation, BusinessOpeningHours, Message


class ChatFullInfo(Chat):
    """
    This object contains full information about a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.Chat.id` is equal.

    Caution:
        This class is a subclass of :class:`telegram.Chat` and inherits all attributes and methods
        for backwards compatibility. In the future, this class will *NOT* inherit from
        :class:`telegram.Chat`.

    .. seealso::
        All arguments and attributes can be found in :class:`telegram.Chat`.

    .. versionadded:: 21.2

    Args:
        max_reaction_count (:obj:`int`): The maximum number of reactions that can be set on a
            message in the chat.

            .. versionadded:: 21.2

    Attributes:
        max_reaction_count (:obj:`int`): The maximum number of reactions that can be set on a
            message in the chat.

            .. versionadded:: 21.2
    """

    __slots__ = ("max_reaction_count",)

    def __init__(
        self,
        id: int,
        type: str,
        accent_color_id: int,  # API 7.3 made this argument required
        max_reaction_count: int,  # NEW arg in api 7.3 and is required
        title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_forum: Optional[bool] = None,
        photo: Optional[ChatPhoto] = None,
        active_usernames: Optional[Sequence[str]] = None,
        birthdate: Optional[Birthdate] = None,
        business_intro: Optional["BusinessIntro"] = None,
        business_location: Optional["BusinessLocation"] = None,
        business_opening_hours: Optional["BusinessOpeningHours"] = None,
        personal_chat: Optional["Chat"] = None,
        available_reactions: Optional[Sequence[ReactionType]] = None,
        background_custom_emoji_id: Optional[str] = None,
        profile_accent_color_id: Optional[int] = None,
        profile_background_custom_emoji_id: Optional[str] = None,
        emoji_status_custom_emoji_id: Optional[str] = None,
        emoji_status_expiration_date: Optional[datetime] = None,
        bio: Optional[str] = None,
        has_private_forwards: Optional[bool] = None,
        has_restricted_voice_and_video_messages: Optional[bool] = None,
        join_to_send_messages: Optional[bool] = None,
        join_by_request: Optional[bool] = None,
        description: Optional[str] = None,
        invite_link: Optional[str] = None,
        pinned_message: Optional["Message"] = None,
        permissions: Optional[ChatPermissions] = None,
        slow_mode_delay: Optional[int] = None,
        unrestrict_boost_count: Optional[int] = None,
        message_auto_delete_time: Optional[int] = None,
        has_aggressive_anti_spam_enabled: Optional[bool] = None,
        has_hidden_members: Optional[bool] = None,
        has_protected_content: Optional[bool] = None,
        has_visible_history: Optional[bool] = None,
        sticker_set_name: Optional[str] = None,
        can_set_sticker_set: Optional[bool] = None,
        custom_emoji_sticker_set_name: Optional[str] = None,
        linked_chat_id: Optional[int] = None,
        location: Optional[ChatLocation] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(
            id=id,
            type=type,
            title=title,
            username=username,
            first_name=first_name,
            last_name=last_name,
            photo=photo,
            description=description,
            invite_link=invite_link,
            pinned_message=pinned_message,
            permissions=permissions,
            sticker_set_name=sticker_set_name,
            can_set_sticker_set=can_set_sticker_set,
            slow_mode_delay=slow_mode_delay,
            bio=bio,
            linked_chat_id=linked_chat_id,
            location=location,
            message_auto_delete_time=message_auto_delete_time,
            has_private_forwards=has_private_forwards,
            has_protected_content=has_protected_content,
            join_to_send_messages=join_to_send_messages,
            join_by_request=join_by_request,
            has_restricted_voice_and_video_messages=has_restricted_voice_and_video_messages,
            is_forum=is_forum,
            active_usernames=active_usernames,
            emoji_status_custom_emoji_id=emoji_status_custom_emoji_id,
            emoji_status_expiration_date=emoji_status_expiration_date,
            has_aggressive_anti_spam_enabled=has_aggressive_anti_spam_enabled,
            has_hidden_members=has_hidden_members,
            available_reactions=available_reactions,
            accent_color_id=accent_color_id,
            background_custom_emoji_id=background_custom_emoji_id,
            profile_accent_color_id=profile_accent_color_id,
            profile_background_custom_emoji_id=profile_background_custom_emoji_id,
            has_visible_history=has_visible_history,
            unrestrict_boost_count=unrestrict_boost_count,
            custom_emoji_sticker_set_name=custom_emoji_sticker_set_name,
            birthdate=birthdate,
            personal_chat=personal_chat,
            business_intro=business_intro,
            business_location=business_location,
            business_opening_hours=business_opening_hours,
            api_kwargs=api_kwargs,
        )

        # Required and unique to this class-
        with self._unfrozen():
            self.max_reaction_count: int = max_reaction_count

        self._freeze()
