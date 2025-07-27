#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
import datetime as dtm

import pytest

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultGif,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_gif():
    return InlineQueryResultGif(
        InlineQueryResultGifTestBase.id_,
        InlineQueryResultGifTestBase.gif_url,
        InlineQueryResultGifTestBase.thumbnail_url,
        gif_width=InlineQueryResultGifTestBase.gif_width,
        gif_height=InlineQueryResultGifTestBase.gif_height,
        gif_duration=InlineQueryResultGifTestBase.gif_duration,
        title=InlineQueryResultGifTestBase.title,
        caption=InlineQueryResultGifTestBase.caption,
        parse_mode=InlineQueryResultGifTestBase.parse_mode,
        caption_entities=InlineQueryResultGifTestBase.caption_entities,
        input_message_content=InlineQueryResultGifTestBase.input_message_content,
        reply_markup=InlineQueryResultGifTestBase.reply_markup,
        thumbnail_mime_type=InlineQueryResultGifTestBase.thumbnail_mime_type,
        show_caption_above_media=InlineQueryResultGifTestBase.show_caption_above_media,
    )


class InlineQueryResultGifTestBase:
    id_ = "id"
    type_ = "gif"
    gif_url = "gif url"
    gif_width = 10
    gif_height = 15
    gif_duration = dtm.timedelta(seconds=1)
    thumbnail_url = "thumb url"
    thumbnail_mime_type = "image/jpeg"
    title = "title"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])
    show_caption_above_media = True


class TestInlineQueryResultGifWithoutRequest(InlineQueryResultGifTestBase):
    def test_slot_behaviour(self, inline_query_result_gif):
        inst = inline_query_result_gif
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultGif(self.id_, self.gif_url, self.thumbnail_url)
        assert result.caption_entities == ()

    def test_expected_values(self, inline_query_result_gif):
        assert inline_query_result_gif.type == self.type_
        assert inline_query_result_gif.id == self.id_
        assert inline_query_result_gif.gif_url == self.gif_url
        assert inline_query_result_gif.gif_width == self.gif_width
        assert inline_query_result_gif.gif_height == self.gif_height
        assert inline_query_result_gif._gif_duration == self.gif_duration
        assert inline_query_result_gif.thumbnail_url == self.thumbnail_url
        assert inline_query_result_gif.thumbnail_mime_type == self.thumbnail_mime_type
        assert inline_query_result_gif.title == self.title
        assert inline_query_result_gif.caption == self.caption
        assert inline_query_result_gif.parse_mode == self.parse_mode
        assert inline_query_result_gif.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_gif.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_gif.reply_markup.to_dict() == self.reply_markup.to_dict()
        assert inline_query_result_gif.show_caption_above_media == self.show_caption_above_media

    def test_to_dict(self, inline_query_result_gif):
        inline_query_result_gif_dict = inline_query_result_gif.to_dict()

        assert isinstance(inline_query_result_gif_dict, dict)
        assert inline_query_result_gif_dict["type"] == inline_query_result_gif.type
        assert inline_query_result_gif_dict["id"] == inline_query_result_gif.id
        assert inline_query_result_gif_dict["gif_url"] == inline_query_result_gif.gif_url
        assert inline_query_result_gif_dict["gif_width"] == inline_query_result_gif.gif_width
        assert inline_query_result_gif_dict["gif_height"] == inline_query_result_gif.gif_height
        assert inline_query_result_gif_dict["gif_duration"] == int(
            self.gif_duration.total_seconds()
        )
        assert isinstance(inline_query_result_gif_dict["gif_duration"], int)
        assert (
            inline_query_result_gif_dict["thumbnail_url"] == inline_query_result_gif.thumbnail_url
        )
        assert (
            inline_query_result_gif_dict["thumbnail_mime_type"]
            == inline_query_result_gif.thumbnail_mime_type
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
        assert (
            inline_query_result_gif_dict["show_caption_above_media"]
            == inline_query_result_gif.show_caption_above_media
        )

    def test_time_period_properties(self, PTB_TIMEDELTA, inline_query_result_gif):
        gif_duration = inline_query_result_gif.gif_duration

        if PTB_TIMEDELTA:
            assert gif_duration == self.gif_duration
            assert isinstance(gif_duration, dtm.timedelta)
        else:
            assert gif_duration == int(self.gif_duration.total_seconds())
            assert isinstance(gif_duration, int)

    def test_time_period_int_deprecated(self, recwarn, PTB_TIMEDELTA, inline_query_result_gif):
        inline_query_result_gif.gif_duration

        if PTB_TIMEDELTA:
            assert len(recwarn) == 0
        else:
            assert len(recwarn) == 1
            assert "`gif_duration` will be of type `datetime.timedelta`" in str(recwarn[0].message)
            assert recwarn[0].category is PTBDeprecationWarning

    def test_equality(self):
        a = InlineQueryResultGif(self.id_, self.gif_url, self.thumbnail_url)
        b = InlineQueryResultGif(self.id_, self.gif_url, self.thumbnail_url)
        c = InlineQueryResultGif(self.id_, "", self.thumbnail_url)
        d = InlineQueryResultGif("", self.gif_url, self.thumbnail_url)
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
