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

import sys

from telegram import (TelegramObject, User, MessageEntity)
from telegram.utils.helpers import to_timestamp, from_timestamp


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
        explanation (:obj:`str`): Optional. Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll.
        explanation_entities (List[:class:`telegram.MessageEntity`]): Optional. Special entities
            like usernames, URLs, bot commands, etc. that appear in the :attr:`explanation`.
        open_period (:obj:`int`): Optional. Amount of time in seconds the poll will be active
            after creation.
        close_date (:obj:`datetime.datetime`): Optional. Point in time when the poll will be
            automatically closed.

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
        explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll, 0-200 characters.
        explanation_entities (List[:class:`telegram.MessageEntity`], optional): Special entities
            like usernames, URLs, bot commands, etc. that appear in the :attr:`explanation`.
        open_period (:obj:`int`, optional): Amount of time in seconds the poll will be active
            after creation.
        close_date (:obj:`datetime.datetime`, optional): Point in time (Unix timestamp) when the
            poll will be automatically closed. Converted to :obj:`datetime.datetime`.

    """

    def __init__(self,
                 id,
                 question,
                 options,
                 total_voter_count,
                 is_closed,
                 is_anonymous,
                 type,
                 allows_multiple_answers,
                 correct_option_id=None,
                 explanation=None,
                 explanation_entities=None,
                 open_period=None,
                 close_date=None,
                 **kwargs):
        self.id = id
        self.question = question
        self.options = options
        self.total_voter_count = total_voter_count
        self.is_closed = is_closed
        self.is_anonymous = is_anonymous
        self.type = type
        self.allows_multiple_answers = allows_multiple_answers
        self.correct_option_id = correct_option_id
        self.explanation = explanation
        self.explanation_entities = explanation_entities
        self.open_period = open_period
        self.close_date = close_date

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Poll, cls).de_json(data, bot)

        data['options'] = [PollOption.de_json(option, bot) for option in data['options']]
        data['explanation_entities'] = MessageEntity.de_list(data.get('explanation_entities'), bot)
        data['close_date'] = from_timestamp(data.get('close_date'))

        return cls(**data)

    def to_dict(self):
        data = super(Poll, self).to_dict()

        data['options'] = [x.to_dict() for x in self.options]
        if self.explanation_entities:
            data['explanation_entities'] = [e.to_dict() for e in self.explanation_entities]
        data['close_date'] = to_timestamp(data.get('close_date'))

        return data

    def parse_explanation_entity(self, entity):
        """Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to this message.

        Returns:
            :obj:`str`: The text of the given entity.

        """
        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xffff:
            return self.explanation[entity.offset:entity.offset + entity.length]
        else:
            entity_text = self.explanation.encode('utf-16-le')
            entity_text = entity_text[entity.offset * 2:(entity.offset + entity.length) * 2]

        return entity_text.decode('utf-16-le')

    def parse_explanation_entities(self, types=None):
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls explanation filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`explanation_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_explanation_entity` for more info.

        Args:
            types (List[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            Dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_explanation_entity(entity)
            for entity in self.explanation_entities if entity.type in types
        }

    REGULAR = "regular"
    """:obj:`str`: 'regular'"""
    QUIZ = "quiz"
    """:obj:`str`: 'quiz'"""
