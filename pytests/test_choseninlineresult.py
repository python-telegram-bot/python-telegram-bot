#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import User, ChosenInlineResult, Location, Voice


@pytest.fixture(scope='class')
def user():
    return User(1, 'First name')


@pytest.fixture(scope='class')
def chosen_inline_result(user):
    return ChosenInlineResult(TestChosenInlineResult.result_id, user, TestChosenInlineResult.query)


class TestChosenInlineResult:
    result_id = 'result id'
    query = 'query text'

    def test_choseninlineresult_de_json_required(self, bot, user):
        json_dict = {'result_id': self.result_id,
                     'from': user.to_dict(),
                     'query': self.query}
        result = ChosenInlineResult.de_json(json_dict, bot)

        assert result.result_id == self.result_id
        assert result.from_user == user
        assert result.query == self.query

    def test_choseninlineresult_de_json_all(self, bot, user):
        loc = Location(-42.003, 34.004)
        json_dict = {'result_id': self.result_id,
                     'from': user.to_dict(),
                     'query': self.query,
                     'location': loc.to_dict(),
                     'inline_message_id': "a random id"}
        result = ChosenInlineResult.de_json(json_dict, bot)

        assert result.result_id == self.result_id
        assert result.from_user == user
        assert result.query == self.query
        assert result.location == loc
        assert result.inline_message_id == "a random id"

    def test_choseninlineresult_to_json(self, chosen_inline_result):
        json.loads(chosen_inline_result.to_json())

    def test_choseninlineresult_to_dict(self, chosen_inline_result):
        choseninlineresult_dict = chosen_inline_result.to_dict()

        assert isinstance(choseninlineresult_dict, dict)
        assert choseninlineresult_dict['result_id'] == chosen_inline_result.result_id
        assert choseninlineresult_dict['from'] == chosen_inline_result.from_user.to_dict()
        assert choseninlineresult_dict['query'] == chosen_inline_result.query

    def test_equality(self, user):
        a = ChosenInlineResult(self.result_id, user, 'Query', '')
        b = ChosenInlineResult(self.result_id, user, 'Query', '')
        c = ChosenInlineResult(self.result_id, user, '', '')
        d = ChosenInlineResult('', user, 'Query', '')
        e = Voice(self.result_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
