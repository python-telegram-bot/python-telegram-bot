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
"""This module contains an object that represents a Telegram ChatMember."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ChatMember(TelegramObject):
    """Base class for Telegram ChatMember Objects.
    Currently, the following 6 types of chat members are supported:

    * :class:`telegram.ChatMemberOwner`
    * :class:`telegram.ChatMemberAdministrator`
    * :class:`telegram.ChatMemberMember`
    * :class:`telegram.ChatMemberRestricted`
    * :class:`telegram.ChatMemberLeft`
    * :class:`telegram.ChatMemberBanned`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` and :attr:`status` are equal.

    Examples:
        :any:`Chat Member Bot <examples.chatmemberbot>`

    .. versionchanged:: 20.0

        * As of Bot API 5.3, :class:`ChatMember` is nothing but the base class for the subclasses
          listed above and is no longer returned directly by :meth:`~telegram.Bot.get_chat`.
          Therefore, most of the arguments and attributes were removed and you should no longer
          use :class:`ChatMember` directly.
        * The constant ``ChatMember.CREATOR`` was replaced by :attr:`~telegram.ChatMember.OWNER`
        * The constant ``ChatMember.KICKED`` was replaced by :attr:`~telegram.ChatMember.BANNED`

    Args:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be
            :attr:`~telegram.ChatMember.ADMINISTRATOR`, :attr:`~telegram.ChatMember.OWNER`,
            :attr:`~telegram.ChatMember.BANNED`, :attr:`~telegram.ChatMember.LEFT`,
            :attr:`~telegram.ChatMember.MEMBER` or :attr:`~telegram.ChatMember.RESTRICTED`.

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be
            :attr:`~telegram.ChatMember.ADMINISTRATOR`, :attr:`~telegram.ChatMember.OWNER`,
            :attr:`~telegram.ChatMember.BANNED`, :attr:`~telegram.ChatMember.LEFT`,
            :attr:`~telegram.ChatMember.MEMBER` or :attr:`~telegram.ChatMember.RESTRICTED`.

    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "status",
        {
            "creator": "ChatMemberOwner",
            "administrator": "ChatMemberAdministrator",
            "member": "ChatMemberMember",
            "restricted": "ChatMemberRestricted",
            "left": "ChatMemberLeft",
            "kicked": "ChatMemberBanned",
        },
    )

    ADMINISTRATOR: ClassVar[str] = constants.ChatMemberStatus.ADMINISTRATOR
    """:const:`telegram.constants.ChatMemberStatus.ADMINISTRATOR`"""
    OWNER: ClassVar[str] = constants.ChatMemberStatus.OWNER
    """:const:`telegram.constants.ChatMemberStatus.OWNER`"""
    BANNED: ClassVar[str] = constants.ChatMemberStatus.BANNED
    """:const:`telegram.constants.ChatMemberStatus.BANNED`"""
    LEFT: ClassVar[str] = constants.ChatMemberStatus.LEFT
    """:const:`telegram.constants.ChatMemberStatus.LEFT`"""
    MEMBER: ClassVar[str] = constants.ChatMemberStatus.MEMBER
    """:const:`telegram.constants.ChatMemberStatus.MEMBER`"""
    RESTRICTED: ClassVar[str] = constants.ChatMemberStatus.RESTRICTED
    """:const:`telegram.constants.ChatMemberStatus.RESTRICTED`"""

    @staticmethod
    def _status_converter(value: str) -> str:
        return enum.get_member(constants.BotCommandScopeType, value, value)

    # Required by all subclasses
    user: User = tg_field(compare=True)
    status: str = tg_field(compare=True, converter=_status_converter)


@tg_dataclass()
class ChatMemberOwner(ChatMember):
    """
    Represents a chat member that owns the chat
    and has all administrator privileges.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the
            user's presence in the chat is hidden.
        custom_title (:obj:`str`, optional): Custom title for this user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.OWNER`.
        user (:class:`telegram.User`): Information about the user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's
            presence in the chat is hidden.
        custom_title (:obj:`str`): Optional. Custom title for
            this user.
    """

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.OWNER)

    is_anonymous: bool = tg_field()
    custom_title: str | None = tg_field(default=None)


@tg_dataclass()
class ChatMemberAdministrator(ChatMember):
    """
    Represents a chat member that has some additional privileges.

    .. versionadded:: 13.7
    .. versionchanged:: 20.0

       * Argument and attribute ``can_manage_voice_chats`` were renamed to
         :paramref:`can_manage_video_chats` and  :attr:`can_manage_video_chats` in accordance to
         Bot API 6.0.
       * The argument :paramref:`can_manage_topics` was added, which changes the position of the
         optional argument :paramref:`custom_title`.

    .. versionchanged:: 21.1
        As of this version, :attr:`can_post_stories`, :attr:`can_edit_stories`,
        and :attr:`can_delete_stories` is now required. Thus, the order of arguments had to be
        changed.

    Args:
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`): :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, get boost list, see hidden supergroup and channel members, report spam messages
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 20.0
        can_restrict_members (:obj:`bool`): :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator
            can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by
            administrators that were appointed by the user).
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_post_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can post messages in the channel, or access channel statistics;
            for channels only.
        can_edit_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; for channels only.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to pin messages; for groups and supergroups only.
        can_post_stories (:obj:`bool`): :obj:`True`, if the administrator can post
            stories to the chat.

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_edit_stories (:obj:`bool`): :obj:`True`, if the administrator can edit stories posted
            by other users, post stories to the chat page, pin chat stories, and access the chat's
            story archive

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_delete_stories (:obj:`bool`): :obj:`True`, if the administrator can delete
            stories posted by other users.

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_manage_topics (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to create, rename, close, and reopen forum topics; for supergroups only.

            .. versionadded:: 20.0
        custom_title (:obj:`str`, optional): Custom title for this user.
        can_manage_direct_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can
            manage direct messages of the channel and decline suggested posts; for channels only.

            .. versionadded:: 22.4
        can_manage_tags (:obj:`bool`, optional): :obj:`True`, if the administrator can edit the
            tags of regular members; for groups and supergroups only. If omitted defaults to the
            value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.ADMINISTRATOR`.
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`): :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        is_anonymous (:obj:`bool`): :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, get boost list, see hidden supergroup and channel members, report spam messages
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 20.0
        can_restrict_members (:obj:`bool`): :obj:`True`, if the
            administrator can restrict, ban or unban chat members, or access supergroup statistics.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators
            that they have promoted, directly or indirectly (promoted by administrators that
            were appointed by the user).
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_post_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can post messages in the channel or access channel statistics;
            for channels only.
        can_edit_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; for channels only.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to pin messages; for groups and supergroups only.
        can_post_stories (:obj:`bool`): :obj:`True`, if the administrator can post
            stories to the chat.

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_edit_stories (:obj:`bool`): :obj:`True`, if the administrator can edit stories posted
            by other users, post stories to the chat page, pin chat stories, and access the chat's
            story archive

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_delete_stories (:obj:`bool`): :obj:`True`, if the administrator can delete
            stories posted by other users.

            .. versionadded:: 20.6
            .. versionchanged:: 21.0
                |non_optional_story_argument|
        can_manage_topics (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to create, rename, close, and reopen forum topics; for supergroups only

            .. versionadded:: 20.0
        custom_title (:obj:`str`): Optional. Custom title for this user.
        can_manage_direct_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can
            manage direct messages of the channel and decline suggested posts; for channels only.

            .. versionadded:: 22.4
        can_manage_tags (:obj:`bool`): Optional. :obj:`True`, if the administrator can edit the
            tags of regular members; for groups and supergroups only. If omitted defaults to the
            value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7
    """

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.ADMINISTRATOR)

    can_be_edited: bool = tg_field()
    is_anonymous: bool = tg_field()
    can_manage_chat: bool = tg_field()
    can_delete_messages: bool = tg_field()
    can_manage_video_chats: bool = tg_field()
    can_restrict_members: bool = tg_field()
    can_promote_members: bool = tg_field()
    can_change_info: bool = tg_field()
    can_invite_users: bool = tg_field()
    can_post_stories: bool = tg_field()
    can_edit_stories: bool = tg_field()
    can_delete_stories: bool = tg_field()

    # Optionals
    can_post_messages: bool | None = tg_field(default=None)
    can_edit_messages: bool | None = tg_field(default=None)
    can_pin_messages: bool | None = tg_field(default=None)
    can_manage_topics: bool | None = tg_field(default=None)
    custom_title: str | None = tg_field(default=None)
    can_manage_direct_messages: bool | None = tg_field(default=None)
    can_manage_tags: bool | None = tg_field(default=None)


@tg_dataclass()
class ChatMemberMember(ChatMember):
    """
    Represents a chat member that has no additional
    privileges or restrictions.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`, optional): Date when the user's subscription will
            expire.

            .. versionadded:: 21.5
        tag (:obj:`str`, optional): Tag of the member.

            .. versionadded:: 22.7

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.MEMBER`.
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Optional. Date when the user's subscription will
            expire.

            .. versionadded:: 21.5
        tag (:obj:`str`): Optional. Tag of the member.

            .. versionadded:: 22.7

    """

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.MEMBER)

    until_date: dtm.datetime | None = tg_field()
    tag: str | None = tg_field()


@tg_dataclass()
class ChatMemberRestricted(ChatMember):
    """
    Represents a chat member that is under certain restrictions
    in the chat. Supergroups only.

    .. versionadded:: 13.7
    .. versionchanged:: 20.0
       All arguments were made positional and their order was changed.
       The argument can_manage_topics was added.

    .. versionchanged:: 20.5
      Removed deprecated argument and attribute ``can_send_media_messages``.

    Args:
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`): :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send text messages, contacts, invoices, locations and venues.
        can_send_polls (:obj:`bool`): :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`): :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        can_manage_topics (:obj:`bool`): :obj:`True`, if the user is allowed to create
            forum topics.

            .. versionadded:: 20.0
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|
        can_send_audios (:obj:`bool`): :obj:`True`, if the user is allowed to send audios.

            .. versionadded:: 20.1
        can_send_documents (:obj:`bool`): :obj:`True`, if the user is allowed to send documents.

            .. versionadded:: 20.1
        can_send_photos (:obj:`bool`): :obj:`True`, if the user is allowed to send photos.

            .. versionadded:: 20.1
        can_send_videos (:obj:`bool`): :obj:`True`, if the user is allowed to send videos.

            .. versionadded:: 20.1
        can_send_video_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send video
            notes.

            .. versionadded:: 20.1
        can_send_voice_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send voice
            notes.

            .. versionadded:: 20.1
        can_edit_tag (:obj:`bool`): :obj:`True`, if the user is allowed to edit their own tag.
            If omitted, defaults to the value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7
        can_react_to_messages (:obj:`bool`): :obj:`True`, if the user is allowed to react to
            messages.

            .. versionadded:: 22.8
        tag (:obj:`str`, optional): Tag of the member.

            .. versionadded:: 22.7

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.RESTRICTED`.
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`): :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send text messages, contacts, locations and venues.
        can_send_polls (:obj:`bool`): :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`): :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`): :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        can_manage_topics (:obj:`bool`): :obj:`True`, if the user is allowed to create
            forum topics.

            .. versionadded:: 20.0
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|
        can_send_audios (:obj:`bool`): :obj:`True`, if the user is allowed to send audios.

            .. versionadded:: 20.1
        can_send_documents (:obj:`bool`): :obj:`True`, if the user is allowed to send documents.

            .. versionadded:: 20.1
        can_send_photos (:obj:`bool`): :obj:`True`, if the user is allowed to send photos.

            .. versionadded:: 20.1
        can_send_videos (:obj:`bool`): :obj:`True`, if the user is allowed to send videos.

            .. versionadded:: 20.1
        can_send_video_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send video
            notes.

            .. versionadded:: 20.1
        can_send_voice_notes (:obj:`bool`): :obj:`True`, if the user is allowed to send voice
            notes.

            .. versionadded:: 20.1
        can_edit_tag (:obj:`bool`): :obj:`True`, if the user is allowed to edit their own tag.
            If omitted, defaults to the value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7
        can_react_to_messages (:obj:`bool`): :obj:`True`, if the user is allowed to react to
            messages.

            .. versionadded:: 22.8
        tag (:obj:`str`): Optional. Tag of the member.

            .. versionadded:: 22.7

    """

    __REMOVED_API_FIELDS__: ClassVar[frozenset[str]] = frozenset({"can_send_media_messages"})

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.RESTRICTED)

    is_member: bool = tg_field()
    can_change_info: bool = tg_field()
    can_invite_users: bool = tg_field()
    can_pin_messages: bool = tg_field()
    can_send_messages: bool = tg_field()
    can_send_polls: bool = tg_field()
    can_send_other_messages: bool = tg_field()
    can_add_web_page_previews: bool = tg_field()
    can_manage_topics: bool = tg_field()
    until_date: dtm.datetime = tg_field()
    can_send_audios: bool = tg_field()
    can_send_documents: bool = tg_field()
    can_send_photos: bool = tg_field()
    can_send_videos: bool = tg_field()
    can_send_video_notes: bool = tg_field()
    can_send_voice_notes: bool = tg_field()
    can_edit_tag: bool = tg_field()
    can_react_to_messages: bool = tg_field()
    tag: str | None = tg_field(default=None)


@tg_dataclass()
class ChatMemberLeft(ChatMember):
    """
    Represents a chat member that isn't currently a member of the chat,
    but may join it themselves.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.LEFT`.
        user (:class:`telegram.User`): Information about the user.
    """

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.LEFT)


@tg_dataclass()
class ChatMemberBanned(ChatMember):
    """
    Represents a chat member that was banned in the chat and
    can't return to the chat or view chat messages.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :tg-const:`telegram.ChatMember.BANNED`.
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Date when restrictions
           will be lifted for this user.

            .. versionchanged:: 20.3
                |datetime_localization|

    """

    # Attribute only (init=False)
    status: str = tg_field(init=False, default=ChatMember.BANNED)

    until_date: dtm.datetime = tg_field()
