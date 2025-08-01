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
import datetime as dtm

import pytest

from telegram import (
    Checklist,
    ChecklistTask,
    ChecklistTasksAdded,
    ChecklistTasksDone,
    Dice,
    MessageEntity,
    User,
)
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ZERO_DATE
from tests.auxil.build_messages import make_message
from tests.auxil.slots import mro_slots


class ChecklistTaskTestBase:
    id = 42
    text = "here is a text"
    text_entities = [
        MessageEntity(type="bold", offset=0, length=4),
        MessageEntity(type="italic", offset=5, length=2),
    ]
    completed_by_user = User(id=1, first_name="Test", last_name="User", is_bot=False)
    completion_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


@pytest.fixture(scope="module")
def checklist_task():
    return ChecklistTask(
        id=ChecklistTaskTestBase.id,
        text=ChecklistTaskTestBase.text,
        text_entities=ChecklistTaskTestBase.text_entities,
        completed_by_user=ChecklistTaskTestBase.completed_by_user,
        completion_date=ChecklistTaskTestBase.completion_date,
    )


class TestChecklistTaskWithoutRequest(ChecklistTaskTestBase):
    def test_slot_behaviour(self, checklist_task):
        for attr in checklist_task.__slots__:
            assert getattr(checklist_task, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(checklist_task)) == len(set(mro_slots(checklist_task))), (
            "duplicate slot"
        )

    def test_to_dict(self, checklist_task):
        clt_dict = checklist_task.to_dict()
        assert isinstance(clt_dict, dict)
        assert clt_dict["id"] == self.id
        assert clt_dict["text"] == self.text
        assert clt_dict["text_entities"] == [entity.to_dict() for entity in self.text_entities]
        assert clt_dict["completed_by_user"] == self.completed_by_user.to_dict()
        assert clt_dict["completion_date"] == to_timestamp(self.completion_date)

    def test_de_json(self, offline_bot):
        json_dict = {
            "id": self.id,
            "text": self.text,
            "text_entities": [entity.to_dict() for entity in self.text_entities],
            "completed_by_user": self.completed_by_user.to_dict(),
            "completion_date": to_timestamp(self.completion_date),
        }
        clt = ChecklistTask.de_json(json_dict, offline_bot)
        assert isinstance(clt, ChecklistTask)
        assert clt.id == self.id
        assert clt.text == self.text
        assert clt.text_entities == tuple(self.text_entities)
        assert clt.completed_by_user == self.completed_by_user
        assert clt.completion_date == self.completion_date
        assert clt.api_kwargs == {}

    def test_de_json_required_fields(self, offline_bot):
        json_dict = {
            "id": self.id,
            "text": self.text,
        }
        clt = ChecklistTask.de_json(json_dict, offline_bot)
        assert isinstance(clt, ChecklistTask)
        assert clt.id == self.id
        assert clt.text == self.text
        assert clt.text_entities == ()
        assert clt.completed_by_user is None
        assert clt.completion_date is None
        assert clt.api_kwargs == {}

    def test_de_json_localization(self, offline_bot, raw_bot, tz_bot):
        json_dict = {
            "id": self.id,
            "text": self.text,
            "completion_date": to_timestamp(self.completion_date),
        }
        clt_bot = ChecklistTask.de_json(json_dict, offline_bot)
        clt_bot_raw = ChecklistTask.de_json(json_dict, raw_bot)
        clt_bot_tz = ChecklistTask.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing tzinfo objects is not reliable
        completion_date_offset = clt_bot_tz.completion_date.utcoffset()
        completion_date_offset_tz = tz_bot.defaults.tzinfo.utcoffset(
            clt_bot_tz.completion_date.replace(tzinfo=None)
        )

        assert clt_bot.completion_date.tzinfo == UTC
        assert clt_bot_raw.completion_date.tzinfo == UTC
        assert completion_date_offset_tz == completion_date_offset

    @pytest.mark.parametrize(
        ("completion_date", "expected"),
        [
            (None, None),
            (0, ZERO_DATE),
            (1735689600, dtm.datetime(2025, 1, 1, tzinfo=UTC)),
        ],
    )
    def test_de_json_completion_date(self, offline_bot, completion_date, expected):
        json_dict = {
            "id": self.id,
            "text": self.text,
            "completion_date": completion_date,
        }
        clt = ChecklistTask.de_json(json_dict, offline_bot)
        assert isinstance(clt, ChecklistTask)
        assert clt.completion_date == expected

    def test_parse_entity(self, checklist_task):
        assert checklist_task.parse_entity(checklist_task.text_entities[0]) == "here"

    def test_parse_entities(self, checklist_task):
        assert checklist_task.parse_entities(MessageEntity.BOLD) == {
            checklist_task.text_entities[0]: "here"
        }
        assert checklist_task.parse_entities() == {
            checklist_task.text_entities[0]: "here",
            checklist_task.text_entities[1]: "is",
        }

    def test_equality(self, checklist_task):
        clt1 = checklist_task
        clt2 = ChecklistTask(
            id=self.id,
            text="other text",
        )
        clt3 = ChecklistTask(
            id=self.id + 1,
            text=self.text,
        )
        clt4 = Dice(value=1, emoji="🎲")

        assert clt1 == clt2
        assert hash(clt1) == hash(clt2)

        assert clt1 != clt3
        assert hash(clt1) != hash(clt3)

        assert clt1 != clt4
        assert hash(clt1) != hash(clt4)


