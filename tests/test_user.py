#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

from telegram import User, Update


@pytest.fixture(scope='function')
def json_dict():
    return {
        'id': TestUser.id,
        'first_name': TestUser.first_name,
        'last_name': TestUser.last_name,
        'username': TestUser.username,
        'language_code': TestUser.language_code
    }


@pytest.fixture(scope='function')
def user(bot):
    return User(TestUser.id, TestUser.first_name, last_name=TestUser.last_name,
                username=TestUser.username, language_code=TestUser.language_code, bot=bot)


class TestUser(object):
    id = 1
    first_name = 'first_name'
    last_name = 'last_name'
    username = 'username'
    language_code = 'en_us'

    def test_de_json(self, json_dict, bot):
        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.username == self.username
        assert user.language_code == self.language_code

    def test_de_json_without_username(self, json_dict, bot):
        del json_dict['username']

        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.username is None
        assert user.language_code == self.language_code

    def test_de_json_without_username_and_last_name(self, json_dict, bot):
        del json_dict['username']
        del json_dict['last_name']

        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.first_name == self.first_name
        assert user.last_name is None
        assert user.username is None
        assert user.language_code == self.language_code

    def test_name(self, user):
        assert user.name == '@username'
        user.username = None
        assert user.name == 'first_name last_name'
        user.last_name = None
        assert user.name == 'first_name'
        user.username = self.username
        assert user.name == '@username'

    def test_get_profile_photos(self, monkeypatch, user):
        def test(_, *args, **kwargs):
            return args[0] == user.id

        monkeypatch.setattr('telegram.Bot.get_user_profile_photos', test)
        assert user.get_profile_photos()

    def test_equality(self):
        a = User(self.id, self.first_name, self.last_name)
        b = User(self.id, self.first_name, self.last_name)
        c = User(self.id, self.first_name)
        d = User(0, self.first_name, self.last_name)
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
