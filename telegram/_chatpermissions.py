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
"""This module contains an object that represents a Telegram ChatPermission."""

from typing import Any

from telegram._telegramobject import TelegramObject


class ChatPermissions(TelegramObject):
    """Describes actions that a non-administrator user is allowed to take in a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`can_send_messages`, :attr:`can_send_media_messages`,
    :attr:`can_send_polls`, :attr:`can_send_other_messages`, :attr:`can_add_web_page_previews`,
    :attr:`can_change_info`, :attr:`can_invite_users` and :attr:`can_pin_messages` are equal.

    Note:
        Though not stated explicitly in the official docs, Telegram changes not only the
        permissions that are set, but also sets all the others to :obj:`False`. However, since not
        documented, this behaviour may change unbeknown to PTB.

    Args:
        can_send_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to
            send audios, documents, photos, videos, video notes and voice notes, implies
            :attr:`can_send_messages`.
        can_send_polls (:obj:`bool`, optional): :obj:`True`, if the user is allowed to send polls,
            implies :attr:`can_send_messages`.
        can_send_other_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to
            send animations, games, stickers and use inline bots, implies
            :attr:`can_send_media_messages`.
        can_add_web_page_previews (:obj:`bool`, optional): :obj:`True`, if the user is allowed to
            add web page previews to their messages, implies :attr:`can_send_media_messages`.
        can_change_info (:obj:`bool`, optional): :obj:`True`, if the user is allowed to change the
            chat title, photo and other settings. Ignored in public supergroups.
        can_invite_users (:obj:`bool`, optional): :obj:`True`, if the user is allowed to invite new
            users to the chat.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed to pin
            messages. Ignored in public supergroups.

    Attributes:
        can_send_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to
            send audios, documents, photos, videos, video notes and voice notes, implies
            :attr:`can_send_messages`.
        can_send_polls (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to send polls,
            implies :attr:`can_send_messages`.
        can_send_other_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to
            send animations, games, stickers and use inline bots, implies
            :attr:`can_send_media_messages`.
        can_add_web_page_previews (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to
            add web page previews to their messages, implies :attr:`can_send_media_messages`.
        can_change_info (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to change the
            chat title, photo and other settings. Ignored in public supergroups.
        can_invite_users (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to pin
            messages. Ignored in public supergroups.

    """

    __slots__ = (
        "can_send_other_messages",
        "can_invite_users",
        "can_send_polls",
        "can_send_messages",
        "can_send_media_messages",
        "can_change_info",
        "can_pin_messages",
        "can_add_web_page_previews",
    )

    def __init__(
        self,
        can_send_messages: bool = None,
        can_send_media_messages: bool = None,
        can_send_polls: bool = None,
        can_send_other_messages: bool = None,
        can_add_web_page_previews: bool = None,
        can_change_info: bool = None,
        can_invite_users: bool = None,
        can_pin_messages: bool = None,
        **_kwargs: Any,
    ):
        # Required
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_polls = can_send_polls
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_pin_messages = can_pin_messages

        self._id_attrs = (
            self.can_send_messages,
            self.can_send_media_messages,
            self.can_send_polls,
            self.can_send_other_messages,
            self.can_add_web_page_previews,
            self.can_change_info,
            self.can_invite_users,
            self.can_pin_messages,
        )

    @classmethod
    def all_permissions(cls) -> "ChatPermissions":
        """
        This method returns an :class:`ChatPermissions` instance with all attributes
        set to :obj:`True`. This is e.g. useful when unrestricting a chat member with
        :meth:`telegram.Bot.restrict_chat_member`.

        .. versionadded:: 20.0

        """
        return cls(True, True, True, True, True, True, True, True)

    @classmethod
    def no_permissions(cls) -> "ChatPermissions":
        """
        This method returns an :class:`ChatPermissions` instance
        with all attributes set to :obj:`False`.

        .. versionadded:: 20.0
        """
        return cls(False, False, False, False, False, False, False, False)
