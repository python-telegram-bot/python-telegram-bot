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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultVideo,
                      InlineKeyboardMarkup, InlineQueryResultArticle)


@pytest.fixture(scope='class')
def json_dict():
    return {
        'type': TestInlineQueryResultVideo.type,
        'id': TestInlineQueryResultVideo.id,
        'video_url': TestInlineQueryResultVideo.video_url,
        'mime_type': TestInlineQueryResultVideo.mime_type,
        'video_width': TestInlineQueryResultVideo.video_width,
        'video_height': TestInlineQueryResultVideo.video_height,
        'video_duration': TestInlineQueryResultVideo.video_duration,
        'thumb_url': TestInlineQueryResultVideo.thumb_url,
        'title': TestInlineQueryResultVideo.title,
        'caption': TestInlineQueryResultVideo.caption,
        'description': TestInlineQueryResultVideo.description,
        'input_message_content': TestInlineQueryResultVideo.input_message_content.to_dict(),
        'reply_markup': TestInlineQueryResultVideo.reply_markup.to_dict(),
    }


@pytest.fixture(scope='class')
def inline_query_result_video():
    return InlineQueryResultVideo(type=TestInlineQueryResultVideo.type,
                                  id=TestInlineQueryResultVideo.id,
                                  video_url=TestInlineQueryResultVideo.video_url,
                                  mime_type=TestInlineQueryResultVideo.mime_type,
                                  video_width=TestInlineQueryResultVideo.video_width,
                                  video_height=TestInlineQueryResultVideo.video_height,
                                  video_duration=TestInlineQueryResultVideo.video_duration,
                                  thumb_url=TestInlineQueryResultVideo.thumb_url,
                                  title=TestInlineQueryResultVideo.title,
                                  caption=TestInlineQueryResultVideo.caption,
                                  description=TestInlineQueryResultVideo.description,
                                  input_message_content=TestInlineQueryResultVideo.input_message_content,
                                  reply_markup=TestInlineQueryResultVideo.reply_markup)


class TestInlineQueryResultVideo:
    """This object represents Tests for Telegram InlineQueryResultVideo."""

    id = 'id'
    type = 'video'
    video_url = 'video url'
    mime_type = 'mime type'
    video_width = 10
    video_height = 15
    video_duration = 15
    thumb_url = 'thumb url'
    title = 'title'
    caption = 'caption'
    description = 'description'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('reply_markup')]])

    def test_video_de_json(self):
        video = InlineQueryResultVideo.de_json(json_dict, bot)

        assert video.type == self.type
        assert video.id == self.id
        assert video.video_url == self.video_url
        assert video.mime_type == self.mime_type
        assert video.video_width == self.video_width
        assert video.video_height == self.video_height
        assert video.video_duration == self.video_duration
        assert video.thumb_url == self.thumb_url
        assert video.title == self.title
        assert video.description == self.description
        assert video.caption == self.caption
        self.assertDictEqual(video.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        assert video.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_video_to_json(self):
        video = InlineQueryResultVideo.de_json(json_dict, bot)

        json.loads(video.to_json())

    def test_video_to_dict(self):
        video = InlineQueryResultVideo.de_json(json_dict, bot).to_dict()

        assert isinstance(video, dict)
        assert json_dict == video

    def test_equality(self):
        a = InlineQueryResultVideo(self.id, self.video_url, self.mime_type,
                                   self.thumb_url, self.title)
        b = InlineQueryResultVideo(self.id, self.video_url, self.mime_type,
                                   self.thumb_url, self.title)
        c = InlineQueryResultVideo(self.id, "", self.mime_type, self.thumb_url,
                                   self.title)
        d = InlineQueryResultVideo("", self.video_url, self.mime_type, self.thumb_url,
                                   self.title)
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
