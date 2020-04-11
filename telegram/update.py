#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
                      CallbackQuery, ShippingQuery, PreCheckoutQuery, Poll)
from telegram.poll import PollAnswer


class Update(TelegramObject):
    """This object represents an incoming update.

    Note:
        At most one of the optional parameters can be present in any given update.

    Attributes:
        update_id (:obj:`int`): The update's unique identifier.
        message (:class:`telegram.Message`): Optional. New incoming message.
        edited_message (:class:`telegram.Message`): Optional. New version of a message.
        channel_post (:class:`telegram.Message`): Optional. New incoming channel post.
        edited_channel_post (:class:`telegram.Message`): Optional. New version of a channel post.
        inline_query (:class:`telegram.InlineQuery`): Optional. New incoming inline query.
        chosen_inline_result (:class:`telegram.ChosenInlineResult`): Optional. The result of an
            inline query that was chosen by a user.
        callback_query (:class:`telegram.CallbackQuery`): Optional. New incoming callback query.
        shipping_query (:class:`telegram.ShippingQuery`): Optional. New incoming shipping query.
        pre_checkout_query (:class:`telegram.PreCheckoutQuery`): Optional. New incoming
            pre-checkout query.
        poll (:class:`telegram.Poll`): Optional. New poll state. Bots receive only updates
            about stopped polls and polls, which are sent by the bot
        poll_answer (:class:`telegram.PollAnswer`): Optional. A user changed their answer
            in a non-anonymous poll. Bots receive new votes only in polls that were sent
            by the bot itself.

    Args:
        update_id (:obj:`int`): The update's unique identifier. Update identifiers start from a
            certain positive number and increase sequentially. This ID becomes especially handy if
            you're using Webhooks, since it allows you to ignore repeated updates or to restore the
            correct update sequence, should they get out of order.
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
        poll (:class:`telegram.Poll`, optional): New poll state. Bots receive only updates
            about polls, which are sent or stopped by the bot
        poll_answer (:class:`telegram.PollAnswer`, optional): A user changed their answer
            in a non-anonymous poll. Bots receive new votes only in polls that were sent
            by the bot itself.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 update_id,
                 message=None,
                 edited_message=None,
                 channel_post=None,
                 edited_channel_post=None,
                 inline_query=None,
                 chosen_inline_result=None,
                 callback_query=None,
                 shipping_query=None,
                 pre_checkout_query=None,
                 poll=None,
                 poll_answer=None,
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
        self.poll = poll
        self.poll_answer = poll_answer

        self._effective_user = None
        self._effective_chat = None
        self._effective_message = None

        self._id_attrs = (self.update_id,)

    @property
    def effective_user(self):
        """
        :class:`telegram.User`: The user that sent this update, no matter what kind of update this
            is. Will be ``None`` for :attr:`channel_post` and :attr:`poll`.

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

        elif self.poll_answer:
            user = self.poll_answer.user

        self._effective_user = user
        return user

    @property
    def effective_chat(self):
        """
        :class:`telegram.Chat`: The chat that this update was sent in, no matter what kind of
            update this is. Will be ``None`` for :attr:`inline_query`,
            :attr:`chosen_inline_result`, :attr:`callback_query` from inline messages,
            :attr:`shipping_query`, :attr:`pre_checkout_query`, :attr:`poll` and
            :attr:`poll_answer`.

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
        :class:`telegram.Message`: The message included in this update, no matter what kind of
            update this is. Will be ``None`` for :attr:`inline_query`,
            :attr:`chosen_inline_result`, :attr:`callback_query` from inline messages,
            :attr:`shipping_query`, :attr:`pre_checkout_query`, :attr:`poll` and
            :attr:`poll_answer`.

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

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super().de_json(data, bot)

        message = data.get('message')
        if message:
            message['default_quote'] = data.get('default_quote')
        data['message'] = Message.de_json(message, bot)
        edited_message = data.get('edited_message')
        if edited_message:
            edited_message['default_quote'] = data.get('default_quote')
        data['edited_message'] = Message.de_json(edited_message, bot)
        data['inline_query'] = InlineQuery.de_json(data.get('inline_query'), bot)
        data['chosen_inline_result'] = ChosenInlineResult.de_json(
            data.get('chosen_inline_result'), bot)
        callback_query = data.get('callback_query')
        if callback_query:
            callback_query['default_quote'] = data.get('default_quote')
        data['callback_query'] = CallbackQuery.de_json(callback_query, bot)
        data['shipping_query'] = ShippingQuery.de_json(data.get('shipping_query'), bot)
        data['pre_checkout_query'] = PreCheckoutQuery.de_json(data.get('pre_checkout_query'), bot)
        channel_post = data.get('channel_post')
        if channel_post:
            channel_post['default_quote'] = data.get('default_quote')
        data['channel_post'] = Message.de_json(channel_post, bot)
        edited_channel_post = data.get('edited_channel_post')
        if edited_channel_post:
            edited_channel_post['default_quote'] = data.get('default_quote')
        data['edited_channel_post'] = Message.de_json(edited_channel_post, bot)
        data['poll'] = Poll.de_json(data.get('poll'), bot)
        data['poll_answer'] = PollAnswer.de_json(data.get('poll_answer'), bot)

        return cls(**data)
