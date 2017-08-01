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

import pytest

from telegram import (InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton,
                      InlineKeyboardMarkup, InlineQueryResultContact)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'id': TestInlineQueryResultContact.id,
        'type': TestInlineQueryResultContact.type,
        'phone_number': TestInlineQueryResultContact.phone_number,
        'first_name': TestInlineQueryResultContact.first_name,
        'last_name': TestInlineQueryResultContact.last_name,
        'thumb_url': TestInlineQueryResultContact.thumb_url,
        'thumb_width': TestInlineQueryResultContact.thumb_width,
        'thumb_height': TestInlineQueryResultContact.thumb_height,
        'input_message_content': TestInlineQueryResultContact.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultContact.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_contact():
    return InlineQueryResultContact(id=TestInlineQueryResultContact.id,
                                    type=TestInlineQueryResultContact.type,
                                    phone_number=TestInlineQueryResultContact.phone_number,
                                    first_name=TestInlineQueryResultContact.first_name,
                                    last_name=TestInlineQueryResultContact.last_name,
                                    thumb_url=TestInlineQueryResultContact.thumb_url,
                                    thumb_width=TestInlineQueryResultContact.thumb_width,
                                    thumb_height=TestInlineQueryResultContact.thumb_height,
                                    input_message_content=TestInlineQueryResultContact.input_message_content,
                                    reply_markup=TestInlineQueryResultContact.reply_markup)


class TestInlineQueryResultContact:
    """This object represents Tests for Telegram InlineQueryResultContact."""

    id = 'id'
    type = 'contact'
    phone_number = 'phone_number'
    first_name = 'first_name'
    last_name = 'last_name'
    thumb_url = 'thumb url'
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_contact_de_json(self):
        contact = InlineQueryResultContact.de_json(json_dict, bot)

        assert contact.id == self.id
        assert contact.type == self.type
        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name
        assert contact.last_name == self.last_name
        assert contact.thumb_url == self.thumb_url
        assert contact.thumb_width == self.thumb_width
        assert contact.thumb_height == self.thumb_height
        self.assertDictEqual(contact.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert contact.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_contact_to_json(self):
        contact = InlineQueryResultContact.de_json(json_dict, bot)

        json.loads(contact.to_json())

    def test_contact_to_dict(self):
        contact = InlineQueryResultContact.de_json(json_dict, bot).to_dict()

        assert isinstance(contact, dict)
        assert json_dict == contact

    def test_equality(self):
        a = InlineQueryResultContact(self.id, self.phone_number, self.first_name)
        b = InlineQueryResultContact(self.id, self.phone_number, self.first_name)
        c = InlineQueryResultContact(self.id, "", self.first_name)
        d = InlineQueryResultContact("", self.phone_number, self.first_name)
        e = InlineQueryResultArticle(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
