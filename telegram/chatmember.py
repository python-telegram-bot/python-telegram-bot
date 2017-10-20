#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

from telegram import User, TelegramObject
from telegram.utils.helpers import to_timestamp, from_timestamp


class ChatMember(TelegramObject):
    """This object contains information about one member of the chat.

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat.
        until_date (:class:`datetime.datetime`): Optional. Date when restrictions will be lifted
            for this user.
        can_be_edited (:obj:`bool`): Optional. If the bot is allowed to edit administrator
            privileges of that user.
        can_change_info (:obj:`bool`): Optional. If the administrator can change the chat title,
            photo and other settings.
        can_post_messages (:obj:`bool`): Optional. If the administrator can post in the channel.
        can_edit_messages (:obj:`bool`): Optional. If the administrator can edit messages of other
            users.
        can_delete_messages (:obj:`bool`): Optional. If the administrator can delete messages of
            other users.
        can_invite_users (:obj:`bool`): Optional. If the administrator can invite new users to the
            chat.
        can_restrict_members (:obj:`bool`): Optional. If the administrator can restrict, ban or
            unban chat members.
        can_pin_messages (:obj:`bool`): Optional. If the administrator can pin messages.
        can_promote_members (:obj:`bool`): Optional. If the administrator can add new
            administrators.
        can_send_messages (:obj:`bool`): Optional. If the user can send text messages, contacts,
            locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. If the user can send media messages,
            implies can_send_messages.
        can_send_other_messages (:obj:`bool`): Optional. If the user can send animations, games,
            stickers and use inline bots, implies can_send_media_messages.
        can_add_web_page_previews (:obj:`bool`): Optional. If user may add web page previews to his
            messages, implies can_send_media_messages

    Args:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be 'creator', 'administrator',
            'member', 'restricted', 'left' or 'kicked'.
        until_date (:class:`datetime.datetime`, optional): Restricted and kicked only. Date when
            restrictions will be lifted for this user.
        can_be_edited (:obj:`bool`, optional): Administrators only. True, if the bot is allowed to
            edit administrator privileges of that user.
        can_change_info (:obj:`bool`, optional): Administrators only. True, if the administrator
            can change the chat title, photo and other settings.
        can_post_messages (:obj:`bool`, optional): Administrators only. True, if the administrator
            can post in the channel, channels only.
        can_edit_messages (:obj:`bool`, optional): Administrators only. True, if the administrator
            can edit messages of other users, channels only.
        can_delete_messages (:obj:`bool`, optional): Administrators only. True, if the
            administrator can delete messages of other user.
        can_invite_users (:obj:`bool`, optional): Administrators only. True, if the administrator
            can invite new users to the chat.
        can_restrict_members (:obj:`bool`, optional): Administrators only. True, if the
            administrator can restrict, ban or unban chat members.
        can_pin_messages (:obj:`bool`, optional): Administrators only. True, if the administrator
            can pin messages, supergroups only.
        can_promote_members (:obj:`bool`, optional): Administrators only. True, if the
            administrator can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by administrators
            that were appointed by the user).
        can_send_messages (:obj:`bool`, optional): Restricted only. True, if the user can send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): Restricted only. True, if the user can
            send audios, documents, photos, videos, video notes and voice notes, implies
            can_send_messages.
        can_send_other_messages (:obj:`bool`, optional): Restricted only. True, if the user can
            send animations, games, stickers and use inline bots, implies can_send_media_messages.
        can_add_web_page_previews (:obj:`bool`, optional): Restricted only. True, if user may add
            web page previews to his messages, implies can_send_media_messages.

    """
    ADMINISTRATOR = 'administrator'
    """:obj:`str`: 'administrator'"""
    CREATOR = 'creator'
    """:obj:`str`: 'creator'"""
    KICKED = 'kicked'
    """:obj:`str`: 'kicked'"""
    LEFT = 'left'
    """:obj:`str`: 'left'"""
    MEMBER = 'member'
    """:obj:`str`: 'member'"""
    RESTRICTED = 'restricted'
    """:obj:`str`: 'restricted'"""

    def __init__(self, user, status, until_date=None, can_be_edited=None,
                 can_change_info=None, can_post_messages=None, can_edit_messages=None,
                 can_delete_messages=None, can_invite_users=None,
                 can_restrict_members=None, can_pin_messages=None,
                 can_promote_members=None, can_send_messages=None,
                 can_send_media_messages=None, can_send_other_messages=None,
                 can_add_web_page_previews=None, **kwargs):
        # Required
        self.user = user
        self.status = status
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
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews

        self._id_attrs = (self.user, self.status)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(ChatMember, cls).de_json(data, bot)

        data['user'] = User.de_json(data.get('user'), bot)
        data['until_date'] = from_timestamp(data.get('until_date', None))

        return cls(**data)

    def to_dict(self):
        data = super(ChatMember, self).to_dict()

        data['until_date'] = to_timestamp(self.until_date)

        return data
