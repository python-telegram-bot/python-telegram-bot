#!/usr/bin/env python
# pylint: disable=C0103,W0622
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
"""This module contains an object that represents a Telegram Chat."""

from telegram import TelegramObject, ChatPhoto
from .chatpermissions import ChatPermissions

from telegram.utils.types import JSONDict
from typing import Any, Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot, Message, ChatMember


class Chat(TelegramObject):
    """This object represents a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Attributes:
        id (:obj:`int`): Unique identifier for this chat.
        type (:obj:`str`): Type of chat.
        title (:obj:`str`): Optional. Title, for supergroups, channels and group chats.
        username (:obj:`str`): Optional. Username.
        first_name (:obj:`str`): Optional. First name of the other party in a private chat.
        last_name (:obj:`str`): Optional. Last name of the other party in a private chat.
        photo (:class:`telegram.ChatPhoto`): Optional. Chat photo.
        description (:obj:`str`): Optional. Description, for groups, supergroups and channel chats.
        invite_link (:obj:`str`): Optional. Chat invite link, for supergroups and channel chats.
        pinned_message (:class:`telegram.Message`): Optional. Pinned message, for supergroups.
            Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`): Optional. For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user. Returned only in
            :meth:`telegram.Bot.get_chat`.
        sticker_set_name (:obj:`str`): Optional. For supergroups, name of Group sticker set.
        can_set_sticker_set (:obj:`bool`): Optional. :obj:`True`, if the bot can change group the
            sticker set.

    Args:
        id (:obj:`int`): Unique identifier for this chat. This number may be greater than 32 bits
            and some programming languages may have difficulty/silent defects in interpreting it.
            But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
            type are safe for storing this identifier.
        type (:obj:`str`): Type of chat, can be either 'private', 'group', 'supergroup' or
            'channel'.
        title (:obj:`str`, optional): Title, for supergroups, channels and group chats.
        username(:obj:`str`, optional): Username, for private chats, supergroups and channels if
            available.
        first_name(:obj:`str`, optional): First name of the other party in a private chat.
        last_name(:obj:`str`, optional): Last name of the other party in a private chat.
        photo (:class:`telegram.ChatPhoto`, optional): Chat photo.
            Returned only in :meth:`telegram.Bot.get_chat`.
        description (:obj:`str`, optional): Description, for groups, supergroups and channel chats.
            Returned only in :meth:`telegram.Bot.get_chat`.
        invite_link (:obj:`str`, optional): Chat invite link, for groups, supergroups and channel
            chats. Each administrator in a chat generates their own invite links, so the bot must
            first generate the link using ``export_chat_invite_link()``. Returned only
            in :meth:`telegram.Bot.get_chat`.
        pinned_message (:class:`telegram.Message`, optional): Pinned message, for groups,
            supergroups and channels. Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`, optional): For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user.
            Returned only in :meth:`telegram.Bot.get_chat`.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        sticker_set_name (:obj:`str`, optional): For supergroups, name of group sticker set.
            Returned only in :meth:`telegram.Bot.get_chat`.
        can_set_sticker_set (:obj:`bool`, optional): :obj:`True`, if the bot can change group the
            sticker set. Returned only in :meth:`telegram.Bot.get_chat`.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    PRIVATE: str = 'private'
    """:obj:`str`: 'private'"""
    GROUP: str = 'group'
    """:obj:`str`: 'group'"""
    SUPERGROUP: str = 'supergroup'
    """:obj:`str`: 'supergroup'"""
    CHANNEL: str = 'channel'
    """:obj:`str`: 'channel'"""

    def __init__(self,
                 id: int,
                 type: str,
                 title: str = None,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 bot: 'Bot' = None,
                 photo: ChatPhoto = None,
                 description: str = None,
                 invite_link: str = None,
                 pinned_message: 'Message' = None,
                 permissions: ChatPermissions = None,
                 sticker_set_name: str = None,
                 can_set_sticker_set: bool = None,
                 slow_mode_delay: int = None,
                 **kwargs: Any):
        # Required
        self.id = int(id)
        self.type = type
        # Optionals
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        # TODO: Remove (also from tests), when Telegram drops this completely
        self.all_members_are_administrators = kwargs.get('all_members_are_administrators')
        self.photo = photo
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.permissions = permissions
        self.slow_mode_delay = slow_mode_delay
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set

        self.bot = bot
        self._id_attrs = (self.id,)

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If the chat has a :attr:`username`, returns a t.me
        link of the chat."""
        if self.username:
            return "https://t.me/{}".format(self.username)
        return None

    @classmethod
    def de_json(cls, data: JSONDict, bot: 'Bot') -> Optional['Chat']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['photo'] = ChatPhoto.de_json(data.get('photo'), bot)
        from telegram import Message
        data['pinned_message'] = Message.de_json(data.get('pinned_message'), bot)
        data['permissions'] = ChatPermissions.de_json(data.get('permissions'), bot)

        return cls(bot=bot, **data)

    def leave(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

            bot.leave_chat(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`bool` If the action was sent successfully.

        """
        return self.bot.leave_chat(self.id, *args, **kwargs)

    def get_administrators(self, *args: Any, **kwargs: Any) -> List['ChatMember']:
        """Shortcut for::

            bot.get_chat_administrators(update.effective_chat.id, *args, **kwargs)

        Returns:
            List[:class:`telegram.ChatMember`]: A list of administrators in a chat. An Array of
            :class:`telegram.ChatMember` objects that contains information about all
            chat administrators except other bots. If the chat is a group or a supergroup
            and no administrators were appointed, only the creator will be returned.

        """
        return self.bot.get_chat_administrators(self.id, *args, **kwargs)

    def get_members_count(self, *args: Any, **kwargs: Any) -> int:
        """Shortcut for::

            bot.get_chat_members_count(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`int`

        """
        return self.bot.get_chat_members_count(self.id, *args, **kwargs)

    def get_member(self, *args: Any, **kwargs: Any) -> 'ChatMember':
        """Shortcut for::

            bot.get_chat_member(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.ChatMember`

        """
        return self.bot.get_chat_member(self.id, *args, **kwargs)

    def kick_member(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

                bot.kick_chat_member(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent successfully.

        Note:
            This method will only work if the `All Members Are Admins` setting is off in the
            target group. Otherwise members may only be removed by the group's creator or by the
            member that added them.

        """
        return self.bot.kick_chat_member(self.id, *args, **kwargs)

    def unban_member(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

                bot.unban_chat_member(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent successfully.

        """
        return self.bot.unban_chat_member(self.id, *args, **kwargs)

    def set_permissions(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

                bot.set_chat_permissions(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent successfully.

    """
        return self.bot.set_chat_permissions(self.id, *args, **kwargs)

    def set_administrator_custom_title(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

                bot.set_chat_administrator_custom_title(update.effective_chat.id, *args, **kwargs)

        Returns:
        :obj:`bool`: If the action was sent successfully.

    """
        return self.bot.set_chat_administrator_custom_title(self.id, *args, **kwargs)

    def send_message(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(self.id, *args, **kwargs)

    def send_media_group(self, *args: Any, **kwargs: Any) -> List['Message']:
        """Shortcut for::

            bot.send_media_group(update.effective_chat.id, *args, **kwargs)

        Returns:
            List[:class:`telegram.Message`:] On success, instance representing the message posted.

        """
        return self.bot.send_media_group(self.id, *args, **kwargs)

    def send_chat_action(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

            bot.send_chat_action(update.effective_chat.id, *args, **kwargs)

        Returns:
            :obj:`True`: On success.

        """
        return self.bot.send_chat_action(self.id, *args, **kwargs)

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    def send_photo(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_photo(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(self.id, *args, **kwargs)

    def send_contact(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_contact(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_contact(self.id, *args, **kwargs)

    def send_audio(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_audio(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(self.id, *args, **kwargs)

    def send_document(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_document(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(self.id, *args, **kwargs)

    def send_dice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_dice(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_dice(self.id, *args, **kwargs)

    def send_game(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_game(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_game(self.id, *args, **kwargs)

    def send_invoice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_invoice(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_invoice(self.id, *args, **kwargs)

    def send_location(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_location(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_location(self.id, *args, **kwargs)

    def send_animation(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_animation(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_animation(self.id, *args, **kwargs)

    def send_sticker(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_sticker(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(self.id, *args, **kwargs)

    def send_venue(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_venue(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_venue(self.id, *args, **kwargs)

    def send_video(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_video(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(self.id, *args, **kwargs)

    def send_video_note(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_video_note(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(self.id, *args, **kwargs)

    def send_voice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_voice(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(self.id, *args, **kwargs)

    def send_poll(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_poll(update.effective_chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_poll(self.id, *args, **kwargs)
