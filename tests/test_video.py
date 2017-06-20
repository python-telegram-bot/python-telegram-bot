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

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot


class VideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Video."""
    @classmethod
    def setUpClass(cls):
        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])
        video_file = open('tests/data/telegram.mp4', 'rb')
        video = cls._bot.send_video(cls._chat_id, video_file, timeout=10).video
        cls.video_file_id = video.file_id
        cls.width = video.width
        cls.height = video.height
        cls.duration = video.duration
        cls.thumb = video.thumb
        cls.mime_type = video.mime_type
        cls.file_size = video.file_size
        cls.video_file_url = 'https://python-telegram-bot.org/static/website/telegram.mp4'
        cls.caption = u'VideoTest - Caption'
        cls.thumb_from_url = telegram.PhotoSize.de_json({
            'file_id': 'AAQEABPZU2EZAAQ_tPcvcRTF4i1GAQABAg',
            'file_size': 645,
            'height': 90,
            'width': 51
        }, cls._bot)

    def setUp(self):
        self.video_file = open('tests/data/telegram.mp4', 'rb')
        self.json_dict = {
            'file_id': self.video_file_id,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumb': self.thumb.to_dict(),
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_required_args_only(self):
        # obsolete since it's done in the setUpClass
        self.assertEqual(True, True)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_all_args(self):
        message = self._bot.sendVideo(
            self._chat_id,
            self.video_file,
            timeout=10,
            duration=self.duration,
            caption=self.caption)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.width, self.width)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file(self):
        # identical to all_args so obsolete
        self.assertEqual(True, True)


    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file_with_custom_filename(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file,
            timeout=10,
            duration=self.duration,
            caption=self.caption,
            filename='telegram_custom.mp4')

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, '')
        self.assertEqual(video.width, self.width)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file_url(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file_url,
            timeout=10,
            caption=self.caption)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb_from_url)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_resend(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file_id,
            timeout=10,
            duration=self.duration,
            caption=self.caption)

        video = message.video

        self.assertEqual(video.file_id, self.video_file_id)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb)
        self.assertEqual(video.mime_type, self.mime_type)

        self.assertEqual(message.caption, self.caption)

    def test_video_de_json(self):
        video = telegram.Video.de_json(self.json_dict, self._bot)

        self.assertEqual(video.file_id, self.video_file_id)
        self.assertEqual(video.width, self.width)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.file_size, self.file_size)

    def test_video_to_json(self):
        video = telegram.Video.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(video.to_json()))

    def test_video_to_dict(self):
        video = telegram.Video.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(video.to_dict()))
        self.assertEqual(video['file_id'], self.video_file_id)
        self.assertEqual(video['width'], self.width)
        self.assertEqual(video['height'], self.height)
        self.assertEqual(video['duration'], self.duration)
        self.assertEqual(video['mime_type'], self.mime_type)
        self.assertEqual(video['file_size'], self.file_size)

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
            self._bot.sendVideo(chat_id=self._chat_id,timeout=10,**json_dict)

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
        a = telegram.Video(self.video_file_id, self.width, self.height, self.duration)
        b = telegram.Video(self.video_file_id, self.width, self.height, self.duration)
        c = telegram.Video(self.video_file_id, 0, 0, 0)
        d = telegram.Video("", self.width, self.height, self.duration)
        e = telegram.Voice(self.video_file_id, self.duration)

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
