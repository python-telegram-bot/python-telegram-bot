#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import Poll, PollOption


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

    def test_equality(self):
        a = PollOption('text', 1)
        b = PollOption('text', 2)
        c = PollOption('text_1', 1)
        d = Poll(123, 'question', ['O1', 'O2'], False)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture(scope='class')
def poll():
    return Poll(TestPoll.id,
                TestPoll.question,
                TestPoll.options,
                TestPoll.is_closed)


class TestPoll(object):
    id = 'id'
    question = 'Test?'
    options = [PollOption('test', 10), PollOption('test2', 11)]
    is_closed = True

    def test_de_json(self):
        json_dict = {
            'id': self.id,
            'question': self.question,
            'options': [o.to_dict() for o in self.options],
            'is_closed': self.is_closed
        }
        poll = Poll.de_json(json_dict, None)

        assert poll.id == self.id
        assert poll.question == self.question
        assert poll.options == self.options
        assert poll.options[0].text == self.options[0].text
        assert poll.options[0].voter_count == self.options[0].voter_count
        assert poll.options[1].text == self.options[1].text
        assert poll.options[1].voter_count == self.options[1].voter_count
        assert poll.is_closed == self.is_closed

    def test_to_dict(self, poll):
        poll_dict = poll.to_dict()

        assert isinstance(poll_dict, dict)
        assert poll_dict['id'] == poll.id
        assert poll_dict['question'] == poll.question
        assert poll_dict['options'] == [o.to_dict() for o in poll.options]
        assert poll_dict['is_closed'] == poll.is_closed

    def test_equality(self):
        a = Poll(123, 'question', ['o1', 'o2'], False)
        b = Poll(123, 'question?', ['o1.1', 'o2.2'], True)
        c = Poll(456, 'question?', ['o1.1', 'o2.2'], True)
        d = PollOption('Text', 1)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
