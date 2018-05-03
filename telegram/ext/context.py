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
    This object represents an incoming update from a telegram bot.
    It operates like a supercharged :class:`telegram.Update`, in that it includes
    data that the handler passed along.
    To use it set :attr:`use_context` to ``True`` when creating your handlers, and use the
    following signature for your callback functions ``def callbackname(context):``.
    Note that setting :attr:`use_context` may not be required unless using old versions of
    python or decorators on the callback.

    Attributes:
        bot (:class:`telegram.Bot`): The bot associated with this context.
        update (:class:`telegram.Update`): The update that spawned this context.
        chat_data (:obj:`dict`, optional): A dict that can be used to keep any data in. For each
            update from the same chat it will be the same ``dict``.
        user_data (:obj:`dict`, optional): A dict that can be used to keep any data in. For each
            update from the same user it will be the same ``dict``.
        groups (:obj:`tuple`, optional): If the associated update originated from a
            regex-supported handler, this will contain the ``re.match(pattern, data).groups()``.
        groupdict (:obj:`dict`, optional): If the associated update originated from a
            regex-supported handler, this will contain the ``re.match(pattern, data).groupdict()``.
        job_queue (:class:`telegram.ext.JobQueue`): The JobQueue created by the
            :class:`telegram.ext.Updater` which can be used to schedule new jobs.
        update_queue (:class:`queue.Queue`): The ``Queue`` instance used by the
            :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            which contains new updates and can be used to insert updates.
        args (List[:obj:`str`], optional): Arguments passed to a command if the associated update
            originated from a :class:`telegram.ext.CommandHandler` or a
            :class:`telegram.ext.StringCommandHandler`. It will contain a list of strings,
            which is the text following the command split on single or consecutive whitespace
            characters.
        message (:class:`telegram.Message`, optional): New incoming message of any kind - text,
            photo, sticker, etc. Extracted from :attr:`update`.
        edited_message (:class:`telegram.Message`, optional): New version of a message that is
            known to the bot and was edited. Extracted from :attr:`update`.
        channel_post (:class:`telegram.Message`, optional): New incoming channel post of any kind
            - text, photo, sticker, etc. Extracted from :attr:`update`.
        edited_channel_post (:class:`telegram.Message`, optional): New version of a channel post
            that is known to the bot and was edited. Extracted from :attr:`update`.
        inline_query (:class:`telegram.InlineQuery`, optional): New incoming inline query.
            Extracted from :attr:`update`.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`, optional): The result of an
            inline query that was chosen by a user and sent to their chat partner. Extracted
            from :attr:`update`.
        callback_query (:class:`telegram.CallbackQuery`, optional): New incoming callback query.
            Extracted from :attr:`update`.
        shipping_query (:class:`telegram.ShippingQuery`, optional): New incoming shipping query.
            Only for invoices with flexible price. Extracted from :attr:`update`.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`, optional): New incoming
            pre-checkout query. Contains full information about checkout. Extracted from
            :attr:`update`.
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
