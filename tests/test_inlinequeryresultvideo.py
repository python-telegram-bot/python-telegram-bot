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
    InlineQueryResultVideo,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_video():
    return InlineQueryResultVideo(
        Space.id_,
        Space.video_url,
        Space.mime_type,
        Space.thumb_url,
        Space.title,
        video_width=Space.video_width,
        video_height=Space.video_height,
        video_duration=Space.video_duration,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        description=Space.description,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "video"
    video_url = "video url"
    mime_type = "mime type"
    video_width = 10
    video_height = 15
    video_duration = 15
    thumb_url = "thumb url"
    title = "title"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    description = "description"
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultVideoWithoutRequest:
    def test_slot_behaviour(self, inline_query_result_video, mro_slots):
        inst = inline_query_result_video
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_video):
        assert inline_query_result_video.type == Space.type_
        assert inline_query_result_video.id == Space.id_
        assert inline_query_result_video.video_url == Space.video_url
        assert inline_query_result_video.mime_type == Space.mime_type
        assert inline_query_result_video.video_width == Space.video_width
        assert inline_query_result_video.video_height == Space.video_height
        assert inline_query_result_video.video_duration == Space.video_duration
        assert inline_query_result_video.thumb_url == Space.thumb_url
        assert inline_query_result_video.title == Space.title
        assert inline_query_result_video.description == Space.description
        assert inline_query_result_video.caption == Space.caption
        assert inline_query_result_video.parse_mode == Space.parse_mode
        assert inline_query_result_video.caption_entities == tuple(Space.caption_entities)
        assert (
            inline_query_result_video.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_video.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        video = InlineQueryResultVideo(
            Space.id_, Space.video_url, Space.mime_type, Space.thumb_url, Space.title
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
        assert inline_query_result_video_dict["thumb_url"] == inline_query_result_video.thumb_url
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
            Space.id_, Space.video_url, Space.mime_type, Space.thumb_url, Space.title
        )
        b = InlineQueryResultVideo(
            Space.id_, Space.video_url, Space.mime_type, Space.thumb_url, Space.title
        )
        c = InlineQueryResultVideo(Space.id_, "", Space.mime_type, Space.thumb_url, Space.title)
        d = InlineQueryResultVideo(
            "", Space.video_url, Space.mime_type, Space.thumb_url, Space.title
        )
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
