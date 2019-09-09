#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import TelegramObject


class ChatPermissions(TelegramObject):
    """Describes actions that a non-administrator user is allowed to take in a chat.

    Attributes:
        can_send_messages (:obj:`bool`): Optional. True, if the user is allowed to send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. True, if the user is allowed to send
            audios, documents, photos, videos, video notes and voice notes, implies
            :attr:`can_send_messages`.
        can_send_polls (:obj:`bool`): Optional. True, if the user is allowed to send polls, implies
            :attr:`can_send_messages`.
        can_send_other_messages (:obj:`bool`): Optional. True, if the user is allowed to send
            animations, games, stickers and use inline bots, implies
            :attr:`can_send_media_messages`.
        can_add_web_page_previews (:obj:`bool`): Optional. True, if the user is allowed to add web
            page previews to their messages, implies :attr:`can_send_media_messages`.
        can_change_info (:obj:`bool`): Optional. True, if the user is allowed to change the chat
            title, photo and other settings. Ignored in public supergroups.
        can_invite_users (:obj:`bool`): Optional. True, if the user is allowed to invite new users
            to the chat.
        can_pin_messages (:obj:`bool`): Optional. True, if the user is allowed to pin messages.
            Ignored in public supergroups.

    Args:
        can_send_messages (:obj:`bool`, optional): True, if the user is allowed to send text
            messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): True, if the user is allowed to send
            audios, documents, photos, videos, video notes and voice notes, implies
            :attr:`can_send_messages`.
        can_send_polls (:obj:`bool`, optional): True, if the user is allowed to send polls, implies
            :attr:`can_send_messages`.
        can_send_other_messages (:obj:`bool`, optional): True, if the user is allowed to send
            animations, games, stickers and use inline bots, implies
            :attr:`can_send_media_messages`.
        can_add_web_page_previews (:obj:`bool`, optional): True, if the user is allowed to add web
            page previews to their messages, implies :attr:`can_send_media_messages`.
        can_change_info (:obj:`bool`, optional): True, if the user is allowed to change the chat
            title, photo and other settings. Ignored in public supergroups.
        can_invite_users (:obj:`bool`, optional): True, if the user is allowed to invite new users
            to the chat.
        can_pin_messages (:obj:`bool`, optional): True, if the user is allowed to pin messages.
            Ignored in public supergroups.

    """

    def __init__(self, can_send_messages=None, can_send_media_messages=None, can_send_polls=None,
                 can_send_other_messages=None, can_add_web_page_previews=None,
                 can_change_info=None, can_invite_users=None, can_pin_messages=None, **kwargs):
        # Required
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_send_polls = can_send_polls
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_pin_messages = can_pin_messages

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
