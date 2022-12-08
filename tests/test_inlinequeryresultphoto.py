#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
    InlineQueryResultPhoto,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_photo():
    return InlineQueryResultPhoto(
        Space.id_,
        Space.photo_url,
        Space.thumb_url,
        photo_width=Space.photo_width,
        photo_height=Space.photo_height,
        title=Space.title,
        description=Space.description,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "photo"
    photo_url = "photo url"
    photo_width = 10
    photo_height = 15
    thumb_url = "thumb url"
    title = "title"
    description = "description"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]

    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultPhotoNoReq:
    def test_slot_behaviour(self, inline_query_result_photo, mro_slots):
        inst = inline_query_result_photo
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_photo):
        assert inline_query_result_photo.type == Space.type_
        assert inline_query_result_photo.id == Space.id_
        assert inline_query_result_photo.photo_url == Space.photo_url
        assert inline_query_result_photo.photo_width == Space.photo_width
        assert inline_query_result_photo.photo_height == Space.photo_height
        assert inline_query_result_photo.thumb_url == Space.thumb_url
        assert inline_query_result_photo.title == Space.title
        assert inline_query_result_photo.description == Space.description
        assert inline_query_result_photo.caption == Space.caption
        assert inline_query_result_photo.parse_mode == Space.parse_mode
        assert inline_query_result_photo.caption_entities == tuple(Space.caption_entities)
        assert (
            inline_query_result_photo.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_photo.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultPhoto(Space.id_, Space.photo_url, Space.thumb_url)
        assert result.caption_entities == ()

    def test_to_dict(self, inline_query_result_photo):
        inline_query_result_photo_dict = inline_query_result_photo.to_dict()

        assert isinstance(inline_query_result_photo_dict, dict)
        assert inline_query_result_photo_dict["type"] == inline_query_result_photo.type
        assert inline_query_result_photo_dict["id"] == inline_query_result_photo.id
        assert inline_query_result_photo_dict["photo_url"] == inline_query_result_photo.photo_url
        assert (
            inline_query_result_photo_dict["photo_width"] == inline_query_result_photo.photo_width
        )
        assert (
            inline_query_result_photo_dict["photo_height"]
            == inline_query_result_photo.photo_height
        )
        assert inline_query_result_photo_dict["thumb_url"] == inline_query_result_photo.thumb_url
        assert inline_query_result_photo_dict["title"] == inline_query_result_photo.title
        assert (
            inline_query_result_photo_dict["description"] == inline_query_result_photo.description
        )
        assert inline_query_result_photo_dict["caption"] == inline_query_result_photo.caption
        assert inline_query_result_photo_dict["parse_mode"] == inline_query_result_photo.parse_mode
        assert inline_query_result_photo_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_photo.caption_entities
        ]
        assert (
            inline_query_result_photo_dict["input_message_content"]
            == inline_query_result_photo.input_message_content.to_dict()
        )
        assert (
            inline_query_result_photo_dict["reply_markup"]
            == inline_query_result_photo.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultPhoto(Space.id_, Space.photo_url, Space.thumb_url)
        b = InlineQueryResultPhoto(Space.id_, Space.photo_url, Space.thumb_url)
        c = InlineQueryResultPhoto(Space.id_, "", Space.thumb_url)
        d = InlineQueryResultPhoto("", Space.photo_url, Space.thumb_url)
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
