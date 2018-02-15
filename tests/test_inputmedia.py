#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
import pytest
from flaky import flaky

from telegram import InputMediaVideo, InputMediaPhoto, Message
from .test_video import video, video_file
from .test_photo import _photo, photo_file, photo, thumb


@pytest.fixture(scope='class')
def input_media_video():
    return InputMediaVideo(media=TestInputMediaVideo.media,
                           caption=TestInputMediaVideo.caption,
                           width=TestInputMediaVideo.width,
                           height=TestInputMediaVideo.height,
                           duration=TestInputMediaVideo.duration,
                           parse_mode=TestInputMediaVideo.parse_mode,
                           supports_streaming=TestInputMediaVideo.supports_streaming)


@pytest.fixture(scope='class')
def input_media_photo():
    return InputMediaPhoto(media=TestInputMediaPhoto.media,
                           caption=TestInputMediaPhoto.caption,
                           parse_mode=TestInputMediaPhoto.parse_mode)


class TestInputMediaVideo(object):
    type = "video"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    width = 3
    height = 4
    duration = 5
    parse_mode = 'HTML'
    supports_streaming = True

    def test_expected_values(self, input_media_video):
        assert input_media_video.type == self.type
        assert input_media_video.media == self.media
        assert input_media_video.caption == self.caption
        assert input_media_video.width == self.width
        assert input_media_video.height == self.height
        assert input_media_video.duration == self.duration
        assert input_media_video.parse_mode == self.parse_mode
        assert input_media_video.supports_streaming == self.supports_streaming

    def test_to_dict(self, input_media_video):
        input_media_video_dict = input_media_video.to_dict()
        assert input_media_video_dict['type'] == input_media_video.type
        assert input_media_video_dict['media'] == input_media_video.media
        assert input_media_video_dict['caption'] == input_media_video.caption
        assert input_media_video_dict['width'] == input_media_video.width
        assert input_media_video_dict['height'] == input_media_video.height
        assert input_media_video_dict['duration'] == input_media_video.duration
        assert input_media_video_dict['parse_mode'] == input_media_video.parse_mode
        assert input_media_video_dict['supports_streaming'] == input_media_video.supports_streaming

    def test_with_video(self, video):
        # fixture found in test_video
        input_media_video = InputMediaVideo(video, caption="test 3")
        assert input_media_video.type == self.type
        assert input_media_video.media == video.file_id
        assert input_media_video.width == video.width
        assert input_media_video.height == video.height
        assert input_media_video.duration == video.duration
        assert input_media_video.caption == "test 3"

    def test_error_with_file(self, video_file):
        # fixture found in test_video
        with pytest.raises(ValueError, match="file_id, url or Video"):
            InputMediaVideo(video_file)


class TestInputMediaPhoto(object):
    type = "photo"
    media = "NOTAREALFILEID"
    caption = "My Caption"
    parse_mode = 'Markdown'

    def test_expected_values(self, input_media_photo):
        assert input_media_photo.type == self.type
        assert input_media_photo.media == self.media
        assert input_media_photo.caption == self.caption
        assert input_media_photo.parse_mode == self.parse_mode

    def test_to_dict(self, input_media_photo):
        input_media_photo_dict = input_media_photo.to_dict()
        assert input_media_photo_dict['type'] == input_media_photo.type
        assert input_media_photo_dict['media'] == input_media_photo.media
        assert input_media_photo_dict['caption'] == input_media_photo.caption
        assert input_media_photo_dict['parse_mode'] == input_media_photo.parse_mode

    def test_with_photo(self, photo):
        # fixture found in test_photo
        imp = InputMediaPhoto(photo, caption="test 2")
        assert imp.type == self.type
        assert imp.media == photo.file_id
        assert imp.caption == "test 2"

    def test_error_with_file(self, photo_file):
        # fixture found in test_photo
        with pytest.raises(ValueError, match="file_id, url or PhotoSize"):
            InputMediaPhoto(photo_file)


@pytest.fixture(scope='function')
def media_group(photo, thumb):
    return [InputMediaPhoto(photo, caption='photo `1`', parse_mode='Markdown'),
            InputMediaPhoto(thumb, caption='<b>photo</b> 2', parse_mode='HTML')]


class TestSendMediaGroup(object):
    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_media_group_photo(self, bot, chat_id, media_group):
        messages = bot.send_media_group(chat_id, media_group)
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all([isinstance(mes, Message) for mes in messages])
        assert all([mes.media_group_id == messages[0].media_group_id for mes in messages])

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_media_group_all_args(self, bot, chat_id, media_group):
        m1 = bot.send_message(chat_id, text="test")
        messages = bot.send_media_group(chat_id, media_group, disable_notification=True,
                                        reply_to_message_id=m1.message_id)
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all([isinstance(mes, Message) for mes in messages])
        assert all([mes.media_group_id == messages[0].media_group_id for mes in messages])

    @pytest.mark.skip(reason="Needs a rework to send new files")
    def test_send_media_group_new_files(self):
        pass
