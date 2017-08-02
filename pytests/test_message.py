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
from datetime import datetime

import pytest

from telegram import Update, Message, User, MessageEntity, TelegramError, Chat


@pytest.fixture(scope="function")
def message(bot):
    return Message(1, User(2, 'testuser'), datetime.now(), Chat(3, 'private'))

class TestMessage:
    """This object represents Tests for Telegram MessageTest."""

    test_entities = [{'length': 4,'offset': 10,'type': 'bold'},
                     {'length': 7,'offset': 16,'type': 'italic'},
                     {'length': 4,'offset': 25,'type': 'code'},
                     {'length': 5,'offset': 31,'type': 'text_link','url': 'http://github.com/'},
                     {'length': 3,'offset': 41,'type': 'pre'},]
    test_text = 'Test for <bold, ita_lic, code, links and pre.'
    test_message = Message(message_id=1,
                           from_user=None,
                           date=None,
                           chat=None,
                           text=test_text,
                           entities=[MessageEntity(**e) for e in test_entities])

    def test_de_json(self, bot):
    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[entity])
        assert message.parse_entity(entity) == 'http://google.com'

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            message_id=1,
            from_user=None,
            date=None,
            chat=None,
            text=text,
            entities=[entity_2, entity])
        self.assertDictEqual(
            message.parse_entities(MessageEntity.URL), {entity: 'http://google.com'})
        self.assertDictEqual(message.parse_entities(),
                             {entity: 'http://google.com',
                              entity_2: 'h'})

    def test_text_html_simple(self):
        test_html_string = 'Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, <a href="http://github.com/">links</a> and <pre>pre</pre>.'
        text_html = self.test_message.text_html
        assert test_html_string == text_html

    def test_text_markdown_simple(self):
        test_md_string = 'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/) and ```pre```.'
        text_markdown = self.test_message.text_markdown
        assert test_md_string == text_markdown

    def test_text_html_emoji(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d ABC').decode('unicode-escape')
        expected = (b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>').decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[bold_entity])
        assert expected == message.text_html

    def test_text_markdown_emoji(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d ABC').decode('unicode-escape')
        expected = (b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*').decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[bold_entity])
        assert expected == message.text_markdown

    def test_parse_entities_url_emoji(self):
        url = b'http://github.com/?unicode=\\u2713\\U0001f469'.decode('unicode-escape')
        text = 'some url'
        link_entity = MessageEntity(type=MessageEntity.URL, offset=0, length=8, url=url)
        message = Message(
            message_id=1,
            from_user=None,
            date=None,
            chat=None,
            text=text,
            entities=[link_entity])
        assert message.parse_entities() == {link_entity: text}
        assert next(iter(message.parse_entities())).url == url

    @flaky(3, 1)
    def test_reply_text(self):
        """Test for Message.reply_text"""
        message = bot.sendMessage(chat_id, '.')
        message = message.reply_text('Testing class method')

        json.loads(message.to_json())
        assert message.text == 'Testing class method'

    @flaky(3, 1)
    def test_forward(self):
        """Test for Message.forward"""
        message = bot.sendMessage(chat_id, 'Testing class method')
        message = message.forward(self._chat_id)

        json.loads(message.to_json())
        assert message.text == 'Testing class method'

    @flaky(3, 1)
    def test_edit_text(self):
        """Test for Message.edit_text"""
        message = bot.sendMessage(chat_id, '.')
        message = message.edit_text('Testing class method')

        json.loads(message.to_json())
        assert message.text == 'Testing class method'

    @flaky(3, 1)
    def test_delete1(self):
        """Test for Message.delete"""
        message = bot.send_message(
            chat_id=chat_id, text='This message will be deleted')

        assert message.delete() is True

    @flaky(3, 1)
    def test_delete2(self):
        """Another test for Message.delete"""
        message = bot.send_message(
            chat_id=chat_id,
            text='This ^ message will not be deleted',
            reply_to_message_id=1)

        with self.assertRaisesRegexp(TelegramError, "can't be deleted"):
            message.reply_to_message.delete()

    def test_equality(self):
        _id = 1
        a = Message(_id, User(1, ""), None, None)
        b = Message(_id, User(1, ""), None, None)
        c = Message(_id, User(0, ""), None, None)
        d = Message(0, User(1, ""), None, None)
        e = Update(_id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


