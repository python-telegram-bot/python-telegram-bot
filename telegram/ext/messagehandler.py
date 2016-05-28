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
    def text(message):
        return message.text and not message.text.startswith('/')

    @staticmethod
    def command(message):
        return message.text and message.text.startswith('/')

    @staticmethod
    def audio(message):
        return bool(message.audio)

    @staticmethod
    def document(message):
        return bool(message.document)

    @staticmethod
    def photo(message):
        return bool(message.photo)

    @staticmethod
    def sticker(message):
        return bool(message.sticker)

    @staticmethod
    def video(message):
        return bool(message.video)

    @staticmethod
    def voice(message):
        return bool(message.voice)

    @staticmethod
    def contact(message):
        return bool(message.contact)

    @staticmethod
    def location(message):
        return bool(message.location)

    @staticmethod
    def venue(message):
        return bool(message.venue)

    @staticmethod
    def status_update(message):
        return bool(message.new_chat_member or message.left_chat_member or message.new_chat_title
                    or message.new_chat_photo or message.delete_chat_photo
                    or message.group_chat_created or message.supergroup_chat_created
                    or message.channel_chat_created or message.migrate_to_chat_id
                    or message.migrate_from_chat_id or message.pinned_message)


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
        allow_edited (Optional[bool]): If the handler should also accept edited messages.
            Default is ``False``
        pass_update_queue (optional[bool]): If the handler should be passed the
            update queue as a keyword argument called ``update_queue``. It can
            be used to insert updates. Default is ``False``
    """

    def __init__(self, filters, callback, allow_edited=False, pass_update_queue=False):
        super(MessageHandler, self).__init__(callback, pass_update_queue)
        self.filters = filters
        self.allow_edited = allow_edited

    def check_update(self, update):
        if (isinstance(update, Update)
                and (update.message or update.edited_message and self.allow_edited)):

            if not self.filters:
                res = True

            else:
                message = update.message or update.edited_message
                res = any(func(message) for func in self.filters)

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
