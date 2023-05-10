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
"""This module contains classes that represent Telegram errors.

.. versionchanged:: 20.0
    Replaced ``Unauthorized`` by :class:`Forbidden`.
"""

__all__ = (
    "BadRequest",
    "ChatMigrated",
    "Conflict",
    "Forbidden",
    "InvalidToken",
    "NetworkError",
    "PassportDecryptionError",
    "RetryAfter",
    "TelegramError",
    "TimedOut",
)

from typing import Optional, Tuple, Union


def _lstrip_str(in_s: str, lstr: str) -> str:
    """
    Args:
        in_s (:obj:`str`): in string
        lstr (:obj:`str`): substr to strip from left side

    Returns:
        :obj:`str`: The stripped string.

    """
    return in_s[len(lstr) :] if in_s.startswith(lstr) else in_s


class TelegramError(Exception):
    """
    Base class for Telegram errors.

    Tip:
        Objects of this type can be serialized via Python's :mod:`pickle` module and pickled
        objects from one version of PTB are usually loadable in future versions. However, we can
        not guarantee that this compatibility will always be provided. At least a manual one-time
        conversion of the data may be needed on major updates of the library.

    .. seealso:: :wiki:`Exceptions, Warnings and Logging <Exceptions%2C-Warnings-and-Logging>`
    """

    __slots__ = ("message",)

    def __init__(self, message: str):
        super().__init__()

        msg = _lstrip_str(message, "Error: ")
        msg = _lstrip_str(msg, "[Error]: ")
        msg = _lstrip_str(msg, "Bad Request: ")
        if msg != message:
            # api_error - capitalize the msg...
            msg = msg.capitalize()
        self.message: str = msg

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"

    def __reduce__(self) -> Tuple[type, Tuple[str]]:
        return self.__class__, (self.message,)


class Forbidden(TelegramError):
    """Raised when the bot has not enough rights to perform the requested action.

    Examples:
        :any:`Raw API Bot <examples.rawapibot>`

    .. versionchanged:: 20.0
        This class was previously named ``Unauthorized``.
    """

    __slots__ = ()


class InvalidToken(TelegramError):
    """Raised when the token is invalid.

    Args:
        message (:obj:`str`, optional): Any additional information about the exception.

            .. versionadded:: 20.0
    """

    __slots__ = ()

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__("Invalid token" if message is None else message)


class NetworkError(TelegramError):
    """Base class for exceptions due to networking errors.

    Examples:
        :any:`Raw API Bot <examples.rawapibot>`
    """

    __slots__ = ()


class BadRequest(NetworkError):
    """Raised when Telegram could not process the request correctly."""

    __slots__ = ()


class TimedOut(NetworkError):
    """Raised when a request took too long to finish.

    Args:
        message (:obj:`str`, optional): Any additional information about the exception.

            .. versionadded:: 20.0
    """

    __slots__ = ()

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "Timed out")


class ChatMigrated(TelegramError):
    """
    Raised when the requested group chat migrated to supergroup and has a new chat id.

    .. seealso::
        :wiki:`Storing Bot, User and Chat Related Data <Storing-bot%2C-user-and-chat-related-data>`

    Args:
        new_chat_id (:obj:`int`): The new chat id of the group.

    Attributes:
        new_chat_id (:obj:`int`): The new chat id of the group.

    """

    __slots__ = ("new_chat_id",)

    def __init__(self, new_chat_id: int):
        super().__init__(f"Group migrated to supergroup. New chat id: {new_chat_id}")
        self.new_chat_id: int = new_chat_id

    def __reduce__(self) -> Tuple[type, Tuple[int]]:  # type: ignore[override]
        return self.__class__, (self.new_chat_id,)


class RetryAfter(TelegramError):
    """
    Raised when flood limits where exceeded.

    .. versionchanged:: 20.0
       :attr:`retry_after` is now an integer to comply with the Bot API.

    Args:
        retry_after (:obj:`int`): Time in seconds, after which the bot can retry the request.

    Attributes:
        retry_after (:obj:`int`): Time in seconds, after which the bot can retry the request.

    """

    __slots__ = ("retry_after",)

    def __init__(self, retry_after: int):
        super().__init__(f"Flood control exceeded. Retry in {retry_after} seconds")
        self.retry_after: int = retry_after

    def __reduce__(self) -> Tuple[type, Tuple[float]]:  # type: ignore[override]
        return self.__class__, (self.retry_after,)


class Conflict(TelegramError):
    """Raised when a long poll or webhook conflicts with another one."""

    __slots__ = ()

    def __reduce__(self) -> Tuple[type, Tuple[str]]:
        return self.__class__, (self.message,)


class PassportDecryptionError(TelegramError):
    """Something went wrong with decryption.

    .. versionchanged:: 20.0
        This class was previously named ``TelegramDecryptionError`` and was available via
        ``telegram.TelegramDecryptionError``.
    """

    __slots__ = ("_msg",)

    def __init__(self, message: Union[str, Exception]):
        super().__init__(f"PassportDecryptionError: {message}")
        self._msg = str(message)

    def __reduce__(self) -> Tuple[type, Tuple[str]]:
        return self.__class__, (self._msg,)
