#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains an objects related to Telegram checklists."""
import datetime as dtm
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import de_json_optional, de_list_optional, parse_sequence_arg
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.entities import parse_message_entities, parse_message_entity
from telegram._utils.types import JSONDict
from telegram.constants import ZERO_DATE

if TYPE_CHECKING:
    from telegram import Bot


class ChecklistTask(TelegramObject):
    """
    Describes a task in a checklist.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if all their :attr:`id` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        id (:obj:`int`): Unique identifier of the task.
        text (:obj:`str`): Text of the task.
        text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities that appear in the task text.
        completed_by_user (:class:`telegram.User`, optional): User that completed the task; omitted
            if the task wasn't completed
        completion_date (:class:`datetime.datetime`, optional): Point in time when
            the task was completed; :attr:`~telegram.constants.ZERO_DATE` if the task wasn't
            completed

            |datetime_localization|

    Attributes:
        id (:obj:`int`): Unique identifier of the task.
        text (:obj:`str`): Text of the task.
        text_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. Special
            entities that appear in the task text.
        completed_by_user (:class:`telegram.User`): Optional. User that completed the task; omitted
            if the task wasn't completed
        completion_date (:class:`datetime.datetime`): Optional. Point in time when
            the task was completed; :attr:`~telegram.constants.ZERO_DATE` if the task wasn't
            completed

            |datetime_localization|
    """

    __slots__ = (
        "completed_by_user",
        "completion_date",
        "id",
        "text",
        "text_entities",
    )

    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        text: str,
        text_entities: Optional[Sequence[MessageEntity]] = None,
        completed_by_user: Optional[User] = None,
        completion_date: Optional[dtm.datetime] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: int = id
        self.text: str = text
        self.text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(text_entities)
        self.completed_by_user: Optional[User] = completed_by_user
        self.completion_date: Optional[dtm.datetime] = completion_date

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "ChecklistTask":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        if (date := data.get("completion_date")) == 0:
            data["completion_date"] = ZERO_DATE
        else:
            data["completion_date"] = from_timestamp(date, tzinfo=loc_tzinfo)

        data["completed_by_user"] = de_json_optional(data.get("completed_by_user"), User, bot)
        data["text_entities"] = de_list_optional(data.get("text_entities"), MessageEntity, bot)

        return super().de_json(data=data, bot=bot)

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`text`
        from a given :class:`telegram.MessageEntity` of :attr:`text_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``ChecklistTask.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`text_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.text, entity)

    def parse_entities(self, types: Optional[list[str]] = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this checklist task filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`text_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.
        """
        return parse_message_entities(self.text, self.text_entities, types)
