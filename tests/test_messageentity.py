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

from telegram import MessageEntity, User


@pytest.fixture(scope="class",
                params=MessageEntity.ALL_TYPES)
def message_entity(request):
    type = request.param
    url = None
    if type == MessageEntity.TEXT_LINK:
        url = 't.me'
    user = None
    if type == MessageEntity.TEXT_MENTION:
        user = User(1, 'test_user', False)
    return MessageEntity(type, 1, 3, url=url, user=user)


class TestMessageEntity(object):
    type = 'url'
    offset = 1
    length = 2
    url = 'url'

    def test_de_json(self, bot):
        json_dict = {
            'type': self.type,
            'offset': self.offset,
            'length': self.length
        }
        entity = MessageEntity.de_json(json_dict, bot)

        assert entity.type == self.type
        assert entity.offset == self.offset
        assert entity.length == self.length

    def test_to_dict(self, message_entity):
        entity_dict = message_entity.to_dict()

        assert isinstance(entity_dict, dict)
        assert entity_dict['type'] == message_entity.type
        assert entity_dict['offset'] == message_entity.offset
        assert entity_dict['length'] == message_entity.length
        if message_entity.url:
            assert entity_dict['url'] == message_entity.url
        if message_entity.user:
            assert entity_dict['user'] == message_entity.user.to_dict()
