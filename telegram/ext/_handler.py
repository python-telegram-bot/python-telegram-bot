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
"""This module contains the base class for handlers as used by the Dispatcher."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union, Generic

from telegram._utils.defaultvalue import DefaultValue, DEFAULT_FALSE
from telegram.ext._utils.promise import Promise
from telegram.ext._utils.types import CCT
from telegram.ext._extbot import ExtBot

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')
UT = TypeVar('UT')


class Handler(Generic[UT, CCT], ABC):
    """The base class for all update handlers. Create custom handlers by inheriting from it.

    Warning:
        When setting :paramref:`run_async` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = (
        'callback',
        'run_async',
    )

    def __init__(
        self,
        callback: Callable[[UT, CCT], RT],
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        self.callback = callback
        self.run_async = run_async

    @abstractmethod
    def check_update(self, update: object) -> Optional[Union[bool, object]]:
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Note:
            Custom updates types can be handled by the dispatcher. Therefore, an implementation of
            this method should always check the type of :paramref:`update`.

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update to be tested.

        Returns:
            Either :obj:`None` or :obj:`False` if the update should not be handled. Otherwise an
            object that will be passed to :meth:`handle_update` and
            :meth:`collect_additional_context` when the update gets handled.

        """

    def handle_update(
        self,
        update: UT,
        dispatcher: 'Dispatcher',
        check_result: object,
        context: CCT,
    ) -> Union[RT, Promise]:
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from :attr:`callback`.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result (:class:`object`): The result from :attr:`check_update`.
            context (:class:`telegram.ext.CallbackContext`): The context as provided by
                the dispatcher.

        """
        run_async = self.run_async
        if (
            self.run_async is DEFAULT_FALSE
            and isinstance(dispatcher.bot, ExtBot)
            and dispatcher.bot.defaults
            and dispatcher.bot.defaults.run_async
        ):
            run_async = True

        self.collect_additional_context(context, update, dispatcher, check_result)
        if run_async:
            return dispatcher.run_async(self.callback, update, context, update=update)
        return self.callback(update, context)

    def collect_additional_context(
        self,
        context: CCT,
        update: UT,
        dispatcher: 'Dispatcher',
        check_result: Any,
    ) -> None:
        """Prepares additional arguments for the context. Override if needed.

        Args:
            context (:class:`telegram.ext.CallbackContext`): The context object.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result (return value) from :attr:`check_update`.

        """
