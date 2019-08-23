#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains an object that represents a Telegram Poll."""

from telegram import (TelegramObject)


class PollOption(TelegramObject):
    """
    This object contains information about one answer option in a poll.

    Attributes:
        text (:obj:`str`): Option text, 1-100 characters.
        voter_count (:obj:`int`): Number of users that voted for this option.

    Args:
        text (:obj:`str`): Option text, 1-100 characters.
        voter_count (:obj:`int`): Number of users that voted for this option.

    """

    def __init__(self, text, voter_count, **kwargs):
        self.text = text
        self.voter_count = voter_count

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)


class Poll(TelegramObject):
    """
    This object contains information about a poll.

    Attributes:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, 1-255 characters.
        options (List[:class:`PollOption`]): List of poll options.
        is_closed (:obj:`bool`): True, if the poll is closed.

    Args:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, 1-255 characters.
        options (List[:class:`PollOption`]): List of poll options.
        is_closed (:obj:`bool`): True, if the poll is closed.

    """

    def __init__(self, id, question, options, is_closed, **kwargs):
        self.id = id
        self.question = question
        self.options = options
        self.is_closed = is_closed

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Poll, cls).de_json(data, bot)

        data['options'] = [PollOption.de_json(option, bot) for option in data['options']]

        return cls(**data)

    def to_dict(self):
        data = super(Poll, self).to_dict()

        data['options'] = [x.to_dict() for x in self.options]

        return data
