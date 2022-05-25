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
"""This module contains an object that represents a Telegram ChatMember."""
import datetime
from typing import TYPE_CHECKING, Any, Optional, ClassVar, Dict, Type

from telegram import TelegramObject, User, constants
from telegram.utils.helpers import from_timestamp, to_timestamp
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatMember(TelegramObject):
    """Base class for Telegram ChatMember Objects.
    Currently, the following 6 types of chat members are supported:

    * :class:`telegram.ChatMemberOwner`
    * :class:`telegram.ChatMemberAdministrator`
    * :class:`telegram.ChatMemberMember`
    * :class:`telegram.ChatMemberRestricted`
    * :class:`telegram.ChatMemberLeft`
    * :class:`telegram.ChatMemberBanned`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user` and :attr:`status` are equal.

    Note:
        As of Bot API 5.3, :class:`ChatMember` is nothing but the base class for the subclasses
        listed above and is no longer returned directly by :meth:`~telegram.Bot.get_chat`.
        Therefore, most of the arguments and attributes were deprecated and you should no longer
        use :class:`ChatMember` directly.

    Args:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat. Can be
            :attr:`~telegram.ChatMember.ADMINISTRATOR`, :attr:`~telegram.ChatMember.CREATOR`,
            :attr:`~telegram.ChatMember.KICKED`, :attr:`~telegram.ChatMember.LEFT`,
            :attr:`~telegram.ChatMember.MEMBER` or :attr:`~telegram.ChatMember.RESTRICTED`.
        custom_title (:obj:`str`, optional): Owner and administrators only.
            Custom title for this user.

            .. deprecated:: 13.7

        is_anonymous (:obj:`bool`, optional): Owner and administrators only. :obj:`True`, if the
            user's presence in the chat is hidden.

            .. deprecated:: 13.7

        until_date (:class:`datetime.datetime`, optional): Restricted and kicked only. Date when
            restrictions will be lifted for this user.

            .. deprecated:: 13.7

        can_be_edited (:obj:`bool`, optional): Administrators only. :obj:`True`, if the bot is
            allowed to edit administrator privileges of that user.

            .. deprecated:: 13.7

        can_manage_chat (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can access the chat event log, chat statistics, message statistics in
            channels, see channel members, see anonymous administrators in supergroups and ignore
            slow mode. Implied by any other administrator privilege.

            .. versionadded:: 13.4
            .. deprecated:: 13.7

        can_manage_voice_chats (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can manage voice chats.

            .. versionadded:: 13.4
            .. deprecated:: 13.7

        can_change_info (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can change the chat title, photo and other settings.

            .. deprecated:: 13.7

        can_post_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can post in the channel, channels only.

            .. deprecated:: 13.7

        can_edit_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can edit messages of other users and can pin messages; channels only.

            .. deprecated:: 13.7

        can_delete_messages (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can delete messages of other users.

            .. deprecated:: 13.7

        can_invite_users (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can invite new users to the chat.

            .. deprecated:: 13.7

        can_restrict_members (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can restrict, ban or unban chat members.

            .. deprecated:: 13.7

        can_pin_messages (:obj:`bool`, optional): Administrators and restricted only. :obj:`True`,
            if the user can pin messages, groups and supergroups only.

            .. deprecated:: 13.7

        can_promote_members (:obj:`bool`, optional): Administrators only. :obj:`True`, if the
            administrator can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by administrators
            that were appointed by the user).

            .. deprecated:: 13.7

        is_member (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user is a member of
            the chat at the moment of the request.

            .. deprecated:: 13.7

        can_send_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user can
            send text messages, contacts, locations and venues.

            .. deprecated:: 13.7

        can_send_media_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user
            can send audios, documents, photos, videos, video notes and voice notes.

            .. deprecated:: 13.7

        can_send_polls (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user is
            allowed to send polls.

            .. deprecated:: 13.7

        can_send_other_messages (:obj:`bool`, optional): Restricted only. :obj:`True`, if the user
            can send animations, games, stickers and use inline bots.

            .. deprecated:: 13.7

        can_add_web_page_previews (:obj:`bool`, optional): Restricted only. :obj:`True`, if user
            may add web page previews to his messages.

            .. deprecated:: 13.7

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (:obj:`str`): The member's status in the chat.
        custom_title (:obj:`str`): Optional. Custom title for owner and administrators.

            .. deprecated:: 13.7

        is_anonymous (:obj:`bool`): Optional. :obj:`True`, if the user's presence in the chat is
            hidden.

            .. deprecated:: 13.7

        until_date (:class:`datetime.datetime`): Optional. Date when restrictions will be lifted
            for this user.

            .. deprecated:: 13.7

        can_be_edited (:obj:`bool`): Optional. If the bot is allowed to edit administrator
            privileges of that user.

            .. deprecated:: 13.7

        can_manage_chat (:obj:`bool`): Optional. If the administrator can access the chat event
            log, chat statistics, message statistics in channels, see channel members, see
            anonymous administrators in supergroups and ignore slow mode.

            .. versionadded:: 13.4
            .. deprecated:: 13.7

        can_manage_voice_chats (:obj:`bool`): Optional. if the administrator can manage
            voice chats.

            .. versionadded:: 13.4
            .. deprecated:: 13.7

        can_change_info (:obj:`bool`): Optional. If the user can change the chat title, photo and
            other settings.

            .. deprecated:: 13.7

        can_post_messages (:obj:`bool`): Optional. If the administrator can post in the channel.

            .. deprecated:: 13.7

        can_edit_messages (:obj:`bool`): Optional. If the administrator can edit messages of other
            users.

            .. deprecated:: 13.7

        can_delete_messages (:obj:`bool`): Optional. If the administrator can delete messages of
            other users.

            .. deprecated:: 13.7

        can_invite_users (:obj:`bool`): Optional. If the user can invite new users to the chat.

            .. deprecated:: 13.7

        can_restrict_members (:obj:`bool`): Optional. If the administrator can restrict, ban or
            unban chat members.

            .. deprecated:: 13.7

        can_pin_messages (:obj:`bool`): Optional. If the user can pin messages.

            .. deprecated:: 13.7

        can_promote_members (:obj:`bool`): Optional. If the administrator can add new
            administrators.

            .. deprecated:: 13.7

        is_member (:obj:`bool`): Optional. Restricted only. :obj:`True`, if the user is a member of
            the chat at the moment of the request.

            .. deprecated:: 13.7

        can_send_messages (:obj:`bool`): Optional. If the user can send text messages, contacts,
            locations and venues.

            .. deprecated:: 13.7

        can_send_media_messages (:obj:`bool`): Optional. If the user can send media messages,
            implies can_send_messages.

            .. deprecated:: 13.7

        can_send_polls (:obj:`bool`): Optional. :obj:`True`, if the user is allowed to
            send polls.

            .. deprecated:: 13.7

        can_send_other_messages (:obj:`bool`): Optional. If the user can send animations, games,
            stickers and use inline bots, implies can_send_media_messages.

            .. deprecated:: 13.7

        can_add_web_page_previews (:obj:`bool`): Optional. If user may add web page previews to his
            messages, implies can_send_media_messages

            .. deprecated:: 13.7

    """

    __slots__ = (
        'is_member',
        'can_restrict_members',
        'can_delete_messages',
        'custom_title',
        'can_be_edited',
        'can_post_messages',
        'can_send_messages',
        'can_edit_messages',
        'can_send_media_messages',
        'is_anonymous',
        'can_add_web_page_previews',
        'can_send_other_messages',
        'can_invite_users',
        'can_send_polls',
        'user',
        'can_promote_members',
        'status',
        'can_change_info',
        'can_pin_messages',
        'can_manage_chat',
        'can_manage_voice_chats',
        'can_manage_video_chats',
        'until_date',
        '_id_attrs',
    )

    ADMINISTRATOR: ClassVar[str] = constants.CHATMEMBER_ADMINISTRATOR
    """:const:`telegram.constants.CHATMEMBER_ADMINISTRATOR`"""
    CREATOR: ClassVar[str] = constants.CHATMEMBER_CREATOR
    """:const:`telegram.constants.CHATMEMBER_CREATOR`"""
    KICKED: ClassVar[str] = constants.CHATMEMBER_KICKED
    """:const:`telegram.constants.CHATMEMBER_KICKED`"""
    LEFT: ClassVar[str] = constants.CHATMEMBER_LEFT
    """:const:`telegram.constants.CHATMEMBER_LEFT`"""
    MEMBER: ClassVar[str] = constants.CHATMEMBER_MEMBER
    """:const:`telegram.constants.CHATMEMBER_MEMBER`"""
    RESTRICTED: ClassVar[str] = constants.CHATMEMBER_RESTRICTED
    """:const:`telegram.constants.CHATMEMBER_RESTRICTED`"""

    def __init__(
        self,
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
        is_anonymous: bool = None,
        can_manage_chat: bool = None,
        can_manage_voice_chats: bool = None,
        can_manage_video_chats: bool = None,
        **_kwargs: Any,
    ):
        # check before required to not waste resources if the error is raised
        if can_manage_voice_chats is not None and can_manage_video_chats is not None:
            # if they are the same it's fine...
            if can_manage_voice_chats != can_manage_video_chats:
                raise ValueError(
                    "Only supply one of `can_manage_video_chats`/`can_manage_voice_chats`,"
                    " not both."
                )

        # Required
        self.user = user
        self.status = status

        # Optionals
        self.custom_title = custom_title
        self.is_anonymous = is_anonymous
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
        self.can_manage_chat = can_manage_chat
        temp = (
            can_manage_video_chats
            if can_manage_video_chats is not None
            else can_manage_voice_chats
        )
        self.can_manage_voice_chats = temp
        self.can_manage_video_chats = temp

        self._id_attrs = (self.user, self.status)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ChatMember']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['user'] = User.de_json(data.get('user'), bot)
        data['until_date'] = from_timestamp(data.get('until_date', None))

        _class_mapping: Dict[str, Type['ChatMember']] = {
            cls.CREATOR: ChatMemberOwner,
            cls.ADMINISTRATOR: ChatMemberAdministrator,
            cls.MEMBER: ChatMemberMember,
            cls.RESTRICTED: ChatMemberRestricted,
            cls.LEFT: ChatMemberLeft,
            cls.KICKED: ChatMemberBanned,
        }

        if cls is ChatMember:
            return _class_mapping.get(data['status'], cls)(**data, bot=bot)
        return cls(**data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data['until_date'] = to_timestamp(self.until_date)

        return data


class ChatMemberOwner(ChatMember):
    """
    Represents a chat member that owns the chat
    and has all administrator privileges.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        custom_title (:obj:`str`, optional): Custom title for this user.
        is_anonymous (:obj:`bool`, optional): :obj:`True`, if the
            user's presence in the chat is hidden.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.CREATOR`.
        user (:class:`telegram.User`): Information about the user.
        custom_title (:obj:`str`): Optional. Custom title for
            this user.
        is_anonymous (:obj:`bool`): Optional. :obj:`True`, if the user's
            presence in the chat is hidden.
    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        custom_title: str = None,
        is_anonymous: bool = None,
        **_kwargs: Any,
    ):
        super().__init__(
            status=ChatMember.CREATOR,
            user=user,
            custom_title=custom_title,
            is_anonymous=is_anonymous,
        )


class ChatMemberAdministrator(ChatMember):
    """
    Represents a chat member that has some additional privileges.

    .. versionadded:: 13.7

    .. versionchanged:: 13.12
        Since Bot API 6.0, voice chat was renamed to video chat.

    Args:
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`, optional): :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        custom_title (:obj:`str`, optional): Custom title for this user.
        is_anonymous (:obj:`bool`, optional): :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`, optional): :obj:`True`, if the administrator
            can access the chat event log, chat statistics, message statistics in
            channels, see channel members, see anonymous administrators in supergroups
            and ignore slow mode. Implied by any other administrator privilege.
        can_post_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can post in the channel, channels only.
        can_edit_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; channels only.
        can_delete_messages (:obj:`bool`, optional): :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_voice_chats (:obj:`bool`, optional): :obj:`True`, if the
            administrator can manage voice chats.

            .. deprecated:: 13.12
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 13.12
        can_restrict_members (:obj:`bool`, optional): :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_promote_members (:obj:`bool`, optional): :obj:`True`, if the administrator
            can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by
            administrators that were appointed by the user).
        can_change_info (:obj:`bool`, optional): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`, optional): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.ADMINISTRATOR`.
        user (:class:`telegram.User`): Information about the user.
        can_be_edited (:obj:`bool`): Optional. :obj:`True`, if the bot
            is allowed to edit administrator privileges of that user.
        custom_title (:obj:`str`): Optional. Custom title for this user.
        is_anonymous (:obj:`bool`): Optional. :obj:`True`, if the  user's
            presence in the chat is hidden.
        can_manage_chat (:obj:`bool`): Optional. :obj:`True`, if the administrator
            can access the chat event log, chat statistics, message statistics in
            channels, see channel members, see anonymous administrators in supergroups
            and ignore slow mode. Implied by any other administrator privilege.
        can_post_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can post in the channel, channels only.
        can_edit_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can edit messages of other users and can pin
            messages; channels only.
        can_delete_messages (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can delete messages of other users.
        can_manage_voice_chats (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can manage voice chats.

            .. deprecated:: 13.12 contains the same value as :attr:`can_manage_video_chats`
                for backwards compatibility.
        can_manage_video_chats (:obj:`bool`): :obj:`True`, if the
            administrator can manage video chats.

            .. versionadded:: 13.12
        can_restrict_members (:obj:`bool`): Optional. :obj:`True`, if the
            administrator can restrict, ban or unban chat members.
        can_promote_members (:obj:`bool`): Optional. :obj:`True`, if the administrator
            can add new administrators with a subset of his own privileges or demote
            administrators that he has promoted, directly or indirectly (promoted by
            administrators that were appointed by the user).
        can_change_info (:obj:`bool`): Optional. :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): Optional. :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        can_be_edited: bool = None,
        custom_title: str = None,
        is_anonymous: bool = None,
        can_manage_chat: bool = None,
        can_post_messages: bool = None,
        can_edit_messages: bool = None,
        can_delete_messages: bool = None,
        can_manage_voice_chats: bool = None,
        can_restrict_members: bool = None,
        can_promote_members: bool = None,
        can_change_info: bool = None,
        can_invite_users: bool = None,
        can_pin_messages: bool = None,
        can_manage_video_chats: bool = None,
        **_kwargs: Any,
    ):
        super().__init__(
            status=ChatMember.ADMINISTRATOR,
            user=user,
            can_be_edited=can_be_edited,
            custom_title=custom_title,
            is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_manage_voice_chats=can_manage_voice_chats,
            can_restrict_members=can_restrict_members,
            can_promote_members=can_promote_members,
            can_change_info=can_change_info,
            can_invite_users=can_invite_users,
            can_pin_messages=can_pin_messages,
            can_manage_video_chats=can_manage_video_chats,
        )


