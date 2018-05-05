#!/usr/bin/env python
#
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

from telegram import User, Location, InlineQuery, Update


@pytest.fixture(scope='class')
def inline_query(bot):
    return InlineQuery(TestInlineQuery.id, TestInlineQuery.from_user, TestInlineQuery.query,
                       TestInlineQuery.offset, location=TestInlineQuery.location, bot=bot)


class TestInlineQuery(object):
    id = 1234
    from_user = User(1, 'First name', False)
    query = 'query text'
    offset = 'offset'
    location = Location(8.8, 53.1)

    def test_de_json(self, bot):
        json_dict = {
            'id': self.id,
            'from': self.from_user.to_dict(),
            'query': self.query,
            'offset': self.offset,
            'location': self.location.to_dict()
        }
        inline_query_json = InlineQuery.de_json(json_dict, bot)

        assert inline_query_json.id == self.id
        assert inline_query_json.from_user == self.from_user
        assert inline_query_json.location == self.location
        assert inline_query_json.query == self.query
        assert inline_query_json.offset == self.offset

    def test_to_dict(self, inline_query):
        inline_query_dict = inline_query.to_dict()

        assert isinstance(inline_query_dict, dict)
        assert inline_query_dict['id'] == inline_query.id
        assert inline_query_dict['from'] == inline_query.from_user.to_dict()
        assert inline_query_dict['location'] == inline_query.location.to_dict()
        assert inline_query_dict['query'] == inline_query.query
        assert inline_query_dict['offset'] == inline_query.offset

    def test_answer(self, monkeypatch, inline_query):
        def test(*args, **kwargs):
            return args[1] == inline_query.id

        monkeypatch.setattr('telegram.Bot.answer_inline_query', test)
        assert inline_query.answer()

    def test_equality(self):
        a = InlineQuery(self.id, User(1, '', False), '', '')
        b = InlineQuery(self.id, User(1, '', False), '', '')
        c = InlineQuery(self.id, User(0, '', False), '', '')
        d = InlineQuery(0, User(1, '', False), '', '')
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
