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
import datetime as dtm

import pytest

from telegram import Chat, InputPollOption, MessageEntity, Poll, PollAnswer, PollOption, User
from telegram._utils.datetime import UTC, to_timestamp
from telegram.constants import PollType
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def input_poll_option():
    out = InputPollOption(
        text=InputPollOptionTestBase.text,
        text_parse_mode=InputPollOptionTestBase.text_parse_mode,
        text_entities=InputPollOptionTestBase.text_entities,
    )
    out._unfreeze()
    return out


class InputPollOptionTestBase:
    text = "test option"
    text_parse_mode = "MarkdownV2"
    text_entities = [
        MessageEntity(0, 4, MessageEntity.BOLD),
        MessageEntity(5, 7, MessageEntity.ITALIC),
    ]


class TestInputPollOptionWithoutRequest(InputPollOptionTestBase):
    def test_slot_behaviour(self, input_poll_option):
        for attr in input_poll_option.__slots__:
            assert getattr(input_poll_option, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(input_poll_option)) == len(
            set(mro_slots(input_poll_option))
        ), "duplicate slot"

    def test_de_json(self):

        json_dict = {
            "text": self.text,
            "text_parse_mode": self.text_parse_mode,
            "text_entities": [e.to_dict() for e in self.text_entities],
        }
        input_poll_option = InputPollOption.de_json(json_dict, None)
        assert input_poll_option.api_kwargs == {}

        assert input_poll_option.text == self.text
        assert input_poll_option.text_parse_mode == self.text_parse_mode
        assert input_poll_option.text_entities == tuple(self.text_entities)

    def test_to_dict(self, input_poll_option):
        input_poll_option_dict = input_poll_option.to_dict()

        assert isinstance(input_poll_option_dict, dict)
        assert input_poll_option_dict["text"] == input_poll_option.text
        assert input_poll_option_dict["text_parse_mode"] == input_poll_option.text_parse_mode
        assert input_poll_option_dict["text_entities"] == [
            e.to_dict() for e in input_poll_option.text_entities
        ]

        # Test that the default-value parameter is handled correctly
        input_poll_option = InputPollOption("text")
        input_poll_option_dict = input_poll_option.to_dict()
        assert "text_parse_mode" not in input_poll_option_dict

    def test_equality(self):
        a = InputPollOption("text")
        b = InputPollOption("text", self.text_parse_mode)
        c = InputPollOption("text", text_entities=self.text_entities)
        d = InputPollOption("different_text")
        e = Poll(123, "question", ["O1", "O2"], 1, False, True, Poll.REGULAR, True)

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def poll_option():
    out = PollOption(
        text=PollOptionTestBase.text,
        voter_count=PollOptionTestBase.voter_count,
        text_entities=PollOptionTestBase.text_entities,
    )
    out._unfreeze()
    return out


class PollOptionTestBase:
    text = "test option"
    voter_count = 3
    text_entities = [
        MessageEntity(MessageEntity.BOLD, 0, 4),
        MessageEntity(MessageEntity.ITALIC, 5, 6),
    ]


class TestPollOptionWithoutRequest(PollOptionTestBase):
    def test_slot_behaviour(self, poll_option):
        for attr in poll_option.__slots__:
            assert getattr(poll_option, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(poll_option)) == len(set(mro_slots(poll_option))), "duplicate slot"

    def test_de_json(self):
        json_dict = {"text": self.text, "voter_count": self.voter_count}
        poll_option = PollOption.de_json(json_dict, None)
        assert poll_option.api_kwargs == {}

        assert poll_option.text == self.text
        assert poll_option.voter_count == self.voter_count

    def test_de_json_all(self):
        json_dict = {
            "text": self.text,
            "voter_count": self.voter_count,
            "text_entities": [e.to_dict() for e in self.text_entities],
        }
        poll_option = PollOption.de_json(json_dict, None)

        assert poll_option.api_kwargs == {}

        assert poll_option.text == self.text
        assert poll_option.voter_count == self.voter_count
        assert poll_option.text_entities == tuple(self.text_entities)

    def test_to_dict(self, poll_option):
        poll_option_dict = poll_option.to_dict()

        assert isinstance(poll_option_dict, dict)
        assert poll_option_dict["text"] == poll_option.text
        assert poll_option_dict["voter_count"] == poll_option.voter_count
        assert poll_option_dict["text_entities"] == [
            e.to_dict() for e in poll_option.text_entities
        ]

    def test_parse_entity(self, poll_option):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)
        poll_option.text_entities = [entity]

        assert poll_option.parse_entity(entity) == "test"

    def test_parse_entities(self, poll_option):
        entity = MessageEntity(MessageEntity.BOLD, 0, 4)
        entity_2 = MessageEntity(MessageEntity.ITALIC, 5, 6)
        poll_option.text_entities = [entity, entity_2]

        assert poll_option.parse_entities(MessageEntity.BOLD) == {entity: "test"}
        assert poll_option.parse_entities() == {entity: "test", entity_2: "option"}

    def test_equality(self):
        a = PollOption("text", 1)
        b = PollOption("text", 1)
        c = PollOption("text_1", 1)
        d = PollOption("text", 2)
        e = Poll(123, "question", ["O1", "O2"], 1, False, True, Poll.REGULAR, True)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope="module")
