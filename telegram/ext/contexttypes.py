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
# pylint: disable=R0201
"""This module contains the auxiliary class ContextTypes."""
from typing import Type, Generic, overload, Dict  # pylint: disable=W0611

from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.utils.types import CCT, UD, CD, BD


class ContextTypes(Generic[CCT, UD, CD, BD]):
    """
    Convenience class to gather customizable types of the :class:`telegram.ext.CallbackContext`
    interface.

    .. versionadded:: 13.6

    Args:
        context (:obj:`type`, optional): Determines the type of the ``context`` argument of all
            (error-)handler callbacks and job callbacks. Must be a subclass of
            :class:`telegram.ext.CallbackContext`. Defaults to
            :class:`telegram.ext.CallbackContext`.
        bot_data (:obj:`type`, optional): Determines the type of ``context.bot_data`` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`. Must support
            instantiating without arguments.
        chat_data (:obj:`type`, optional): Determines the type of ``context.chat_data`` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`. Must support
            instantiating without arguments.
        user_data (:obj:`type`, optional): Determines the type of ``context.user_data`` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`. Must support
            instantiating without arguments.

    """

    __slots__ = ('_context', '_bot_data', '_chat_data', '_user_data')

    # overload signatures generated with https://git.io/JtJPj

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[Dict, Dict, Dict], Dict, Dict, Dict]',
    ):
        ...

    @overload
    def __init__(self: 'ContextTypes[CCT, Dict, Dict, Dict]', context: Type[CCT]):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[UD, Dict, Dict], UD, Dict, Dict]', user_data: Type[UD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[Dict, CD, Dict], Dict, CD, Dict]', chat_data: Type[CD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[Dict, Dict, BD], Dict, Dict, BD]', bot_data: Type[BD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, UD, Dict, Dict]', context: Type[CCT], user_data: Type[UD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, Dict, CD, Dict]', context: Type[CCT], chat_data: Type[CD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, Dict, Dict, BD]', context: Type[CCT], bot_data: Type[BD]
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[UD, CD, Dict], UD, CD, Dict]',
        user_data: Type[UD],
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[UD, Dict, BD], UD, Dict, BD]',
        user_data: Type[UD],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[Dict, CD, BD], Dict, CD, BD]',
        chat_data: Type[CD],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, UD, CD, Dict]',
        context: Type[CCT],
        user_data: Type[UD],
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, UD, Dict, BD]',
        context: Type[CCT],
        user_data: Type[UD],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, Dict, CD, BD]',
        context: Type[CCT],
        chat_data: Type[CD],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CallbackContext[UD, CD, BD], UD, CD, BD]',
        user_data: Type[UD],
        chat_data: Type[CD],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: 'ContextTypes[CCT, UD, CD, BD]',
        context: Type[CCT],
        user_data: Type[UD],
        chat_data: Type[CD],
        bot_data: Type[BD],
    ):
        ...

    def __init__(  # type: ignore[no-untyped-def]
        self,
        context=CallbackContext,
        bot_data=dict,
        chat_data=dict,
        user_data=dict,
    ):
        if not issubclass(context, CallbackContext):
            raise ValueError('context must be a subclass of CallbackContext.')

        # We make all those only accessible via properties because we don't currently support
        # changing this at runtime, so overriding the attributes doesn't make sense
        self._context = context
        self._bot_data = bot_data
        self._chat_data = chat_data
        self._user_data = user_data

    @property
    def context(self) -> Type[CCT]:
        return self._context

    @property
    def bot_data(self) -> Type[BD]:
        return self._bot_data

    @property
    def chat_data(self) -> Type[CD]:
        return self._chat_data

    @property
    def user_data(self) -> Type[UD]:
        return self._user_data
