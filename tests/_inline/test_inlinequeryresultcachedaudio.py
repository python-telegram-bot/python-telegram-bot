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
    InlineQueryResultCachedAudio,
    InlineQueryResultCachedVoice,
    InputTextMessageContent,
    MessageEntity,
)
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_cached_audio():
    return InlineQueryResultCachedAudio(
        TestInlineQueryResultCachedAudioBase.id_,
        TestInlineQueryResultCachedAudioBase.audio_file_id,
        caption=TestInlineQueryResultCachedAudioBase.caption,
        parse_mode=TestInlineQueryResultCachedAudioBase.parse_mode,
        caption_entities=TestInlineQueryResultCachedAudioBase.caption_entities,
        input_message_content=TestInlineQueryResultCachedAudioBase.input_message_content,
        reply_markup=TestInlineQueryResultCachedAudioBase.reply_markup,
    )


class TestInlineQueryResultCachedAudioBase:
    id_ = "id"
    type_ = "audio"
    audio_file_id = "audio file id"
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultCachedAudioWithoutRequest(TestInlineQueryResultCachedAudioBase):
    def test_slot_behaviour(self, inline_query_result_cached_audio):
        inst = inline_query_result_cached_audio
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_cached_audio):
        assert inline_query_result_cached_audio.type == self.type_
        assert inline_query_result_cached_audio.id == self.id_
        assert inline_query_result_cached_audio.audio_file_id == self.audio_file_id
        assert inline_query_result_cached_audio.caption == self.caption
        assert inline_query_result_cached_audio.parse_mode == self.parse_mode
        assert inline_query_result_cached_audio.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_cached_audio.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_audio.reply_markup.to_dict() == self.reply_markup.to_dict()
        )

    def test_caption_entities_always_tuple(self):
        audio = InlineQueryResultCachedAudio(self.id_, self.audio_file_id)
        assert audio.caption_entities == ()

    def test_to_dict(self, inline_query_result_cached_audio):
        inline_query_result_cached_audio_dict = inline_query_result_cached_audio.to_dict()

        assert isinstance(inline_query_result_cached_audio_dict, dict)
        assert (
            inline_query_result_cached_audio_dict["type"] == inline_query_result_cached_audio.type
        )
        assert inline_query_result_cached_audio_dict["id"] == inline_query_result_cached_audio.id
        assert (
            inline_query_result_cached_audio_dict["audio_file_id"]
            == inline_query_result_cached_audio.audio_file_id
        )
        assert (
            inline_query_result_cached_audio_dict["caption"]
            == inline_query_result_cached_audio.caption
        )
        assert (
            inline_query_result_cached_audio_dict["parse_mode"]
            == inline_query_result_cached_audio.parse_mode
        )
        assert inline_query_result_cached_audio_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_cached_audio.caption_entities
        ]
        assert (
            inline_query_result_cached_audio_dict["input_message_content"]
            == inline_query_result_cached_audio.input_message_content.to_dict()
        )
        assert (
            inline_query_result_cached_audio_dict["reply_markup"]
            == inline_query_result_cached_audio.reply_markup.to_dict()
        )

    def test_equality(self):
        a = InlineQueryResultCachedAudio(self.id_, self.audio_file_id)
        b = InlineQueryResultCachedAudio(self.id_, self.audio_file_id)
        c = InlineQueryResultCachedAudio(self.id_, "")
        d = InlineQueryResultCachedAudio("", self.audio_file_id)
        e = InlineQueryResultCachedVoice(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
