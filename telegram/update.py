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
"""This module contains an object that represents a Telegram Update."""

from telegram import (Message, TelegramObject, InlineQuery, ChosenInlineResult, CallbackQuery)


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

    Args:
        update_id (int):
        message (Optional[:class:`telegram.Message`]):
        edited_message (Optional[:class:`telegram.Message`]):
        inline_query (Optional[:class:`telegram.InlineQuery`]):
        chosen_inline_result (Optional[:class:`telegram.ChosenInlineResult`])
        callback_query (Optional[:class:`telegram.CallbackQuery`]):
        channel_post (Optional[:class:`telegram.Message`]):
        edited_channel_post (Optional[:class:`telegram.Message`]):
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
                 **kwargs):
        # Required
        self.update_id = int(update_id)
        # Optionals
        self.message = message
        self.edited_message = edited_message
        self.inline_query = inline_query
        self.chosen_inline_result = chosen_inline_result
        self.callback_query = callback_query
        self.channel_post = channel_post
        self.edited_channel_post = edited_channel_post

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

        data['message'] = Message.de_json(data.get('message'), bot)
        data['edited_message'] = Message.de_json(data.get('edited_message'), bot)
        data['inline_query'] = InlineQuery.de_json(data.get('inline_query'), bot)
        data['chosen_inline_result'] = ChosenInlineResult.de_json(
            data.get('chosen_inline_result'), bot)
        data['callback_query'] = CallbackQuery.de_json(data.get('callback_query'), bot)
        data['channel_post'] = Message.de_json(data.get('channel_post'), bot)
        data['edited_channel_post'] = Message.de_json(data.get('edited_channel_post'), bot)

        return Update(**data)
