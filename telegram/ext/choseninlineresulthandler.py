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
""" This module contains the ChosenInlineResultHandler class """

from .handler import Handler
from telegram import Update
from telegram.utils.deprecate import deprecate


class ChosenInlineResultHandler(Handler):
    """
    Handler class to handle Telegram updates that contain a chosen inline
    result.

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
        super(ChosenInlineResultHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

    def check_update(self, update):
        return isinstance(update, Update) and update.chosen_inline_result

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)

        return self.callback(dispatcher.bot, update, **optional_args)

    # old non-PEP8 Handler methods
    m = "telegram.ChosenInlineResultHandler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
