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


class Context(object):
    """

    Attributes:
        bot:
        update:
        chat_data:
        user_data:
        groups:
        groupdict:
        job_queue:
        update_queue:
        args:
        message (:class:`telegram.Message`, optional): New incoming message of any kind - text,
            photo, sticker, etc.
        edited_message (:class:`telegram.Message`, optional): New version of a message that is
            known to the bot and was edited.
        channel_post (:class:`telegram.Message`, optional): New incoming channel post of any kind
            - text, photo, sticker, etc.
        edited_channel_post (:class:`telegram.Message`, optional): New version of a channel post
            that is known to the bot and was edited.
        inline_query (:class:`telegram.InlineQuery`, optional): New incoming inline query.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`, optional): The result of an
            inline query that was chosen by a user and sent to their chat partner.
        callback_query (:class:`telegram.CallbackQuery`, optional): New incoming callback query.
        shipping_query (:class:`telegram.ShippingQuery`, optional): New incoming shipping query.
            Only for invoices with flexible price.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`, optional): New incoming
            pre-checkout query. Contains full information about checkout
    """

    def __init__(self, update, dispatcher):
        self.update = update
        self.bot = dispatcher.bot
        self.chat_data = None
        self.user_data = None
        if update is not None:
            chat = update.effective_chat
            user = update.effective_user

            if chat:
                self.chat_data = dispatcher.chat_data[chat.id]
            if user:
                self.user_data = dispatcher.user_data[user.id]

        self.job_queue = dispatcher.job_queue
        self.update_queue = dispatcher.update_queue

        self.message = self.update.message
        self.edited_message = self.update.edited_message
        self.inline_query = self.update.inline_query
        self.chosen_inline_result = self.update.chosen_inline_result
        self.callback_query = self.update.callback_query
        self.shipping_query = self.update.shipping_query
        self.pre_checkout_query = self.update.pre_checkout_query
        self.channel_post = self.update.channel_post
        self.edited_channel_post = self.update.edited_channel_post

        self.args = None
        self.groups = None
        self.groupdict = None
