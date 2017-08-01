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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultArticle,
                      InlineQueryResultVoice, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultVoice.type,
        'id': TestInlineQueryResultVoice.id,
        'voice_url': TestInlineQueryResultVoice.voice_url,
        'title': TestInlineQueryResultVoice.title,
        'voice_duration': TestInlineQueryResultVoice.voice_duration,
        'caption': TestInlineQueryResultVoice.caption,
        'input_message_content': TestInlineQueryResultVoice.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultVoice.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_voice():
    return InlineQueryResultVoice(type=TestInlineQueryResultVoice.type,
                                  id=TestInlineQueryResultVoice.id,
                                  voice_url=TestInlineQueryResultVoice.voice_url,
                                  title=TestInlineQueryResultVoice.title,
                                  voice_duration=TestInlineQueryResultVoice.voice_duration,
                                  caption=TestInlineQueryResultVoice.caption,
                                  input_message_content=TestInlineQueryResultVoice.input_message_content,
                                  reply_markup=TestInlineQueryResultVoice.reply_markup)


class TestInlineQueryResultVoice:
    """This object represents Tests for Telegram InlineQueryResultVoice."""

    id = 'id'
    type = 'voice'
    voice_url = 'voice url'
    title = 'title'
    voice_duration = 'voice_duration'
    caption = 'caption'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_voice_de_json(self):
        voice = InlineQueryResultVoice.de_json(json_dict, bot)

        assert voice.type == self.type
        assert voice.id == self.id
        assert voice.voice_url == self.voice_url
        assert voice.title == self.title
        assert voice.voice_duration == self.voice_duration
        assert voice.caption == self.caption
        self.assertDictEqual(voice.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert voice.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_voice_to_json(self):
        voice = InlineQueryResultVoice.de_json(json_dict, bot)

        json.loads(voice.to_json())

    def test_voice_to_dict(self):
        voice = InlineQueryResultVoice.de_json(json_dict, bot).to_dict()

        assert isinstance(voice, dict)
        assert json_dict == voice

    def test_equality(self):
        a = InlineQueryResultVoice(self.id, self.voice_url, self.title)
        b = InlineQueryResultVoice(self.id, self.voice_url, self.title)
        c = InlineQueryResultVoice(self.id, "", self.title)
        d = InlineQueryResultVoice("", self.voice_url, self.title)
        e = InlineQueryResultArticle(self.id, "", "")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
