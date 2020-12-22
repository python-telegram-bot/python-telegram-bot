#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2020
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
"""This module contains the auxiliary class ContextCustomizer."""
from collections import defaultdict, Mapping
from typing import Type, Optional, Any, NoReturn, Generic

from telegram.ext.callbackcontext import CallbackContext
from telegram.utils.types import CCT, UD, CD, BD, CDM, UDM


class ContextCustomizer(Generic[CCT, UD, CD, BD, UDM, CDM]):
    """
    Convenience class to gather customizable types of the ``context`` interface.

    Args:
        context (:obj:`type`, optional): Determines the type of the ``context`` argument of all
            (error-)handler callbacks and job callbacks. Must be a subclass of
            :class:`telegram.ext.CallbackContext`. Defaults to
            :class:`telegram.ext.CallbackContext`.
        bot_data (:obj:`type`, optional): Determines the type of ``context.bot_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`. Must support
            instantiating without arguments
        chat_data (:obj:`type`, optional): Determines the type of ``context.chat_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`.
        user_data (:obj:`type`, optional): Determines the type of ``context.user_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`dict`.
        chat_data_mapping (:obj:`type`, optional): In combination with :attr:`chat_data` determines
            the type of :attr:`telegram.ext.Dispatcher.chat_data`. Must support instantiating via

            .. code:: python

                chat_data_mapping(chat_data)

        user_data_mapping (:obj:`type`, optional): In combination with :attr:`user_data` determines
            the type of :attr:`telegram.ext.Dispatcher.user_data`. Must support instantiating via

            .. code:: python

                user_data_mapping(user_data)

    """

    def __init__(
        self,
        context: Type[CCT] = CallbackContext,
        bot_data: Type[BD] = dict,
        chat_data: Type[CD] = dict,
        user_data: Type[UD] = dict,
        chat_data_mapping: Type[CDM] = defaultdict,
        user_data_mapping: Type[UDM] = defaultdict,
    ):
        if not issubclass(context, CallbackContext):
            raise ValueError('context must be a subclass of CallbackContext.')
        if not issubclass(chat_data_mapping, Mapping):
            raise ValueError('chat_data_mapping must be a subclass of collections.Mapping.')
        if not issubclass(user_data_mapping, Mapping):
            raise ValueError('user_data_mapping must be a subclass of collections.Mapping.')

        self._context = context
        self._bot_data = bot_data
        self._chat_data = chat_data
        self._user_data = user_data
        self._chat_data_mapping = chat_data_mapping
        self._user_data_mapping = user_data_mapping

    @property
    def context(self) -> Optional[Type]:
        return self._context

    @context.setter
    def context(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def bot_data(self) -> Optional[Type]:
        return self._bot_data

    @bot_data.setter
    def bot_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def chat_data(self) -> Optional[Type]:
        return self._chat_data

    @chat_data.setter
    def chat_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def user_data(self) -> Optional[Type]:
        return self._user_data

    @user_data.setter
    def user_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def user_data_mapping(self) -> Optional[Type]:
        return self._user_data_mapping

    @user_data_mapping.setter
    def user_data_mapping(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def chat_data_mapping(self) -> Optional[Type]:
        return self._chat_data_mapping

    @chat_data_mapping.setter
    def chat_data_mapping(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")
