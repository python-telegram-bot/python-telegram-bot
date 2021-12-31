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
"""This module contains an object that represents a Telegram ChatMemberUpdated."""
import datetime
from typing import TYPE_CHECKING, Any, Optional, Dict, Tuple, Union

from telegram import TelegramObject, User, Chat, ChatMember, ChatInviteLink
from telegram.utils.helpers import from_timestamp, to_timestamp
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatMemberUpdated(TelegramObject):
    """This object represents changes in the status of a chat member.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, :attr:`from_user`, :attr:`date`,
    :attr:`old_chat_member` and :attr:`new_chat_member` are equal.

    .. versionadded:: 13.4

    Note:
        In Python ``from`` is a reserved word, use ``from_user`` instead.

    Args:
        chat (:class:`telegram.Chat`): Chat the user belongs to.
        from_user (:class:`telegram.User`): Performer of the action, which resulted in the change.
        date (:class:`datetime.datetime`): Date the change was done in Unix time. Converted to
            :class:`datetime.datetime`.
        old_chat_member (:class:`telegram.ChatMember`): Previous information about the chat member.
        new_chat_member (:class:`telegram.ChatMember`): New information about the chat member.
        invite_link (:class:`telegram.ChatInviteLink`, optional): Chat invite link, which was used
            by the user to join the chat. For joining by invite link events only.

    Attributes:
        chat (:class:`telegram.Chat`): Chat the user belongs to.
        from_user (:class:`telegram.User`): Performer of the action, which resulted in the change.
        date (:class:`datetime.datetime`): Date the change was done in Unix time. Converted to
            :class:`datetime.datetime`.
        old_chat_member (:class:`telegram.ChatMember`): Previous information about the chat member.
        new_chat_member (:class:`telegram.ChatMember`): New information about the chat member.
        invite_link (:class:`telegram.ChatInviteLink`): Optional. Chat invite link, which was used
            by the user to join the chat.

    """

    __slots__ = (
        'chat',
        'from_user',
        'date',
        'old_chat_member',
        'new_chat_member',
        'invite_link',
        '_id_attrs',
    )

    def __init__(
        self,
        chat: Chat,
        from_user: User,
        date: datetime.datetime,
        old_chat_member: ChatMember,
        new_chat_member: ChatMember,
        invite_link: ChatInviteLink = None,
        **_kwargs: Any,
    ):
        # Required
        self.chat = chat
        self.from_user = from_user
        self.date = date
        self.old_chat_member = old_chat_member
        self.new_chat_member = new_chat_member

        # Optionals
        self.invite_link = invite_link

        self._id_attrs = (
            self.chat,
            self.from_user,
            self.date,
            self.old_chat_member,
            self.new_chat_member,
        )

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ChatMemberUpdated']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['chat'] = Chat.de_json(data.get('chat'), bot)
        data['from_user'] = User.de_json(data.get('from'), bot)
        data['date'] = from_timestamp(data.get('date'))
        data['old_chat_member'] = ChatMember.de_json(data.get('old_chat_member'), bot)
        data['new_chat_member'] = ChatMember.de_json(data.get('new_chat_member'), bot)
        data['invite_link'] = ChatInviteLink.de_json(data.get('invite_link'), bot)

        return cls(**data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        # Required
        data['date'] = to_timestamp(self.date)

        return data

    def difference(
        self,
    ) -> Dict[
        str,
        Tuple[
            Union[str, bool, datetime.datetime, User], Union[str, bool, datetime.datetime, User]
        ],
    ]:
        """Computes the difference between :attr:`old_chat_member` and :attr:`new_chat_member`.

        Example:
            .. code:: python

                >>> chat_member_updated.difference()
                {'custom_title': ('old title', 'new title')}

        Note:
            To determine, if the :attr:`telegram.ChatMember.user` attribute has changed, *every*
            attribute of the user will be checked.

        .. versionadded:: 13.5

        Returns:
            Dict[:obj:`str`, Tuple[:obj:`obj`, :obj:`obj`]]: A dictionary mapping attribute names
            to tuples of the form ``(old_value, new_value)``
        """
        # we first get the names of the attributes that have changed
        # user.to_dict() is unhashable, so that needs some special casing further down
        old_dict = self.old_chat_member.to_dict()
        old_user_dict = old_dict.pop('user')
        new_dict = self.new_chat_member.to_dict()
        new_user_dict = new_dict.pop('user')

        # Generator for speed: we only need to iterate over it once
        # we can't directly use the values from old_dict ^ new_dict b/c that set is unordered
        attributes = (entry[0] for entry in set(old_dict.items()) ^ set(new_dict.items()))

        result = {
            attribute: (self.old_chat_member[attribute], self.new_chat_member[attribute])
            for attribute in attributes
        }
        if old_user_dict != new_user_dict:
            result['user'] = (self.old_chat_member.user, self.new_chat_member.user)

        return result  # type: ignore[return-value]
