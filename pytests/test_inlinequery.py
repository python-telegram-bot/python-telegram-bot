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

from telegram import User, Location, InlineQuery, Update


@pytest.fixture(scope='class')
def inlinequery():
    return InlineQuery(TestInlineQuery.id, TestInlineQuery.from_user, TestInlineQuery.query,
                       TestInlineQuery.offset, location=TestInlineQuery.location)


class TestInlineQuery:
    id = 1234
    from_user = User(1, 'First name')
    query = 'query text'
    offset = 'offset'
    location = Location(8.8, 53.1)

    def test_inlinequery_de_json(self, bot):
        json_dict = {
            'id': self.id,
            'from': self.from_user.to_dict(),
            'query': self.query,
            'offset': self.offset,
            'location': self.location.to_dict()
        }
        inlinequery_json = InlineQuery.de_json(json_dict, bot)

        assert inlinequery_json.id == self.id
        assert inlinequery_json.from_user == self.from_user
        assert inlinequery_json.location == self.location
        assert inlinequery_json.query == self.query
        assert inlinequery_json.offset == self.offset

    def test_inlinequery_to_json(self, inlinequery):
        json.loads(inlinequery.to_json())

    def test_inlinequery_to_dict(self, inlinequery):
        inlinequery_dict = inlinequery.to_dict()
        
        assert isinstance(inlinequery_dict, dict)
        assert inlinequery_dict['id'] == inlinequery.id
        assert inlinequery_dict['from'] == inlinequery.from_user.to_dict()
        assert inlinequery_dict['location'] == inlinequery.location.to_dict()
        assert inlinequery_dict['query'] == inlinequery.query
        assert inlinequery_dict['offset'] == inlinequery.offset

    def test_equality(self):
        a = InlineQuery(self.id, User(1, ""), "", "")
        b = InlineQuery(self.id, User(1, ""), "", "")
        c = InlineQuery(self.id, User(0, ""), "", "")
        d = InlineQuery(0, User(1, ""), "", "")
        e = Update(self.id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
