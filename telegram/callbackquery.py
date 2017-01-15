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
"""This module contains an object that represents a Telegram CallbackQuery"""

from telegram import TelegramObject, Message, User


class CallbackQuery(TelegramObject):
    """This object represents a Telegram CallbackQuery."""

    def __init__(self,
                 id,
                 from_user,
                 chat_instance,
                 message=None,
                 data=None,
                 inline_message_id=None,
                 game_short_name=None,
                 bot=None,
                 **kwargs):
        # Required
        self.id = id
        self.from_user = from_user
        self.chat_instance = chat_instance
        # Optionals
        self.message = message
        self.data = data
        self.inline_message_id = inline_message_id
        self.game_short_name = game_short_name

        self.bot = bot

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.CallbackQuery:
        """

        if not data:
            return None

        data = super(CallbackQuery, CallbackQuery).de_json(data, bot)

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['message'] = Message.de_json(data.get('message'), bot)

        return CallbackQuery(bot=bot, **data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(CallbackQuery, self).to_dict()

        # Required
        data['from'] = data.pop('from_user', None)
        return data

    def answer(self, *args, **kwargs):
        """Shortcut for ``bot.answerCallbackQuery(update.callback_query.id, *args, **kwargs)``"""
        return self.bot.answerCallbackQuery(self.id, *args, **kwargs)

    def edit_message_text(self, *args, **kwargs):
        """
        Shortcut for either ``bot.editMessageText(chat_id=update.callback_query.message.chat_id, \
message_id=update.callback_query.message.message_id, \
*args, **kwargs)``
        or ``bot.editMessageText(inline_message_id=update.callback_query.inline_message_id, \
*args, **kwargs)``
        """
        if self.inline_message_id:
            return self.bot.edit_message_text(
                inline_message_id=self.inline_message_id, *args, **kwargs)
        else:
            return self.bot.edit_message_text(
                chat_id=self.message.chat_id, message_id=self.message.message_id, *args, **kwargs)

    def edit_message_caption(self, *args, **kwargs):
        """
        Shortcut for either
        ``bot.editMessageCaption(chat_id=update.callback_query.message.chat_id, \
message_id=update.callback_query.message.message_id, \
*args, **kwargs)``
        or
        ``bot.editMessageCaption(inline_message_id=update.callback_query.inline_message_id, \
*args, **kwargs)``
        """
        if self.inline_message_id:
            return self.bot.edit_message_caption(
                inline_message_id=self.inline_message_id, *args, **kwargs)
        else:
            return self.bot.edit_message_caption(
                chat_id=self.message.chat_id, message_id=self.message.message_id, *args, **kwargs)

    def edit_message_reply_markup(self, *args, **kwargs):
        """
        Shortcut for either
        ``bot.editMessageReplyMarkup(chat_id=update.callback_query.message.chat_id, \
message_id=update.callback_query.message.message_id, \
*args, **kwargs)``
        or
        ``bot.editMessageReplyMarkup(inline_message_id=update.callback_query.inline_message_id, \
*args, **kwargs)``
        """
        if self.inline_message_id:
            return self.bot.edit_message_reply_markup(
                inline_message_id=self.inline_message_id, *args, **kwargs)
        else:
            return self.bot.edit_message_reply_markup(
                chat_id=self.message.chat_id, message_id=self.message.message_id, *args, **kwargs)
