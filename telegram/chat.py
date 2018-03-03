#!/usr/bin/env python
# pylint: disable=C0103,W0622
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
"""This module contains an object that represents a Telegram Chat."""

from telegram import TelegramObject, ChatPhoto


class Chat(TelegramObject):
    """This object represents a chat.

    Attributes:
        id (:obj:`int`): Unique identifier for this chat.
        type (:obj:`str`): Type of chat.
        title (:obj:`str`): Optional. Title, for supergroups, channels and group chats.
        username (:obj:`str`): Optional. Username.
        first_name (:obj:`str`): Optional. First name of the other party in a private chat.
        last_name (:obj:`str`): Optional. Last name of the other party in a private chat.
        all_members_are_administrators (:obj:`bool`): Optional.
        photo (:class:`telegram.ChatPhoto`): Optional. Chat photo.
        description (:obj:`str`): Optional. Description, for supergroups and channel chats.
        invite_link (:obj:`str`): Optional. Chat invite link, for supergroups and channel chats.
        pinned_message (:class:`telegram.Message`): Optional. Pinned message, for supergroups.
            Returned only in get_chat.
        sticker_set_name (:obj:`str`): Optional. For supergroups, name of Group sticker set.
        can_set_sticker_set (:obj:`bool`): Optional. ``True``, if the bot can change group the
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
        all_members_are_administrators (:obj:`bool`, optional): True if a group has `All Members
            Are Admins` enabled.
        photo (:class:`telegram.ChatPhoto`, optional): Chat photo. Returned only in getChat.
        description (:obj:`str`, optional): Description, for supergroups and channel chats.
            Returned only in get_chat.
        invite_link (:obj:`str`, optional): Chat invite link, for supergroups and channel chats.
            Returned only in get_chat.
        pinned_message (:class:`telegram.Message`, optional): Pinned message, for supergroups.
            Returned only in get_chat.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        sticker_set_name (:obj:`str`, optional): For supergroups, name of Group sticker set.
            Returned only in get_chat.
        can_set_sticker_set (:obj:`bool`, optional): ``True``, if the bot can change group the
            sticker set. Returned only in get_chat.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    PRIVATE = 'private'
    """:obj:`str`: 'private'"""
    GROUP = 'group'
    """:obj:`str`: 'group'"""
    SUPERGROUP = 'supergroup'
    """:obj:`str`: 'supergroup'"""
    CHANNEL = 'channel'
    """:obj:`str`: 'channel'"""

    def __init__(self,
                 id,
                 type,
                 title=None,
                 username=None,
                 first_name=None,
                 last_name=None,
                 all_members_are_administrators=None,
                 bot=None,
                 photo=None,
                 description=None,
                 invite_link=None,
                 pinned_message=None,
                 sticker_set_name=None,
                 can_set_sticker_set=None,
                 **kwargs):
        # Required
        self.id = int(id)
        self.type = type
        # Optionals
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.all_members_are_administrators = all_members_are_administrators
        self.photo = photo
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set

        self.bot = bot
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data['photo'] = ChatPhoto.de_json(data.get('photo'), bot)
        from telegram import Message
        data['pinned_message'] = Message.de_json(data.get('pinned_message'), bot)

        return cls(bot=bot, **data)

    def send_action(self, *args, **kwargs):
        """Shortcut for::

            bot.send_chat_action(update.message.chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent successfully.

        """

        return self.bot.send_chat_action(self.id, *args, **kwargs)

    def leave(self, *args, **kwargs):
        """Shortcut for::

            bot.leave_chat(update.message.chat.id, *args, **kwargs)

        Returns:
            :obj:`bool` If the action was sent successfully.

        """
        return self.bot.leave_chat(self.id, *args, **kwargs)

    def get_administrators(self, *args, **kwargs):
        """Shortcut for::

            bot.get_chat_administrators(update.message.chat.id, *args, **kwargs)

        Returns:
            List[:class:`telegram.ChatMember`]: A list of administrators in a chat. An Array of
            :class:`telegram.ChatMember` objects that contains information about all
            chat administrators except other bots. If the chat is a group or a supergroup
            and no administrators were appointed, only the creator will be returned

        """
        return self.bot.get_chat_administrators(self.id, *args, **kwargs)

    def get_members_count(self, *args, **kwargs):
        """Shortcut for::

            bot.get_chat_members_count(update.message.chat.id, *args, **kwargs)

        Returns:
            :obj:`int`

        """
        return self.bot.get_chat_members_count(self.id, *args, **kwargs)

    def get_member(self, *args, **kwargs):
        """Shortcut for::

            bot.get_chat_member(update.message.chat.id, *args, **kwargs)

        Returns:
            :class:`telegram.ChatMember`

        """
        return self.bot.get_chat_member(self.id, *args, **kwargs)

    def kick_member(self, *args, **kwargs):
        """Shortcut for::

                bot.kick_chat_member(update.message.chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent succesfully.

        Note:
            This method will only work if the `All Members Are Admins` setting is off in the
            target group. Otherwise members may only be removed by the group's creator or by the
            member that added them.

        """
        return self.bot.kick_chat_member(self.id, *args, **kwargs)

    def unban_member(self, *args, **kwargs):
        """Shortcut for::

                bot.unban_chat_member(update.message.chat.id, *args, **kwargs)

        Returns:
            :obj:`bool`: If the action was sent successfully.

        """
        return self.bot.unban_chat_member(self.id, *args, **kwargs)

    def send_message(self, *args, **kwargs):
        """Shortcut for::

            bot.send_message(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(chat_id=self.id, *args, **kwargs)

    def send_photo(self, *args, **kwargs):
        """Shortcut for::

            bot.send_photo(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(chat_id=self.id, *args, **kwargs)

    def send_audio(self, *args, **kwargs):
        """Shortcut for::

            bot.send_audio(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(chat_id=self.id, *args, **kwargs)

    def send_document(self, *args, **kwargs):
        """Shortcut for::

            bot.send_document(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(chat_id=self.id, *args, **kwargs)

    def send_sticker(self, *args, **kwargs):
        """Shortcut for::

            bot.send_sticker(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(chat_id=self.id, *args, **kwargs)

    def send_video(self, *args, **kwargs):
        """Shortcut for::

            bot.send_video(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(chat_id=self.id, *args, **kwargs)

    def send_video_note(self, *args, **kwargs):
        """Shortcut for::

            bot.send_video_note(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(chat_id=self.id, *args, **kwargs)

    def send_voice(self, *args, **kwargs):
        """Shortcut for::

            bot.send_voice(Chat.chat_id, *args, **kwargs)

        Where Chat is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(chat_id=self.id, *args, **kwargs)