class ChecklistTestBase:
    title = "Checklist Title"
    title_entities = [
        MessageEntity(type="bold", offset=0, length=9),
        MessageEntity(type="italic", offset=10, length=5),
    ]
    tasks = [
        ChecklistTask(
            id=1,
            text="Task 1",
        ),
        ChecklistTask(
            id=2,
            text="Task 2",
        ),
    ]
    others_can_add_tasks = True
    others_can_mark_tasks_as_done = False


@pytest.fixture(scope="module")
def checklist():
    return Checklist(
        title=ChecklistTestBase.title,
        title_entities=ChecklistTestBase.title_entities,
        tasks=ChecklistTestBase.tasks,
        others_can_add_tasks=ChecklistTestBase.others_can_add_tasks,
        others_can_mark_tasks_as_done=ChecklistTestBase.others_can_mark_tasks_as_done,
    )


class TestChecklistWithoutRequest(ChecklistTestBase):
    def test_slot_behaviour(self, checklist):
        for attr in checklist.__slots__:
            assert getattr(checklist, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(checklist)) == len(set(mro_slots(checklist))), "duplicate slot"

    def test_to_dict(self, checklist):
        cl_dict = checklist.to_dict()
        assert isinstance(cl_dict, dict)
        assert cl_dict["title"] == self.title
        assert cl_dict["title_entities"] == [entity.to_dict() for entity in self.title_entities]
        assert cl_dict["tasks"] == [task.to_dict() for task in self.tasks]
        assert cl_dict["others_can_add_tasks"] is self.others_can_add_tasks
        assert cl_dict["others_can_mark_tasks_as_done"] is self.others_can_mark_tasks_as_done

    def test_de_json(self, offline_bot):
        json_dict = {
            "title": self.title,
            "title_entities": [entity.to_dict() for entity in self.title_entities],
            "tasks": [task.to_dict() for task in self.tasks],
            "others_can_add_tasks": self.others_can_add_tasks,
            "others_can_mark_tasks_as_done": self.others_can_mark_tasks_as_done,
        }
        cl = Checklist.de_json(json_dict, offline_bot)
        assert isinstance(cl, Checklist)
        assert cl.title == self.title
        assert cl.title_entities == tuple(self.title_entities)
        assert cl.tasks == tuple(self.tasks)
        assert cl.others_can_add_tasks is self.others_can_add_tasks
        assert cl.others_can_mark_tasks_as_done is self.others_can_mark_tasks_as_done
        assert cl.api_kwargs == {}

    def test_de_json_required_fields(self, offline_bot):
        json_dict = {
            "title": self.title,
            "tasks": [task.to_dict() for task in self.tasks],
        }
        cl = Checklist.de_json(json_dict, offline_bot)
        assert isinstance(cl, Checklist)
        assert cl.title == self.title
        assert cl.title_entities == ()
        assert cl.tasks == tuple(self.tasks)
        assert not cl.others_can_add_tasks
        assert not cl.others_can_mark_tasks_as_done

    def test_parse_entity(self, checklist):
        assert checklist.parse_entity(checklist.title_entities[0]) == "Checklist"
        assert checklist.parse_entity(checklist.title_entities[1]) == "Title"

    def test_parse_entities(self, checklist):
        assert checklist.parse_entities(MessageEntity.BOLD) == {
            checklist.title_entities[0]: "Checklist"
        }
        assert checklist.parse_entities() == {
            checklist.title_entities[0]: "Checklist",
            checklist.title_entities[1]: "Title",
        }

    def test_equality(self, checklist, checklist_task):
        cl1 = checklist
        cl2 = Checklist(
            title=self.title + " other",
            tasks=[ChecklistTask(id=1, text="something"), ChecklistTask(id=2, text="something")],
        )
        cl3 = Checklist(
            title=self.title + " other",
            tasks=[ChecklistTask(id=42, text="Task 2")],
        )
        cl4 = checklist_task

        assert cl1 == cl2
        assert hash(cl1) == hash(cl2)

        assert cl1 != cl3
        assert hash(cl1) != hash(cl3)

        assert cl1 != cl4
        assert hash(cl1) != hash(cl4)


