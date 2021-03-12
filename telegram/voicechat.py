#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains objects related to Telegram voice chats."""

from typing import TYPE_CHECKING, Any, Optional, List

from telegram import TelegramObject, User
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class VoiceChatStarted(TelegramObject):
    """
    This object represents a service message about a voice
    chat started in the chat. Currently holds no information.

    .. versionadded:: 13.4
    """

    def __init__(self, **_kwargs: Any):
        pass


class VoiceChatEnded(TelegramObject):
    """
    This object represents a service message about a
    voice chat ended in the chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`duration` are equal.

    .. versionadded:: 13.4

    Args:
        duration (:obj:`int`): Voice chat duration in seconds.

    Attributes:
        duration (:obj:`int`): Voice chat duration in seconds.

    """

    def __init__(self, duration: int, **_kwargs: Any) -> None:
        self.duration = int(duration) if duration is not None else None
        self._id_attrs = (self.duration,)


class VoiceChatParticipantsInvited(TelegramObject):
    """
    This object represents a service message about
    new members invited to a voice chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`users` are equal.

    .. versionadded:: 13.4

    Args:
        users (List[:class:`telegram.User`]):  New members that
            were invited to the voice chat.

    Attributes:
        users (List[:class:`telegram.User`]):  New members that
            were invited to the voice chat.

    """

    def __init__(self, users: List[User], **_kwargs: Any) -> None:
        self.users = users
        self._id_attrs = (self.users,)

    def __hash__(self) -> int:
        return hash(tuple(self.users))

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: 'Bot'
    ) -> Optional['VoiceChatParticipantsInvited']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['users'] = User.de_list(data.get('users', []), bot)
        return cls(**data)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data["users"] = [u.to_dict() for u in self.users]
        return data
