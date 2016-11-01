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
""" This module contains the TypeHandler class """

from .handler import Handler
from telegram.utils.deprecate import deprecate


class TypeHandler(Handler):
    """
    Handler class to handle updates of custom types.

    Args:
        type (type): The ``type`` of updates this handler should process, as
            determined by ``isinstance``
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        strict (optional[bool]): Use ``type`` instead of ``isinstance``.
            Default is ``False``
        pass_update_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the ``Updater`` and ``Dispatcher`` that contains new updates which can
            be used to insert updates. Default is ``False``.
        pass_job_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a ``JobQueue``
            instance created by the ``Updater`` which can be used to schedule new jobs.
            Default is ``False``.
    """

    def __init__(self, type, callback, strict=False, pass_update_queue=False,
                 pass_job_queue=False):
        super(TypeHandler, self).__init__(
            callback, pass_update_queue=pass_update_queue, pass_job_queue=pass_job_queue)
        self.type = type
        self.strict = strict

    def check_update(self, update):
        if not self.strict:
            return isinstance(update, self.type)
        else:
            return type(update) is self.type

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher)

        return self.callback(dispatcher.bot, update, **optional_args)

    # old non-PEP8 Handler methods
    m = "telegram.TypeHandler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
