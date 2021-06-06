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
# pylint: disable=C0115
"""This module contains an object that represents Telegram errors."""
from typing import Tuple


def _lstrip_str(in_s: str, lstr: str) -> str:
    """
    Args:
        in_s (:obj:`str`): in string
        lstr (:obj:`str`): substr to strip from left side

    Returns:
        :obj:`str`: The stripped string.

    """
    if in_s.startswith(lstr):
        res = in_s[len(lstr) :]
    else:
        res = in_s
    return res


class TelegramError(Exception):
    """Base class for Telegram errors."""

    # Apparently the base class Exception already has __dict__ in it, so its not included here
    __slots__ = ('message',)

    def __init__(self, message: str):
        super().__init__()

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        msg = _lstrip_str(msg, 'Bad Request: ')
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message = msg

    def __str__(self) -> str:
        return '%s' % self.message

    def __reduce__(self) -> Tuple[type, Tuple[str]]:
        return self.__class__, (self.message,)


class Unauthorized(TelegramError):
    """Raised when the bot has not enough rights to perform the requested action."""

    __slots__ = ()


class InvalidToken(TelegramError):
    """Raised when the token is invalid."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__('Invalid token')

    def __reduce__(self) -> Tuple[type, Tuple]:  # type: ignore[override]
        return self.__class__, ()


class NetworkError(TelegramError):
    """Base class for exceptions due to networking errors."""

    __slots__ = ()


class BadRequest(NetworkError):
    """Raised when Telegram could not process the request correctly."""

    __slots__ = ()


class TimedOut(NetworkError):
    """Raised when a request took too long to finish."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__('Timed out')

    def __reduce__(self) -> Tuple[type, Tuple]:  # type: ignore[override]
        return self.__class__, ()


class ChatMigrated(TelegramError):
    """
    Raised when the requested group chat migrated to supergroup and has a new chat id.

    Args:
        new_chat_id (:obj:`int`): The new chat id of the group.

    """

    __slots__ = ('new_chat_id',)

    def __init__(self, new_chat_id: int):
        super().__init__(f'Group migrated to supergroup. New chat id: {new_chat_id}')
        self.new_chat_id = new_chat_id

    def __reduce__(self) -> Tuple[type, Tuple[int]]:  # type: ignore[override]
        return self.__class__, (self.new_chat_id,)


class RetryAfter(TelegramError):
    """
    Raised when flood limits where exceeded.

    Args:
        retry_after (:obj:`int`): Time in seconds, after which the bot can retry the request.

    """

    __slots__ = ('retry_after',)

    def __init__(self, retry_after: int):
        super().__init__(f'Flood control exceeded. Retry in {float(retry_after)} seconds')
        self.retry_after = float(retry_after)

    def __reduce__(self) -> Tuple[type, Tuple[float]]:  # type: ignore[override]
        return self.__class__, (self.retry_after,)


class Conflict(TelegramError):
    """Raised when a long poll or webhook conflicts with another one."""

    __slots__ = ()

    def __reduce__(self) -> Tuple[type, Tuple[str]]:
        return self.__class__, (self.message,)
