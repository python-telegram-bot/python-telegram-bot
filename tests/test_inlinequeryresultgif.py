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
    InlineQueryResultGif,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_gif():
    return InlineQueryResultGif(
        Space.id_,
        Space.gif_url,
        Space.thumb_url,
        gif_width=Space.gif_width,
        gif_height=Space.gif_height,
        gif_duration=Space.gif_duration,
        title=Space.title,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
        thumb_mime_type=Space.thumb_mime_type,
    )


class Space:
    id_ = "id"
    type_ = "gif"
    gif_url = "gif url"
    gif_width = 10
    gif_height = 15
    gif_duration = 1
    thumb_url = "thumb url"
    thumb_mime_type = "image/jpeg"
    title = "title"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultGifWithoutRequest:
    def test_slot_behaviour(self, inline_query_result_gif, mro_slots):
        inst = inline_query_result_gif
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultGif(Space.id_, Space.gif_url, Space.thumb_url)
        assert result.caption_entities == ()

    def test_expected_values(self, inline_query_result_gif):
        assert inline_query_result_gif.type == Space.type_
        assert inline_query_result_gif.id == Space.id_
        assert inline_query_result_gif.gif_url == Space.gif_url
        assert inline_query_result_gif.gif_width == Space.gif_width
        assert inline_query_result_gif.gif_height == Space.gif_height
        assert inline_query_result_gif.gif_duration == Space.gif_duration
        assert inline_query_result_gif.thumb_url == Space.thumb_url
        assert inline_query_result_gif.thumb_mime_type == Space.thumb_mime_type
        assert inline_query_result_gif.title == Space.title
        assert inline_query_result_gif.caption == Space.caption
        assert inline_query_result_gif.parse_mode == Space.parse_mode
        assert inline_query_result_gif.caption_entities == tuple(Space.caption_entities)
        assert (
            inline_query_result_gif.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_gif.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_gif):
        inline_query_result_gif_dict = inline_query_result_gif.to_dict()

        assert isinstance(inline_query_result_gif_dict, dict)
        assert inline_query_result_gif_dict["type"] == inline_query_result_gif.type
        assert inline_query_result_gif_dict["id"] == inline_query_result_gif.id
        assert inline_query_result_gif_dict["gif_url"] == inline_query_result_gif.gif_url
        assert inline_query_result_gif_dict["gif_width"] == inline_query_result_gif.gif_width
        assert inline_query_result_gif_dict["gif_height"] == inline_query_result_gif.gif_height
        assert inline_query_result_gif_dict["gif_duration"] == inline_query_result_gif.gif_duration
        assert inline_query_result_gif_dict["thumb_url"] == inline_query_result_gif.thumb_url
        assert (
            inline_query_result_gif_dict["thumb_mime_type"]
            == inline_query_result_gif.thumb_mime_type
        )
        assert inline_query_result_gif_dict["title"] == inline_query_result_gif.title
        assert inline_query_result_gif_dict["caption"] == inline_query_result_gif.caption
        assert inline_query_result_gif_dict["parse_mode"] == inline_query_result_gif.parse_mode
        assert inline_query_result_gif_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_gif.caption_entities
        ]
        assert (
            inline_query_result_gif_dict["input_message_content"]
            == inline_query_result_gif.input_message_content.to_dict()
        )
        assert (
            inline_query_result_gif_dict["reply_markup"]
            == inline_query_result_gif.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultGif(Space.id_, Space.gif_url, Space.thumb_url)
        b = InlineQueryResultGif(Space.id_, Space.gif_url, Space.thumb_url)
        c = InlineQueryResultGif(Space.id_, "", Space.thumb_url)
        d = InlineQueryResultGif("", Space.gif_url, Space.thumb_url)
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
