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
"""This module contains an object that represents a Telegram ChatJoinRequest."""
import datetime
from typing import TYPE_CHECKING, Optional

from telegram._chat import Chat
from telegram._chatinvitelink import ChatInviteLink
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.datetime import from_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot


class ChatJoinRequest(TelegramObject):
    """This object represents a join request sent to a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`chat`, :attr:`from_user` and :attr:`date` are equal.

    Note:
        * Since Bot API 5.5, bots are allowed to contact users who sent a join request to a chat
          where the bot is an administrator with the
          :attr:`~telegram.ChatMemberAdministrator.can_invite_users` administrator right – even
          if the user never interacted with the bot before.
        * Telegram does not guarantee that :attr:`from_user.id <from_user>` coincides with the
          ``chat_id`` of the user. Please use :attr:`user_chat_id` to contact the user in
          response to their join request.

    .. versionadded:: 13.8
    .. versionchanged:: 20.1
       In Bot API 6.5 the argument :paramref:`user_chat_id` was added, which changes the position
       of the optional arguments :paramref:`bio` and :paramref:`invite_link`.

    Args:
        chat (:class:`telegram.Chat`): Chat to which the request was sent.
        from_user (:class:`telegram.User`): User that sent the join request.
        date (:class:`datetime.datetime`): Date the request was sent.
        user_chat_id (:obj:`int`): Identifier of a private chat with the user who sent the join
            request. This number may have more than 32 significant bits and some programming
            languages may have difficulty/silent defects in interpreting it. But it has at most 52
            significant bits, so a 64-bit integer or double-precision float type are safe for
            storing this identifier. The bot can use this identifier for 24 hours to send messages
            until the join request is processed, assuming no other administrator contacted the
            user.

            .. versionadded:: 20.1
        bio (:obj:`str`, optional): Bio of the user.
        invite_link (:class:`telegram.ChatInviteLink`, optional): Chat invite link that was used
            by the user to send the join request.

    Attributes:
        chat (:class:`telegram.Chat`): Chat to which the request was sent.
        from_user (:class:`telegram.User`): User that sent the join request.
        date (:class:`datetime.datetime`): Date the request was sent.
        user_chat_id (:obj:`int`): Identifier of a private chat with the user who sent the join
            request. This number may have more than 32 significant bits and some programming
            languages may have difficulty/silent defects in interpreting it. But it has at most 52
            significant bits, so a 64-bit integer or double-precision float type are safe for
            storing this identifier. The bot can use this identifier for 24 hours to send messages
            until the join request is processed, assuming no other administrator contacted the
            user.

            .. versionadded:: 20.1
        bio (:obj:`str`): Optional. Bio of the user.
        invite_link (:class:`telegram.ChatInviteLink`): Optional. Chat invite link that was used
            by the user to send the join request.

    """

    __slots__ = ("chat", "from_user", "date", "bio", "invite_link", "user_chat_id")

    def __init__(
        self,
        chat: Chat,
        from_user: User,
        date: datetime.datetime,
        user_chat_id: int,
        bio: str = None,
        invite_link: ChatInviteLink = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.chat: Chat = chat
        self.from_user: User = from_user
        self.date: datetime.datetime = date
        self.user_chat_id: int = user_chat_id

        # Optionals
        self.bio: Optional[str] = bio
        self.invite_link: Optional[ChatInviteLink] = invite_link

        self._id_attrs = (self.chat, self.from_user, self.date)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ChatJoinRequest"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["chat"] = Chat.de_json(data.get("chat"), bot)
        data["from_user"] = User.de_json(data.pop("from", None), bot)
        data["date"] = from_timestamp(data.get("date", None))
        data["invite_link"] = ChatInviteLink.de_json(data.get("invite_link"), bot)

        return super().de_json(data=data, bot=bot)

    async def approve(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            await bot.approve_chat_join_request(
                chat_id=update.effective_chat.id, user_id=update.effective_user.id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.approve_chat_join_request`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().approve_chat_join_request(
            chat_id=self.chat.id,
            user_id=self.from_user.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def decline(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            await bot.decline_chat_join_request(
                chat_id=update.effective_chat.id, user_id=update.effective_user.id, *args, **kwargs
            )

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.decline_chat_join_request`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().decline_chat_join_request(
            chat_id=self.chat.id,
            user_id=self.from_user.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
