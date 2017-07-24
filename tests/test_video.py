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
"""This module contains an object that represents Tests for Telegram Video"""

import os
import unittest

from flaky import flaky

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot


class VideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Video."""

    @classmethod
    def setUpClass(cls):
        cls.caption = u'VideoTest - Caption'
        cls.video_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp4'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])

        video_file = open('tests/data/telegram.mp4', 'rb')
        video = cls._bot.send_video(cls._chat_id, video=video_file, timeout=10).video
        cls.video = video

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.video, telegram.Video)
        assert isinstance(cls.video.file_id, str)
        assert cls.video.file_id is not ''

    def setUp(self):
        self.video_file = open('tests/data/telegram.mp4', 'rb')
        self.json_dict = {
            'file_id': self.video.file_id,
            'width': self.video.width,
            'height': self.video.height,
            'duration': self.video.duration,
            'thumb': self.video.thumb.to_dict(),
            'mime_type': self.video.mime_type,
            'file_size': self.video.file_size
        }

    def test_expected_values(self):
        self.assertEqual(self.video.width, 360)
        self.assertEqual(self.video.height, 640)
        self.assertEqual(self.video.duration, 5)
        self.assertEqual(self.video.file_size, 326534)
        self.assertEqual(self.video.mime_type, 'video/mp4')

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_all_args(self):
        message = self._bot.sendVideo(
            self._chat_id,
            self.video_file,
            timeout=10,
            duration=self.video.duration,
            caption=self.caption,
            disable_notification=False)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.width, self.video.width)
        self.assertEqual(video.height, self.video.height)
        self.assertEqual(video.duration, self.video.duration)
        self.assertEqual(video.thumb, self.video.thumb)
        self.assertEqual(video.mime_type, self.video.mime_type)
        self.assertEqual(video.file_size, self.video.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_video(self):
        new_file = self._bot.getFile(self.video.file_id)

        self.assertEqual(new_file.file_size, self.video.file_size)
        self.assertEqual(new_file.file_id, self.video.file_id)
        self.assertTrue(new_file.file_path.startswith('https://'))

        new_file.download('telegram.mp4')

        self.assertTrue(os.path.isfile('telegram.mp4'))

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file_url(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file_url,
            timeout=10,
            caption=self.caption)

        video = message.video

        self.assertIsInstance(video.file_id, str)
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.height, self.video.height)
        self.assertEqual(video.duration, self.video.duration)
        self.assertEqual(video.mime_type, self.video.mime_type)
        self.assertEqual(video.file_size, self.video.file_size)
        self.assertEqual(message.caption, self.caption)
        thumb = video.thumb
        self.assertEqual(thumb.height, self.video.thumb.height)
        self.assertEqual(thumb.width, self.video.thumb.width)
        self.assertEqual(thumb.file_size, self.video.thumb.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_resend(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video.file_id,
            timeout=10)

        video = message.video

        self.assertEqual(video.file_id, self.video.file_id)
        self.assertEqual(video.duration, self.video.duration)
        self.assertEqual(video.thumb, self.video.thumb)
        self.assertEqual(video.mime_type, self.video.mime_type)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_with_video(self):
        message = self._bot.send_video(video=self.video, chat_id=self._chat_id)
        video = message.video

        self.assertEqual(video, self.video)


    def test_video_de_json(self):
        video = telegram.Video.de_json(self.json_dict, self._bot)

        self.assertEqual(video, self.video)

    def test_video_to_json(self):
        self.assertTrue(self.is_json(self.video.to_json()))

    def test_video_to_dict(self):
        video = self.video.to_dict()

        self.assertTrue(self.is_dict(video))
        self.assertEqual(video['file_id'], self.video.file_id)
        self.assertEqual(video['width'], self.video.width)
        self.assertEqual(video['height'], self.video.height)
        self.assertEqual(video['duration'], self.video.duration)
        self.assertEqual(video['mime_type'], self.video.mime_type)
        self.assertEqual(video['file_size'], self.video.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_video_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['video'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendVideo(chat_id=self._chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_video_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['video'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendVideo(chat_id=self._chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_video_without_required_args(self):
        # Obsolete: only required args are chat_id and video. Both tested above
        self.assertEqual(True, True)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_video(self):
        """Test for Message.reply_video"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_video(self.video_file)

        self.assertNotEqual(message.video.file_id, None)

    def test_equality(self):
        a = telegram.Video(self.video.file_id, self.video.width, self.video.height, self.video.duration)
        b = telegram.Video(self.video.file_id, self.video.width, self.video.height, self.video.duration)
        c = telegram.Video(self.video.file_id, 0, 0, 0)
        d = telegram.Video("", self.video.width, self.video.height, self.video.duration)
        e = telegram.Voice(self.video.file_id, self.video.duration)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertEqual(a, c)
        self.assertEqual(hash(a), hash(c))

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))


if __name__ == '__main__':
    unittest.main()
