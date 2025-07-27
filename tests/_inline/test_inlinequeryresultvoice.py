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
def inline_query_result_voice():
    return InlineQueryResultVoice(
        id=InlineQueryResultVoiceTestBase.id_,
        voice_url=InlineQueryResultVoiceTestBase.voice_url,
        title=InlineQueryResultVoiceTestBase.title,
        voice_duration=InlineQueryResultVoiceTestBase.voice_duration,
        caption=InlineQueryResultVoiceTestBase.caption,
        parse_mode=InlineQueryResultVoiceTestBase.parse_mode,
        caption_entities=InlineQueryResultVoiceTestBase.caption_entities,
        input_message_content=InlineQueryResultVoiceTestBase.input_message_content,
        reply_markup=InlineQueryResultVoiceTestBase.reply_markup,
    )


class InlineQueryResultVoiceTestBase:
    id_ = "id"
    type_ = "voice"
    voice_url = "voice url"
    title = "title"
    voice_duration = dtm.timedelta(seconds=10)
    caption = "caption"
    parse_mode = "HTML"
    caption_entities = [MessageEntity(MessageEntity.ITALIC, 0, 7)]
    input_message_content = InputTextMessageContent("input_message_content")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("reply_markup")]])


class TestInlineQueryResultVoiceWithoutRequest(InlineQueryResultVoiceTestBase):
    def test_slot_behaviour(self, inline_query_result_voice):
        inst = inline_query_result_voice
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, inline_query_result_voice):
        assert inline_query_result_voice.type == self.type_
        assert inline_query_result_voice.id == self.id_
        assert inline_query_result_voice.voice_url == self.voice_url
        assert inline_query_result_voice.title == self.title
        assert inline_query_result_voice._voice_duration == self.voice_duration
        assert inline_query_result_voice.caption == self.caption
        assert inline_query_result_voice.parse_mode == self.parse_mode
        assert inline_query_result_voice.caption_entities == tuple(self.caption_entities)
        assert (
            inline_query_result_voice.input_message_content.to_dict()
            == self.input_message_content.to_dict()
        )
        assert inline_query_result_voice.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_caption_entities_always_tuple(self):
        result = InlineQueryResultVoice(
            self.id_,
            self.voice_url,
            self.title,
        )

        assert result.caption_entities == ()

    def test_to_dict(self, inline_query_result_voice):
        inline_query_result_voice_dict = inline_query_result_voice.to_dict()

        assert isinstance(inline_query_result_voice_dict, dict)
        assert inline_query_result_voice_dict["type"] == inline_query_result_voice.type
        assert inline_query_result_voice_dict["id"] == inline_query_result_voice.id
        assert inline_query_result_voice_dict["voice_url"] == inline_query_result_voice.voice_url
        assert inline_query_result_voice_dict["title"] == inline_query_result_voice.title
        assert inline_query_result_voice_dict["voice_duration"] == int(
            self.voice_duration.total_seconds()
        )
        assert isinstance(inline_query_result_voice_dict["voice_duration"], int)
        assert inline_query_result_voice_dict["caption"] == inline_query_result_voice.caption
        assert inline_query_result_voice_dict["parse_mode"] == inline_query_result_voice.parse_mode
        assert inline_query_result_voice_dict["caption_entities"] == [
            ce.to_dict() for ce in inline_query_result_voice.caption_entities
        ]
        assert (
            inline_query_result_voice_dict["input_message_content"]
            == inline_query_result_voice.input_message_content.to_dict()
        )
        assert (
            inline_query_result_voice_dict["reply_markup"]
            == inline_query_result_voice.reply_markup.to_dict()
        )

    def test_time_period_properties(self, PTB_TIMEDELTA, inline_query_result_voice):
        voice_duration = inline_query_result_voice.voice_duration

        if PTB_TIMEDELTA:
            assert voice_duration == self.voice_duration
            assert isinstance(voice_duration, dtm.timedelta)
        else:
            assert voice_duration == int(self.voice_duration.total_seconds())
            assert isinstance(voice_duration, int)

    def test_time_period_int_deprecated(self, recwarn, PTB_TIMEDELTA, inline_query_result_voice):
        inline_query_result_voice.voice_duration

        if PTB_TIMEDELTA:
            assert len(recwarn) == 0
        else:
            assert len(recwarn) == 1
            assert "`voice_duration` will be of type `datetime.timedelta`" in str(
                recwarn[0].message
            )
            assert recwarn[0].category is PTBDeprecationWarning

    def test_equality(self):
        a = InlineQueryResultVoice(self.id_, self.voice_url, self.title)
        b = InlineQueryResultVoice(self.id_, self.voice_url, self.title)
        c = InlineQueryResultVoice(self.id_, "", self.title)
        d = InlineQueryResultVoice("", self.voice_url, self.title)
        e = InlineQueryResultAudio(self.id_, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
