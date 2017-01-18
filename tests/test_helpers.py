#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains an object that represents Tests for Telegram
MessageEntity"""

import sys
import unittest

from telegram.utils import helpers

sys.path.append('.')

import telegram
from tests.base import BaseTest


class HelpersTest(BaseTest, unittest.TestCase):
    """This object represents Tests for the Helpers Module"""

    def setUp(self):
        self.test_entities = [
            {
                'length': 4,
                'offset': 9,
                'type': 'bold'
            },
            {
                'length': 6,
                'offset': 15,
                'type': 'italic'
            },
            {
                'length': 4,
                'offset': 23,
                'type': 'code'
            },
            {
                'length': 5,
                'offset': 29,
                'type': 'text_link',
                'url': 'http://github.com/'
            },
            {
                'length': 3,
                'offset': 39,
                'type': 'pre'
            },
        ]

        self.test_text = 'Test for bold, italic, code, links and pre.'
        self.update_id = 868573637
        self.message = {
            'message_id': 319,
            'from': {
                'id': 12173560,
                'first_name': "Leandro",
                'last_name': "S.",
                'username': "leandrotoledo"
            },
            'chat': {
                'id': 12173560,
                'type': 'private',
                'first_name': "Leandro",
                'last_name': "S.",
                'username': "leandrotoledo"
            },
            'entities': self.test_entities,
            'date': 1441644592,
            'text': self.test_text
        }

        self.json_dict = {'update_id': self.update_id, 'message': self.message}

    def test_parse_html_from_update(self):
        test_html_string = 'Test for <b>bold</b>, <i>italic</i>, <code>code</code>, ' \
                           '<a href="http://github.com/">links</a> and <pre>pre</pre>.'
        update = telegram.Update.de_json(self.json_dict, self._bot)
        self.assertEquals(test_html_string, helpers.parse_html_from_update(update))

    def test_parse_markdown_from_update(self):
        test_md_string = 'Test for *bold*, _italic_, `code`, [links](http://github.com/) and ```\npre\n```.'
        update = telegram.Update.de_json(self.json_dict, self._bot)
        self.assertEquals(test_md_string, helpers.parse_markdown_from_update(update))

    def test_escape_markdown(self):
        test_str = "*bold*, _italic_, `code`, [text_link](http://github.com/)"
        expected_str = "\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)"
        self.assertEquals(expected_str, helpers.escape_markdown(test_str))


if __name__ == '__main__':
    unittest.main()
