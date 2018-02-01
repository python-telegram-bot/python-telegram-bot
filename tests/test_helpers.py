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

from telegram.utils import helpers


class TestHelpers(object):
    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = '\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    def test_create_deep_linked_url(self):
        username = 'JamesTheMock'

        payload = "hello"
        expected = "https://t.me/{}?start={}".format(username, payload)
        actual = helpers.create_deep_linked_url(username, payload)
        assert expected == actual

        payload = ""
        expected = "https://t.me/{}".format(username)
        assert expected == helpers.create_deep_linked_url(username, payload)
        assert expected == helpers.create_deep_linked_url(username)

        try:
            # Invalid characters
            helpers.create_deep_linked_url(username, 'text with spaces')
            pytest.fail()
        except Exception as e:
            assert isinstance(e, ValueError)

        try:
            # Too long payload
            helpers.create_deep_linked_url(username, '0' * 65)
            pytest.fail()
        except Exception as e:
            assert isinstance(e, ValueError)
