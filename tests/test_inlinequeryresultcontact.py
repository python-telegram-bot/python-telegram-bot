#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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


@pytest.fixture(scope="module")
def inline_query_result_contact():
    return InlineQueryResultContact(
        Space.id_,
        Space.phone_number,
        Space.first_name,
        last_name=Space.last_name,
        thumb_url=Space.thumb_url,
        thumb_width=Space.thumb_width,
        thumb_height=Space.thumb_height,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "contact"
    phone_number = "phone_number"
    first_name = "first_name"
    last_name = "last_name"
    thumb_url = "thumb url"
    thumb_width = 10
    thumb_height = 15
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultContactWithoutRequest:
    def test_slot_behaviour(self, inline_query_result_contact, mro_slots):
        inst = inline_query_result_contact
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_contact):
        assert inline_query_result_contact.id == Space.id_
        assert inline_query_result_contact.type == Space.type_
        assert inline_query_result_contact.phone_number == Space.phone_number
        assert inline_query_result_contact.first_name == Space.first_name
        assert inline_query_result_contact.last_name == Space.last_name
        assert inline_query_result_contact.thumb_url == Space.thumb_url
        assert inline_query_result_contact.thumb_width == Space.thumb_width
        assert inline_query_result_contact.thumb_height == Space.thumb_height
        assert (
            inline_query_result_contact.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_contact.reply_markup.to_dict() == Space.reply_markup.to_dict()

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
            inline_query_result_contact_dict["thumb_url"] == inline_query_result_contact.thumb_url
        )
        assert (
            inline_query_result_contact_dict["thumb_width"]
            == inline_query_result_contact.thumb_width
        )
        assert (
            inline_query_result_contact_dict["thumb_height"]
            == inline_query_result_contact.thumb_height
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
        a = InlineQueryResultContact(Space.id_, Space.phone_number, Space.first_name)
        b = InlineQueryResultContact(Space.id_, Space.phone_number, Space.first_name)
        c = InlineQueryResultContact(Space.id_, "", Space.first_name)
        d = InlineQueryResultContact("", Space.phone_number, Space.first_name)
        e = InlineQueryResultVoice(Space.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
