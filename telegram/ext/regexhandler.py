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
# TODO: Remove allow_edited
"""This module contains the RegexHandler class."""

import warnings

from telegram.utils.deprecate import TelegramDeprecationWarning

from telegram.ext import MessageHandler, Filters


class RegexHandler(MessageHandler):
    """Handler class to handle Telegram updates based on a regex.

    It uses a regular expression to check text messages. Read the documentation of the ``re``
    module for more information. The ``re.match`` function is used to determine if an update should
    be handled by this handler.

    Attributes:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler.
        pass_groups (:obj:`bool`): Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Determines whether ``groupdict``. will be passed to
            the callback function.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.

    Note:
        This handler is being deprecated. For the same usecase use:
        ``MessageHandler(Filters.regex(r'pattern'), callback)``


    Args:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is ``False``
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is ``False``
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

    Raises:
        ValueError

    """

    def __init__(self,
                 pattern,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 allow_edited=False,
                 message_updates=True,
                 channel_post_updates=False,
                 edited_updates=False):
        warnings.warn('RegexHandler is deprecated. See https://git.io/fxJuV for more info',
                      TelegramDeprecationWarning,
                      stacklevel=2)
        super(RegexHandler, self).__init__(Filters.regex(pattern),
                                           callback,
                                           pass_update_queue=pass_update_queue,
                                           pass_job_queue=pass_job_queue,
                                           pass_user_data=pass_user_data,
                                           pass_chat_data=pass_chat_data,
                                           message_updates=message_updates,
                                           channel_post_updates=channel_post_updates,
                                           edited_updates=edited_updates)
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def collect_optional_args(self, dispatcher, update=None, check_result=None):
        optional_args = super(RegexHandler, self).collect_optional_args(dispatcher, update,
                                                                        check_result)
        if self.pass_groups:
            optional_args['groups'] = check_result['matches'][0].groups()
        if self.pass_groupdict:
            optional_args['groupdict'] = check_result['matches'][0].groupdict()
        return optional_args
