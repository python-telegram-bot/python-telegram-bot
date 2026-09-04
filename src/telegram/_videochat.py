#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg, to_timedelta
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import get_timedelta_value


@tg_dataclass()
class VideoChatStarted(TelegramObject):
    """
    This object represents a service message about a video
    chat started in the chat. Currently holds no information.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatStarted`` in accordance to Bot API 6.0.
    """


@tg_dataclass()
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

    .. versionchanged:: v22.2
       As part of the migration to representing time periods using ``datetime.timedelta``,
       equality comparison now considers integer durations and equivalent timedeltas as equal.

    Args:
        duration (:obj:`int` | :class:`datetime.timedelta`): Voice chat duration
            in seconds.

            .. versionchanged:: v22.2
                |time-period-input|

    Attributes:
        duration (:obj:`int` | :class:`datetime.timedelta`): Voice chat duration in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|

    """

    _duration: dtm.timedelta = tg_field(compare=True, alias="duration", converter=to_timedelta)

    @property
    def duration(self) -> int | dtm.timedelta:
        return get_timedelta_value(  # type: ignore[return-value]
            self._duration, attribute="duration"
        )


@tg_dataclass()
class VideoChatParticipantsInvited(TelegramObject):
    """
    This object represents a service message about new members invited to a video chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`users` are equal.

    .. versionadded:: 13.4
    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatParticipantsInvited`` in accordance to Bot API 6.0.

    Args:
        users (Sequence[:class:`telegram.User`]): New members that were invited to the video chat.

            .. versionchanged:: 20.0
                |sequenceclassargs|

    Attributes:
        users (tuple[:class:`telegram.User`]): New members that were invited to the video chat.

            .. versionchanged:: 20.0
                |tupleclassattrs|

    """

    users: tuple[User, ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class VideoChatScheduled(TelegramObject):
    """This object represents a service message about a video chat scheduled in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`start_date` are equal.

    .. versionchanged:: 20.0
        This class was renamed from ``VoiceChatScheduled`` in accordance to Bot API 6.0.

    Args:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator

            .. versionchanged:: 20.3
                |datetime_localization|
    Attributes:
        start_date (:obj:`datetime.datetime`): Point in time (Unix timestamp) when the video
            chat is supposed to be started by a chat administrator

            .. versionchanged:: 20.3
                |datetime_localization|

    """

    start_date: dtm.datetime = tg_field(compare=True)
