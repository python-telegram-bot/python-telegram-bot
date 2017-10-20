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
# TODO: Remove allow_edited
"""This module contains the MessageHandler class."""
import warnings

from telegram import Update
from .handler import Handler


class MessageHandler(Handler):
    """Handler class to handle telegram messages. They might contain text, media or status updates.

    Attributes:
        filters (:obj:`Filter`): Only allow updates with these Filters. See
            :mod:`telegram.ext.filters` for a full list of all available filters.
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Optional. Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Optional. Determines whether ``chat_data`` will be passed to
            the callback function.
        message_updates (:obj:`bool`): Optional. Should "normal" message updates be handled?
            Default is ``True``.
        channel_post_updates (:obj:`bool`): Optional. Should channel posts updates be handled?
            Default is ``True``.
        edited_updates (:obj:`bool`): Optional. Should "edited" message updates be handled?
            Default is ``False``.
        allow_edited (:obj:`bool`): Optional. If the handler should also accept edited messages.
            Default is ``False`` - Deprecated. use edited_updates instead.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

    Args:
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.
        message_updates (:obj:`bool`, optional): Should "normal" message updates be handled?
            Default is ``True``.
        channel_post_updates (:obj:`bool`, optional): Should channel posts updates be handled?
            Default is ``True``.
        edited_updates (:obj:`bool`, optional): Should "edited" message updates be handled? Default
            is ``False``.
        allow_edited (:obj:`bool`, optional): If the handler should also accept edited messages.
            Default is ``False`` - Deprecated. use edited_updates instead.

    Raises:
        ValueError

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
        return any([self.message_updates and update.message,
                    self.edited_updates and (update.edited_message or update.edited_channel_post),
                    self.channel_post_updates and update.channel_post])

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
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
        """Send the update to the :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the Update.

        """
        optional_args = self.collect_optional_args(dispatcher, update)

        return self.callback(dispatcher.bot, update, **optional_args)
