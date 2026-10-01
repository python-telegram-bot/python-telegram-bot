#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
from typing import TYPE_CHECKING

from telegram._chat import Chat
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.entities import parse_message_entities, parse_message_entity

if TYPE_CHECKING:
    from telegram import Message


@tg_dataclass()
class ChecklistTask(TelegramObject):
    """
    Describes a task in a checklist.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`id` is equal.

    .. versionadded:: 22.3

    Args:
        id (:obj:`int`): Unique identifier of the task.
        text (:obj:`str`): Text of the task.
        text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities that appear in the task text.
        completed_by_user (:class:`telegram.User`, optional): User that completed the task; omitted
            if the task wasn't completed
        completed_by_chat (:class:`telegram.Chat`, optional): Chat that completed the task; omitted
            if the task wasn't completed by a chat

            .. versionadded:: 22.6
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
        completed_by_chat (:class:`telegram.Chat`): Optional. Chat that completed the task; omitted
            if the task wasn't completed by a chat

            .. versionadded:: 22.6
        completion_date (:class:`datetime.datetime`): Optional. Point in time when
            the task was completed; :attr:`~telegram.constants.ZERO_DATE` if the task wasn't
            completed

            |datetime_localization|
    """

    id: int = tg_field(compare=True)
    text: str = tg_field()
    text_entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    completed_by_user: User | None = tg_field(default=None)
    completion_date: dtm.datetime | None = tg_field(default=None)
    completed_by_chat: Chat | None = tg_field(default=None)

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

    def parse_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
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


@tg_dataclass()
class Checklist(TelegramObject):
    """
    Describes a checklist.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if all their :attr:`tasks` are equal.

    .. versionadded:: 22.3

    Args:
        title (:obj:`str`): Title of the checklist.
        title_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities that appear in the checklist title.
        tasks (Sequence[:class:`telegram.ChecklistTask`]): List of tasks in the checklist.
        others_can_add_tasks (:obj:`bool`, optional): :obj:`True` if users other than the creator
            of the list can add tasks to the list
        others_can_mark_tasks_as_done (:obj:`bool`, optional): :obj:`True` if users other than the
            creator of the list can mark tasks as done or not done

    Attributes:
        title (:obj:`str`): Title of the checklist.
        title_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. Special
            entities that appear in the checklist title.
        tasks (Tuple[:class:`telegram.ChecklistTask`]): List of tasks in the checklist.
        others_can_add_tasks (:obj:`bool`): Optional. :obj:`True` if users other than the creator
            of the list can add tasks to the list
        others_can_mark_tasks_as_done (:obj:`bool`): Optional. :obj:`True` if users other than the
            creator of the list can mark tasks as done or not done
    """

    title: str = tg_field()
    tasks: tuple[ChecklistTask, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    title_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    others_can_add_tasks: bool | None = tg_field(default=None)
    others_can_mark_tasks_as_done: bool | None = tg_field(default=None)

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`title`
        from a given :class:`telegram.MessageEntity` of :attr:`title_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice :attr:`title` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`title_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.title, entity)

    def parse_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this checklist's title filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`title_entities`
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
        return parse_message_entities(self.title, self.title_entities, types)


@tg_dataclass()
class ChecklistTasksDone(TelegramObject):
    """
    Describes a service message about checklist tasks marked as done or not done.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`marked_as_done_task_ids` and
    :attr:`marked_as_not_done_task_ids` are equal.

    .. versionadded:: 22.3

    Args:
        checklist_message (:class:`telegram.Message`, optional): Message containing the checklist
            whose tasks were marked as done or not done. Note that the ~:class:`telegram.Message`
            object in this field will not contain the :attr:`~telegram.Message.reply_to_message`
            field even if it itself is a reply.
        marked_as_done_task_ids (Sequence[:obj:`int`], optional): Identifiers of the tasks that
            were marked as done
        marked_as_not_done_task_ids (Sequence[:obj:`int`], optional): Identifiers of the tasks that
            were marked as not done

    Attributes:
        checklist_message (:class:`telegram.Message`): Optional. Message containing the checklist
            whose tasks were marked as done or not done. Note that the ~:class:`telegram.Message`
            object in this field will not contain the :attr:`~telegram.Message.reply_to_message`
            field even if it itself is a reply.
        marked_as_done_task_ids (Tuple[:obj:`int`]): Optional. Identifiers of the tasks that were
            marked as done
        marked_as_not_done_task_ids (Tuple[:obj:`int`]): Optional. Identifiers of the tasks that
            were marked as not done
    """

    checklist_message: "Message | None" = tg_field(default=None)
    marked_as_done_task_ids: tuple[int, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )
    marked_as_not_done_task_ids: tuple[int, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )


@tg_dataclass()
class ChecklistTasksAdded(TelegramObject):
    """
    Describes a service message about tasks added to a checklist.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their :attr:`tasks` are equal.

    .. versionadded:: 22.3

    Args:
        checklist_message (:class:`telegram.Message`, optional): Message containing the checklist
            to which tasks were added. Note that the ~:class:`telegram.Message`
            object in this field will not contain the :attr:`~telegram.Message.reply_to_message`
            field even if it itself is a reply.
        tasks (Sequence[:class:`telegram.ChecklistTask`]): List of tasks added to the checklist

    Attributes:
        checklist_message (:class:`telegram.Message`): Optional. Message containing the checklist
            to which tasks were added. Note that the ~:class:`telegram.Message`
            object in this field will not contain the :attr:`~telegram.Message.reply_to_message`
            field even if it itself is a reply.
        tasks (Tuple[:class:`telegram.ChecklistTask`]): List of tasks added to the checklist
    """

    tasks: tuple[ChecklistTask, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    checklist_message: "Message | None" = tg_field(default=None)