def poll_answer():
    return PollAnswer(
        PollAnswerTestBase.poll_id,
        PollAnswerTestBase.option_ids,
        PollAnswerTestBase.user,
        PollAnswerTestBase.voter_chat,
    )


class PollAnswerTestBase:
    poll_id = "id"
    option_ids = [2]
    user = User(1, "", False)
    voter_chat = Chat(1, "")


class TestPollAnswerWithoutRequest(PollAnswerTestBase):
    def test_de_json(self):
        json_dict = {
            "poll_id": self.poll_id,
            "option_ids": self.option_ids,
            "user": self.user.to_dict(),
            "voter_chat": self.voter_chat.to_dict(),
        }
        poll_answer = PollAnswer.de_json(json_dict, None)
        assert poll_answer.api_kwargs == {}

        assert poll_answer.poll_id == self.poll_id
        assert poll_answer.option_ids == tuple(self.option_ids)
        assert poll_answer.user == self.user
        assert poll_answer.voter_chat == self.voter_chat

    def test_to_dict(self, poll_answer):
        poll_answer_dict = poll_answer.to_dict()

        assert isinstance(poll_answer_dict, dict)
        assert poll_answer_dict["poll_id"] == poll_answer.poll_id
        assert poll_answer_dict["option_ids"] == list(poll_answer.option_ids)
        assert poll_answer_dict["user"] == poll_answer.user.to_dict()
        assert poll_answer_dict["voter_chat"] == poll_answer.voter_chat.to_dict()

    def test_equality(self):
        a = PollAnswer(123, [2], self.user, self.voter_chat)
        b = PollAnswer(123, [2], self.user, Chat(1, ""))
        c = PollAnswer(123, [2], User(1, "first", False), self.voter_chat)
        d = PollAnswer(123, [1, 2], self.user, self.voter_chat)
        e = PollAnswer(456, [2], self.user, self.voter_chat)
        f = PollOption("Text", 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)


@pytest.fixture(scope="module")
def poll():
    poll = Poll(
        PollTestBase.id_,
        PollTestBase.question,
        PollTestBase.options,
        PollTestBase.total_voter_count,
        PollTestBase.is_closed,
        PollTestBase.is_anonymous,
        PollTestBase.type,
        PollTestBase.allows_multiple_answers,
        explanation=PollTestBase.explanation,
        explanation_entities=PollTestBase.explanation_entities,
        open_period=PollTestBase.open_period,
        close_date=PollTestBase.close_date,
        question_entities=PollTestBase.question_entities,
    )
    poll._unfreeze()
    return poll


class PollTestBase:
    id_ = "id"
    question = "Test Question?"
    options = [PollOption("test", 10), PollOption("test2", 11)]
    total_voter_count = 0
    is_closed = True
    is_anonymous = False
    type = Poll.REGULAR
    allows_multiple_answers = True
    explanation = (
        b"\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467"
        b"\\u200d\\U0001f467\\U0001f431http://google.com"
    ).decode("unicode-escape")
    explanation_entities = [MessageEntity(13, 17, MessageEntity.URL)]
    open_period = 42
    close_date = dtm.datetime.now(dtm.timezone.utc)
    question_entities = [
        MessageEntity(MessageEntity.BOLD, 0, 4),
        MessageEntity(MessageEntity.ITALIC, 5, 8),
    ]