class ChecklistTasksDoneTestBase:
    checklist_message = make_message("Checklist message")
    marked_as_done_task_ids = [1, 2, 3]
    marked_as_not_done_task_ids = [4, 5]


@pytest.fixture(scope="module")
def checklist_tasks_done():
    return ChecklistTasksDone(
        checklist_message=ChecklistTasksDoneTestBase.checklist_message,
        marked_as_done_task_ids=ChecklistTasksDoneTestBase.marked_as_done_task_ids,
        marked_as_not_done_task_ids=ChecklistTasksDoneTestBase.marked_as_not_done_task_ids,
    )


class TestChecklistTasksDoneWithoutRequest(ChecklistTasksDoneTestBase):
    def test_slot_behaviour(self, checklist_tasks_done):
        for attr in checklist_tasks_done.__slots__:
            assert getattr(checklist_tasks_done, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(checklist_tasks_done)) == len(set(mro_slots(checklist_tasks_done))), (
            "duplicate slot"
        )

    def test_to_dict(self, checklist_tasks_done):
        cltd_dict = checklist_tasks_done.to_dict()
        assert isinstance(cltd_dict, dict)
        assert cltd_dict["checklist_message"] == self.checklist_message.to_dict()
        assert cltd_dict["marked_as_done_task_ids"] == self.marked_as_done_task_ids
        assert cltd_dict["marked_as_not_done_task_ids"] == self.marked_as_not_done_task_ids

    def test_de_json(self, offline_bot):
        json_dict = {
            "checklist_message": self.checklist_message.to_dict(),
            "marked_as_done_task_ids": self.marked_as_done_task_ids,
            "marked_as_not_done_task_ids": self.marked_as_not_done_task_ids,
        }
        cltd = ChecklistTasksDone.de_json(json_dict, offline_bot)
        assert isinstance(cltd, ChecklistTasksDone)
        assert cltd.checklist_message == self.checklist_message
        assert cltd.marked_as_done_task_ids == tuple(self.marked_as_done_task_ids)
        assert cltd.marked_as_not_done_task_ids == tuple(self.marked_as_not_done_task_ids)
        assert cltd.api_kwargs == {}

    def test_de_json_required_fields(self, offline_bot):
        cltd = ChecklistTasksDone.de_json({}, offline_bot)
        assert isinstance(cltd, ChecklistTasksDone)
        assert cltd.checklist_message is None
        assert cltd.marked_as_done_task_ids == ()
        assert cltd.marked_as_not_done_task_ids == ()
        assert cltd.api_kwargs == {}

    def test_equality(self, checklist_tasks_done):
        cltd1 = checklist_tasks_done
        cltd2 = ChecklistTasksDone(
            checklist_message=None,
            marked_as_done_task_ids=[1, 2, 3],
            marked_as_not_done_task_ids=[4, 5],
        )
        cltd3 = ChecklistTasksDone(
            checklist_message=make_message("Checklist message"),
            marked_as_done_task_ids=[1, 2, 3],
        )
        cltd4 = make_message("Not a checklist tasks done")

        assert cltd1 == cltd2
        assert hash(cltd1) == hash(cltd2)

        assert cltd1 != cltd3
        assert hash(cltd1) != hash(cltd3)

        assert cltd1 != cltd4
        assert hash(cltd1) != hash(cltd4)


