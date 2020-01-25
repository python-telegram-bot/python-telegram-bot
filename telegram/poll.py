#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains an object that represents a Telegram Poll."""

from telegram import (TelegramObject, User)


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


class PollAnswer(TelegramObject):
    """
    This object represents an answer of a user in a non-anonymous poll.

    Attributes:
        poll_id (:obj:`str`): Unique poll identifier.
        user (:class:`telegram.User`): The user, who changed the answer to the poll.
        option_ids (List[:obj:`int`]): Identifiers of answer options, chosen by the user.

    Args:
        poll_id (:obj:`str`): Unique poll identifier.
        user (:class:`telegram.User`): The user, who changed the answer to the poll.
        option_ids (List[:obj:`int`]): 0-based identifiers of answer options, chosen by the user.
            May be empty if the user retracted their vote.

    """
    def __init__(self, poll_id, user, option_ids, **kwargs):
        self.poll_id = poll_id
        self.user = user
        self.option_ids = option_ids

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(PollAnswer, cls).de_json(data, bot)

        data['user'] = User.de_json(data.get('user'), bot)

        return cls(**data)


class Poll(TelegramObject):
    """
    This object contains information about a poll.

    Attributes:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, 1-255 characters.
        options (List[:class:`PollOption`]): List of poll options.
        total_voter_count (:obj:`int`): Total number of users that voted in the poll.
        is_closed (:obj:`bool`): True, if the poll is closed.
        is_anonymous (:obj:`bool`): True, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): True, if the poll allows multiple answers.
        correct_option_id (:obj:`int`): Optional. Identifier of the correct answer option.

    Args:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, 1-255 characters.
        options (List[:class:`PollOption`]): List of poll options.
        is_closed (:obj:`bool`): True, if the poll is closed.
        is_anonymous (:obj:`bool`): True, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): True, if the poll allows multiple answers.
        correct_option_id (:obj:`int`, optional): 0-based identifier of the correct answer option.
            Available only for polls in the quiz mode, which are closed, or was sent (not
            forwarded) by the bot or to the private chat with the bot.

    """

    def __init__(self, id, question, options, total_voter_count, is_closed, is_anonymous, type,
                 allows_multiple_answers, correct_option_id=None, **kwargs):
        self.id = id
        self.question = question
        self.options = options
        self.total_voter_count = total_voter_count
        self.is_closed = is_closed
        self.is_anonymous = is_anonymous
        self.type = type
        self.allows_multiple_answers = allows_multiple_answers
        self.correct_option_id = correct_option_id

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

    REGULAR = "regular"
    """:obj:`str`: 'regular'"""
    QUIZ = "quiz"
    """:obj:`str`: 'quiz'"""
