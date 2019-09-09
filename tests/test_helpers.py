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
from telegram import MessageEntity
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

    def test_extract_urls_entities(self):
        test_entities = [{
            'length': 6, 'offset': 0, 'type': 'text_link',
            'url': 'http://github.com/'
        }, {
            'length': 17, 'offset': 23, 'type': 'url'
        }, {
            'length': 14, 'offset': 43, 'type': 'text_link',
            'url': 'http://google.com'
        }]
        test_text = 'Github can be found at http://github.com. Google is here.'
        test_message = Message(message_id=1,
                               from_user=None,
                               date=None,
                               chat=None,
                               text=test_text,
                               entities=[MessageEntity(**e) for e in test_entities])
        result = helpers.extract_urls(test_message)

        assert len(result) == 2
        assert (test_entities[0]['url'] == result[0])
        assert (test_entities[2]['url'] == result[1])

    def test_extract_urls_caption(self):
        test_entities = [{
            'length': 109, 'offset': 11, 'type': 'url'
        }]
        caption = "Taken from https://stackoverflow.com/questions/520031/whats" \
                  "-the-cleanest-way-to-extract-urls-from-a-string-using-python/"
        test_message = Message(message_id=1,
                               from_user=None,
                               date=None,
                               chat=None,
                               caption=caption,
                               caption_entities=[MessageEntity(**e) for e in test_entities]
                               )
        results = helpers.extract_urls(test_message)

        assert len(results) == 1
        assert results[0] == 'https://stackoverflow.com/questions/520031/whats-the-' \
                             'cleanest-way-to-extract-urls-from-a-string-using-python/'

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
