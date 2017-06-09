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
"""This module contains an object that represents a Telegram Update."""

from telegram import (Message, TelegramObject, InlineQuery, ChosenInlineResult,
                      CallbackQuery, ShippingQuery, PreCheckoutQuery)


class Update(TelegramObject):
    """This object represents a Telegram Update.

    Attributes:
        update_id (int): The update's unique identifier.
        message (:class:`telegram.Message`): New incoming message of any kind - text, photo,
            sticker, etc.
        edited_message (:class:`telegram.Message`): New version of a message that is known to the
            bot and was edited
        inline_query (:class:`telegram.InlineQuery`): New incoming inline query.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`): The result of an inline query
            that was chosen by a user and sent to their chat partner.
        callback_query (:class:`telegram.CallbackQuery`): New incoming callback query.
        channel_post (Optional[:class:`telegram.Message`]): New incoming channel post of any kind -
            text, photo, sticker, etc.
        edited_channel_post (Optional[:class:`telegram.Message`]): New version of a channel post
            that is known to the bot and was edited.
        shipping_query (:class:`telegram.ShippingQuery`): New incoming shipping query.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`): New incoming pre-checkout query.


    Args:
        update_id (int):
        message (Optional[:class:`telegram.Message`]):
        edited_message (Optional[:class:`telegram.Message`]):
        inline_query (Optional[:class:`telegram.InlineQuery`]):
        chosen_inline_result (Optional[:class:`telegram.ChosenInlineResult`])
        callback_query (Optional[:class:`telegram.CallbackQuery`]):
        channel_post (Optional[:class:`telegram.Message`]):
        edited_channel_post (Optional[:class:`telegram.Message`]):
        shipping_query (Optional[:class:`telegram.ShippingQuery`]):
        pre_checkout_query (Optional[:class:`telegram.PreCheckoutQuery`]):
        **kwargs: Arbitrary keyword arguments.

    """

    def __init__(self,
                 update_id,
                 message=None,
                 edited_message=None,
                 inline_query=None,
                 chosen_inline_result=None,
                 callback_query=None,
                 channel_post=None,
                 edited_channel_post=None,
                 shipping_query=None,
                 pre_checkout_query=None,
                 **kwargs):
        # Required
        self.update_id = int(update_id)
        # Optionals
        self.message = message
        self.edited_message = edited_message
        self.inline_query = inline_query
        self.chosen_inline_result = chosen_inline_result
        self.callback_query = callback_query
        self.shipping_query = shipping_query
        self.pre_checkout_query = pre_checkout_query
        self.channel_post = channel_post
        self.edited_channel_post = edited_channel_post

        self._effective_user = None
        self._effective_chat = None
        self._effective_message = None

        self._id_attrs = (self.update_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Update:
        """
        if not data:
            return None

        data = super(Update, Update).de_json(data, bot)

        data['message'] = Message.de_json(data.get('message'), bot)
        data['edited_message'] = Message.de_json(data.get('edited_message'), bot)
        data['inline_query'] = InlineQuery.de_json(data.get('inline_query'), bot)
        data['chosen_inline_result'] = ChosenInlineResult.de_json(
            data.get('chosen_inline_result'), bot)
        data['callback_query'] = CallbackQuery.de_json(data.get('callback_query'), bot)
        data['shipping_query'] = ShippingQuery.de_json(data.get('shipping_query'), bot)
        data['pre_checkout_query'] = PreCheckoutQuery.de_json(data.get('pre_checkout_query'), bot)
        data['channel_post'] = Message.de_json(data.get('channel_post'), bot)
        data['edited_channel_post'] = Message.de_json(data.get('edited_channel_post'), bot)

        return Update(**data)

    @property
    def effective_user(self):
        """
        A property that contains the ``User`` that sent this update, no matter what kind of update
        this is. Will be ``None`` for channel posts.
        """

        if self._effective_user:
            return self._effective_user

        user = None

        if self.message:
            user = self.message.from_user

        elif self.edited_message:
            user = self.edited_message.from_user

        elif self.inline_query:
            user = self.inline_query.from_user

        elif self.chosen_inline_result:
            user = self.chosen_inline_result.from_user

        elif self.callback_query:
            user = self.callback_query.from_user

        elif self.shipping_query:
            user = self.shipping_query.from_user

        elif self.pre_checkout_query:
            user = self.pre_checkout_query.from_user

        self._effective_user = user
        return user

    @property
    def effective_chat(self):
        """
        A property that contains the ``Chat`` that this update was sent in, no matter what kind of
        update this is. Will be ``None`` for inline queries and chosen inline results.
        """

        if self._effective_chat:
            return self._effective_chat

        chat = None

        if self.message:
            chat = self.message.chat

        elif self.edited_message:
            chat = self.edited_message.chat

        elif self.callback_query and self.callback_query.message:
            chat = self.callback_query.message.chat

        elif self.channel_post:
            chat = self.channel_post.chat

        elif self.edited_channel_post:
            chat = self.edited_channel_post.chat

        self._effective_chat = chat
        return chat

    @property
    def effective_message(self):
        """
        A property that contains the ``Message`` included in this update, no matter what kind
        of update this is. Will be ``None`` for inline queries, chosen inline results and callback
        queries from inline messages.
        """

        if self._effective_message:
            return self._effective_message

        message = None

        if self.message:
            message = self.message

        elif self.edited_message:
            message = self.edited_message

        elif self.callback_query:
            message = self.callback_query.message

        elif self.channel_post:
            message = self.channel_post

        elif self.edited_channel_post:
            message = self.edited_channel_post

        self._effective_message = message
        return message
