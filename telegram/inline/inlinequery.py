#!/usr/bin/env python
# pylint: disable=R0902,R0912,R0913
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
"""This module contains an object that represents a Telegram InlineQuery."""

from telegram import TelegramObject, User, Location


class InlineQuery(TelegramObject):
    """
    This object represents an incoming inline query. When the user sends an empty query, your bot
    could return some default or trending results.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        location (:class:`telegram.Location`): Optional. Sender location, only for bots that
            request user location.
        query (:obj:`str`): Text of the query (up to 256 characters).
        offset (:obj:`str`): Offset of the results to be returned, can be controlled by the bot.

    Args:
        id (:obj:`str`): Unique identifier for this query.
        from_user (:class:`telegram.User`): Sender.
        location (:class:`telegram.Location`, optional): Sender location, only for bots that
            request user location.
        query (:obj:`str`): Text of the query (up to 256 characters).
        offset (:obj:`str`): Offset of the results to be returned, can be controlled by the bot.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, id, from_user, query, offset, location=None, bot=None, **kwargs):
        # Required
        self.id = id
        self.from_user = from_user
        self.query = query
        self.offset = offset

        # Optional
        self.location = location

        self.bot = bot
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data, bot):
        data = super(InlineQuery, cls).de_json(data, bot)

        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['location'] = Location.de_json(data.get('location'), bot)

        return cls(bot=bot, **data)

    def answer(self, *args, **kwargs):
        """Shortcut for::

            bot.answer_inline_query(update.inline_query.id, *args, **kwargs)

        Args:
            results (List[:class:`telegram.InlineQueryResult`]): A list of results for the inline
                query.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the inline query may be cached on the server. Defaults to 300.
            is_personal (:obj:`bool`, optional): Pass True, if results may be cached on the server
                side only for the user that sent the query. By default, results may be returned to
                any user who sends the same query.
            next_offset (:obj:`str`, optional): Pass the offset that a client should send in the
                next query with the same text to receive more results. Pass an empty string if
                there are no more results or if you don't support pagination. Offset length can't
                exceed 64 bytes.
            switch_pm_text (:obj:`str`, optional): If passed, clients will display a button with
                specified text that switches the user to a private chat with the bot and sends the
                bot a start message with the parameter switch_pm_parameter.
            switch_pm_parameter (:obj:`str`, optional): Deep-linking parameter for the /start
                message sent to the bot when user presses the switch button. 1-64 characters,
                only A-Z, a-z, 0-9, _ and - are allowed.

        """
        return self.bot.answer_inline_query(self.id, *args, **kwargs)
