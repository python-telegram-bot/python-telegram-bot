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
    InlineQueryResultVideo,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_video():
    return InlineQueryResultVideo(
        TestInlineQueryResultVideoBase.id_,
        TestInlineQueryResultVideoBase.video_url,
        TestInlineQueryResultVideoBase.mime_type,
        TestInlineQueryResultVideoBase.thumbnail_url,
        TestInlineQueryResultVideoBase.title,
        video_width=TestInlineQueryResultVideoBase.video_width,
        video_height=TestInlineQueryResultVideoBase.video_height,
        video_duration=TestInlineQueryResultVideoBase.video_duration,
        caption=TestInlineQueryResultVideoBase.caption,
        parse_mode=TestInlineQueryResultVideoBase.parse_mode,
        caption_entities=TestInlineQueryResultVideoBase.caption_entities,
        description=TestInlineQueryResultVideoBase.description,
        input_message_content=TestInlineQueryResultVideoBase.input_message_content,
        reply_markup=TestInlineQueryResultVideoBase.reply_markup,
    )


class TestInlineQueryResultVideoBase:
    id_ = "id"
    type_ = "video"
    video_url = "video url"
    mime_type = "mime type"
    video_width = 10
    video_height = 15
    video_duration = 15
    thumbnail_url = "thumbnail url"
    title = "title"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    description = "description"
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultVideoWithoutRequest(TestInlineQueryResultVideoBase):
    def test_slot_behaviour(self, inline_query_result_video):
        inst = inline_query_result_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_video):
        assert inline_query_result_video.type == self.type_
        assert inline_query_result_video.id == self.id_
        assert inline_query_result_video.video_url == self.video_url
        assert inline_query_result_video.mime_type == self.mime_type
        assert inline_query_result_video.video_width == self.video_width
        assert inline_query_result_video.video_height == self.video_height
        assert inline_query_result_video.video_duration == self.video_duration
        assert inline_query_result_video.thumbnail_url == self.thumbnail_url
        assert inline_query_result_video.title == self.title
        assert inline_query_result_video.description == self.description
        assert inline_query_result_video.caption == self.caption
        assert inline_query_result_video.parse_mode == self.parse_mode
        assert inline_query_result_video.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_video.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_video.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        video = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        assert video.caption_entities == ()

    def test_to_dict(self, inline_query_result_video):
        inline_query_result_video_dict = inline_query_result_video.to_dict()

        assert isinstance(inline_query_result_video_dict, dict)
        assert inline_query_result_video_dict["type"] == inline_query_result_video.type
        assert inline_query_result_video_dict["id"] == inline_query_result_video.id
        assert inline_query_result_video_dict["video_url"] == inline_query_result_video.video_url
        assert inline_query_result_video_dict["mime_type"] == inline_query_result_video.mime_type
        assert (
            inline_query_result_video_dict["video_width"] == inline_query_result_video.video_width
        )
        assert (
            inline_query_result_video_dict["video_height"]
            == inline_query_result_video.video_height
        )
        assert (
            inline_query_result_video_dict["video_duration"]
            == inline_query_result_video.video_duration
        )
        assert (
            inline_query_result_video_dict["thumbnail_url"]
            == inline_query_result_video.thumbnail_url
        )
        assert inline_query_result_video_dict["title"] == inline_query_result_video.title
        assert (
            inline_query_result_video_dict["description"] == inline_query_result_video.description
        )
        assert inline_query_result_video_dict["caption"] == inline_query_result_video.caption
        assert inline_query_result_video_dict["parse_mode"] == inline_query_result_video.parse_mode
        assert inline_query_result_video_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_video.caption_entities
        ]
        assert (
            inline_query_result_video_dict["input_message_content"]
            == inline_query_result_video.input_message_content.to_dict()
        )
        assert (
            inline_query_result_video_dict["reply_markup"]
            == inline_query_result_video.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        b = InlineQueryResultVideo(
            self.id_, self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
        c = InlineQueryResultVideo(self.id_, "", self.mime_type, self.thumbnail_url, self.title)
        d = InlineQueryResultVideo(
            "", self.video_url, self.mime_type, self.thumbnail_url, self.title
        )
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
