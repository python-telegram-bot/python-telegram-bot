#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains objects related to Telegram video chats."""

import datetime as dtm
from typing import TYPE_CHECKING, Any, Optional, List

from telegram import TelegramObject, User
from telegram.utils.helpers import from_timestamp, to_timestamp
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class VideoChatStarted(TelegramObject):
    """
    This object represents a service message about a video
    chat started in the chat. Currently holds no information.

    .. versionadded:: 13.12
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):  # skipcq: PTC-W0049
        pass


class VideoChatEnded(TelegramObject):
    """
    This object represents a service message about a
    video chat ended in the chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`duration` are equal.

    .. versionadded:: 13.12

    Args:
        duration (:obj:`int`): Voice chat duration in seconds.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        duration (:obj:`int`): Voice chat duration in seconds.

    """

    __slots__ = ('duration', '_id_attrs')

    def __init__(self, duration: int, **_kwargs: Any) -> None:
        self.duration = int(duration) if duration is not None else None
        self._id_attrs = (self.duration,)


class VideoChatParticipantsInvited(TelegramObject):
    """
    This object represents a service message about new members invited to a video chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`users` are equal.

    .. versionadded:: 13.12

    Args:
        users (List[:class:`telegram.User`]): New members that were invited to the video chat.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        users (List[:class:`telegram.User`]): New members that were invited to the video chat.

    """

    __slots__ = ('users', '_id_attrs')

    def __init__(self, users: List[User], **_kwargs: Any) -> None:
        self.users = users
        self._id_attrs = (self.users,)

    def __hash__(self) -> int:
        return hash(tuple(self.users))

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: 'Bot'
    ) -> Optional['VideoChatParticipantsInvited']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['users'] = User.de_list(data.get('users', []), bot)
        return cls(**data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data["users"] = [u.to_dict() for u in self.users]
        return data


class VideoChatScheduled(TelegramObject):
    """This object represents a service message about a video chat scheduled in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`start_date` are equal.

    .. versionadded:: 13.12

    Args:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator

    """

    __slots__ = ('start_date', '_id_attrs')

    def __init__(self, start_date: dtm.datetime, **_kwargs: Any) -> None:
        self.start_date = start_date

        self._id_attrs = (self.start_date,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['VideoChatScheduled']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['start_date'] = from_timestamp(data['start_date'])

        return cls(**data, bot=bot)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        # Required
        data['start_date'] = to_timestamp(self.start_date)

        return data
