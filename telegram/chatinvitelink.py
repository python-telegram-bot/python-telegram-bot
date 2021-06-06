#!/usr/bin/env python
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
"""This module contains an object that represents an invite link for a chat."""
import datetime
from typing import TYPE_CHECKING, Any, Optional

from telegram import TelegramObject, User
from telegram.utils.helpers import from_timestamp, to_timestamp
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class ChatInviteLink(TelegramObject):
    """This object represents an invite link for a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`invite_link`, :attr:`creator`, :attr:`is_primary` and
    :attr:`is_revoked` are equal.

    .. versionadded:: 13.4

    Args:
        invite_link (:obj:`str`): The invite link.
        creator (:class:`telegram.User`): Creator of the link.
        is_primary (:obj:`bool`): :obj:`True`, if the link is primary.
        is_revoked (:obj:`bool`): :obj:`True`, if the link is revoked.
        expire_date (:class:`datetime.datetime`, optional): Date when the link will expire or
            has been expired.
        member_limit (:obj:`int`, optional): Maximum number of users that can be members of the
            chat simultaneously after joining the chat via this invite link; 1-99999.

    Attributes:
        invite_link (:obj:`str`): The invite link. If the link was created by another chat
            administrator, then the second part of the link will be replaced with ``'…'``.
        creator (:class:`telegram.User`): Creator of the link.
        is_primary (:obj:`bool`): :obj:`True`, if the link is primary.
        is_revoked (:obj:`bool`): :obj:`True`, if the link is revoked.
        expire_date (:class:`datetime.datetime`): Optional. Date when the link will expire or
            has been expired.
        member_limit (:obj:`int`): Optional. Maximum number of users that can be members
            of the chat simultaneously after joining the chat via this invite link; 1-99999.

    """

    __slots__ = (
        'invite_link',
        'creator',
        'is_primary',
        'is_revoked',
        'expire_date',
        'member_limit',
        '_id_attrs',
    )

    def __init__(
        self,
        invite_link: str,
        creator: User,
        is_primary: bool,
        is_revoked: bool,
        expire_date: datetime.datetime = None,
        member_limit: int = None,
        **_kwargs: Any,
    ):
        # Required
        self.invite_link = invite_link
        self.creator = creator
        self.is_primary = is_primary
        self.is_revoked = is_revoked

        # Optionals
        self.expire_date = expire_date
        self.member_limit = int(member_limit) if member_limit is not None else None

        self._id_attrs = (self.invite_link, self.creator, self.is_primary, self.is_revoked)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['ChatInviteLink']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['creator'] = User.de_json(data.get('creator'), bot)
        data['expire_date'] = from_timestamp(data.get('expire_date', None))

        return cls(**data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data['expire_date'] = to_timestamp(self.expire_date)

        return data
