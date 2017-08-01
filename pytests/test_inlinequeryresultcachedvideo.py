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

from telegram import (InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultCachedVideo, InlineKeyboardButton, InlineQueryResultCachedVoice)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'type': TestInlineQueryResultCachedVideo.type,
            'id': TestInlineQueryResultCachedVideo.id,
            'video_file_id': TestInlineQueryResultCachedVideo.video_file_id,
            'title': TestInlineQueryResultCachedVideo.title,
            'caption': TestInlineQueryResultCachedVideo.caption,
            'description': TestInlineQueryResultCachedVideo.description,
            'input_message_content': TestInlineQueryResultCachedVideo.input_message_content.to_dict(),
            'reply_markup': TestInlineQueryResultCachedVideo.reply_markup.to_dict(),
        }

@pytest.fixture(scope='class')
def inline_query_result_cached_video():
   return InlineQueryResultCachedVideo(type=TestInlineQueryResultCachedVideo.type, id=TestInlineQueryResultCachedVideo.id, video_file_id=TestInlineQueryResultCachedVideo.video_file_id, title=TestInlineQueryResultCachedVideo.title, caption=TestInlineQueryResultCachedVideo.caption, description=TestInlineQueryResultCachedVideo.description, input_message_content=TestInlineQueryResultCachedVideo.input_message_content, reply_markup=TestInlineQueryResultCachedVideo.reply_markup)

class TestInlineQueryResultCachedVideo:
    """This object represents Tests for Telegram
    InlineQueryResultCachedVideo."""

    id = 'id'
    type = 'video'
    video_file_id = 'video file id'
    title = 'title'
    caption = 'caption'
    description = 'description'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton('reply_markup')]])
    
    
    
    def test_video_de_json(self):
        video = InlineQueryResultCachedVideo.de_json(json_dict, bot)

        assert video.type == self.type
        assert video.id == self.id
        assert video.video_file_id == self.video_file_id
        assert video.title == self.title
        assert video.description == self.description
        assert video.caption == self.caption
        self.assertDictEqual(video.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert video.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_video_to_json(self):
        video = InlineQueryResultCachedVideo.de_json(json_dict, bot)

        json.loads(video.to_json())

    def test_video_to_dict(self):
        video = InlineQueryResultCachedVideo.de_json(json_dict, bot).to_dict()

        assert isinstance(video, dict)
        assert json_dict == video

    def test_equality(self):
        a = InlineQueryResultCachedVideo(self.id, self.video_file_id, self.title)
        b = InlineQueryResultCachedVideo(self.id, self.video_file_id, self.title)
        c = InlineQueryResultCachedVideo(self.id, "", self.title)
        d = InlineQueryResultCachedVideo("", self.video_file_id, self.title)
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


