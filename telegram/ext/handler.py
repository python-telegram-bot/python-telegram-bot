#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
import warnings

from telegram import Update
from telegram.utils.deprecate import TelegramDeprecationWarning


class Handler(object):
    """The base class for all update handlers. Create custom handlers by inheriting from it.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        use_context (:obj:`bool`): Determines whether all `pass_` arguments will be
            ignored in favor of passing a :class:`telegram.ext.Context` object to the callback.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

        Note that this is DEPRECATED, and you should use Context Based Handlers. See
        https://git.io/vpVe8 for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: HandlerContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
            DEPRECATED: Please switch to context based handlers.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
            DEPRECATED: Please switch to context based handlers.
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
            DEPRECATED: Please switch to context based handlers.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.
            DEPRECATED: Please switch to context based handlers.
        use_context (:obj:`bool`, optional): If set to ``True`` Use the context based callback API.
            During the deprecation period of the old API the default is ``False``. **New users**:
            set this to ``True``.

    """
    def __init__(self,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 use_context=False):
        self.callback = callback
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data
        self.use_context = use_context

        if use_context and (
                pass_update_queue or pass_job_queue or pass_user_data or pass_chat_data):
            raise ValueError('Mix of Context Based Handler API and old Handler API is not allowed')

        if not use_context:
            warnings.warn('Old Handler API is deprecated - see https://git.io/vpVe8 for details',
                          TelegramDeprecationWarning, stacklevel=3)

    def check_update(self, update):
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be tested.

        Returns:
            Either ``None`` or ``False`` if the update should not be handled. Otherwise an object
            that will be passed to :attr:`handle_update` and :attr:`collect_additional_context`
            when the update gets handled.

        """
        raise NotImplementedError

    def handle_update(self, update, dispatcher, check_result):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`self.callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from ``self.callback``.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result from :attr:`check_update`.

        """
        if self.use_context:
            context = HandlerContext(update, dispatcher)
            self.collect_additional_context(context, update, dispatcher, check_result)
            return self.callback(update, context)
        else:
            optional_args = self.collect_optional_args(dispatcher, update, check_result)
            return self.callback(dispatcher.bot, update, **optional_args)

    def collect_additional_context(self, context, update, dispatcher, check_result):
        """Prepares additional arguments for the context. Override if needed.

        Args:
            context (:class:`telegram.ext.HandlerContext`): The context object.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result (return value) from :attr:`check_update`.

        """
        pass

    def collect_optional_args(self, dispatcher, update=None, check_result=None):
        """
        Prepares the optional arguments. If the handler has additional optional args,
        it should subclass this method, but remember to call this super method.

        DEPRECATED: This method is being replaced by new Context Based Handlers. Please see
        https://git.io/vpVe8 for more info.

        Args:
            dispatcher (:class:`telegram.ext.Dispatcher`): The dispatcher.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            check_result: The result from check_update

        """
        optional_args = dict()

        if self.pass_update_queue:
            optional_args['update_queue'] = dispatcher.update_queue
        if self.pass_job_queue:
            optional_args['job_queue'] = dispatcher.job_queue
        if self.pass_user_data or self.pass_chat_data:
            chat = update.effective_chat
            user = update.effective_user

            if self.pass_user_data:
                optional_args['user_data'] = dispatcher.user_data[user.id if user else None]

            if self.pass_chat_data:
                optional_args['chat_data'] = dispatcher.chat_data[chat.id if chat else None]

        return optional_args


class HandlerContext(object):
    """This is a context object passed to the callback called by :class:`telegram.ext.Handler`.

    Attributes:
        chat_data (:obj:`dict`, optional): A dict that can be used to keep any data in. For each
            update from the same chat it will be the same ``dict``.
        user_data (:obj:`dict`, optional): A dict that can be used to keep any data in. For each
            update from the same user it will be the same ``dict``.
        match (:obj:`re match object`, optional): If the associated update originated from a
            regex-supported handler, this will contain the object returned from
            ``re.match(pattern, string)``.
        args (List[:obj:`str`], optional): Arguments passed to a command if the associated update
            is handled by :class:`telegram.ext.CommandHandler` or
            :class:`telegram.ext.StringCommandHandler`. It contains a list of the words in the text
            after the command, using any whitespace string as a delimiter.

    """
    def __init__(self, update, dispatcher):
        """
        Args:
            update (:class:`telegram.Update`):
            dispatcher (:class:`telegram.ext.Dispatcher`):

        """
        self.update = update
        self._dispatcher = dispatcher
        self.chat_data = None
        self.user_data = None
        self.args = None
        self.match = None

        if update is not None and isinstance(update, Update):
            chat = update.effective_chat
            user = update.effective_user

            if chat:
                self.chat_data = dispatcher.chat_data[chat.id]
            if user:
                self.user_data = dispatcher.user_data[user.id]

    @property
    def bot(self):
        """:class:`telegram.Bot`: The bot associated with this context."""
        return self._dispatcher.bot

    @property
    def job_queue(self):
        """
        :class:`telegram.ext.JobQueue`: The ``JobQueue`` used by the
            :class:`telegram.ext.Dispatcher` and (usually) the :class:`telegrm.ext.Updater`
            associated with this context.

        """
        return self._dispatcher.job_queue

    @property
    def update_queue(self):
        """
        :class:`queue.Queue`: The ``Queue`` instance used by the
            :class:`telegram.ext.Dispatcher` and (usually) the :class:`telegrm.ext.Updater`
            associated with this context.

        """
        return self._dispatcher.update_queue