class ChecklistTasksAddedTestBase:
    checklist_message = make_message("Checklist message")
    tasks = [
        ChecklistTask(id=1, text="Task 1"),
        ChecklistTask(id=2, text="Task 2"),
        ChecklistTask(id=3, text="Task 3"),
    ]


@pytest.fixture(scope="module")
def checklist_tasks_added():
    return ChecklistTasksAdded(
        checklist_message=ChecklistTasksAddedTestBase.checklist_message,
        tasks=ChecklistTasksAddedTestBase.tasks,
    )


class TestChecklistTasksAddedWithoutRequest(ChecklistTasksAddedTestBase):
    def test_slot_behaviour(self, checklist_tasks_added):
        for attr in checklist_tasks_added.__slots__:
            assert getattr(checklist_tasks_added, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(checklist_tasks_added)) == len(
            set(mro_slots(checklist_tasks_added))
        ), "duplicate slot"

    def test_to_dict(self, checklist_tasks_added):
        clta_dict = checklist_tasks_added.to_dict()
        assert isinstance(clta_dict, dict)
        assert clta_dict["checklist_message"] == self.checklist_message.to_dict()
        assert clta_dict["tasks"] == [task.to_dict() for task in self.tasks]

    def test_de_json(self, offline_bot):
        json_dict = {
            "checklist_message": self.checklist_message.to_dict(),
            "tasks": [task.to_dict() for task in self.tasks],
        }
        clta = ChecklistTasksAdded.de_json(json_dict, offline_bot)
        assert isinstance(clta, ChecklistTasksAdded)
        assert clta.checklist_message == self.checklist_message
        assert clta.tasks == tuple(self.tasks)
        assert clta.api_kwargs == {}

    def test_de_json_required_fields(self, offline_bot):
        clta = ChecklistTasksAdded.de_json(
            {"tasks": [task.to_dict() for task in self.tasks]}, offline_bot
        )
        assert isinstance(clta, ChecklistTasksAdded)
        assert clta.checklist_message is None
        assert clta.tasks == tuple(self.tasks)
        assert clta.api_kwargs == {}

    def test_equality(self, checklist_tasks_added):
        clta1 = checklist_tasks_added
        clta2 = ChecklistTasksAdded(
            checklist_message=None,
            tasks=[
                ChecklistTask(id=1, text="Other Task 1"),
                ChecklistTask(id=2, text="Other Task 2"),
                ChecklistTask(id=3, text="Other Task 3"),
            ],
        )
        clta3 = ChecklistTasksAdded(
            checklist_message=make_message("Checklist message"),
            tasks=[ChecklistTask(id=1, text="Task 1")],
        )
        clta4 = make_message("Not a checklist tasks added")

        assert clta1 == clta2
        assert hash(clta1) == hash(clta2)

        assert clta1 != clta3
        assert hash(clta1) != hash(clta3)

        assert clta1 != clta4
        assert hash(clta1) != hash(clta4)
