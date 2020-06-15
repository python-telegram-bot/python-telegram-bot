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
"""This module contains an object that represents a Telegram CallbackQuery"""

from telegram import TelegramObject, Message, User


class CallbackQuery(TelegramObject):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.

    If the button that originated the query was attached to a message sent by the bot, the field
    :attr:`message` will be present. If the button was attached to a message sent via the bot (in
    inline mode), the field :attr:`inline_message_id` will be present.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.
        * Exactly one of the fields :attr:`data` or :attr:`game_short_name` will be present.

    Attributes:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent.
        message (:class:`telegram.Message`): Optional. Message with the callback button that
            originated the query.
        data (:obj:`str`): Optional. Data associated with the callback button.
        inline_message_id (:obj:`str`): Optional. Identifier of the message sent via the bot in
                inline mode, that originated the query.
        game_short_name (:obj:`str`): Optional. Short name of a Game to be returned.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Args:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        chat_instance (:obj:`str`): Global identifier, uniquely corresponding to the chat to which
            the message with the callback button was sent. Useful for high scores in games.
        message (:class:`telegram.Message`, optional): Message with the callback button that
            originated the query. Note that message content and message date will not be available
            if the message is too old.
        data (:obj:`str`, optional): Data associated with the callback button. Be aware that a bad
            client can send arbitrary data in this field.
        inline_message_id (:obj:`str`, optional): Identifier of the message sent via the bot in
            inline mode, that originated the query.
        game_short_name (:obj:`str`, optional): Short name of a Game to be returned, serves as
            the unique identifier for the game
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Note:
        After the user presses an inline button, Telegram clients will display a progress bar
        until you call :attr:`answer`. It is, therefore, necessary to react
        by calling :attr:`telegram.Bot.answer_callback_query` even if no notification to the user
        is needed (e.g., without specifying any of the optional parameters).

    """

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

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super().de_json(data, bot)

        data['from_user'] = User.de_json(data.get('from'), bot)
        message = data.get('message')
        if message:
            message['default_quote'] = data.get('default_quote')
        data['message'] = Message.de_json(message, bot)

        return cls(bot=bot, **data)

    def answer(self, *args, **kwargs):
        """Shortcut for::

            bot.answer_callback_query(update.callback_query.id, *args, **kwargs)

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        """
        return self.bot.answerCallbackQuery(self.id, *args, **kwargs)

    def edit_message_text(self, text, *args, **kwargs):
        """Shortcut for either::

            bot.edit_message_text(text, chat_id=update.callback_query.message.chat_id,
                                message_id=update.callback_query.message.message_id,
                                *args, **kwargs)

        or::

            bot.edit_message_text(text, inline_message_id=update.callback_query.inline_message_id,
                                *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_text(text, inline_message_id=self.inline_message_id,
                                              *args, **kwargs)
        else:
            return self.bot.edit_message_text(text, chat_id=self.message.chat_id,
                                              message_id=self.message.message_id, *args, **kwargs)

    def edit_message_caption(self, caption, *args, **kwargs):
        """Shortcut for either::

            bot.edit_message_caption(caption=caption,
                                   chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id,
                                   *args, **kwargs)

        or::

            bot.edit_message_caption(caption=caption
                                    inline_message_id=update.callback_query.inline_message_id,
                                   *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_caption(caption=caption,
                                                 inline_message_id=self.inline_message_id,
                                                 *args, **kwargs)
        else:
            return self.bot.edit_message_caption(caption=caption, chat_id=self.message.chat_id,
                                                 message_id=self.message.message_id,
                                                 *args, **kwargs)

    def edit_message_reply_markup(self, reply_markup, *args, **kwargs):
        """Shortcut for either::

            bot.edit_message_replyMarkup(chat_id=update.callback_query.message.chat_id,
                                       message_id=update.callback_query.message.message_id,
                                       reply_markup=reply_markup,
                                       *args, **kwargs)

        or::

            bot.edit_message_reply_markup(inline_message_id=update.callback_query.inline_message_id,
                                        reply_markup=reply_markup,
                                       *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        """
        if self.inline_message_id:
            return self.bot.edit_message_reply_markup(reply_markup=reply_markup,
                                                      inline_message_id=self.inline_message_id,
                                                      *args, **kwargs)
        else:
            return self.bot.edit_message_reply_markup(reply_markup=reply_markup,
                                                      chat_id=self.message.chat_id,
                                                      message_id=self.message.message_id,
                                                      *args, **kwargs)
