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

from telegram import Message
from telegram import MessageEntity
from telegram.utils import helpers


class TestHelpers(object):
    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = '\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    def test_extract_urls(self):
        test_entities = [{'length': 6, 'offset': 0, 'type': 'text_link',
                          'url': 'http://github.com/'},
                         {'length': 17, 'offset': 23, 'type': 'url'},
                         {'length': 14, 'offset': 43, 'type': 'text_link',
                          'url': 'http://google.com'}]
        test_text = 'Github can be found at http://github.com. Google is here.'
        test_message = Message(message_id=1,
                               from_user=None,
                               date=None,
                               chat=None,
                               text=test_text,
                               entities=[MessageEntity(**e) for e in test_entities])
        result = helpers.extract_urls(test_message)

        assert len(result) == 3
        assert (test_entities[0]['url'] == result[0])
        assert (result[1] == 'http://github.com')
        assert (test_entities[2]['url'] == result[2])
