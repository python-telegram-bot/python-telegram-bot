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

from telegram import Sticker
from telegram import Update
from telegram import User
from telegram.message import Message
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

        expected = "https://t.me/{}?startgroup={}".format(username, payload)
        actual = helpers.create_deep_linked_url(username, payload, group=True)
        assert expected == actual

        payload = ""
        expected = "https://t.me/{}".format(username)
        assert expected == helpers.create_deep_linked_url(username)
        assert expected == helpers.create_deep_linked_url(username, payload)
        payload = None
        assert expected == helpers.create_deep_linked_url(username, payload)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, 'text with spaces')

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, '0' * 65)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(None, None)
        with pytest.raises(ValueError):  # too short username (4 is minimum)
            helpers.create_deep_linked_url("abc", None)

    def test_effective_message_type(self):

        def build_test_message(**kwargs):
            config = dict(
                message_id=1,
                from_user=None,
                date=None,
                chat=None,
            )
            config.update(**kwargs)
            return Message(**config)

        test_message = build_test_message(text='Test')
        assert helpers.effective_message_type(test_message) == 'text'
        test_message.text = None

        test_message = build_test_message(sticker=Sticker('sticker_id', 50, 50, False))
        assert helpers.effective_message_type(test_message) == 'sticker'
        test_message.sticker = None

        test_message = build_test_message(new_chat_members=[User(55, 'new_user', False)])
        assert helpers.effective_message_type(test_message) == 'new_chat_members'

        test_message = build_test_message(left_chat_member=[User(55, 'new_user', False)])
        assert helpers.effective_message_type(test_message) == 'left_chat_member'

        test_update = Update(1)
        test_message = build_test_message(text='Test')
        test_update.message = test_message
        assert helpers.effective_message_type(test_update) == 'text'

        empty_update = Update(2)
        assert helpers.effective_message_type(empty_update) is None

    def test_mention_html(self):
        expected = '<a href="tg://user?id=1">the name</a>'

        assert expected == helpers.mention_html(1, 'the name')

    def test_mention_markdown(self):
        expected = '[the name](tg://user?id=1)'

        assert expected == helpers.mention_markdown(1, 'the name')
