#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
""" This module contains the base class for handlers as used by the
Dispatcher """

from telegram.utils.deprecate import deprecate
from telegram.utils.helpers import extract_chat_and_user


class Handler(object):
    """
    The base class for all update handlers. You can create your own handlers
    by inheriting from this class.

    Args:
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        pass_update_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the ``Updater`` and ``Dispatcher`` that contains new updates which can
             be used to insert updates. Default is ``False``.
        pass_job_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a ``JobQueue``
            instance created by the ``Updater`` which can be used to schedule new jobs.
            Default is ``False``.
        pass_user_data (optional[bool]): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the user that sent the update. For each update of
            the same user, it will be the same ``dict``. Default is ``False``.
        pass_chat_data (optional[bool]): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the chat that the update was sent in.
            For each update in the same chat, it will be the same ``dict``. Default is ``False``.
    """

    def __init__(self,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        self.callback = callback
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data

    def check_update(self, update):
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (object): The update to be tested

        Returns:
            bool
        """
        raise NotImplementedError

    def handle_update(self, update, dispatcher):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. It should also be overridden, but in most
        cases call ``self.callback(dispatcher.bot, update)``, possibly along with
        optional arguments. To work with the ``ConversationHandler``, this method should return the
        value returned from ``self.callback``

        Args:
            update (object): The update to be handled
            dispatcher (Dispatcher): The dispatcher to collect optional args

        """
        raise NotImplementedError

    def collect_optional_args(self, dispatcher, update=None):
        """
        Prepares the optional arguments that are the same for all types of
        handlers

        Args:
            dispatcher (Dispatcher):
        """
        optional_args = dict()

        if self.pass_update_queue:
            optional_args['update_queue'] = dispatcher.update_queue
        if self.pass_job_queue:
            optional_args['job_queue'] = dispatcher.job_queue
        if self.pass_user_data or self.pass_chat_data:
            chat, user = extract_chat_and_user(update)

            if self.pass_user_data:
                optional_args['user_data'] = dispatcher.user_data[user.id]

            if self.pass_chat_data:
                optional_args['chat_data'] = dispatcher.chat_data[chat.id if chat else None]

        return optional_args

    # old non-PEP8 Handler methods
    m = "telegram.Handler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
    collectOptionalArgs = deprecate(collect_optional_args, m + "collectOptionalArgs",
                                    m + "collect_optional_args")
