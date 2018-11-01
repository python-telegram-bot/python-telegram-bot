#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultAudio,
                      InlineQueryResultVoice, InlineKeyboardMarkup)


@pytest.fixture(scope='class')
def inline_query_result_voice():
    return InlineQueryResultVoice(
        type=TestInlineQueryResultVoice.type,
        id=TestInlineQueryResultVoice.id,
        voice_url=TestInlineQueryResultVoice.voice_url,
        title=TestInlineQueryResultVoice.title,
        voice_duration=TestInlineQueryResultVoice.voice_duration,
        caption=TestInlineQueryResultVoice.caption,
        parse_mode=TestInlineQueryResultVoice.parse_mode,
        input_message_content=TestInlineQueryResultVoice.input_message_content,
        reply_markup=TestInlineQueryResultVoice.reply_markup)


class TestInlineQueryResultVoice(object):
    id = 'id'
    type = 'voice'
    voice_url = 'voice url'
    title = 'title'
    voice_duration = 'voice_duration'
    caption = 'caption'
    parse_mode = 'HTML'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_voice):
        assert inline_query_result_voice.type == self.type
        assert inline_query_result_voice.id == self.id
        assert inline_query_result_voice.voice_url == self.voice_url
        assert inline_query_result_voice.title == self.title
        assert inline_query_result_voice.voice_duration == self.voice_duration
        assert inline_query_result_voice.caption == self.caption
        assert inline_query_result_voice.parse_mode == self.parse_mode
        assert (inline_query_result_voice.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_voice.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_voice):
        inline_query_result_voice_dict = inline_query_result_voice.to_dict()

        assert isinstance(inline_query_result_voice_dict, dict)
        assert inline_query_result_voice_dict['type'] == inline_query_result_voice.type
        assert inline_query_result_voice_dict['id'] == inline_query_result_voice.id
        assert inline_query_result_voice_dict['voice_url'] == inline_query_result_voice.voice_url
        assert inline_query_result_voice_dict['title'] == inline_query_result_voice.title
        assert (inline_query_result_voice_dict['voice_duration']
                == inline_query_result_voice.voice_duration)
        assert inline_query_result_voice_dict['caption'] == inline_query_result_voice.caption
        assert inline_query_result_voice_dict['parse_mode'] == inline_query_result_voice.parse_mode
        assert (inline_query_result_voice_dict['input_message_content']
                == inline_query_result_voice.input_message_content.to_dict())
        assert (inline_query_result_voice_dict['reply_markup']
                == inline_query_result_voice.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultVoice(self.id, self.voice_url, self.title)
        b = InlineQueryResultVoice(self.id, self.voice_url, self.title)
        c = InlineQueryResultVoice(self.id, '', self.title)
        d = InlineQueryResultVoice('', self.voice_url, self.title)
        e = InlineQueryResultAudio(self.id, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
