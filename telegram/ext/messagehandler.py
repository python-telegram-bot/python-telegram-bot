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
""" This module contains the MessageHandler class """

from .handler import Handler
from telegram import Update
from telegram.utils.deprecate import deprecate


class Filters(object):
    """
    Convenient namespace (class) & methods for the filter funcs of the
    MessageHandler class.
    """

    @staticmethod
    def text(update):
        return update.message.text and not update.message.text.startswith('/')

    @staticmethod
    def command(update):
        return update.message.text and update.message.text.startswith('/')

    @staticmethod
    def audio(update):
        return bool(update.message.audio)

    @staticmethod
    def document(update):
        return bool(update.message.document)

    @staticmethod
    def photo(update):
        return bool(update.message.photo)

    @staticmethod
    def sticker(update):
        return bool(update.message.sticker)

    @staticmethod
    def video(update):
        return bool(update.message.video)

    @staticmethod
    def voice(update):
        return bool(update.message.voice)

    @staticmethod
    def contact(update):
        return bool(update.message.contact)

    @staticmethod
    def location(update):
        return bool(update.message.location)

    @staticmethod
    def venue(update):
        return bool(update.message.venue)

    @staticmethod
    def status_update(update):
        # yapf: disable
        # https://github.com/google/yapf/issues/252
        return bool(update.message.new_chat_member or update.message.left_chat_member or
                    update.message.new_chat_title or update.message.new_chat_photo or
                    update.message.delete_chat_photo or update.message.group_chat_created or
                    update.message.supergroup_chat_created or
                    update.message.channel_chat_created or update.message.migrate_to_chat_id or
                    update.message.migrate_from_chat_id or update.message.pinned_message)
        # yapf: enable


class MessageHandler(Handler):
    """
    Handler class to handle telegram messages. Messages are Telegram Updates
    that do not contain a command. They might contain text, media or status
    updates.

    Args:
        filters (list[function]): A list of filter functions. Standard filters
            can be found in the Filters class above.
          | Each `function` takes ``Update`` as arg and returns ``bool``.
          | All messages that match at least one of those filters will be
            accepted. If ``bool(filters)`` evaluates to ``False``, messages are
            not filtered.
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        pass_update_queue (optional[bool]): If the handler should be passed the
            update queue as a keyword argument called ``update_queue``. It can
            be used to insert updates. Default is ``False``
    """

    def __init__(self, filters, callback, pass_update_queue=False):
        super(MessageHandler, self).__init__(callback, pass_update_queue)
        self.filters = filters

    def check_update(self, update):
        if isinstance(update, Update) and update.message:
            if not self.filters:
                res = True
            else:
                res = any(func(update) for func in self.filters)
        else:
            res = False
        return res

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher)

        self.callback(dispatcher.bot, update, **optional_args)

    # old non-PEP8 Handler methods
    m = "telegram.MessageHandler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
