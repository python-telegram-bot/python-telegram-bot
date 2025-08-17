#!/usr/bin/env python
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

import pytest

from telegram import Dice, InputChecklist, InputChecklistTask, MessageEntity
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_checklist_task():
    return InputChecklistTask(
        id=InputChecklistTaskTestBase.id,
        text=InputChecklistTaskTestBase.text,
        parse_mode=InputChecklistTaskTestBase.parse_mode,
        text_entities=InputChecklistTaskTestBase.text_entities,
    )


class InputChecklistTaskTestBase:
    id = 1
    text = "buy food"
    parse_mode = "MarkdownV2"
    text_entities = [
        MessageEntity(type="bold", offset=0, length=3),
        MessageEntity(type="italic", offset=4, length=4),
    ]


class TestInputChecklistTaskWithoutRequest(InputChecklistTaskTestBase):
    def test_slot_behaviour(self, input_checklist_task):
        for attr in input_checklist_task.__slots__:
            assert getattr(input_checklist_task, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(input_checklist_task)) == len(set(mro_slots(input_checklist_task))), (
            "duplicate slot"
        )

    def test_expected_values(self, input_checklist_task):
        assert input_checklist_task.id == self.id
        assert input_checklist_task.text == self.text
        assert input_checklist_task.parse_mode == self.parse_mode
        assert input_checklist_task.text_entities == tuple(self.text_entities)

    def test_to_dict(self, input_checklist_task):
        iclt_dict = input_checklist_task.to_dict()

        assert isinstance(iclt_dict, dict)
        assert iclt_dict["id"] == self.id
        assert iclt_dict["text"] == self.text
        assert iclt_dict["parse_mode"] == self.parse_mode
        assert iclt_dict["text_entities"] == [entity.to_dict() for entity in self.text_entities]

        # Test that default-value parameter `parse_mode` is handled correctly
        input_checklist_task = InputChecklistTask(id=1, text="text")
        iclt_dict = input_checklist_task.to_dict()
        assert "parse_mode" not in iclt_dict

    def test_equality(self, input_checklist_task):
        a = input_checklist_task
        b = InputChecklistTask(id=self.id, text=f"other {self.text}")
        c = InputChecklistTask(id=self.id + 1, text=self.text)
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope="module")
def input_checklist():
    return InputChecklist(
        title=InputChecklistTestBase.title,
        tasks=InputChecklistTestBase.tasks,
        parse_mode=InputChecklistTestBase.parse_mode,
        title_entities=InputChecklistTestBase.title_entities,
        others_can_add_tasks=InputChecklistTestBase.others_can_add_tasks,
        others_can_mark_tasks_as_done=InputChecklistTestBase.others_can_mark_tasks_as_done,
    )


class InputChecklistTestBase:
    title = "test list"
    tasks = [
        InputChecklistTask(id=1, text="eat"),
        InputChecklistTask(id=2, text="sleep"),
    ]
    parse_mode = "MarkdownV2"
    title_entities = [
        MessageEntity(type="bold", offset=0, length=4),
        MessageEntity(type="italic", offset=5, length=4),
    ]
    others_can_add_tasks = True
    others_can_mark_tasks_as_done = False


class TestInputChecklistWithoutRequest(InputChecklistTestBase):
    def test_slot_behaviour(self, input_checklist):
        for attr in input_checklist.__slots__:
            assert getattr(input_checklist, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(input_checklist)) == len(set(mro_slots(input_checklist))), (
            "duplicate slot"
        )

    def test_expected_values(self, input_checklist):
        assert input_checklist.title == self.title
        assert input_checklist.tasks == tuple(self.tasks)
        assert input_checklist.parse_mode == self.parse_mode
        assert input_checklist.title_entities == tuple(self.title_entities)
        assert input_checklist.others_can_add_tasks == self.others_can_add_tasks
        assert input_checklist.others_can_mark_tasks_as_done == self.others_can_mark_tasks_as_done

    def test_to_dict(self, input_checklist):
        icl_dict = input_checklist.to_dict()

        assert isinstance(icl_dict, dict)
        assert icl_dict["title"] == self.title
        assert icl_dict["tasks"] == [task.to_dict() for task in self.tasks]
        assert icl_dict["parse_mode"] == self.parse_mode
        assert icl_dict["title_entities"] == [entity.to_dict() for entity in self.title_entities]
        assert icl_dict["others_can_add_tasks"] == self.others_can_add_tasks
        assert icl_dict["others_can_mark_tasks_as_done"] == self.others_can_mark_tasks_as_done

        # Test that default-value parameter `parse_mode` is handled correctly
        input_checklist = InputChecklist(title=self.title, tasks=self.tasks)
        icl_dict = input_checklist.to_dict()
        assert "parse_mode" not in icl_dict

    def test_equality(self, input_checklist):
        a = input_checklist
        b = InputChecklist(
            title=f"other {self.title}",
            tasks=[InputChecklistTask(id=1, text="eat"), InputChecklistTask(id=2, text="sleep")],
        )
        c = InputChecklist(
            title=self.title,
            tasks=[InputChecklistTask(id=9, text="Other Task")],
        )
        d = Dice(value=1, emoji="🎲")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
