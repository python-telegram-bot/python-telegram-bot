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

from dataclasses import dataclass
from telegram import User, TelegramObject
from telegram.utils.helpers import to_timestamp, from_timestamp

from telegram.utils.types import JSONDict
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot


class _ChatMember:
    """This object only for storing constants of ChatMember
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


@dataclass(eq=False)
class ChatMember(TelegramObject, _ChatMember):
    """This object contains information about one member of the chat.

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
        is_member (:obj:`bool`): Optional. Restricted only. True, if the user is a member of the
            chat at the moment of the request.
        can_send_messages (:obj:`bool`): Optional. If the user can send text messages, contacts,
            locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. If the user can send media messages,
            implies can_send_messages.
        can_send_polls (:obj:`bool`): Optional. True, if the user is allowed to
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
        can_be_edited (:obj:`bool`, optional): Administrators only. True, if the bot is allowed to
            edit administrator privileges of that user.
        can_change_info (:obj:`bool`, optional): Administrators and restricted only. True, if the
            user can change the chat title, photo and other settings.
        can_post_messages (:obj:`bool`, optional): Administrators only. True, if the administrator
            can post in the channel, channels only.
        can_edit_messages (:obj:`bool`, optional): Administrators only. True, if the administrator
            can edit messages of other users, channels only.
        can_delete_messages (:obj:`bool`, optional): Administrators only. True, if the
            administrator can delete messages of other user.
        can_invite_users (:obj:`bool`, optional): Administrators and restricted only. True, if the
            user can invite new users to the chat.
        can_restrict_members (:obj:`bool`, optional): Administrators only. True, if the
            administrator can restrict, ban or unban chat members.
        can_pin_messages (:obj:`bool`, optional): Administrators and restricted only. True, if the
            user can pin messages, supergroups only.
        can_promote_members (:obj:`bool`, optional): Administrators only. True, if the
            administrator can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by administrators
            that were appointed by the user).
        is_member (:obj:`bool`, optional): Restricted only. True, if the user is a member of the
            chat at the moment of the request.
        can_send_messages (:obj:`bool`, optional): Restricted only. True, if the user can send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): Restricted only. True, if the user can
            send audios, documents, photos, videos, video notes and voice notes, implies
            can_send_messages.
        can_send_polls (:obj:`bool`, optional): Restricted only. True, if the user is allowed to
            send polls.
        can_send_other_messages (:obj:`bool`, optional): Restricted only. True, if the user can
            send animations, games, stickers and use inline bots, implies can_send_media_messages.
        can_add_web_page_previews (:obj:`bool`, optional): Restricted only. True, if user may add
            web page previews to his messages, implies can_send_media_messages.

    """

    # Required
    user: User
    status: str
    # Optionals
    until_date: Optional[datetime.datetime] = None
    can_be_edited: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    is_member: Optional[bool] = None
    custom_title: Optional[str] = None

    def __post_init__(self, **kwargs: Any) -> None:
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
