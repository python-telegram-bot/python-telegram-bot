#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union

from telegram._chat import Chat
from telegram._chatinvitelink import ChatInviteLink
from telegram._chatmember import ChatMember
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatMemberUpdated(TelegramObject):
    """This object represents changes in the status of a chat member.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, :attr:`from_user`, :attr:`date`,
    :attr:`old_chat_member` and :attr:`new_chat_member` are equal.

    .. versionadded:: 13.4

    Note:
        In Python :keyword:`from` is a reserved word. Use :paramref:`from_user` instead.

    Examples:
        :any:`Chat Member Bot <examples.chatmemberbot>`

    Args:
        chat (:class:`telegram.Chat`): Chat the user belongs to.
        from_user (:class:`telegram.User`): Performer of the action, which resulted in the change.
        date (:class:`datetime.datetime`): Date the change was done in Unix time. Converted to
            :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        old_chat_member (:class:`telegram.ChatMember`): Previous information about the chat member.
        new_chat_member (:class:`telegram.ChatMember`): New information about the chat member.
        invite_link (:class:`telegram.ChatInviteLink`, optional): Chat invite link, which was used
            by the user to join the chat. For joining by invite link events only.
        via_chat_folder_invite_link (:obj:`bool`, optional): :obj:`True`, if the user joined the
            chat via a chat folder invite link

            .. versionadded:: 20.3

    Attributes:
        chat (:class:`telegram.Chat`): Chat the user belongs to.
        from_user (:class:`telegram.User`): Performer of the action, which resulted in the change.
        date (:class:`datetime.datetime`): Date the change was done in Unix time. Converted to
            :class:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        old_chat_member (:class:`telegram.ChatMember`): Previous information about the chat member.
        new_chat_member (:class:`telegram.ChatMember`): New information about the chat member.
        invite_link (:class:`telegram.ChatInviteLink`): Optional. Chat invite link, which was used
            by the user to join the chat. For joining by invite link events only.
        via_chat_folder_invite_link (:obj:`bool`): Optional. :obj:`True`, if the user joined the
            chat via a chat folder invite link

            .. versionadded:: 20.3

    """

    __slots__ = (
        "chat",
        "date",
        "from_user",
        "invite_link",
        "new_chat_member",
        "old_chat_member",
        "via_chat_folder_invite_link",
    )

    def __init__(
        self,
        chat: Chat,
        from_user: User,
        date: datetime.datetime,
        old_chat_member: ChatMember,
        new_chat_member: ChatMember,
        invite_link: Optional[ChatInviteLink] = None,
        via_chat_folder_invite_link: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.chat: Chat = chat
        self.from_user: User = from_user
        self.date: datetime.datetime = date
        self.old_chat_member: ChatMember = old_chat_member
        self.new_chat_member: ChatMember = new_chat_member
        self.via_chat_folder_invite_link: Optional[bool] = via_chat_folder_invite_link

        # Optionals
        self.invite_link: Optional[ChatInviteLink] = invite_link

        self._id_attrs = (
            self.chat,
            self.from_user,
            self.date,
            self.old_chat_member,
            self.new_chat_member,
        )

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ChatMemberUpdated"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["chat"] = Chat.de_json(data.get("chat"), bot)
        data["from_user"] = User.de_json(data.pop("from", None), bot)
        data["date"] = from_timestamp(data.get("date"), tzinfo=loc_tzinfo)
        data["old_chat_member"] = ChatMember.de_json(data.get("old_chat_member"), bot)
        data["new_chat_member"] = ChatMember.de_json(data.get("new_chat_member"), bot)
        data["invite_link"] = ChatInviteLink.de_json(data.get("invite_link"), bot)

        return super().de_json(data=data, bot=bot)

    def _get_attribute_difference(self, attribute: str) -> Tuple[object, object]:
        try:
            old = self.old_chat_member[attribute]
        except KeyError:
            old = None

        try:
            new = self.new_chat_member[attribute]
        except KeyError:
            new = None

        return old, new

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
            .. code:: pycon

                >>> chat_member_updated.difference()
                {'custom_title': ('old title', 'new title')}

        Note:
            To determine, if the :attr:`telegram.ChatMember.user` attribute has changed, *every*
            attribute of the user will be checked.

        .. versionadded:: 13.5

        Returns:
            Dict[:obj:`str`, Tuple[:class:`object`, :class:`object`]]: A dictionary mapping
            attribute names to tuples of the form ``(old_value, new_value)``
        """
        # we first get the names of the attributes that have changed
        # user.to_dict() is unhashable, so that needs some special casing further down
        old_dict = self.old_chat_member.to_dict()
        old_user_dict = old_dict.pop("user")
        new_dict = self.new_chat_member.to_dict()
        new_user_dict = new_dict.pop("user")

        # Generator for speed: we only need to iterate over it once
        # we can't directly use the values from old_dict ^ new_dict b/c that set is unordered
        attributes = (entry[0] for entry in set(old_dict.items()) ^ set(new_dict.items()))

        result = {attribute: self._get_attribute_difference(attribute) for attribute in attributes}
        if old_user_dict != new_user_dict:
            result["user"] = (self.old_chat_member.user, self.new_chat_member.user)

        return result  # type: ignore[return-value]
