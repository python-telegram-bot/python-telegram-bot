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

from telegram import (Bot, Video, TelegramError, mp4'

        bot_info = get_bot, mp4', Voice, mp4', 'rb')

@pytest.fixture(scope='class')
def json_dict():
    return {
            'file_id': TestVideo.video.file_id,
            'width': TestVideo.video.width,
            'height': TestVideo.video.height,
            'duration': TestVideo.video.duration,
            'thumb': TestVideo.video.thumb.to_dict(),
            'mime_type': TestVideo.video.mime_type,
            'file_size': TestVideo.video.file_size
        }

@pytest.fixture(scope='class')
def video():
   return Video(file_id=TestVideo.video, width=TestVideo.video, height=TestVideo.video, duration=TestVideo.video, thumb=TestVideo.video, mime_type=TestVideo.video, file_size=TestVideo.video)

class TestVideo:
    """This object represents Tests for Telegram Video."""

    @classmethod
    def setUpClass(cls):
        cls.caption = u'VideoTest - Caption'
        cls.video_file_url = 'https://python-telegram-bot.org/static/testfiles/mp4'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = Bot(bot_info['token'])

        video_file = open('tests/data/mp4', 'rb')
        video = cls._bot.send_video(cls._chat_id, video=video_file, timeout=10).video
        cls.video = video

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.video, Video)
        assert isinstance(cls.video.file_id, str)
        assert cls.video.file_id is not ''

    video_file = open('tests/data/mp4', 'rb')
    
    
    def test_expected_values(self):
        assert self.video.width == 360
        assert self.video.height == 640
        assert self.video.duration == 5
        assert self.video.file_size == 326534
        assert self.video.mime_type == 'video/mp4'

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_all_args(self):
        message = bot.sendVideo(
            chat_id,
            self.video_file,
            timeout=10,
            duration=self.video.duration,
            caption=self.caption,
            disable_notification=False)

        video = message.video

        assert isinstance(video.file_id, str)
        assert video.file_id != None
        assert video.width == self.video.width
        assert video.height == self.video.height
        assert video.duration == self.video.duration
        assert video.thumb == self.video.thumb
        assert video.mime_type == self.video.mime_type
        assert video.file_size == self.video.file_size

        assert message.caption == self.caption

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_video(self):
        new_file = bot.getFile(self.video.file_id)

        assert new_file.file_size == self.video.file_size
        assert new_file.file_id == self.video.file_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('mp4')

        assert os.path.isfile('mp4') is True

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file_url(self):
        message = bot.sendVideo(
            chat_id=chat_id,
            video=self.video_file_url,
            timeout=10,
            caption=self.caption)

        video = message.video

        assert isinstance(video.file_id, str)
        assert video.file_id != None
        assert video.height == self.video.height
        assert video.duration == self.video.duration
        assert video.mime_type == self.video.mime_type
        assert video.file_size == self.video.file_size
        assert message.caption == self.caption
        thumb = video.thumb
        assert thumb.height == self.video.thumb.height
        assert thumb.width == self.video.thumb.width
        assert thumb.file_size == self.video.thumb.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_resend(self):
        message = bot.sendVideo(
            chat_id=chat_id,
            video=self.video.file_id,
            timeout=10)

        video = message.video

        assert video.file_id == self.video.file_id
        assert video.duration == self.video.duration
        assert video.thumb == self.video.thumb
        assert video.mime_type == self.video.mime_type

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_with_video(self):
        message = bot.send_video(video=self.video, chat_id=self._chat_id)
        video = message.video

        assert video == self.video


    def test_de_json(self):
        video = Video.de_json(json_dict, bot)

        assert video == self.video

    def test_to_json(self):
        json.loads(self.video.to_json())

    def test_to_dict(self):
        video = self.video.to_dict()

        assert isinstance(video, dict)
        assert video['file_id'] == self.video.file_id
        assert video['width'] == self.video.width
        assert video['height'] == self.video.height
        assert video['duration'] == self.video.duration
        assert video['mime_type'] == self.video.mime_type
        assert video['file_size'] == self.video.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_video_empty_file(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['video'] = open(os.devnull, 'rb')

        with self.assertRaises(TelegramError):
            bot.sendVideo(chat_id=chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_video_empty_file_id(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['video'] = ''

        with self.assertRaises(TelegramError):
            bot.sendVideo(chat_id=chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_video_without_required_args(self):
        # Obsolete: only required args are chat_id and video. Both tested above
        assert True == True

    @flaky(3, 1)
    @timeout(10)
    def test_reply_video(self):
        """Test for Message.reply_video"""
        message = bot.sendMessage(chat_id, '.')
        message = message.reply_video(self.video_file)

        assert message.video.file_id != None

    def test_equality(self):
        a = Video(self.video.file_id, self.video.width, self.video.height, self.video.duration)
        b = Video(self.video.file_id, self.video.width, self.video.height, self.video.duration)
        c = Video(self.video.file_id, 0, 0, 0)
        d = Video("", self.video.width, self.video.height, self.video.duration)
        e = Voice(self.video.file_id, self.video.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


