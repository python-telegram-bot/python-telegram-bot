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
"""This module contains objects related to Telegram video chats."""

import datetime as dtm
from typing import TYPE_CHECKING, List, Optional

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.datetime import from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class VideoChatStarted(TelegramObject):
    """
    This object represents a service message about a video
    chat started in the chat. Currently holds no information.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatStarted`` in accordance to Bot API 6.0.
    """

    __slots__ = ()


class VideoChatEnded(TelegramObject):
    """
    This object represents a service message about a
    video chat ended in the chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`duration` are equal.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatEnded`` in accordance to Bot API 6.0.

    Args:
        duration (:obj:`int`): Voice chat duration in seconds.

    Attributes:
        duration (:obj:`int`): Voice chat duration in seconds.

    """

    __slots__ = ("duration",)

    def __init__(
        self,
        duration: int,
        *,
        api_kwargs: JSONDict = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.duration = duration
        self._id_attrs = (self.duration,)


class VideoChatParticipantsInvited(TelegramObject):
    """
    This object represents a service message about new members invited to a video chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`users` are equal.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatParticipantsInvited`` in accordance to Bot API 6.0.

    Args:
        users (List[:class:`telegram.User`]): New members that were invited to the video chat.

    Attributes:
        users (List[:class:`telegram.User`]): New members that were invited to the video chat.

    """

    __slots__ = ("users",)

    def __init__(
        self,
        users: List[User],
        *,
        api_kwargs: JSONDict = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.users = users
        self._id_attrs = (self.users,)

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: "Bot"
    ) -> Optional["VideoChatParticipantsInvited"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["users"] = User.de_list(data.get("users", []), bot)
        return super().de_json(data=data, bot=bot)

    def __hash__(self) -> int:
        return hash(None) if self.users is None else hash(tuple(self.users))


class VideoChatScheduled(TelegramObject):
    """This object represents a service message about a video chat scheduled in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`start_date` are equal.

    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatScheduled`` in accordance to Bot API 6.0.

    Args:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator
    Attributes:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator

    """

    __slots__ = ("start_date",)

    def __init__(
        self,
        start_date: dtm.datetime,
        *,
        api_kwargs: JSONDict = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.start_date = start_date

        self._id_attrs = (self.start_date,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["VideoChatScheduled"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["start_date"] = from_timestamp(data["start_date"])

        return super().de_json(data=data, bot=bot)
