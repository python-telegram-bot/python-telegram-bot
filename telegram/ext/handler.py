#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from telegram.utils.promise import Promise
from telegram.utils.types import HandlerArg
from telegram import Update
from typing import Callable, TYPE_CHECKING, Any, Optional, Union, TypeVar, Dict
if TYPE_CHECKING:
    from telegram.ext import CallbackContext, Dispatcher

RT = TypeVar('RT')


class Handler(ABC):
    """The base class for all update handlers. Create custom handlers by inheriting from it.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

        Note that this is DEPRECATED, and you should use context based callbacks. See
        https://git.io/fxJuV for more info.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_update_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    """
    def __init__(self,
                 callback: Callable[[HandlerArg, 'CallbackContext'], RT],
                 pass_update_queue: bool = False,
                 pass_job_queue: bool = False,
                 pass_user_data: bool = False,
                 pass_chat_data: bool = False,
                 run_async: bool = False):
        self.callback: Callable[[HandlerArg, 'CallbackContext'], RT] = callback
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data
        self.run_async = run_async

    @abstractmethod
    def check_update(self, update: HandlerArg) -> Optional[Union[bool, object]]:
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be tested.

        Returns:
            Either :obj:`None` or :obj:`False` if the update should not be handled. Otherwise an
            object that will be passed to :meth:`handle_update` and
            :meth:`collect_additional_context` when the update gets handled.

        """

    def handle_update(self,
                      update: HandlerArg,
                      dispatcher: 'Dispatcher',
                      check_result: object,
                      context: 'CallbackContext' = None) -> Union[RT, Promise]:
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from :attr:`callback`.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result (:obj:`obj`): The result from :attr:`check_update`.
            context (:class:`telegram.ext.CallbackContext`, optional): The context as provided by
                the dispatcher.

        """
        if context:
            self.collect_additional_context(context, update, dispatcher, check_result)
            if self.run_async:
                return dispatcher.run_async(self.callback, update, context, update=update)
            else:
                return self.callback(update, context)
        else:
            optional_args = self.collect_optional_args(dispatcher, update, check_result)
            if self.run_async:
                return dispatcher.run_async(self.callback, dispatcher.bot, update, update=update,
                                            **optional_args)
            else:
                return self.callback(dispatcher.bot, update, **optional_args)  # type: ignore

    def collect_additional_context(self,
                                   context: 'CallbackContext',
                                   update: HandlerArg,
                                   dispatcher: 'Dispatcher',
                                   check_result: Any) -> None:
        """Prepares additional arguments for the context. Override if needed.

        Args:
            context (:class:`telegram.ext.CallbackContext`): The context object.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result (return value) from :attr:`check_update`.

        """
        pass

    def collect_optional_args(self,
                              dispatcher: 'Dispatcher',
                              update: HandlerArg = None,
                              check_result: Any = None) -> Dict[str, Any]:
        """
        Prepares the optional arguments. If the handler has additional optional args,
        it should subclass this method, but remember to call this super method.

        DEPRECATED: This method is being replaced by new context based callbacks. Please see
        https://git.io/fxJuV for more info.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            check_result: The result from check_update

        """
        optional_args: Dict[str, Any] = dict()

        if self.pass_update_queue:
            optional_args['update_queue'] = dispatcher.update_queue
        if self.pass_job_queue:
            optional_args['job_queue'] = dispatcher.job_queue
        if self.pass_user_data and isinstance(update, Update):
            user = update.effective_user
            optional_args['user_data'] = dispatcher.user_data[
                user.id if user else None]  # type: ignore[index]
        if self.pass_chat_data and isinstance(update, Update):
            chat = update.effective_chat
            optional_args['chat_data'] = dispatcher.chat_data[
                chat.id if chat else None]  # type: ignore[index]

        return optional_args
