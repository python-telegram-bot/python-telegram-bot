#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
""" This module contains the MessageHandler class """
import warnings

from .handler import Handler
from telegram import Update


class MessageHandler(Handler):
    """
    Handler class to handle telegram messages. Messages are Telegram Updates
    that do not contain a command. They might contain text, media or status
    updates.

    Args:
        filters (telegram.ext.BaseFilter): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or).
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        pass_update_queue (optional[bool]): If the handler should be passed the
            update queue as a keyword argument called ``update_queue``. It can
            be used to insert updates. Default is ``False``
        pass_user_data (optional[bool]): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the user that sent the update. For each update of
            the same user, it will be the same ``dict``. Default is ``False``.
        pass_chat_data (optional[bool]): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the chat that the update was sent in.
            For each update in the same chat, it will be the same ``dict``. Default is ``False``.
        message_updates (Optional[bool]): Should "normal" message updates be handled? Default is
            ``True``.
        allow_edited (Optional[bool]): If the handler should also accept edited messages.
            Default is ``False`` - Deprecated. use edited updates instead.
        channel_post_updates (Optional[bool]): Should channel posts updates be handled? Default is
            ``True``.
        edited_updates (Optional[bool]): Should "edited" message updates be handled? Default is
            ``False``.

    """

    def __init__(self,
                 filters,
                 callback,
                 allow_edited=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 message_updates=True,
                 channel_post_updates=True,
                 edited_updates=False):
        if not message_updates and not channel_post_updates and not edited_updates:
            raise ValueError(
                'message_updates, channel_post_updates and edited_updates are all False')
        if allow_edited:
            warnings.warn('allow_edited is getting deprecated, please use edited_updates instead')
            edited_updates = allow_edited

        super(MessageHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)
        self.filters = filters
        self.message_updates = message_updates
        self.channel_post_updates = channel_post_updates
        self.edited_updates = edited_updates

        # We put this up here instead of with the rest of checking code
        # in check_update since we don't wanna spam a ton
        if isinstance(self.filters, list):
            warnings.warn('Using a list of filters in MessageHandler is getting '
                          'deprecated, please use bitwise operators (& and |) '
                          'instead. More info: https://git.io/vPTbc.')

    def _is_allowed_update(self, update):
        return any([(self.message_updates and update.message),
                    (self.edited_updates and update.edited_message),
                    (self.channel_post_updates and update.channel_post)])

    def check_update(self, update):
        if isinstance(update, Update) and self._is_allowed_update(update):

            if not self.filters:
                res = True

            else:
                message = update.effective_message
                if isinstance(self.filters, list):
                    res = any(func(message) for func in self.filters)
                else:
                    res = self.filters(message)

        else:
            res = False

        return res

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)

        return self.callback(dispatcher.bot, update, **optional_args)
