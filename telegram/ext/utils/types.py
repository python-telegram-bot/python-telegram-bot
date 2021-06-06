#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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
"""
from typing import TypeVar, TYPE_CHECKING, Tuple, List, Dict, Any, Optional

if TYPE_CHECKING:
    from telegram.ext import CallbackContext  # noqa: F401


ConversationDict = Dict[Tuple[int, ...], Optional[object]]
"""Dicts as maintained by the :class:`telegram.ext.ConversationHandler`.

    .. versionadded:: 13.6
"""

CDCData = Tuple[List[Tuple[str, float, Dict[str, Any]]], Dict[str, str]]
"""Tuple[List[Tuple[:obj:`str`, :obj:`float`, Dict[:obj:`str`, :obj:`any`]]], \
    Dict[:obj:`str`, :obj:`str`]]: Data returned by
    :attr:`telegram.ext.CallbackDataCache.persistence_data`.

    .. versionadded:: 13.6
"""

CCT = TypeVar('CCT', bound='CallbackContext')
"""An instance of :class:`telegram.ext.CallbackContext` or a custom subclass.

.. versionadded:: 13.6
"""
UD = TypeVar('UD')
"""Type of the user data for a single user.

.. versionadded:: 13.6
"""
CD = TypeVar('CD')
"""Type of the chat data for a single user.

.. versionadded:: 13.6
"""
BD = TypeVar('BD')
"""Type of the bot data.

.. versionadded:: 13.6
"""
