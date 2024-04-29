#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultContact,
    InlineQueryResultVoice,
    InputTextMessageContent,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_contact():
    return InlineQueryResultContact(
        TestInlineQueryResultContactBase.id_,
        TestInlineQueryResultContactBase.phone_number,
        TestInlineQueryResultContactBase.first_name,
        last_name=TestInlineQueryResultContactBase.last_name,
        thumbnail_url=TestInlineQueryResultContactBase.thumbnail_url,
        thumbnail_width=TestInlineQueryResultContactBase.thumbnail_width,
        thumbnail_height=TestInlineQueryResultContactBase.thumbnail_height,
        input_message_content=TestInlineQueryResultContactBase.input_message_content,
        reply_markup=TestInlineQueryResultContactBase.reply_markup,
    )


class TestInlineQueryResultContactBase:
    id_ = "id"
    type_ = "contact"
    phone_number = "phone_number"
    first_name = "first_name"
    last_name = "last_name"
    thumbnail_url = "thumb url"
    thumbnail_width = 10
    thumbnail_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultContactWithoutRequest(TestInlineQueryResultContactBase):
    def test_slot_behaviour(self, inline_query_result_contact):
        inst = inline_query_result_contact
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_contact):
        assert inline_query_result_contact.id == self.id_
        assert inline_query_result_contact.type == self.type_
        assert inline_query_result_contact.phone_number == self.phone_number
        assert inline_query_result_contact.first_name == self.first_name
        assert inline_query_result_contact.last_name == self.last_name
        assert inline_query_result_contact.thumbnail_url == self.thumbnail_url
        assert inline_query_result_contact.thumbnail_width == self.thumbnail_width
        assert inline_query_result_contact.thumbnail_height == self.thumbnail_height
        assert (
            inline_query_result_contact.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_contact.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_contact):
        inline_query_result_contact_dict = inline_query_result_contact.to_dict()

        assert isinstance(inline_query_result_contact_dict, dict)
        assert inline_query_result_contact_dict["id"] == inline_query_result_contact.id
        assert inline_query_result_contact_dict["type"] == inline_query_result_contact.type
        assert (
            inline_query_result_contact_dict["phone_number"]
            == inline_query_result_contact.phone_number
        )
        assert (
            inline_query_result_contact_dict["first_name"]
            == inline_query_result_contact.first_name
        )
        assert (
            inline_query_result_contact_dict["last_name"] == inline_query_result_contact.last_name
        )
        assert (
            inline_query_result_contact_dict["thumbnail_url"]
            == inline_query_result_contact.thumbnail_url
        )
        assert (
            inline_query_result_contact_dict["thumbnail_width"]
            == inline_query_result_contact.thumbnail_width
        )
        assert (
            inline_query_result_contact_dict["thumbnail_height"]
            == inline_query_result_contact.thumbnail_height
        )
        assert (
            inline_query_result_contact_dict["input_message_content"]
            == inline_query_result_contact.input_message_content.to_dict()
        )
        assert (
            inline_query_result_contact_dict["reply_markup"]
            == inline_query_result_contact.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultContact(self.id_, self.phone_number, self.first_name)
        b = InlineQueryResultContact(self.id_, self.phone_number, self.first_name)
        c = InlineQueryResultContact(self.id_, "", self.first_name)
        d = InlineQueryResultContact("", self.phone_number, self.first_name)
        e = InlineQueryResultVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
