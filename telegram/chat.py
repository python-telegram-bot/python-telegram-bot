#!/usr/bin/env python
# pylint: disable=W0622
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, ClassVar, Union, Tuple, Any

from telegram import ChatPhoto, TelegramObject, constants
from telegram.utils.types import JSONDict, FileInput, ODVInput, DVInput
from telegram.utils.deprecate import TelegramDeprecationWarning

from .chatpermissions import ChatPermissions
from .chatlocation import ChatLocation
from .utils.helpers import DEFAULT_NONE, DEFAULT_20

if TYPE_CHECKING:
    from telegram import (
        Bot,
        ChatMember,
        ChatInviteLink,
        Message,
        MessageId,
        ReplyMarkup,
        Contact,
        InlineKeyboardMarkup,
        Location,
        Venue,
        MessageEntity,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        PhotoSize,
        Audio,
        Document,
        Animation,
        LabeledPrice,
        Sticker,
        Video,
        VideoNote,
        Voice,
    )


class Chat(TelegramObject):
    """This object represents a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

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
        bio (:obj:`str`, optional): Bio of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.
        description (:obj:`str`, optional): Description, for groups, supergroups and channel chats.
            Returned only in :meth:`telegram.Bot.get_chat`.
        invite_link (:obj:`str`, optional): Primary invite link, for groups, supergroups and
            channel. Returned only in :meth:`telegram.Bot.get_chat`.
        pinned_message (:class:`telegram.Message`, optional): The most recent pinned message
            (by sending date). Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`, optional): For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user.
            Returned only in :meth:`telegram.Bot.get_chat`.
        message_auto_delete_time (:obj:`int`, optional): The time after which all messages sent to
            the chat will be automatically deleted; in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.4
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        sticker_set_name (:obj:`str`, optional): For supergroups, name of group sticker set.
            Returned only in :meth:`telegram.Bot.get_chat`.
        can_set_sticker_set (:obj:`bool`, optional): :obj:`True`, if the bot can change group the
            sticker set. Returned only in :meth:`telegram.Bot.get_chat`.
        linked_chat_id (:obj:`int`, optional): Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats. Returned only in :meth:`telegram.Bot.get_chat`.
        location (:class:`telegram.ChatLocation`, optional): For supergroups, the location to which
            the supergroup is connected. Returned only in :meth:`telegram.Bot.get_chat`.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        id (:obj:`int`): Unique identifier for this chat.
        type (:obj:`str`): Type of chat.
        title (:obj:`str`): Optional. Title, for supergroups, channels and group chats.
        username (:obj:`str`): Optional. Username.
        first_name (:obj:`str`): Optional. First name of the other party in a private chat.
        last_name (:obj:`str`): Optional. Last name of the other party in a private chat.
        photo (:class:`telegram.ChatPhoto`): Optional. Chat photo.
        bio (:obj:`str`): Optional. Bio of the other party in a private chat. Returned only in
            :meth:`telegram.Bot.get_chat`.
        description (:obj:`str`): Optional. Description, for groups, supergroups and channel chats.
        invite_link (:obj:`str`): Optional. Primary invite link, for groups, supergroups and
            channel. Returned only in :meth:`telegram.Bot.get_chat`.
        pinned_message (:class:`telegram.Message`): Optional. The most recent pinned message
            (by sending date). Returned only in :meth:`telegram.Bot.get_chat`.
        permissions (:class:`telegram.ChatPermissions`): Optional. Default chat member permissions,
            for groups and supergroups. Returned only in :meth:`telegram.Bot.get_chat`.
        slow_mode_delay (:obj:`int`): Optional. For supergroups, the minimum allowed delay between
            consecutive messages sent by each unprivileged user. Returned only in
            :meth:`telegram.Bot.get_chat`.
        message_auto_delete_time (:obj:`int`): Optional. The time after which all messages sent to
            the chat will be automatically deleted; in seconds. Returned only in
            :meth:`telegram.Bot.get_chat`.

            .. versionadded:: 13.4
        sticker_set_name (:obj:`str`): Optional. For supergroups, name of Group sticker set.
        can_set_sticker_set (:obj:`bool`): Optional. :obj:`True`, if the bot can change group the
            sticker set.
        linked_chat_id (:obj:`int`): Optional. Unique identifier for the linked chat, i.e. the
            discussion group identifier for a channel and vice versa; for supergroups and channel
            chats. Returned only in :meth:`telegram.Bot.get_chat`.
        location (:class:`telegram.ChatLocation`): Optional. For supergroups, the location to which
            the supergroup is connected. Returned only in :meth:`telegram.Bot.get_chat`.

    """

    __slots__ = (
        'bio',
        'id',
        'type',
        'last_name',
        'bot',
        'sticker_set_name',
        'slow_mode_delay',
        'location',
        'first_name',
        'permissions',
        'invite_link',
        'pinned_message',
        'description',
        'can_set_sticker_set',
        'username',
        'title',
        'photo',
        'linked_chat_id',
        'all_members_are_administrators',
        'message_auto_delete_time',
        '_id_attrs',
    )

    SENDER: ClassVar[str] = constants.CHAT_SENDER
    """:const:`telegram.constants.CHAT_SENDER`

    .. versionadded:: 13.5
    """
    PRIVATE: ClassVar[str] = constants.CHAT_PRIVATE
    """:const:`telegram.constants.CHAT_PRIVATE`"""
    GROUP: ClassVar[str] = constants.CHAT_GROUP
    """:const:`telegram.constants.CHAT_GROUP`"""
    SUPERGROUP: ClassVar[str] = constants.CHAT_SUPERGROUP
    """:const:`telegram.constants.CHAT_SUPERGROUP`"""
    CHANNEL: ClassVar[str] = constants.CHAT_CHANNEL
    """:const:`telegram.constants.CHAT_CHANNEL`"""

    def __init__(
        self,
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
        bio: str = None,
        linked_chat_id: int = None,
        location: ChatLocation = None,
        message_auto_delete_time: int = None,
        **_kwargs: Any,
    ):
        # Required
        self.id = int(id)  # pylint: disable=C0103
        self.type = type
        # Optionals
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        # TODO: Remove (also from tests), when Telegram drops this completely
        self.all_members_are_administrators = _kwargs.get('all_members_are_administrators')
        self.photo = photo
        self.bio = bio
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.permissions = permissions
        self.slow_mode_delay = slow_mode_delay
        self.message_auto_delete_time = (
            int(message_auto_delete_time) if message_auto_delete_time is not None else None
        )
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set
        self.linked_chat_id = linked_chat_id
        self.location = location

        self.bot = bot
        self._id_attrs = (self.id,)

    @property
    def full_name(self) -> Optional[str]:
        """
        :obj:`str`: Convenience property. If :attr:`first_name` is not :obj:`None` gives,
        :attr:`first_name` followed by (if available) :attr:`last_name`.

        Note:
            :attr:`full_name` will always be :obj:`None`, if the chat is a (super)group or
            channel.

        .. versionadded:: 13.2
        """
        if not self.first_name:
            return None
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If the chat has a :attr:`username`, returns a t.me
        link of the chat.
        """
        if self.username:
            return f"https://t.me/{self.username}"
        return None

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['Chat']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['photo'] = ChatPhoto.de_json(data.get('photo'), bot)
        from telegram import Message  # pylint: disable=C0415

        data['pinned_message'] = Message.de_json(data.get('pinned_message'), bot)
        data['permissions'] = ChatPermissions.de_json(data.get('permissions'), bot)
        data['location'] = ChatLocation.de_json(data.get('location'), bot)

        return cls(bot=bot, **data)

    def leave(self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None) -> bool:
        """Shortcut for::

            bot.leave_chat(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.leave_chat`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.leave_chat(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_administrators(
        self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None
    ) -> List['ChatMember']:
        """Shortcut for::

            bot.get_chat_administrators(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_administrators`.

        Returns:
            List[:class:`telegram.ChatMember`]: A list of administrators in a chat. An Array of
            :class:`telegram.ChatMember` objects that contains information about all
            chat administrators except other bots. If the chat is a group or a supergroup
            and no administrators were appointed, only the creator will be returned.

        """
        return self.bot.get_chat_administrators(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_members_count(
        self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None
    ) -> int:
        """
        Deprecated, use :func:`~telegram.Chat.get_member_count` instead.

        .. deprecated:: 13.7
        """
        warnings.warn(
            '`Chat.get_members_count` is deprecated. Use `Chat.get_member_count` instead.',
            TelegramDeprecationWarning,
            stacklevel=2,
        )

        return self.get_member_count(
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_member_count(
        self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None
    ) -> int:
        """Shortcut for::

            bot.get_chat_member_count(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_member_count`.

        Returns:
            :obj:`int`
        """
        return self.bot.get_chat_member_count(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_member(
        self,
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'ChatMember':
        """Shortcut for::

            bot.get_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.get_chat_member`.

        Returns:
            :class:`telegram.ChatMember`

        """
        return self.bot.get_chat_member(
            chat_id=self.id,
            user_id=user_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def kick_member(
        self,
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        until_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        revoke_messages: bool = None,
    ) -> bool:
        """
        Deprecated, use :func:`~telegram.Chat.ban_member` instead.

        .. deprecated:: 13.7
        """
        warnings.warn(
            '`Chat.kick_member` is deprecated. Use `Chat.ban_member` instead.',
            TelegramDeprecationWarning,
            stacklevel=2,
        )

        return self.ban_member(
            user_id=user_id,
            timeout=timeout,
            until_date=until_date,
            api_kwargs=api_kwargs,
            revoke_messages=revoke_messages,
        )

    def ban_member(
        self,
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        until_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        revoke_messages: bool = None,
    ) -> bool:
        """Shortcut for::

            bot.ban_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.ban_chat_member`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return self.bot.ban_chat_member(
            chat_id=self.id,
            user_id=user_id,
            timeout=timeout,
            until_date=until_date,
            api_kwargs=api_kwargs,
            revoke_messages=revoke_messages,
        )

    def unban_member(
        self,
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        only_if_banned: bool = None,
    ) -> bool:
        """Shortcut for::

            bot.unban_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.unban_chat_member`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unban_chat_member(
            chat_id=self.id,
            user_id=user_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            only_if_banned=only_if_banned,
        )

    def promote_member(
        self,
        user_id: Union[str, int],
        can_change_info: bool = None,
        can_post_messages: bool = None,
        can_edit_messages: bool = None,
        can_delete_messages: bool = None,
        can_invite_users: bool = None,
        can_restrict_members: bool = None,
        can_pin_messages: bool = None,
        can_promote_members: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        is_anonymous: bool = None,
        can_manage_chat: bool = None,
        can_manage_voice_chats: bool = None,
    ) -> bool:
        """Shortcut for::

            bot.promote_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.promote_chat_member`.

        .. versionadded:: 13.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.promote_chat_member(
            chat_id=self.id,
            user_id=user_id,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
            timeout=timeout,
            api_kwargs=api_kwargs,
            is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_manage_voice_chats=can_manage_voice_chats,
        )

    def restrict_member(
        self,
        user_id: Union[str, int],
        permissions: ChatPermissions,
        until_date: Union[int, datetime] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.restrict_chat_member(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.restrict_chat_member`.

        .. versionadded:: 13.2

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.restrict_chat_member(
            chat_id=self.id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_date,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def set_permissions(
        self,
        permissions: ChatPermissions,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.set_chat_permissions(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_permissions`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.set_chat_permissions(
            chat_id=self.id,
            permissions=permissions,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def set_administrator_custom_title(
        self,
        user_id: Union[int, str],
        custom_title: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.set_chat_administrator_custom_title(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_administrator_custom_title`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.set_chat_administrator_custom_title(
            chat_id=self.id,
            user_id=user_id,
            custom_title=custom_title,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def pin_message(
        self,
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.pin_chat_message(chat_id=update.effective_chat.id,
                                  *args,
                                  **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.pin_chat_message(
            chat_id=self.id,
            message_id=message_id,
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def unpin_message(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        message_id: int = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_chat_message(chat_id=update.effective_chat.id,
                                    *args,
                                    **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unpin_chat_message(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            message_id=message_id,
        )

    def unpin_all_messages(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_all_chat_messages(chat_id=update.effective_chat.id,
                                         *args,
                                         **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_chat_messages`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unpin_all_chat_messages(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def send_message(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(
            chat_id=self.id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def send_media_group(
        self,
        media: List[
            Union['InputMediaAudio', 'InputMediaDocument', 'InputMediaPhoto', 'InputMediaVideo']
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> List['Message']:
        """Shortcut for::

            bot.send_media_group(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Returns:
            List[:class:`telegram.Message`]: On success, instance representing the message posted.

        """
        return self.bot.send_media_group(
            chat_id=self.id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_chat_action(
        self,
        action: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.send_chat_action(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.send_chat_action(
            chat_id=self.id,
            action=action,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    def send_photo(
        self,
        photo: Union[FileInput, 'PhotoSize'],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_photo(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(
            chat_id=self.id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_contact(
        self,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        contact: 'Contact' = None,
        vcard: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_contact(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_contact(
            chat_id=self.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_audio(
        self,
        audio: Union[FileInput, 'Audio'],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_audio(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(
            chat_id=self.id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_document(
        self,
        document: Union[FileInput, 'Document'],
        filename: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_document(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(
            chat_id=self.id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
        )

    def send_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        emoji: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_dice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_dice(
            chat_id=self.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_game(
        self,
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_game(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_game(
            chat_id=self.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List['LabeledPrice'],
        start_parameter: str = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        is_flexible: bool = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        provider_data: Union[str, object] = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_invoice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :attr:`start_parameter` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :attr:`start_parameter` is optional.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_invoice(
            chat_id=self.id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            start_parameter=start_parameter,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
        )

    def send_location(
        self,
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        location: 'Location' = None,
        live_period: int = None,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_location(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_location(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_animation(
        self,
        animation: Union[FileInput, 'Animation'],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_animation(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_animation(
            chat_id=self.id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_sticker(
        self,
        sticker: Union[FileInput, 'Sticker'],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_sticker(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(
            chat_id=self.id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_venue(
        self,
        latitude: float = None,
        longitude: float = None,
        title: str = None,
        address: str = None,
        foursquare_id: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        venue: 'Venue' = None,
        foursquare_type: str = None,
        api_kwargs: JSONDict = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_venue(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_venue(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_video(
        self,
        video: Union[FileInput, 'Video'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_video(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(
            chat_id=self.id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_video_note(
        self,
        video_note: Union[FileInput, 'VideoNote'],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_video_note(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(
            chat_id=self.id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
        )

    def send_voice(
        self,
        voice: Union[FileInput, 'Voice'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_voice(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(
            chat_id=self.id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_poll(
        self,
        question: str,
        options: List[str],
        is_anonymous: bool = True,
        # We use constant.POLL_REGULAR instead of Poll.REGULAR here to avoid circular imports
        type: str = constants.POLL_REGULAR,  # pylint: disable=W0622
        allows_multiple_answers: bool = False,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_poll(update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_poll(
            chat_id=self.id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            type=type,  # pylint=pylint,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
        )

    def send_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.copy_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def copy_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(from_chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.copy_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def export_invite_link(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> str:
        """Shortcut for::

            bot.export_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.export_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :obj:`str`: New invite link on success.

        """
        return self.bot.export_chat_invite_link(
            chat_id=self.id, timeout=timeout, api_kwargs=api_kwargs
        )

    def create_invite_link(
        self,
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'ChatInviteLink':
        """Shortcut for::

            bot.create_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.create_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return self.bot.create_chat_invite_link(
            chat_id=self.id,
            expire_date=expire_date,
            member_limit=member_limit,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def edit_invite_link(
        self,
        invite_link: str,
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'ChatInviteLink':
        """Shortcut for::

            bot.edit_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.edit_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return self.bot.edit_chat_invite_link(
            chat_id=self.id,
            invite_link=invite_link,
            expire_date=expire_date,
            member_limit=member_limit,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def revoke_invite_link(
        self,
        invite_link: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'ChatInviteLink':
        """Shortcut for::

            bot.revoke_chat_invite_link(chat_id=update.effective_chat.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.revoke_chat_invite_link`.

        .. versionadded:: 13.4

        Returns:
            :class:`telegram.ChatInviteLink`

        """
        return self.bot.revoke_chat_invite_link(
            chat_id=self.id, invite_link=invite_link, timeout=timeout, api_kwargs=api_kwargs
        )
