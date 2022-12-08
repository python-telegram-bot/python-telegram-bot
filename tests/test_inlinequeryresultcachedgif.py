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
    InlineQueryResultCachedGif,
    InlineQueryResultCachedVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_cached_gif():
    return InlineQueryResultCachedGif(
        Space.id_,
        Space.gif_file_id,
        title=Space.title,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "gif"
    gif_file_id = "gif file id"
    title = "title"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultCachedGifNoReq:
    def test_slot_behaviour(self, inline_query_result_cached_gif, mro_slots):
        inst = inline_query_result_cached_gif
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_cached_gif):
        assert inline_query_result_cached_gif.type == Space.type_
        assert inline_query_result_cached_gif.id == Space.id_
        assert inline_query_result_cached_gif.gif_file_id == Space.gif_file_id
        assert inline_query_result_cached_gif.title == Space.title
        assert inline_query_result_cached_gif.caption == Space.caption
        assert inline_query_result_cached_gif.parse_mode == Space.parse_mode
        assert inline_query_result_cached_gif.caption_entities == tuple(Space.caption_entities)
        assert (
            inline_query_result_cached_gif.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_gif.reply_markup.to_dict() == Space.reply_markup.to_dict()
        )

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultCachedGif(Space.id_, Space.gif_file_id)
        assert result.caption_entities == ()

    def test_to_dict(self, inline_query_result_cached_gif):
        inline_query_result_cached_gif_dict = inline_query_result_cached_gif.to_dict()

        assert isinstance(inline_query_result_cached_gif_dict, dict)
        assert inline_query_result_cached_gif_dict["type"] == inline_query_result_cached_gif.type
        assert inline_query_result_cached_gif_dict["id"] == inline_query_result_cached_gif.id
        assert (
            inline_query_result_cached_gif_dict["gif_file_id"]
            == inline_query_result_cached_gif.gif_file_id
        )
        assert inline_query_result_cached_gif_dict["title"] == inline_query_result_cached_gif.title
        assert (
            inline_query_result_cached_gif_dict["caption"]
            == inline_query_result_cached_gif.caption
        )
        assert (
            inline_query_result_cached_gif_dict["parse_mode"]
            == inline_query_result_cached_gif.parse_mode
        )
        assert inline_query_result_cached_gif_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_cached_gif.caption_entities
        ]
        assert (
            inline_query_result_cached_gif_dict["input_message_content"]
            == inline_query_result_cached_gif.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_gif_dict["reply_markup"]
            == inline_query_result_cached_gif.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultCachedGif(Space.id_, Space.gif_file_id)
        b = InlineQueryResultCachedGif(Space.id_, Space.gif_file_id)
        c = InlineQueryResultCachedGif(Space.id_, "")
        d = InlineQueryResultCachedGif("", Space.gif_file_id)
        e = InlineQueryResultCachedVoice(Space.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
