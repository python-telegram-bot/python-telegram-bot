#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import datetime
import sys
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Sequence, Tuple

from telegram import constants
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.datetime import from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class PollOption(TelegramObject):
    """
    This object contains information about one answer option in a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text` and :attr:`voter_count` are equal.

    Args:
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        voter_count (:obj:`int`): Number of users that voted for this option.

    Attributes:
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        voter_count (:obj:`int`): Number of users that voted for this option.

    """

    __slots__ = ("voter_count", "text")

    def __init__(self, text: str, voter_count: int, *, api_kwargs: JSONDict = None):
        super().__init__(api_kwargs=api_kwargs)
        self.text: str = text
        self.voter_count: int = voter_count

        self._id_attrs = (self.text, self.voter_count)

        self._freeze()

    MIN_LENGTH: ClassVar[int] = constants.PollLimit.MIN_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_LENGTH: ClassVar[int] = constants.PollLimit.MAX_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_OPTION_LENGTH`

    .. versionadded:: 20.0
    """


class PollAnswer(TelegramObject):
    """
    This object represents an answer of a user in a non-anonymous poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`poll_id`, :attr:`user` and :attr:`option_ids` are equal.

    Args:
        poll_id (:obj:`str`): Unique poll identifier.
        user (:class:`telegram.User`): The user, who changed the answer to the poll.
        option_ids (Sequence[:obj:`int`]): 0-based identifiers of answer options, chosen by the
            user. May be empty if the user retracted their vote.

            .. versionchanged:: 20.0
                |sequenceclassargs|

    Attributes:
        poll_id (:obj:`str`): Unique poll identifier.
        user (:class:`telegram.User`): The user, who changed the answer to the poll.
        option_ids (Tuple[:obj:`int`]): Identifiers of answer options, chosen by the user.  May be
            empty if the user retracted their vote.

            .. versionchanged:: 20.0
                |tupleclassattrs|

    """

    __slots__ = ("option_ids", "user", "poll_id")

    def __init__(
        self, poll_id: str, user: User, option_ids: Sequence[int], *, api_kwargs: JSONDict = None
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.poll_id: str = poll_id
        self.user: User = user
        self.option_ids: Tuple[int, ...] = parse_sequence_arg(option_ids)

        self._id_attrs = (self.poll_id, self.user, tuple(self.option_ids))

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["PollAnswer"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.get("user"), bot)

        return super().de_json(data=data, bot=bot)


class Poll(TelegramObject):
    """
    This object contains information about a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Examples:
        :any:`Poll Bot <examples.pollbot>`

    Args:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, :tg-const:`telegram.Poll.MIN_QUESTION_LENGTH`-
            :tg-const:`telegram.Poll.MAX_QUESTION_LENGTH` characters.
        options (Sequence[:class:`~telegram.PollOption`]): List of poll options.

            .. versionchanged:: 20.0
                |sequenceclassargs|
        is_closed (:obj:`bool`): :obj:`True`, if the poll is closed.
        is_anonymous (:obj:`bool`): :obj:`True`, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): :obj:`True`, if the poll allows multiple answers.
        correct_option_id (:obj:`int`, optional): A zero based identifier of the correct answer
            option. Available only for closed polls in the quiz mode, which were sent
            (not forwarded), by the bot or to a private chat with the bot.
        explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll,
            0-:tg-const:`telegram.Poll.MAX_EXPLANATION_LENGTH` characters.
        explanation_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities like usernames, URLs, bot commands, etc. that appear in the
            :attr:`explanation`. This list is empty if the message does not contain explanation
            entities.

            .. versionchanged:: 20.0

               * This attribute is now always a (possibly empty) list and never :obj:`None`.
               * |sequenceclassargs|
        open_period (:obj:`int`, optional): Amount of time in seconds the poll will be active
            after creation.
        close_date (:obj:`datetime.datetime`, optional): Point in time (Unix timestamp) when the
            poll will be automatically closed. Converted to :obj:`datetime.datetime`.

    Attributes:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, :tg-const:`telegram.Poll.MIN_QUESTION_LENGTH`-
            :tg-const:`telegram.Poll.MAX_QUESTION_LENGTH` characters.
        options (Tuple[:class:`~telegram.PollOption`]): List of poll options.

            .. versionchanged:: 20.0
                |tupleclassattrs|
        total_voter_count (:obj:`int`): Total number of users that voted in the poll.
        is_closed (:obj:`bool`): :obj:`True`, if the poll is closed.
        is_anonymous (:obj:`bool`): :obj:`True`, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): :obj:`True`, if the poll allows multiple answers.
        correct_option_id (:obj:`int`): Optional. A zero based identifier of the correct answer
            option. Available only for closed polls in the quiz mode, which were sent
            (not forwarded), by the bot or to a private chat with the bot.
        explanation (:obj:`str`): Optional. Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll,
            0-:tg-const:`telegram.Poll.MAX_EXPLANATION_LENGTH` characters.
        explanation_entities (Tuple[:class:`telegram.MessageEntity`]): Special entities
            like usernames, URLs, bot commands, etc. that appear in the :attr:`explanation`.
            This list is empty if the message does not contain explanation entities.

            .. versionchanged:: 20.0
                |tupleclassattrs|

            .. versionchanged:: 20.0
               This attribute is now always a (possibly empty) list and never :obj:`None`.
        open_period (:obj:`int`): Optional. Amount of time in seconds the poll will be active
            after creation.
        close_date (:obj:`datetime.datetime`): Optional. Point in time when the poll will be
            automatically closed.

    """

    __slots__ = (
        "total_voter_count",
        "allows_multiple_answers",
        "open_period",
        "options",
        "type",
        "explanation_entities",
        "is_anonymous",
        "close_date",
        "is_closed",
        "id",
        "explanation",
        "question",
        "correct_option_id",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        question: str,
        options: Sequence[PollOption],
        total_voter_count: int,
        is_closed: bool,
        is_anonymous: bool,
        type: str,  # pylint: disable=redefined-builtin
        allows_multiple_answers: bool,
        correct_option_id: int = None,
        explanation: str = None,
        explanation_entities: Sequence[MessageEntity] = None,
        open_period: int = None,
        close_date: datetime.datetime = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id  # pylint: disable=invalid-name
        self.question: str = question
        self.options: Tuple[PollOption, ...] = parse_sequence_arg(options)
        self.total_voter_count: int = total_voter_count
        self.is_closed: bool = is_closed
        self.is_anonymous: bool = is_anonymous
        self.type: str = enum.get_member(constants.PollType, type, type)
        self.allows_multiple_answers: bool = allows_multiple_answers
        self.correct_option_id: Optional[int] = correct_option_id
        self.explanation: Optional[str] = explanation
        self.explanation_entities: Tuple[MessageEntity, ...] = parse_sequence_arg(
            explanation_entities
        )
        self.open_period: Optional[int] = open_period
        self.close_date: Optional[datetime.datetime] = close_date

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["Poll"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["options"] = [PollOption.de_json(option, bot) for option in data["options"]]
        data["explanation_entities"] = MessageEntity.de_list(data.get("explanation_entities"), bot)
        data["close_date"] = from_timestamp(data.get("close_date"))

        return super().de_json(data=data, bot=bot)

    def parse_explanation_entity(self, entity: MessageEntity) -> str:
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

        Raises:
            RuntimeError: If the poll has no explanation.

        """
        if not self.explanation:
            raise RuntimeError("This Poll has no 'explanation'.")

        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xFFFF:
            return self.explanation[entity.offset : entity.offset + entity.length]
        entity_text = self.explanation.encode("utf-16-le")
        entity_text = entity_text[entity.offset * 2 : (entity.offset + entity.length) * 2]

        return entity_text.decode("utf-16-le")

    def parse_explanation_entities(self, types: List[str] = None) -> Dict[MessageEntity, str]:
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
            for entity in self.explanation_entities
            if entity.type in types
        }

    REGULAR: ClassVar[str] = constants.PollType.REGULAR
    """:const:`telegram.constants.PollType.REGULAR`"""
    QUIZ: ClassVar[str] = constants.PollType.QUIZ
    """:const:`telegram.constants.PollType.QUIZ`"""
    MAX_EXPLANATION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_EXPLANATION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_EXPLANATION_LINE_FEEDS: ClassVar[int] = constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS`

    .. versionadded:: 20.0
    """
    MIN_OPEN_PERIOD: ClassVar[int] = constants.PollLimit.MIN_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MIN_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MAX_OPEN_PERIOD: ClassVar[int] = constants.PollLimit.MAX_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MAX_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MIN_QUESTION_LENGTH: ClassVar[int] = constants.PollLimit.MIN_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_QUESTION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_LENGTH: ClassVar[int] = constants.PollLimit.MIN_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_OPTION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_NUMBER: ClassVar[int] = constants.PollLimit.MIN_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MIN_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
    MAX_OPTION_NUMBER: ClassVar[int] = constants.PollLimit.MAX_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MAX_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
