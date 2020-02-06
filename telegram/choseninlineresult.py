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
"""This module contains an object that represents a Telegram ChosenInlineResult."""

from telegram import TelegramObject, User, Location


class ChosenInlineResult(TelegramObject):
    """
    Represents a result of an inline query that was chosen by the user and sent to their chat
    partner.

    Note:
        In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        result_id (:obj:`str`): The unique identifier for the result that was chosen.
        from_user (:class:`telegram.User`): The user that chose the result.
        location (:class:`telegram.Location`): Optional. Sender location.
        inline_message_id (:obj:`str`): Optional. Identifier of the sent inline message.
        query (:obj:`str`): The query that was used to obtain the result.

    Args:
        result_id (:obj:`str`): The unique identifier for the result that was chosen.
        from_user (:class:`telegram.User`): The user that chose the result.
        location (:class:`telegram.Location`, optional): Sender location, only for bots that
            require user location.
        inline_message_id (:obj:`str`, optional): Identifier of the sent inline message. Available
            only if there is an inline keyboard attached to the message. Will be also received in
            callback queries and can be used to edit the message.
        query (:obj:`str`): The query that was used to obtain the result.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 result_id,
                 from_user,
                 query,
                 location=None,
                 inline_message_id=None,
                 **kwargs):
        # Required
        self.result_id = result_id
        self.from_user = from_user
        self.query = query
        # Optionals
        self.location = location
        self.inline_message_id = inline_message_id

        self._id_attrs = (self.result_id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(ChosenInlineResult, cls).de_json(data, bot)
        # Required
        data['from_user'] = User.de_json(data.pop('from'), bot)
        # Optionals
        data['location'] = Location.de_json(data.get('location'), bot)

        return cls(**data)
