#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import (InlineQueryResultCachedAudio, InlineQueryResultCachedVoice, InlineKeyboardMarkup, InputTextMessageContent, InlineKeyboardButton)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedAudio.type,
            'id': TestInlineQueryResultCachedAudio.id,
            'audio_file_id': TestInlineQueryResultCachedAudio.audio_file_id,
            'caption': TestInlineQueryResultCachedAudio.caption,
            'input_message_content': TestInlineQueryResultCachedAudio.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedAudio.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_audio():
   return InlineQueryResultCachedAudio(type=TestInlineQueryResultCachedAudio.type, id=TestInlineQueryResultCachedAudio.id, audio_file_id=TestInlineQueryResultCachedAudio.audio_file_id, caption=TestInlineQueryResultCachedAudio.caption, input_message_content=TestInlineQueryResultCachedAudio.input_message_content, reply_markup=TestInlineQueryResultCachedAudio.reply_markup)

class TestInlineQueryResultCachedAudio:
    """This object represents Tests for Telegram
    InlineQueryResultCachedAudio."""

    id = 'id'
    type = 'audio'
    audio_file_id = 'audio file id'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_audio_de_json(self):
        audio = InlineQueryResultCachedAudio.de_json(json_dict, bot)

        assert audio.type == self.type
        assert audio.id == self.id
        assert audio.audio_file_id == self.audio_file_id
        assert audio.caption == self.caption
        self.assertDictEqual(audio.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert audio.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_audio_to_json(self):
        audio = InlineQueryResultCachedAudio.de_json(json_dict, bot)

        json.loads(audio.to_json())

    def test_audio_to_dict(self):
        audio = InlineQueryResultCachedAudio.de_json(json_dict, bot).to_dict()

        assert isinstance(audio, dict)
        assert json_dict == audio

    def test_equality(self):
        a = InlineQueryResultCachedAudio(self.id, self.audio_file_id)
        b = InlineQueryResultCachedAudio(self.id, self.audio_file_id)
        c = InlineQueryResultCachedAudio(self.id, "")
        d = InlineQueryResultCachedAudio("", self.audio_file_id)
        e = InlineQueryResultCachedVoice(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


