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
# pylint: disable=R0201
"""This module contains the auxiliary class ContextCustomizer."""
from collections import defaultdict
from collections.abc import Mapping
from typing import Type, Any, NoReturn, Generic, overload, Dict  # pylint: disable=W0611

from telegram.ext.callbackcontext import CallbackContext
from telegram.utils.types import CCT, UD, CD, BD, CDM, UDM, IntDD  # pylint: disable=W0611


class ContextCustomizer(Generic[CCT, UD, CD, BD, UDM, CDM]):
    """
    Convenience class to gather customizable types of the ``context`` interface.

    Args:
        context (:obj:`type`, optional): Determines the type of the ``context`` argument of all
            (error-)handler callbacks and job callbacks. Must be a subclass of
            :class:`telegram.ext.CallbackContext`. Defaults to
            :class:`telegram.ext.CallbackContext`.
        bot_data (:obj:`type`, optional): Determines the type of ``context.bot_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`Dict`. Must support
            instantiating without arguments
        chat_data (:obj:`type`, optional): Determines the type of ``context.chat_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`Dict`.
        user_data (:obj:`type`, optional): Determines the type of ``context.user_data` of all
            (error-)handler callbacks and job callbacks. Defaults to :obj:`Dict`.
        chat_data_mapping (:obj:`type`, optional): In combination with :attr:`chat_data` determines
            the type of :attr:`telegram.ext.Dispatcher.chat_data`. Must support instantiating via

            .. code:: python

                chat_data_mapping(chat_data)

        user_data_mapping (:obj:`type`, optional): In combination with :attr:`user_data` determines
            the type of :attr:`telegram.ext.Dispatcher.user_data`. Must support instantiating via

            .. code:: python

                user_data_mapping(user_data)

    """

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, Dict], Dict, Dict, Dict, "
        "IntDD[Dict], IntDD[Dict]]",
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, Dict, IntDD[Dict], IntDD[Dict]]",
        context: Type[CCT],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, Dict], UD, Dict, Dict, "
        "IntDD[UD], IntDD[Dict]]",
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, Dict], Dict, CD, Dict, "
        "IntDD[Dict], IntDD[CD]]",
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, BD], Dict, Dict, BD, "
        "IntDD[Dict], IntDD[Dict]]",
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, Dict], Dict, Dict, "
        "Dict, UDM, IntDD[Dict]]",
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, Dict], Dict, Dict, Dict, "
        "IntDD[Dict], CDM]",
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, Dict, IntDD[UD], IntDD[Dict]]",
        context: Type[CCT],
        bot_data: Type[BD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, Dict, IntDD[Dict], IntDD[CD]]",
        context: Type[CCT],
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, BD, IntDD[Dict], IntDD[Dict]]",
        context: Type[CCT],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, Dict, UDM, IntDD[Dict]]",
        context: Type[CCT],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, Dict, IntDD[Dict], CDM]",
        context: Type[CCT],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, Dict], UD, CD, Dict, "
        "IntDD[UD], IntDD[CD]]",
        bot_data: Type[BD],
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, BD], UD, Dict, BD, "
        "IntDD[UD], IntDD[Dict]]",
        bot_data: Type[BD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, Dict], UD, Dict, Dict, "
        "UDM, IntDD[Dict]]",
        bot_data: Type[BD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, Dict], UD, Dict, Dict, "
        "IntDD[UD], CDM]",
        bot_data: Type[BD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, BD], Dict, CD, BD, "
        "IntDD[Dict], IntDD[CD]]",
        chat_data: Type[CD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, Dict], Dict, CD, Dict, "
        "UDM, IntDD[CD]]",
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, Dict], Dict, CD, Dict, "
        "IntDD[Dict], CDM]",
        chat_data: Type[CD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, BD], Dict, Dict, BD, UDM, "
        "IntDD[Dict]]",
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, BD], Dict, Dict, BD, "
        "IntDD[Dict], CDM]",
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, Dict], Dict, Dict, Dict, UDM, CDM]",
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, Dict, IntDD[UD], IntDD[CD]]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, BD, IntDD[UD], IntDD[Dict]]",
        context: Type[CCT],
        bot_data: Type[BD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, Dict, UDM, IntDD[Dict]]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, Dict, IntDD[UD], CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, BD, IntDD[Dict], IntDD[CD]]",
        context: Type[CCT],
        chat_data: Type[CD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, Dict, UDM, IntDD[CD]]",
        context: Type[CCT],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, Dict, IntDD[Dict], CDM]",
        context: Type[CCT],
        chat_data: Type[CD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, BD, UDM, IntDD[Dict]]",
        context: Type[CCT],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, BD, IntDD[Dict], CDM]",
        context: Type[CCT],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, Dict, UDM, CDM]",
        context: Type[CCT],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, BD], UD, CD, BD, IntDD[UD], IntDD[CD]]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, Dict], UD, CD, Dict, UDM, IntDD[CD]]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, Dict], UD, CD, Dict, IntDD[UD], CDM]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, BD], UD, Dict, BD, UDM, IntDD[Dict]]",
        bot_data: Type[BD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, BD], UD, Dict, BD, IntDD[UD], CDM]",
        bot_data: Type[BD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, Dict], UD, Dict, Dict, UDM, CDM]",
        bot_data: Type[BD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, BD], Dict, CD, BD, UDM, IntDD[CD]]",
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, BD], Dict, CD, BD, IntDD[Dict], CDM]",
        chat_data: Type[CD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, Dict], Dict, CD, Dict, UDM, CDM]",
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, Dict, BD], Dict, Dict, BD, UDM, CDM]",
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, BD, IntDD[UD], IntDD[CD]]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, Dict, UDM, IntDD[CD]]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, Dict, IntDD[UD], CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, BD, UDM, IntDD[Dict]]",
        context: Type[CCT],
        bot_data: Type[BD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, BD, IntDD[UD], CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, Dict, UDM, CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, BD, UDM, IntDD[CD]]",
        context: Type[CCT],
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, BD, IntDD[Dict], CDM]",
        context: Type[CCT],
        chat_data: Type[CD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, Dict, UDM, CDM]",
        context: Type[CCT],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, Dict, BD, UDM, CDM]",
        context: Type[CCT],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, BD], UD, CD, BD, UDM, IntDD[CD]]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, BD], UD, CD, BD, IntDD[UD], CDM]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, Dict], UD, CD, Dict, UDM, CDM]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, Dict, BD], UD, Dict, BD, UDM, CDM]",
        bot_data: Type[BD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[Dict, CD, BD], Dict, CD, BD, UDM, CDM]",
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, BD, UDM, IntDD[CD]]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, BD, IntDD[UD], CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, CD, Dict, UDM, CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        chat_data: Type[CD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, UD, Dict, BD, UDM, CDM]",
        context: Type[CCT],
        bot_data: Type[BD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CCT, Dict, CD, BD, UDM, CDM]",
        context: Type[CCT],
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    @overload
    def __init__(
        self: "ContextCustomizer[CallbackContext[UD, CD, BD], UD, CD, BD, UDM, CDM]",
        bot_data: Type[BD],
        chat_data: Type[CD],
        user_data: Type[UD],
        chat_data_mapping: Type[UDM],
        user_data_mapping: Type[CDM],
    ):
        ...

    def __init__(  # type: ignore[no-untyped-def]
        self,
        context=CallbackContext,
        bot_data=dict,
        chat_data=dict,
        user_data=dict,
        chat_data_mapping=defaultdict,
        user_data_mapping=defaultdict,
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
    def context(self) -> Type[CCT]:
        return self._context

    @context.setter
    def context(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def bot_data(self) -> Type[BD]:
        return self._bot_data

    @bot_data.setter
    def bot_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def chat_data(self) -> Type[CD]:
        return self._chat_data

    @chat_data.setter
    def chat_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def user_data(self) -> Type[UD]:
        return self._user_data

    @user_data.setter
    def user_data(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def user_data_mapping(self) -> Type[UDM]:
        return self._user_data_mapping

    @user_data_mapping.setter
    def user_data_mapping(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")

    @property
    def chat_data_mapping(self) -> Type[CDM]:
        return self._chat_data_mapping

    @chat_data_mapping.setter
    def chat_data_mapping(self, value: Any) -> NoReturn:
        raise AttributeError("You can not assign a new value to ContextCustomizer attributes.")