class TestPollWithoutRequest(PollTestBase):
    def test_de_json(self, offline_bot):
        json_dict = {
            "id": self.id_,
            "question": self.question,
            "options": [o.to_dict() for o in self.options],
            "total_voter_count": self.total_voter_count,
            "is_closed": self.is_closed,
            "is_anonymous": self.is_anonymous,
            "type": self.type,
            "allows_multiple_answers": self.allows_multiple_answers,
            "explanation": self.explanation,
            "explanation_entities": [self.explanation_entities[0].to_dict()],
            "open_period": self.open_period,
            "close_date": to_timestamp(self.close_date),
            "question_entities": [e.to_dict() for e in self.question_entities],
        }
        poll = Poll.de_json(json_dict, offline_bot)
        assert poll.api_kwargs == {}

        assert poll.id == self.id_
        assert poll.question == self.question
        assert poll.options == tuple(self.options)
        assert poll.options[0].text == self.options[0].text
        assert poll.options[0].voter_count == self.options[0].voter_count
        assert poll.options[1].text == self.options[1].text
        assert poll.options[1].voter_count == self.options[1].voter_count
        assert poll.total_voter_count == self.total_voter_count
        assert poll.is_closed == self.is_closed
        assert poll.is_anonymous == self.is_anonymous
        assert poll.type == self.type
        assert poll.allows_multiple_answers == self.allows_multiple_answers
        assert poll.explanation == self.explanation
        assert poll.explanation_entities == tuple(self.explanation_entities)
        assert poll.open_period == self.open_period
        assert abs(poll.close_date - self.close_date) < dtm.timedelta(seconds=1)
        assert to_timestamp(poll.close_date) == to_timestamp(self.close_date)
        assert poll.question_entities == tuple(self.question_entities)

    def test_de_json_localization(self, tz_bot, offline_bot, raw_bot):
        json_dict = {
            "id": self.id_,
            "question": self.question,
            "options": [o.to_dict() for o in self.options],
            "total_voter_count": self.total_voter_count,
            "is_closed": self.is_closed,
            "is_anonymous": self.is_anonymous,
            "type": self.type,
            "allows_multiple_answers": self.allows_multiple_answers,
            "explanation": self.explanation,
            "explanation_entities": [self.explanation_entities[0].to_dict()],
            "open_period": self.open_period,
            "close_date": to_timestamp(self.close_date),
            "question_entities": [e.to_dict() for e in self.question_entities],
        }

        poll_raw = Poll.de_json(json_dict, raw_bot)
        poll_bot = Poll.de_json(json_dict, offline_bot)
        poll_bot_tz = Poll.de_json(json_dict, tz_bot)

        # comparing utcoffsets because comparing timezones is unpredicatable
        poll_bot_tz_offset = poll_bot_tz.close_date.utcoffset()
        tz_bot_offset = tz_bot.defaults.tzinfo.utcoffset(
            poll_bot_tz.close_date.replace(tzinfo=None)
        )

        assert poll_raw.close_date.tzinfo == UTC
        assert poll_bot.close_date.tzinfo == UTC
        assert poll_bot_tz_offset == tz_bot_offset

    def test_to_dict(self, poll):
        poll_dict = poll.to_dict()

        assert isinstance(poll_dict, dict)
        assert poll_dict["id"] == poll.id
        assert poll_dict["question"] == poll.question
        assert poll_dict["options"] == [o.to_dict() for o in poll.options]
        assert poll_dict["total_voter_count"] == poll.total_voter_count
        assert poll_dict["is_closed"] == poll.is_closed
        assert poll_dict["is_anonymous"] == poll.is_anonymous
        assert poll_dict["type"] == poll.type
        assert poll_dict["allows_multiple_answers"] == poll.allows_multiple_answers
        assert poll_dict["explanation"] == poll.explanation
        assert poll_dict["explanation_entities"] == [poll.explanation_entities[0].to_dict()]
        assert poll_dict["open_period"] == poll.open_period
        assert poll_dict["close_date"] == to_timestamp(poll.close_date)
        assert poll_dict["question_entities"] == [e.to_dict() for e in poll.question_entities]

    def test_equality(self):
        a = Poll(123, "question", ["O1", "O2"], 1, False, True, Poll.REGULAR, True)
        b = Poll(123, "question", ["o1", "o2"], 1, True, False, Poll.REGULAR, True)
        c = Poll(456, "question", ["o1", "o2"], 1, True, False, Poll.REGULAR, True)
        d = PollOption("Text", 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

    def test_enum_init(self):
        poll = Poll(
            type="foo",
            id="id",
            question="question",
            options=[],
            total_voter_count=0,
            is_closed=False,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        assert poll.type == "foo"
        poll = Poll(
            type=PollType.QUIZ,
            id="id",
            question="question",
            options=[],
            total_voter_count=0,
            is_closed=False,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        assert poll.type is PollType.QUIZ

    def test_parse_explanation_entity(self, poll):
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        poll.explanation_entities = [entity]

        assert poll.parse_explanation_entity(entity) == "http://google.com"

        with pytest.raises(RuntimeError, match="Poll has no"):
            Poll(
                "id",
                "question",
                [PollOption("text", voter_count=0)],
                total_voter_count=0,
                is_closed=False,
                is_anonymous=False,
                type=Poll.QUIZ,
                allows_multiple_answers=False,
            ).parse_explanation_entity(entity)

    def test_parse_explanation_entities(self, poll):
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        poll.explanation_entities = [entity_2, entity]

        assert poll.parse_explanation_entities(MessageEntity.URL) == {entity: "http://google.com"}
        assert poll.parse_explanation_entities() == {entity: "http://google.com", entity_2: "h"}

        with pytest.raises(RuntimeError, match="Poll has no"):
            Poll(
                "id",
                "question",
                [PollOption("text", voter_count=0)],
                total_voter_count=0,
                is_closed=False,
                is_anonymous=False,
                type=Poll.QUIZ,
                allows_multiple_answers=False,
            ).parse_explanation_entities()

    def test_parse_question_entity(self, poll):
        entity = MessageEntity(MessageEntity.ITALIC, 5, 8)
        poll.question_entities = [entity]

        assert poll.parse_question_entity(entity) == "Question"

    def test_parse_question_entities(self, poll):
        entity = MessageEntity(MessageEntity.ITALIC, 5, 8)
        entity_2 = MessageEntity(MessageEntity.BOLD, 0, 4)
        poll.question_entities = [entity_2, entity]

        assert poll.parse_question_entities(MessageEntity.ITALIC) == {entity: "Question"}
        assert poll.parse_question_entities() == {entity: "Question", entity_2: "Test"}
