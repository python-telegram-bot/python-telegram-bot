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
"""This module contains the class which represents a Telegram ChatAdministratorRights."""

import dataclasses

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ChatAdministratorRights(TelegramObject):
    """Represents the rights of an administrator in a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`is_anonymous`, :attr:`can_manage_chat`,
    :attr:`can_delete_messages`, :attr:`can_manage_video_chats`, :attr:`can_restrict_members`,
    :attr:`can_promote_members`, :attr:`can_change_info`, :attr:`can_invite_users`,
    :attr:`can_post_messages`, :attr:`can_edit_messages`, :attr:`can_pin_messages`,
    :attr:`can_manage_topics`, :attr:`can_post_stories`, :attr:`can_delete_stories`,
    :attr:`can_edit_stories`, :attr:`can_manage_direct_messages` and  :attr:`can_manage_tags` are
    equal.

    .. versionadded:: 20.0

    .. versionchanged:: 20.0
        :attr:`can_manage_topics` is considered as well when comparing objects of
        this type in terms of equality.

    .. versionchanged:: 20.6
        :attr:`can_post_stories`, :attr:`can_edit_stories`, and :attr:`can_delete_stories` are
        considered as well when comparing objects of this type in terms of equality.

    .. versionchanged:: 21.1
        As of this version, :attr:`can_post_stories`, :attr:`can_edit_stories`,
        and :attr:`can_delete_stories` is now required. Thus, the order of arguments had to be
        changed.

    .. versionchanged:: 22.4
        :attr:`can_manage_direct_messages` is considered as well when comparing objects of
        this type in terms of equality.

    .. versionchanged:: 22.7
        :attr:`can_manage_tags` is considered as well when comparing objects of this type in terms
        of equality.

    Args:
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, get boost list, see hidden supergroup and channel members, report spam messages
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the administrator can delete messages of
            other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the administrator can manage video
            chats.
        can_restrict_members (:obj:`bool`): :obj:`True`, if the administrator can restrict, ban or
            unban chat members, or access supergroup statistics.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators
            that they have promoted, directly or indirectly (promoted by administrators that
            were appointed by the user).
        can_change_info (:obj:`bool`): :obj:`True`, if the user is allowed to change the chat title
            , photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user is allowed to invite new users to
            the chat.
        can_post_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can post
            messages in the channel, or access channel statistics; for channels only.
        can_edit_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can edit
            messages of other users and can pin messages; for channels only.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to pin
            messages; for groups and supergroups only.
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
        can_manage_direct_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can
            manage direct messages of the channel and decline suggested posts; for channels only.

            .. versionadded:: 22.4
        can_manage_tags (:obj:`bool`, optional): :obj:`True`, if the administrator can edit the
            tags of regular members; for groups and supergroups only. If omitted defaults to the
            value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7

    Attributes:
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, get boost list, see hidden supergroup and channel members, report spam messages
            and ignore slow mode. Implied by any other administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the administrator can delete messages of
            other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the administrator can manage video
            chats.
        can_restrict_members (:obj:`bool`): :obj:`True`, if the administrator can restrict, ban or
            unban chat members, or access supergroup statistics.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators that he
            has promoted, directly or indirectly (promoted by administrators that were appointed by
            the user.)
        can_change_info (:obj:`bool`): :obj:`True`, if the user is allowed to change the chat title
            ,photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user is allowed to invite new users to
            the chat.
        can_post_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can post
            messages in the channel, or access channel statistics; for channels only.
        can_edit_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can edit
            messages of other users and can pin messages; for channels only.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to pin
            messages; for groups and supergroups only.
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
            to create, rename, close, and reopen forum topics; for supergroups only.

            .. versionadded:: 20.0
        can_manage_direct_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can
            manage direct messages of the channel and decline suggested posts; for channels only.

            .. versionadded:: 22.4
        can_manage_tags (:obj:`bool`): Optional. :obj:`True`, if the administrator can edit the
            tags of regular members; for groups and supergroups only. If omitted defaults to the
            value of :attr:`can_pin_messages`.

            .. versionadded:: 22.7
    """

    # Required
    is_anonymous: bool = tg_field(compare=True)
    can_manage_chat: bool = tg_field(compare=True)
    can_delete_messages: bool = tg_field(compare=True)
    can_manage_video_chats: bool = tg_field(compare=True)
    can_restrict_members: bool = tg_field(compare=True)
    can_promote_members: bool = tg_field(compare=True)
    can_change_info: bool = tg_field(compare=True)
    can_invite_users: bool = tg_field(compare=True)
    can_post_stories: bool = tg_field(compare=True)
    can_edit_stories: bool = tg_field(compare=True)
    can_delete_stories: bool = tg_field(compare=True)
    # Optionals
    can_post_messages: bool | None = tg_field(compare=True, default=None)
    can_edit_messages: bool | None = tg_field(compare=True, default=None)
    can_pin_messages: bool | None = tg_field(compare=True, default=None)
    can_manage_topics: bool | None = tg_field(compare=True, default=None)
    can_manage_direct_messages: bool | None = tg_field(compare=True, default=None)
    can_manage_tags: bool | None = tg_field(compare=True, default=None)

    @classmethod
    def all_rights(cls) -> "ChatAdministratorRights":
        """
        This method returns the :class:`ChatAdministratorRights` object with all attributes set to
        :obj:`True`. This is e.g. useful when changing the bot's default administrator rights with
        :meth:`telegram.Bot.set_my_default_administrator_rights`.

        .. versionadded:: 20.0
        """
        return cls(
            *(True for field in dataclasses.fields(cls) if field.init and not field.kw_only)
        )

    @classmethod
    def no_rights(cls) -> "ChatAdministratorRights":
        """
        This method returns the :class:`ChatAdministratorRights` object with all attributes set to
        :obj:`False`.

        .. versionadded:: 20.0
        """
        return cls(
            *(False for field in dataclasses.fields(cls) if field.init and not field.kw_only)
        )
