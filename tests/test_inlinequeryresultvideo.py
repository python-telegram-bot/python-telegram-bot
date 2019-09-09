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

from telegram import (InlineKeyboardButton, InputTextMessageContent, InlineQueryResultVideo,
                      InlineKeyboardMarkup, InlineQueryResultVoice)


@pytest.fixture(scope='class')
def inline_query_result_video():
    return InlineQueryResultVideo(
        TestInlineQueryResultVideo.id,
        TestInlineQueryResultVideo.video_url,
        TestInlineQueryResultVideo.mime_type,
        TestInlineQueryResultVideo.thumb_url,
        TestInlineQueryResultVideo.title,
        video_width=TestInlineQueryResultVideo.video_width,
        video_height=TestInlineQueryResultVideo.video_height,
        video_duration=TestInlineQueryResultVideo.video_duration,
        caption=TestInlineQueryResultVideo.caption,
        parse_mode=TestInlineQueryResultVideo.parse_mode,
        description=TestInlineQueryResultVideo.description,
        input_message_content=TestInlineQueryResultVideo.input_message_content,
        reply_markup=TestInlineQueryResultVideo.reply_markup)


class TestInlineQueryResultVideo(object):
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
    parse_mode = 'Markdown'
    description = 'description'
    input_message_content = InputTextMessageContent('input_message_content')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('reply_markup')]])

    def test_expected_values(self, inline_query_result_video):
        assert inline_query_result_video.type == self.type
        assert inline_query_result_video.id == self.id
        assert inline_query_result_video.video_url == self.video_url
        assert inline_query_result_video.mime_type == self.mime_type
        assert inline_query_result_video.video_width == self.video_width
        assert inline_query_result_video.video_height == self.video_height
        assert inline_query_result_video.video_duration == self.video_duration
        assert inline_query_result_video.thumb_url == self.thumb_url
        assert inline_query_result_video.title == self.title
        assert inline_query_result_video.description == self.description
        assert inline_query_result_video.caption == self.caption
        assert inline_query_result_video.parse_mode == self.parse_mode
        assert (inline_query_result_video.input_message_content.to_dict()
                == self.input_message_content.to_dict())
        assert inline_query_result_video.reply_markup.to_dict() == self.reply_markup.to_dict()

    def test_to_dict(self, inline_query_result_video):
        inline_query_result_video_dict = inline_query_result_video.to_dict()

        assert isinstance(inline_query_result_video_dict, dict)
        assert inline_query_result_video_dict['type'] == inline_query_result_video.type
        assert inline_query_result_video_dict['id'] == inline_query_result_video.id
        assert inline_query_result_video_dict['video_url'] == inline_query_result_video.video_url
        assert inline_query_result_video_dict['mime_type'] == inline_query_result_video.mime_type
        assert (inline_query_result_video_dict['video_width']
                == inline_query_result_video.video_width)
        assert (inline_query_result_video_dict['video_height']
                == inline_query_result_video.video_height)
        assert (inline_query_result_video_dict['video_duration']
                == inline_query_result_video.video_duration)
        assert inline_query_result_video_dict['thumb_url'] == inline_query_result_video.thumb_url
        assert inline_query_result_video_dict['title'] == inline_query_result_video.title
        assert (inline_query_result_video_dict['description']
                == inline_query_result_video.description)
        assert inline_query_result_video_dict['caption'] == inline_query_result_video.caption
        assert inline_query_result_video_dict['parse_mode'] == inline_query_result_video.parse_mode
        assert (inline_query_result_video_dict['input_message_content']
                == inline_query_result_video.input_message_content.to_dict())
        assert (inline_query_result_video_dict['reply_markup']
                == inline_query_result_video.reply_markup.to_dict())

    def test_equality(self):
        a = InlineQueryResultVideo(self.id, self.video_url, self.mime_type,
                                   self.thumb_url, self.title)
        b = InlineQueryResultVideo(self.id, self.video_url, self.mime_type,
                                   self.thumb_url, self.title)
        c = InlineQueryResultVideo(self.id, '', self.mime_type, self.thumb_url,
                                   self.title)
        d = InlineQueryResultVideo('', self.video_url, self.mime_type, self.thumb_url,
                                   self.title)
        e = InlineQueryResultVoice(self.id, '', '')

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
