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
    InlineQueryResultAudio,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)


@pytest.fixture(scope="module")
def inline_query_result_audio():
    return InlineQueryResultAudio(
        Space.id_,
        Space.audio_url,
        Space.title,
        performer=Space.performer,
        audio_duration=Space.audio_duration,
        caption=Space.caption,
        parse_mode=Space.parse_mode,
        caption_entities=Space.caption_entities,
        input_message_content=Space.input_message_content,
        reply_markup=Space.reply_markup,
    )


class Space:
    id_ = "id"
    type_ = "audio"
    audio_url = "audio url"
    title = "title"
    performer = "performer"
    audio_duration = "audio_duration"
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultAudioNoReq:
    def test_slot_behaviour(self, inline_query_result_audio, mro_slots):
        inst = inline_query_result_audio
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_audio):
        assert inline_query_result_audio.type == Space.type_
        assert inline_query_result_audio.id == Space.id_
        assert inline_query_result_audio.audio_url == Space.audio_url
        assert inline_query_result_audio.title == Space.title
        assert inline_query_result_audio.performer == Space.performer
        assert inline_query_result_audio.audio_duration == Space.audio_duration
        assert inline_query_result_audio.caption == Space.caption
        assert inline_query_result_audio.parse_mode == Space.parse_mode
        assert inline_query_result_audio.caption_entities == tuple(Space.caption_entities)
        assert (
            inline_query_result_audio.input_message_content.to_dict()
            == Space.input_message_content.to_dict()
        )
        assert inline_query_result_audio.reply_markup.to_dict() == Space.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_audio):
        inline_query_result_audio_dict = inline_query_result_audio.to_dict()

        assert isinstance(inline_query_result_audio_dict, dict)
        assert inline_query_result_audio_dict["type"] == inline_query_result_audio.type
        assert inline_query_result_audio_dict["id"] == inline_query_result_audio.id
        assert inline_query_result_audio_dict["audio_url"] == inline_query_result_audio.audio_url
        assert inline_query_result_audio_dict["title"] == inline_query_result_audio.title
        assert inline_query_result_audio_dict["performer"] == inline_query_result_audio.performer
        assert (
            inline_query_result_audio_dict["audio_duration"]
            == inline_query_result_audio.audio_duration
        )
        assert inline_query_result_audio_dict["caption"] == inline_query_result_audio.caption
        assert inline_query_result_audio_dict["parse_mode"] == inline_query_result_audio.parse_mode
        assert inline_query_result_audio_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_audio.caption_entities
        ]
        assert (
            inline_query_result_audio_dict["input_message_content"]
            == inline_query_result_audio.input_message_content.to_dict()
        )
        assert (
            inline_query_result_audio_dict["reply_markup"]
            == inline_query_result_audio.reply_markup.to_dict()
        )

    def test_caption_entities_always_tuple(self):
        inline_query_result_audio = InlineQueryResultAudio(Space.id_, Space.audio_url, Space.title)
        assert inline_query_result_audio.caption_entities == ()

    def test_equality(self):
        a = InlineQueryResultAudio(Space.id_, Space.audio_url, Space.title)
        b = InlineQueryResultAudio(Space.id_, Space.title, Space.title)
        c = InlineQueryResultAudio(Space.id_, "", Space.title)
        d = InlineQueryResultAudio("", Space.audio_url, Space.title)
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
