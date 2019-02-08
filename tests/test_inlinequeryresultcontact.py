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

from telegram import (InlineQueryResultVoice, InputTextMessageContent, InlineKeyboardButton,
                      InlineKeyboardMarkup, InlineQueryResultContact)


@pytest.fixture(scope='class')
def inline_query_result_contact():
    return InlineQueryResultContact(
        TestInlineQueryResultContact.id,
        TestInlineQueryResultContact.phone_number,
        TestInlineQueryResultContact.first_name,
        last_name=TestInlineQueryResultContact.last_name,
        thumb_url=TestInlineQueryResultContact.thumb_url,
        thumb_width=TestInlineQueryResultContact.thumb_width,
        thumb_height=TestInlineQueryResultContact.thumb_height,
        input_message_content=TestInlineQueryResultContact.input_message_content,
        reply_markup=TestInlineQueryResultContact.reply_markup)


class TestInlineQueryResultContact(object):
    id = 'id'
    type = 'contact'
    phone_number = 'phone_number'
    first_name = 'first_name'
    last_name = 'last_name'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_contact):
        assert inline_query_result_contact.id == self.id
        assert inline_query_result_contact.type == self.type
        assert inline_query_result_contact.phone_number == self.phone_number
        assert inline_query_result_contact.first_name == self.first_name
        assert inline_query_result_contact.last_name == self.last_name
        assert inline_query_result_contact.thumb_url == self.thumb_url
        assert inline_query_result_contact.thumb_width == self.thumb_width
        assert inline_query_result_contact.thumb_height == self.thumb_height
        assert (inline_query_result_contact.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_contact.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_contact):
        inline_query_result_contact_dict = inline_query_result_contact.to_dict()

        assert isinstance(inline_query_result_contact_dict, dict)
        assert inline_query_result_contact_dict['id'] == inline_query_result_contact.id
        assert inline_query_result_contact_dict['type'] == inline_query_result_contact.type
        assert (inline_query_result_contact_dict['phone_number']
                == inline_query_result_contact.phone_number)
        assert (inline_query_result_contact_dict['first_name']
                == inline_query_result_contact.first_name)
        assert (inline_query_result_contact_dict['last_name']
                == inline_query_result_contact.last_name)
        assert (inline_query_result_contact_dict['thumb_url']
                == inline_query_result_contact.thumb_url)
        assert (inline_query_result_contact_dict['thumb_width']
                == inline_query_result_contact.thumb_width)
        assert (inline_query_result_contact_dict['thumb_height']
                == inline_query_result_contact.thumb_height)
        assert (inline_query_result_contact_dict['input_message_content']
                == inline_query_result_contact.input_message_content.to_dict())
        assert (inline_query_result_contact_dict['reply_markup']
                == inline_query_result_contact.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultContact(self.id, self.phone_number, self.first_name)
        b = InlineQueryResultContact(self.id, self.phone_number, self.first_name)
        c = InlineQueryResultContact(self.id, '', self.first_name)
        d = InlineQueryResultContact('', self.phone_number, self.first_name)
        e = InlineQueryResultVoice(self.id, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
