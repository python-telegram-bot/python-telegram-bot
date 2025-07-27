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
    InlineQueryResultAudio,
    InlineQueryResultVoice,
    InputTextMessageContent,
    MessageEntity,
)
from telegram.warnings import PTBDeprecationWarning
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def inline_query_result_audio():
    return InlineQueryResultAudio(
        InlineQueryResultAudioTestBase.id_,
        InlineQueryResultAudioTestBase.audio_url,
        InlineQueryResultAudioTestBase.title,
        performer=InlineQueryResultAudioTestBase.performer,
        audio_duration=InlineQueryResultAudioTestBase.audio_duration,
        caption=InlineQueryResultAudioTestBase.caption,
        parse_mode=InlineQueryResultAudioTestBase.parse_mode,
        caption_entities=InlineQueryResultAudioTestBase.caption_entities,
        input_message_content=InlineQueryResultAudioTestBase.input_message_content,
        reply_markup=InlineQueryResultAudioTestBase.reply_markup,
    )


class InlineQueryResultAudioTestBase:
    id_ = "id"
    type_ = "audio"
    audio_url = "audio url"
    title = "title"
    performer = "performer"
    audio_duration = dtm.timedelta(seconds=10)
    caption = "caption"
    parse_mode = "Markdown"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultAudioWithoutRequest(InlineQueryResultAudioTestBase):
    def test_slot_behaviour(self, inline_query_result_audio):
        inst = inline_query_result_audio
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_audio):
        assert inline_query_result_audio.type == self.type_
        assert inline_query_result_audio.id == self.id_
        assert inline_query_result_audio.audio_url == self.audio_url
        assert inline_query_result_audio.title == self.title
        assert inline_query_result_audio.performer == self.performer
        assert inline_query_result_audio._audio_duration == self.audio_duration
        assert inline_query_result_audio.caption == self.caption
        assert inline_query_result_audio.parse_mode == self.parse_mode
        assert inline_query_result_audio.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_audio.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_audio.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_audio):
        inline_query_result_audio_dict = inline_query_result_audio.to_dict()

        assert isinstance(inline_query_result_audio_dict, dict)
        assert inline_query_result_audio_dict["type"] == inline_query_result_audio.type
        assert inline_query_result_audio_dict["id"] == inline_query_result_audio.id
        assert inline_query_result_audio_dict["audio_url"] == inline_query_result_audio.audio_url
        assert inline_query_result_audio_dict["title"] == inline_query_result_audio.title
        assert inline_query_result_audio_dict["performer"] == inline_query_result_audio.performer
        assert inline_query_result_audio_dict["audio_duration"] == int(
            self.audio_duration.total_seconds()
        )
        assert isinstance(inline_query_result_audio_dict["audio_duration"], int)
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
        inline_query_result_audio = InlineQueryResultAudio(self.id_, self.audio_url, self.title)
        assert inline_query_result_audio.caption_entities == ()

    def test_time_period_properties(self, PTB_TIMEDELTA, inline_query_result_audio):
        audio_duration = inline_query_result_audio.audio_duration

        if PTB_TIMEDELTA:
            assert audio_duration == self.audio_duration
            assert isinstance(audio_duration, dtm.timedelta)
        else:
            assert audio_duration == int(self.audio_duration.total_seconds())
            assert isinstance(audio_duration, int)

    def test_time_period_int_deprecated(self, recwarn, PTB_TIMEDELTA, inline_query_result_audio):
        inline_query_result_audio.audio_duration

        if PTB_TIMEDELTA:
            assert len(recwarn) == 0
        else:
            assert len(recwarn) == 1
            assert "`audio_duration` will be of type `datetime.timedelta`" in str(
                recwarn[0].message
            )
            assert recwarn[0].category is PTBDeprecationWarning

    def test_equality(self):
        a = InlineQueryResultAudio(self.id_, self.audio_url, self.title)
        b = InlineQueryResultAudio(self.id_, self.title, self.title)
        c = InlineQueryResultAudio(self.id_, "", self.title)
        d = InlineQueryResultAudio("", self.audio_url, self.title)
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
