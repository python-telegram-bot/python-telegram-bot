#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import datetime

from telegram import User, TelegramObject
from telegram.utils.helpers import to_timestamp, from_timestamp

from telegram.utils.types import JSONDict
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot


class ChatMember(TelegramObject):
    """This object contains information about one member of a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` and :attr:`status` are equal.

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat.
        custom_title (:obj:`str`): Optional. Custom title for owner and administrators.
        until_date (:class:`datetime.datetime`): Optional. Date when restrictions will be lifted
            for this user.
        can_be_edited (:obj:`bool`): Optional. If the bot is allowed to edit administrator
            privileges of that user.
        can_change_info (:obj:`bool`): Optional. If the user can change the chat title, photo and
            other settings.
        can_post_messages (:obj:`bool`): Optional. If the administrator can post in the channel.
        can_edit_messages (:obj:`bool`): Optional. If the administrator can edit messages of other
            users.
        can_delete_messages (:obj:`bool`): Optional. If the administrator can delete messages of
            other users.
        can_invite_users (:obj:`bool`): Optional. If the user can invite new users to the chat.
        can_restrict_members (:obj:`bool`): Optional. If the administrator can restrict, ban or
            unban chat members.
        can_pin_messages (:obj:`bool`): Optional. If the user can pin messages.
        can_promote_members (:obj:`bool`): Optional. If the administrator can add new
            administrators.
        is_member (:obj:`bool`): Optional. Restricted only. :obj:`True`, if the user is a member of
            the chat at the moment of the request.
        can_send_messages (:obj:`bool`): Optional. If the user can send text messages, contacts,
            locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. If the user can send media messages,
            implies can_send_messages.
        can_send_polls (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to
            send polls.
        can_send_other_messages (:obj:`bool`): Optional. If the user can send animations, games,
            stickers and use inline bots, implies can_send_media_messages.
        can_add_web_page_previews (:obj:`bool`): Optional. If user may add web page previews to his
            messages, implies can_send_media_messages

    Args:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be 'creator', 'administrator',
            'member', 'restricted', 'left' or 'kicked'.
        custom_title (:obj:`str`, optional): Owner and administrators only.
            Custom title for this user.
        until_date (:class:`datetime.datetime`, optional): Restricted and kicked only. Date when
            restrictions will be lifted for this user.
        can_be_edited (:obj:`bool`, optional): Administrators only. :obj:`True`, if the bot is
            allowed to edit administrator privileges of that user.
        can_change_info (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can change the chat title, photo and other settings.
        can_post_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can post in the channel, channels only.
        can_edit_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can edit messages of other users and can pin messages; channels only.
        can_delete_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can delete messages of other users.
        can_invite_users (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can invite new users to the chat.
        can_restrict_members (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_pin_messages (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can pin messages, groups and supergroups only.
        can_promote_members (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by administrators
            that were appointed by the user).
        is_member (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user is a member of
            the chat at the moment of the request.
        can_send_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user can
            send text messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user
            can send audios, documents, photos, videos, video notes and voice notes.
        can_send_polls (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user is
            allowed to send polls.
        can_send_other_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user
            can send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`, optional): Restricted only. :obj:`True`, if user
            may add web page previews to his messages.

    """
    ADMINISTRATOR: str = 'administrator'
    """:obj:`str`: 'administrator'"""
    CREATOR: str = 'creator'
    """:obj:`str`: 'creator'"""
    KICKED: str = 'kicked'
    """:obj:`str`: 'kicked'"""
    LEFT: str = 'left'
    """:obj:`str`: 'left'"""
    MEMBER: str = 'member'
    """:obj:`str`: 'member'"""
    RESTRICTED: str = 'restricted'
    """:obj:`str`: 'restricted'"""

    def __init__(self,
                 user: User,
                 status: str,
                 until_date: datetime.datetime = None,
                 can_be_edited: bool = None,
                 can_change_info: bool = None,
                 can_post_messages: bool = None,
                 can_edit_messages: bool = None,
                 can_delete_messages: bool = None,
                 can_invite_users: bool = None,
                 can_restrict_members: bool = None,
                 can_pin_messages: bool = None,
                 can_promote_members: bool = None,
                 can_send_messages: bool = None,
                 can_send_media_messages: bool = None,
                 can_send_polls: bool = None,
                 can_send_other_messages: bool = None,
                 can_add_web_page_previews: bool = None,
                 is_member: bool = None,
                 custom_title: str = None,
                 **kwargs: Any):
        # Required
        self.user = user
        self.status = status
        self.custom_title = custom_title
        self.until_date = until_date
        self.can_be_edited = can_be_edited
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_polls = can_send_polls
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews
        self.is_member = is_member

        self._id_attrs = (self.user, self.status)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ChatMember']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['user'] = User.de_json(data.get('user'), bot)
        data['until_date'] = from_timestamp(data.get('until_date', None))

        return cls(**data)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['until_date'] = to_timestamp(self.until_date)

        return data
