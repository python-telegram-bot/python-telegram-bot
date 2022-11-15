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
"""This module contains an object that represents an invite link for a chat."""
import datetime
from typing import TYPE_CHECKING, Optional

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.datetime import from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatInviteLink(TelegramObject):
    """This object represents an invite link for a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`invite_link`, :attr:`creator`, :attr:`creates_join_request`,
    :attr:`is_primary` and :attr:`is_revoked` are equal.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0

       * The argument & attribute :attr:`creates_join_request` is now required to comply with the
         Bot API.
       * Comparing objects of this class now also takes :attr:`creates_join_request` into account.

    Args:
        invite_link (:obj:`str`): The invite link.
        creator (:class:`telegram.User`): Creator of the link.
        creates_join_request (:obj:`bool`): :obj:`True`, if users joining the chat via
            the link need to be approved by chat administrators.

            .. versionadded:: 13.8
        is_primary (:obj:`bool`): :obj:`True`, if the link is primary.
        is_revoked (:obj:`bool`): :obj:`True`, if the link is revoked.
        expire_date (:class:`datetime.datetime`, optional): Date when the link will expire or
            has been expired.
        member_limit (:obj:`int`, optional): Maximum number of users that can be members of the
            chat simultaneously after joining the chat via this invite link;
            1-:tg-const:`telegram.constants.ChatInviteLinkLimit.MEMBER_LIMIT`.
        name (:obj:`str`, optional): Invite link name.
            0-:tg-const:`telegram.constants.ChatInviteLinkLimit.NAME_LENGTH` characters.

            .. versionadded:: 13.8
        pending_join_request_count (:obj:`int`, optional): Number of pending join requests
            created using this link.

            .. versionadded:: 13.8
    Attributes:
        invite_link (:obj:`str`): The invite link. If the link was created by another chat
            administrator, then the second part of the link will be replaced with ``'…'``.
        creator (:class:`telegram.User`): Creator of the link.
        creates_join_request (:obj:`bool`): :obj:`True`, if users joining the chat via
            the link need to be approved by chat administrators.

            .. versionadded:: 13.8
        is_primary (:obj:`bool`): :obj:`True`, if the link is primary.
        is_revoked (:obj:`bool`): :obj:`True`, if the link is revoked.
        expire_date (:class:`datetime.datetime`): Optional. Date when the link will expire or
            has been expired.
        member_limit (:obj:`int`): Optional. Maximum number of users that can be members
            of the chat simultaneously after joining the chat via this invite link; 1-99999.
        name (:obj:`str`): Optional. Invite link name.

            .. versionadded:: 13.8
        pending_join_request_count (:obj:`int`): Optional. Number of pending join requests
            created using this link.

            .. versionadded:: 13.8

    """

    __slots__ = (
        "invite_link",
        "creator",
        "is_primary",
        "is_revoked",
        "expire_date",
        "member_limit",
        "name",
        "creates_join_request",
        "pending_join_request_count",
    )

    def __init__(
        self,
        invite_link: str,
        creator: User,
        creates_join_request: bool,
        is_primary: bool,
        is_revoked: bool,
        expire_date: datetime.datetime = None,
        member_limit: int = None,
        name: str = None,
        pending_join_request_count: int = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.invite_link = invite_link
        self.creator = creator
        self.creates_join_request = creates_join_request
        self.is_primary = is_primary
        self.is_revoked = is_revoked

        # Optionals
        self.expire_date = expire_date
        self.member_limit = member_limit
        self.name = name
        self.pending_join_request_count = (
            int(pending_join_request_count) if pending_join_request_count is not None else None
        )
        self._id_attrs = (
            self.invite_link,
            self.creates_join_request,
            self.creator,
            self.is_primary,
            self.is_revoked,
        )

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ChatInviteLink"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["creator"] = User.de_json(data.get("creator"), bot)
        data["expire_date"] = from_timestamp(data.get("expire_date", None))

        return super().de_json(data=data, bot=bot)
