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

from telegram import ChecklistTask, MessageEntity, User
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import ZERO_DATE
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
        assert len(mro_slots(checklist_task)) == len(
            set(mro_slots(checklist_task))
        ), "duplicate slot"

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
            (1735689600, dtm.datetime(2025, 1, 1, tzinfo=dtm.UTC)),
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

        assert clt1 == clt2
        assert hash(clt1) == hash(clt2)

        assert clt1 != clt3
        assert hash(clt1) != hash(clt3)
