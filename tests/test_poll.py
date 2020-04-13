#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import pytest

from telegram import Poll, PollOption, PollAnswer, User


@pytest.fixture(scope="class")
def poll_option():
    return PollOption(text=TestPollOption.text,
                      voter_count=TestPollOption.voter_count)


class TestPollOption(object):
    text = "test option"
    voter_count = 3

    def test_de_json(self):
        json_dict = {
            'text': self.text,
            'voter_count': self.voter_count
        }
        poll_option = PollOption.de_json(json_dict, None)

        assert poll_option.text == self.text
        assert poll_option.voter_count == self.voter_count

    def test_to_dict(self, poll_option):
        poll_option_dict = poll_option.to_dict()

        assert isinstance(poll_option_dict, dict)
        assert poll_option_dict['text'] == poll_option.text
        assert poll_option_dict['voter_count'] == poll_option.voter_count


@pytest.fixture(scope="class")
def poll_answer():
    return PollAnswer(poll_id=TestPollAnswer.poll_id, user=TestPollAnswer.user,
                      option_ids=TestPollAnswer.poll_id)


class TestPollAnswer(object):
    poll_id = 'id'
    user = User(1, '', False)
    option_ids = [2]

    def test_de_json(self):
        json_dict = {
            'poll_id': self.poll_id,
            'user': self.user.to_dict(),
            'option_ids': self.option_ids
        }
        poll_answer = PollAnswer.de_json(json_dict, None)

        assert poll_answer.poll_id == self.poll_id
        assert poll_answer.user == self.user
        assert poll_answer.option_ids == self.option_ids

    def test_to_dict(self, poll_answer):
        poll_answer_dict = poll_answer.to_dict()

        assert isinstance(poll_answer_dict, dict)
        assert poll_answer_dict['poll_id'] == poll_answer.poll_id
        assert poll_answer_dict['user'] == poll_answer.user.to_dict()
        assert poll_answer_dict['option_ids'] == poll_answer.option_ids


@pytest.fixture(scope='class')
def poll():
    return Poll(TestPoll.id_,
                TestPoll.question,
                TestPoll.options,
                TestPoll.total_voter_count,
                TestPoll.is_closed,
                TestPoll.is_anonymous,
                TestPoll.type,
                TestPoll.allows_multiple_answers
                )


class TestPoll(object):
    id_ = 'id'
    question = 'Test?'
    options = [PollOption('test', 10), PollOption('test2', 11)]
    total_voter_count = 0
    is_closed = True
    is_anonymous = False
    type = Poll.REGULAR
    allows_multiple_answers = True

    def test_de_json(self):
        json_dict = {
            'id': self.id_,
            'question': self.question,
            'options': [o.to_dict() for o in self.options],
            'total_voter_count': self.total_voter_count,
            'is_closed': self.is_closed,
            'is_anonymous': self.is_anonymous,
            'type': self.type,
            'allows_multiple_answers': self.allows_multiple_answers
        }
        poll = Poll.de_json(json_dict, None)

        assert poll.id == self.id_
        assert poll.question == self.question
        assert poll.options == self.options
        assert poll.options[0].text == self.options[0].text
        assert poll.options[0].voter_count == self.options[0].voter_count
        assert poll.options[1].text == self.options[1].text
        assert poll.options[1].voter_count == self.options[1].voter_count
        assert poll.total_voter_count == self.total_voter_count
        assert poll.is_closed == self.is_closed
        assert poll.is_anonymous == self.is_anonymous
        assert poll.type == self.type
        assert poll.allows_multiple_answers == self.allows_multiple_answers

    def test_to_dict(self, poll):
        poll_dict = poll.to_dict()

        assert isinstance(poll_dict, dict)
        assert poll_dict['id'] == poll.id
        assert poll_dict['question'] == poll.question
        assert poll_dict['options'] == [o.to_dict() for o in poll.options]
        assert poll_dict['total_voter_count'] == poll.total_voter_count
        assert poll_dict['is_closed'] == poll.is_closed
        assert poll_dict['is_anonymous'] == poll.is_anonymous
        assert poll_dict['type'] == poll.type
        assert poll_dict['allows_multiple_answers'] == poll.allows_multiple_answers
