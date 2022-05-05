#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

from typing import Any

from telegram._telegramobject import TelegramObject


class ChatAdministratorRights(TelegramObject):
    """Represents the rights of an administrator in a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`is_anonymous`, :attr:`can_manage_chat`,
    :attr:`can_delete_messages`, :attr:`can_manage_video_chats`, :attr:`can_restrict_members`,
    :attr:`can_promote_members`, :attr:`can_change_info`, :attr:`can_invite_users`,
    :attr:`can_post_messages`, :attr:`can_edit_messages`, :attr:`can_pin_messages` are equal.

    .. seealso: :meth:`Bot.set_my_default_administrator_rights`,
        :meth:`Bot.get_my_default_administrator_rights`

    .. versionadded:: 20.0

    Args:
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, chat statistics, message statistics in channels, see channel members, see
            anonymous administrators in supergroups and ignore slow mode. Implied by any other
            administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the administrator can delete messages of
            other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the administrator can manage video
            chats.
        can_restrict_members (:obj:`bool`): :obj:`True`, if the administrator can restrict, ban or
            unban chat members.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators that he
            has promoted, directly or indirectly (promoted by administrators that were appointed by
            the user.)
        can_change_info (:obj:`bool`): :obj:`True`, if the user is allowed to change the chat title
            ,photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user is allowed to invite new users to
            the chat.
        can_post_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can post
            messages in the channel; channels only.
        can_edit_messages (:obj:`bool`, optional): :obj:`True`, if the administrator can edit
            messages of other users.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to pin
            messages; groups and supergroups only.

    Attributes:
        is_anonymous (:obj:`bool`): :obj:`True`, if the user's presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): :obj:`True`, if the administrator can access the chat event
            log, chat statistics, message statistics in channels, see channel members, see
            anonymous administrators in supergroups and ignore slow mode. Implied by any other
            administrator privilege.
        can_delete_messages (:obj:`bool`): :obj:`True`, if the administrator can delete messages of
            other users.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the administrator can manage video
            chats.
        can_restrict_members (:obj:`bool`): :obj:`True`, if the administrator can restrict, ban or
            unban chat members.
        can_promote_members (:obj:`bool`): :obj:`True`, if the administrator can add new
            administrators with a subset of their own privileges or demote administrators that he
            has promoted, directly or indirectly (promoted by administrators that were appointed by
            the user.)
        can_change_info (:obj:`bool`): :obj:`True`, if the user is allowed to change the chat title
            ,photo and other settings.
        can_invite_users (:obj:`bool`): :obj:`True`, if the user is allowed to invite new users to
            the chat.
        can_post_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can post
            messages in the channel; channels only.
        can_edit_messages (:obj:`bool`): Optional. :obj:`True`, if the administrator can edit
            messages of other users.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to pin
            messages; groups and supergroups only.
    """

    __slots__ = (
        "is_anonymous",
        "can_manage_chat",
        "can_delete_messages",
        "can_manage_video_chats",
        "can_restrict_members",
        "can_promote_members",
        "can_change_info",
        "can_invite_users",
        "can_post_messages",
        "can_edit_messages",
        "can_pin_messages",
    )

    def __init__(
        self,
        is_anonymous: bool,
        can_manage_chat: bool,
        can_delete_messages: bool,
        can_manage_video_chats: bool,
        can_restrict_members: bool,
        can_promote_members: bool,
        can_change_info: bool,
        can_invite_users: bool,
        can_post_messages: bool = None,
        can_edit_messages: bool = None,
        can_pin_messages: bool = None,
        **_kwargs: Any,
    ) -> None:
        # Required
        self.is_anonymous = is_anonymous
        self.can_manage_chat = can_manage_chat
        self.can_delete_messages = can_delete_messages
        self.can_manage_video_chats = can_manage_video_chats
        self.can_restrict_members = can_restrict_members
        self.can_promote_members = can_promote_members
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        # Optionals
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_pin_messages = can_pin_messages

        self._id_attrs = (
            self.is_anonymous,
            self.can_manage_chat,
            self.can_delete_messages,
            self.can_manage_video_chats,
            self.can_restrict_members,
            self.can_promote_members,
            self.can_change_info,
            self.can_invite_users,
            self.can_post_messages,
            self.can_edit_messages,
            self.can_pin_messages,
        )

    @classmethod
    def all_rights(cls) -> "ChatAdministratorRights":
        """
        This method returns the :class:`ChatAdministratorRights` object with all attributes set to
        :obj:`True`. This is e.g. useful when changing the bot's default administrator rights with
        :meth:`telegram.Bot.set_my_default_administrator_rights`.

        .. versionadded:: 20.0
        """
        return cls(True, True, True, True, True, True, True, True, True, True, True)

    @classmethod
    def no_rights(cls) -> "ChatAdministratorRights":
        """
        This method returns the :class:`ChatAdministratorRights` object with all attributes set to
        :obj:`False`.

        .. versionadded:: 20.0
        """
        return cls(False, False, False, False, False, False, False, False, False, False, False)
