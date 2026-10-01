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
"""This module contains an object that represents a Telegram ChatFullInfo."""

import datetime as dtm
from typing import TYPE_CHECKING

from telegram._birthdate import Birthdate
from telegram._chat import Chat, _ChatBase
from telegram._chatlocation import ChatLocation
from telegram._chatpermissions import ChatPermissions
from telegram._files.audio import Audio
from telegram._files.chatphoto import ChatPhoto
from telegram._gifts import AcceptedGiftTypes
from telegram._reaction import ReactionType
from telegram._uniquegift import UniqueGiftColors
from telegram._userrating import UserRating
from telegram._utils.argumentparsing import (
    parse_sequence_arg,
    to_timedelta,
)
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import (
    get_timedelta_value,
)

if TYPE_CHECKING:
    from telegram import BusinessIntro, BusinessLocation, BusinessOpeningHours, Message


@tg_dataclass()
class ChatFullInfo(_ChatBase):
    """
    This object contains full information about a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`~telegram.Chat.id` is equal.

    .. versionadded:: 21.2

    .. versionchanged:: 21.3
        Explicit support for all shortcut methods known from :class:`telegram.Chat` on this
        object. Previously those were only available because this class inherited from
        :class:`telegram.Chat`.

    .. versionremoved:: 22.3
       Removed argument and attribute ``can_send_gift`` deprecated  by API 9.0.

    Args:
        id (:obj:`int`): Unique identifier for this chat.
        type (:obj:`str`): Type of chat, can be either :attr:`PRIVATE`, :attr:`GROUP`,
            :attr:`SUPERGROUP` or :attr:`CHANNEL`.
        accent_color_id (:obj:`int`, optional): Identifier of the
            :class:`accent color <telegram.constants.AccentColor>` for the chat name and
            backgrounds of the chat photo, reply header, and link preview. See `accent colors`_
            for more details.

            .. versionadded:: 20.8
        max_reaction_count (:obj:`int`): The maximum number of reactions that can be set on a
            message in the chat.

            .. versionadded:: 21.2
        accepted_gift_types (:class:`telegram.AcceptedGiftTypes`): Information about types of
            gifts that are accepted by the chat or by the corresponding user for private chats.

            .. versionadded:: 22.1
        title (:obj:`str`, optional): Title, for supergroups, channels and group chats.
        username (:obj:`str`, optional): Username, for private chats, supergroups and channels if
            available.
        first_name (:obj:`str`, optional): First name of the other party in a private chat.
        last_name (:obj:`str`, optional): Last name of the other party in a private chat.
        is_forum (:obj:`bool`, optional): :obj:`True`, if the supergroup chat is a forum
            (has topics_ enabled).

            .. versionadded:: 20.0
        photo (:class:`telegram.ChatPhoto`, optional): Chat photo.
        active_usernames (Sequence[:obj:`str`], optional):  If set, the list of all `active chat
            usernames <https://telegram.org/blog/topics-in-groups-collectible-usernames\
            #collectible-usernames>`_; for private chats, supergroups and channels.

            .. versionadded:: 20.0
        birthdate (:class:`telegram.Birthdate`, optional): For private chats,
            the date of birth of the user.

            .. versionadded:: 21.1
        business_intro (:class:`telegram.BusinessIntro`, optional): For private chats with
            business accounts, the intro of the business.

            .. versionadded:: 21.1
        business_location (:class:`telegram.BusinessLocation`, optional): For private chats with
            business accounts, the location of the business.

            .. versionadded:: 21.1
        business_opening_hours (:class:`telegram.BusinessOpeningHours`, optional): For private
            chats with business accounts, the opening hours of the business.

            .. versionadded:: 21.1
        personal_chat (:class:`telegram.Chat`, optional): For private chats, the personal channel
            of the user.

            .. versionadded:: 21.1
        available_reactions (Sequence[:class:`telegram.ReactionType`], optional): List of available
            reactions allowed in the chat. If omitted, then all of
            :const:`telegram.constants.ReactionEmoji` are allowed.

            .. versionadded:: 20.8
        background_custom_emoji_id (:obj:`str`, optional): Custom emoji identifier of emoji chosen
            by the chat for the reply header and link preview background.

            .. versionadded:: 20.8
        profile_accent_color_id (:obj:`int`, optional): Identifier of the
            :class:`accent color <telegram.constants.ProfileAccentColor>` for the chat's profile
            background. See profile `accent colors`_ for more details.

            .. versionadded:: 20.8
        profile_background_custom_emoji_id (:obj:`str`, optional): Custom emoji identifier of
            the emoji chosen by the chat for its profile background.

            .. versionadded:: 20.8
        emoji_status_custom_emoji_id (:obj:`str`, optional): Custom emoji identifier of emoji
            status of the chat or the other party in a private chat.

            .. versionadded:: 20.0
        emoji_status_expiration_date (:class:`datetime.datetime`, optional): Expiration date of
            emoji status of the chat or the other party in a private chat, as a datetime object,
            if any.

            |datetime_localization|

            .. versionadded:: 20.5
        bio (:obj:`str`, optional): Bio of the other party in a private chat.
        has_private_forwards (:obj:`bool`, optional): :obj:`True`, if privacy settings of the other
            party in the private chat allows to use ``tg://user?id=<user_id>`` links only in chats
            with the user.

            .. versionadded:: 13.9
        has_restricted_voice_and_video_messages (:obj:`bool`, optional): :obj:`True`, if the
            privacy settings of the other party restrict sending voice and video note messages
            in the private chat.

            .. versionadded:: 20.0
        join_to_send_messages (:obj:`bool`, optional): :obj:`True`, if users need to join the
            supergroup before they can send messages.

            .. versionadded:: 20.0
        join_by_request (:obj:`bool`, optional): :obj:`True`, if all users directly joining the
            supergroup without using an invite link need to be approved by supergroup
            administrators.

            .. versionadded:: 20.0
        description (:obj:`str`, optional): Description, for groups, supergroups and channel chats.
        invite_link (:obj:`str`, optional): Primary invite link, for groups, supergroups and
            channel.
        pinned_message (:class:`telegram.Message`, optional): The most recent pinned message
            (by sending date).
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups.
        slow_mode_delay (:obj:`int` | :class:`datetime.timedelta`, optional): For supergroups,
            the minimum allowed delay between consecutive messages sent by each unprivileged user.

            .. versionchanged:: v22.2
                |time-period-input|
        unrestrict_boost_count (:obj:`int`, optional): For supergroups, the minimum number of
            boosts that a non-administrator user needs to add in order to ignore slow mode and chat
            permissions.

            .. versionadded:: 21.0
        message_auto_delete_time (:obj:`int` | :class:`datetime.timedelta`, optional): The time
            after which all messages sent to the chat will be automatically deleted; in seconds.

            .. versionadded:: 13.4

            .. versionchanged:: v22.2
                |time-period-input|
        has_aggressive_anti_spam_enabled (:obj:`bool`, optional): :obj:`True`, if aggressive
            anti-spam checks are enabled in the supergroup. The field is only available to chat
            administrators.

            .. versionadded:: 20.0
        has_hidden_members (:obj:`bool`, optional): :obj:`True`, if non-administrators can only
            get the list of bots and administrators in the chat.

            .. versionadded:: 20.0
        has_protected_content (:obj:`bool`, optional): :obj:`True`, if messages from the chat can't
            be forwarded to other chats.

            .. versionadded:: 13.9
        has_visible_history (:obj:`bool`, optional): :obj:`True`, if new chat members will have
            access to old messages; available only to chat administrators.

            .. versionadded:: 20.8
        sticker_set_name (:obj:`str`, optional): For supergroups, name of group sticker set.
        can_set_sticker_set (:obj:`bool`, optional): :obj:`True`, if the bot can change group the
            sticker set.
        custom_emoji_sticker_set_name (:obj:`str`, optional): For supergroups, the name of the
            group's custom emoji sticker set. Custom emoji from this set can be used by all users
            and bots in the group.

            .. versionadded:: 21.0
        linked_chat_id (:obj:`int`, optional): Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats.
        location (:class:`telegram.ChatLocation`, optional): For supergroups, the location to which
            the supergroup is connected.
        can_send_paid_media (:obj:`bool`, optional): :obj:`True`, if paid media messages can be
            sent or forwarded to the channel chat. The field is available only for channel chats.

            .. versionadded:: 21.4
        is_direct_messages (:obj:`bool`, optional): :obj:`True`, if the chat is the direct messages
            chat of a channel.

            .. versionadded:: 22.4
        parent_chat (:obj:`telegram.Chat`, optional): Information about the corresponding channel
            chat; for direct messages chats only.

            .. versionadded:: 22.4
        rating (:class:`telegram.UserRating`, optional): For private chats, the rating of the user
            if any.

            .. versionadded:: 22.6
        unique_gift_colors (:class:`telegram.UniqueGiftColors`, optional): The color scheme based
            on a unique gift that must be used for the chat's name, message replies and link
            previews

            .. versionadded:: 22.6
        paid_message_star_count (:obj:`int`, optional): The number of Telegram Stars a general user
            has to pay to send a message to the chat

            .. versionadded:: 22.6
        first_profile_audio (:obj:`telegram.Audio`, optional): For private chats, the first audio
            added to the profile of the user.

            .. versionadded:: 22.7


    Attributes:
        id (:obj:`int`): Unique identifier for this chat.
        type (:obj:`str`): Type of chat, can be either :attr:`PRIVATE`, :attr:`GROUP`,
            :attr:`SUPERGROUP` or :attr:`CHANNEL`.
        accent_color_id (:obj:`int`): Optional. Identifier of the
            :class:`accent color <telegram.constants.AccentColor>` for the chat name and
            backgrounds of the chat photo, reply header, and link preview. See `accent colors`_
            for more details.

            .. versionadded:: 20.8
        max_reaction_count (:obj:`int`): The maximum number of reactions that can be set on a
            message in the chat.

            .. versionadded:: 21.2
        accepted_gift_types (:class:`telegram.AcceptedGiftTypes`): Information about types of
            gifts that are accepted by the chat or by the corresponding user for private chats.

            .. versionadded:: 22.1
        title (:obj:`str`, optional): Title, for supergroups, channels and group chats.
        username (:obj:`str`, optional): Username, for private chats, supergroups and channels if
            available.
        first_name (:obj:`str`, optional): First name of the other party in a private chat.
        last_name (:obj:`str`, optional): Last name of the other party in a private chat.
        is_forum (:obj:`bool`, optional): :obj:`True`, if the supergroup chat is a forum
            (has topics_ enabled).

            .. versionadded:: 20.0
        photo (:class:`telegram.ChatPhoto`): Optional. Chat photo.
        active_usernames (tuple[:obj:`str`]): Optional. If set, the list of all `active chat
            usernames <https://telegram.org/blog/topics-in-groups-collectible-usernames\
            #collectible-usernames>`_; for private chats, supergroups and channels.

            This list is empty if the chat has no active usernames or this chat instance was not
            obtained via :meth:`~telegram.Bot.get_chat`.

            .. versionadded:: 20.0
        birthdate (:class:`telegram.Birthdate`): Optional. For private chats,
            the date of birth of the user.

            .. versionadded:: 21.1
        business_intro (:class:`telegram.BusinessIntro`): Optional. For private chats with
            business accounts, the intro of the business.

            .. versionadded:: 21.1
        business_location (:class:`telegram.BusinessLocation`): Optional. For private chats with
            business accounts, the location of the business.

            .. versionadded:: 21.1
        business_opening_hours (:class:`telegram.BusinessOpeningHours`): Optional. For private
            chats with business accounts, the opening hours of the business.

            .. versionadded:: 21.1
        personal_chat (:class:`telegram.Chat`): Optional. For private chats, the personal channel
            of the user.

            .. versionadded:: 21.1
        available_reactions (tuple[:class:`telegram.ReactionType`]): Optional. List of available
            reactions allowed in the chat. If omitted, then all of
            :const:`telegram.constants.ReactionEmoji` are allowed.

            .. versionadded:: 20.8
        background_custom_emoji_id (:obj:`str`): Optional. Custom emoji identifier of emoji chosen
            by the chat for the reply header and link preview background.

            .. versionadded:: 20.8
        profile_accent_color_id (:obj:`int`): Optional. Identifier of the
            :class:`accent color <telegram.constants.ProfileAccentColor>` for the chat's profile
            background. See profile `accent colors`_ for more details.

            .. versionadded:: 20.8
        profile_background_custom_emoji_id (:obj:`str`): Optional. Custom emoji identifier of
            the emoji chosen by the chat for its profile background.

            .. versionadded:: 20.8
        emoji_status_custom_emoji_id (:obj:`str`): Optional. Custom emoji identifier of emoji
            status of the chat or the other party in a private chat.

            .. versionadded:: 20.0
        emoji_status_expiration_date (:class:`datetime.datetime`): Optional. Expiration date of
            emoji status of the chat or the other party in a private chat, as a datetime object,
            if any.

            |datetime_localization|

            .. versionadded:: 20.5
        bio (:obj:`str`): Optional. Bio of the other party in a private chat.
        has_private_forwards (:obj:`bool`): Optional. :obj:`True`, if privacy settings of the other
            party in the private chat allows to use ``tg://user?id=<user_id>`` links only in chats
            with the user.

            .. versionadded:: 13.9
        has_restricted_voice_and_video_messages (:obj:`bool`): Optional. :obj:`True`, if the
            privacy settings of the other party restrict sending voice and video note messages
            in the private chat.

            .. versionadded:: 20.0
        join_to_send_messages (:obj:`bool`): Optional. :obj:`True`, if users need to join
            the supergroup before they can send messages.

            .. versionadded:: 20.0
        join_by_request (:obj:`bool`): Optional. :obj:`True`, if all users directly joining the
            supergroup without using an invite link need to be approved by supergroup
            administrators.

            .. versionadded:: 20.0
        description (:obj:`str`): Optional. Description, for groups, supergroups and channel chats.
        invite_link (:obj:`str`): Optional. Primary invite link, for groups, supergroups and
            channel.
        pinned_message (:class:`telegram.Message`): Optional. The most recent pinned message
            (by sending date).
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups.
        slow_mode_delay (:obj:`int` | :class:`datetime.timedelta`): Optional. For supergroups,
            the minimum allowed delay between consecutive messages sent by each unprivileged user.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        unrestrict_boost_count (:obj:`int`): Optional. For supergroups, the minimum number of
            boosts that a non-administrator user needs to add in order to ignore slow mode and chat
            permissions.

            .. versionadded:: 21.0
        message_auto_delete_time (:obj:`int` | :class:`datetime.timedelta`): Optional. The time
            after which all messages sent to the chat will be automatically deleted; in seconds.

            .. versionadded:: 13.4

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        has_aggressive_anti_spam_enabled (:obj:`bool`): Optional. :obj:`True`, if aggressive
            anti-spam checks are enabled in the supergroup. The field is only available to chat
            administrators.

            .. versionadded:: 20.0
        has_hidden_members (:obj:`bool`): Optional. :obj:`True`, if non-administrators can only
            get the list of bots and administrators in the chat.

            .. versionadded:: 20.0
        has_protected_content (:obj:`bool`): Optional. :obj:`True`, if messages from the chat can't
            be forwarded to other chats.

            .. versionadded:: 13.9
        has_visible_history (:obj:`bool`): Optional. :obj:`True`, if new chat members will have
            access to old messages; available only to chat administrators.

            .. versionadded:: 20.8
        sticker_set_name (:obj:`str`): Optional. For supergroups, name of Group sticker set.
        can_set_sticker_set (:obj:`bool`): Optional. :obj:`True`, if the bot can change group the
            sticker set.
        custom_emoji_sticker_set_name (:obj:`str`): Optional. For supergroups, the name of the
            group's custom emoji sticker set. Custom emoji from this set can be used by all users
            and bots in the group.

            .. versionadded:: 21.0
        linked_chat_id (:obj:`int`): Optional. Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats.
        location (:class:`telegram.ChatLocation`): Optional. For supergroups, the location to which
            the supergroup is connected.
        can_send_paid_media (:obj:`bool`): Optional. :obj:`True`, if paid media messages can be
            sent or forwarded to the channel chat. The field is available only for channel chats.

            .. versionadded:: 21.4
        is_direct_messages (:obj:`bool`): Optional. :obj:`True`, if the chat is the direct messages
            chat of a channel.

            .. versionadded:: 22.4
        parent_chat (:obj:`telegram.Chat`): Optional. Information about the corresponding channel
            chat; for direct messages chats only.

            .. versionadded:: 22.4
        rating (:class:`telegram.UserRating`): Optional. For private chats, the rating of the user
            if any.

            .. versionadded:: 22.6
        unique_gift_colors (:class:`telegram.UniqueGiftColors`): Optional. The color scheme based
            on a unique gift that must be used for the chat's name, message replies and link
            previews

            .. versionadded:: 22.6
        paid_message_star_count (:obj:`int`): Optional. The number of Telegram Stars a general user
            have to pay to send a message to the chat

            .. versionadded:: 22.6
        first_profile_audio (:obj:`telegram.Audio`): Optional. For private chats, the first audio
            added to the profile of the user.

            .. versionadded:: 22.7

    .. _accent colors: https://core.telegram.org/bots/api#accent-colors
    .. _topics: https://telegram.org/blog/topics-in-groups-collectible-usernames#topics-in-groups
    """

    accent_color_id: int = tg_field(compare=True)
    max_reaction_count: int = tg_field(compare=True)
    accepted_gift_types: AcceptedGiftTypes = tg_field(compare=True)

    title: str | None = tg_field(compare=True, default=None)
    username: str | None = tg_field(compare=True, default=None)
    first_name: str | None = tg_field(compare=True, default=None)
    last_name: str | None = tg_field(compare=True, default=None)
    is_forum: bool | None = tg_field(compare=True, default=None)

    photo: ChatPhoto | None = tg_field(compare=True, default=None)
    active_usernames: tuple[str, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )
    birthdate: Birthdate | None = tg_field(compare=True, default=None)
    business_intro: "BusinessIntro | None" = tg_field(compare=True, default=None)
    business_location: "BusinessLocation | None" = tg_field(compare=True, default=None)
    business_opening_hours: "BusinessOpeningHours | None" = tg_field(compare=True, default=None)
    personal_chat: "Chat | None" = tg_field(compare=True, default=None)
    available_reactions: tuple[ReactionType, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )
    background_custom_emoji_id: str | None = tg_field(compare=True, default=None)
    profile_accent_color_id: int | None = tg_field(compare=True, default=None)
    profile_background_custom_emoji_id: str | None = tg_field(compare=True, default=None)
    emoji_status_custom_emoji_id: str | None = tg_field(compare=True, default=None)
    emoji_status_expiration_date: dtm.datetime | None = tg_field(compare=True, default=None)
    bio: str | None = tg_field(compare=True, default=None)
    has_private_forwards: bool | None = tg_field(compare=True, default=None)
    has_restricted_voice_and_video_messages: bool | None = tg_field(compare=True, default=None)
    join_to_send_messages: bool | None = tg_field(compare=True, default=None)
    join_by_request: bool | None = tg_field(compare=True, default=None)
    description: str | None = tg_field(compare=True, default=None)
    invite_link: str | None = tg_field(compare=True, default=None)
    pinned_message: "Message | None" = tg_field(compare=True, default=None)
    permissions: ChatPermissions | None = tg_field(compare=True, default=None)
    _slow_mode_delay: dtm.timedelta | None = tg_field(
        compare=True,
        default=None,
        alias="slow_mode_delay",
        converter=to_timedelta,
    )
    unrestrict_boost_count: int | None = tg_field(compare=True, default=None)
    _message_auto_delete_time: dtm.timedelta | None = tg_field(
        compare=True,
        default=None,
        alias="message_auto_delete_time",
        converter=to_timedelta,
    )
    has_aggressive_anti_spam_enabled: bool | None = tg_field(compare=True, default=None)
    has_hidden_members: bool | None = tg_field(compare=True, default=None)
    has_protected_content: bool | None = tg_field(compare=True, default=None)
    has_visible_history: bool | None = tg_field(compare=True, default=None)
    sticker_set_name: str | None = tg_field(compare=True, default=None)
    can_set_sticker_set: bool | None = tg_field(compare=True, default=None)
    custom_emoji_sticker_set_name: str | None = tg_field(compare=True, default=None)
    linked_chat_id: int | None = tg_field(compare=True, default=None)
    location: ChatLocation | None = tg_field(compare=True, default=None)
    can_send_paid_media: bool | None = tg_field(compare=True, default=None)
    is_direct_messages: bool | None = tg_field(compare=True, default=None)
    parent_chat: Chat | None = tg_field(compare=True, default=None)
    rating: UserRating | None = tg_field(compare=True, default=None)
    unique_gift_colors: UniqueGiftColors | None = tg_field(compare=True, default=None)
    paid_message_star_count: int | None = tg_field(compare=True, default=None)
    first_profile_audio: Audio | None = tg_field(compare=True, default=None)

    @property
    def slow_mode_delay(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._slow_mode_delay, attribute="slow_mode_delay")

    @property
    def message_auto_delete_time(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(
            self._message_auto_delete_time, attribute="message_auto_delete_time"
        )
