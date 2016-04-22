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

from .filters import *  # flake8: noqa


class MessageHandler(Handler):
    """
    Handler class to handle telegram messages. Messages are Telegram Updates
    that do not contain a command. They might contain text, media or status
    updates.

    Args:
        filters (list): A list of filters defined in ``telegram.ext.filters``.
            All messages that match at least one of those filters will be
            accepted. If ``bool(filters)`` evaluates to ``False``, messages are
            not filtered.
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``checkUpdate``
            has determined that an update should be processed by this handler.
        pass_update_queue (optional[bool]): If the handler should be passed the
            update queue as a keyword argument called ``update_queue``. It can
            be used to insert updates. Default is ``False``
    """

    def __init__(self, filters, callback, pass_update_queue=False):
        super(MessageHandler, self).__init__(callback, pass_update_queue)
        self.filters = filters

    def checkUpdate(self, update):
        filters = self.filters
        if isinstance(update, Update) and update.message:
            message = update.message
            return (not filters or  # If filters is empty, accept all messages
                    TEXT in filters and message.text and
                    not message.text.startswith('/') or
                    AUDIO in filters and message.audio or
                    DOCUMENT in filters and message.document or
                    PHOTO in filters and message.photo or
                    STICKER in filters and message.sticker or
                    VIDEO in filters and message.video or
                    VOICE in filters and message.voice or
                    CONTACT in filters and message.contact or
                    LOCATION in filters and message.location or
                    VENUE in filters and message.venue or
                    STATUS_UPDATE in filters and (
                        message.new_chat_member or
                        message.left_chat_member or
                        message.new_chat_title or
                        message.new_chat_photo or
                        message.delete_chat_photo or
                        message.group_chat_created or
                        message.supergroup_chat_created or
                        message.channel_chat_created or
                        message.migrate_to_chat_id or
                        message.migrate_from_chat_id or
                        message.pinned_message)
                    )
        else:
            return False

    def handleUpdate(self, update, dispatcher):
        optional_args = self.collectOptionalArgs(dispatcher)

        self.callback(dispatcher.bot, update, **optional_args)