class ChatMemberMember(ChatMember):
    """
    Represents a chat member that has no additional
    privileges or restrictions.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.MEMBER`.
        user (:class:`telegram.User`): Information about the user.

    """

    __slots__ = ()

    def __init__(self, user: User, **_kwargs: Any):
        super().__init__(status=ChatMember.MEMBER, user=user)


class ChatMemberRestricted(ChatMember):
    """
    Represents a chat member that is under certain restrictions
    in the chat. Supergroups only.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`, optional): :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`, optional): :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`, optional): :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to send text messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to send audios, documents, photos, videos, video notes and voice notes.
        can_send_polls (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`, optional): :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`, optional): :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        until_date (:class:`datetime.datetime`, optional): Date when restrictions
           will be lifted for this user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.RESTRICTED`.
        user (:class:`telegram.User`): Information about the user.
        is_member (:obj:`bool`): Optional. :obj:`True`, if the user is a
            member of the chat at the moment of the request.
        can_change_info (:obj:`bool`): Optional. :obj:`True`, if the user can change
            the chat title, photo and other settings.
        can_invite_users (:obj:`bool`): Optional. :obj:`True`, if the user can invite
            new users to the chat.
        can_pin_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to pin messages; groups and supergroups only.
        can_send_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to send text messages, contacts, locations and venues.
        can_send_media_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to send audios, documents, photos, videos, video notes and voice notes.
        can_send_polls (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to send polls.
        can_send_other_messages (:obj:`bool`): Optional. :obj:`True`, if the user is allowed
            to send animations, games, stickers and use inline bots.
        can_add_web_page_previews (:obj:`bool`): Optional. :obj:`True`, if the user is
           allowed to add web page previews to their messages.
        until_date (:class:`datetime.datetime`): Optional. Date when restrictions
           will be lifted for this user.

    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        is_member: bool = None,
        can_change_info: bool = None,
        can_invite_users: bool = None,
        can_pin_messages: bool = None,
        can_send_messages: bool = None,
        can_send_media_messages: bool = None,
        can_send_polls: bool = None,
        can_send_other_messages: bool = None,
        can_add_web_page_previews: bool = None,
        until_date: datetime.datetime = None,
        **_kwargs: Any,
    ):
        super().__init__(
            status=ChatMember.RESTRICTED,
            user=user,
            is_member=is_member,
            can_change_info=can_change_info,
            can_invite_users=can_invite_users,
            can_pin_messages=can_pin_messages,
            can_send_messages=can_send_messages,
            can_send_media_messages=can_send_media_messages,
            can_send_polls=can_send_polls,
            can_send_other_messages=can_send_other_messages,
            can_add_web_page_previews=can_add_web_page_previews,
            until_date=until_date,
        )


class ChatMemberLeft(ChatMember):
    """
    Represents a chat member that isn't currently a member of the chat,
    but may join it themselves.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.LEFT`.
        user (:class:`telegram.User`): Information about the user.
    """

    __slots__ = ()

    def __init__(self, user: User, **_kwargs: Any):
        super().__init__(status=ChatMember.LEFT, user=user)


class ChatMemberBanned(ChatMember):
    """
    Represents a chat member that was banned in the chat and
    can't return to the chat or view chat messages.

    .. versionadded:: 13.7

    Args:
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`, optional): Date when restrictions
           will be lifted for this user.

    Attributes:
        status (:obj:`str`): The member's status in the chat,
            always :attr:`telegram.ChatMember.KICKED`.
        user (:class:`telegram.User`): Information about the user.
        until_date (:class:`datetime.datetime`): Optional. Date when restrictions
           will be lifted for this user.

    """

    __slots__ = ()

    def __init__(
        self,
        user: User,
        until_date: datetime.datetime = None,
        **_kwargs: Any,
    ):
        super().__init__(
            status=ChatMember.KICKED,
            user=user,
            until_date=until_date,
        )
