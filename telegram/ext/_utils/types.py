#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""This module contains custom typing aliases.

.. versionadded:: 13.6

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    MutableMapping,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from typing import Optional

    from telegram import Bot
    from telegram.ext import BaseRateLimiter, CallbackContext, JobQueue

CCT = TypeVar("CCT", bound="CallbackContext[Any, Any, Any, Any]")
"""An instance of :class:`telegram.ext.CallbackContext` or a custom subclass.

.. versionadded:: 13.6
"""

RT = TypeVar("RT")
UT = TypeVar("UT")
HandlerCallback = Callable[[UT, CCT], Coroutine[Any, Any, RT]]
"""Type of a handler callback

    .. versionadded:: 20.0
"""
JobCallback = Callable[[CCT], Coroutine[Any, Any, Any]]
"""Type of a job callback

    .. versionadded:: 20.0
"""

ConversationKey = Tuple[Union[int, str], ...]
ConversationDict = MutableMapping[ConversationKey, object]
"""Dict[Tuple[:obj:`int` | :obj:`str`, ...], Optional[:obj:`object`]]:
    Dicts as maintained by the :class:`telegram.ext.ConversationHandler`.

    .. versionadded:: 13.6
"""

CDCData = Tuple[List[Tuple[str, float, Dict[str, Any]]], Dict[str, str]]
"""Tuple[List[Tuple[:obj:`str`, :obj:`float`, Dict[:obj:`str`, :class:`object`]]], \
    Dict[:obj:`str`, :obj:`str`]]: Data returned by
    :attr:`telegram.ext.CallbackDataCache.persistence_data`.

    .. versionadded:: 13.6
"""

BT = TypeVar("BT", bound="Bot")
"""Type of the bot.

.. versionadded:: 20.0
"""
UD = TypeVar("UD")
"""Type of the user data for a single user.

.. versionadded:: 13.6
"""
CD = TypeVar("CD")
"""Type of the chat data for a single user.

.. versionadded:: 13.6
"""
BD = TypeVar("BD")
"""Type of the bot data.

.. versionadded:: 13.6
"""
JQ = TypeVar("JQ", bound=Union[None, "JobQueue"])
"""Type of the job queue.

.. versionadded:: 20.0"""

RL = TypeVar("RL", bound="Optional[BaseRateLimiter]")
"""Type of the rate limiter.

.. versionadded:: 20.0"""

RLARGS = TypeVar("RLARGS")
"""Type of the rate limiter arguments.

.. versionadded:: 20.0"""
FilterDataDict = Dict[str, List[Any]]
