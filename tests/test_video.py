#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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


class VideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Video."""

    def setUp(self):
        self.video_file = open('tests/data/telegram.mp4', 'rb')
        self.video_file_id = 'BAADAQADXwADHyP1BwJFTcmY2RYCAg'
        self.video_file_url = 'https://python-telegram-bot.org/static/website/telegram.mp4'
        self.width = 360
        self.height = 640
        self.duration = 5
        self.thumb = telegram.PhotoSize.de_json({
            'file_id': 'AAQBABOMsecvAAQqqoY1Pee_MqcyAAIC',
            'file_size': 645,
            'height': 90,
            'width': 51
        }, self._bot)
        self.thumb_from_url = telegram.PhotoSize.de_json({
            'file_id': 'AAQEABPZU2EZAAQ_tPcvcRTF4i1GAQABAg',
            'file_size': 645,
            'height': 90,
            'width': 51
        }, self._bot)
        self.mime_type = 'video/mp4'
        self.file_size = 326534

        # caption is part of sendVideo method but not Video object
        self.caption = u'VideoTest - Caption'

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
        message = self._bot.sendVideo(self._chat_id, self.video_file, timeout=10)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.width, self.width)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb)
        self.assertEqual(video.mime_type, None)
        self.assertEqual(video.file_size, self.file_size)

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
        self.assertEqual(video.mime_type, None)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file,
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
        self.assertEqual(video.mime_type, None)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

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
        self.assertEqual(video.mime_type, None)
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_mp4_file_url(self):
        message = self._bot.sendVideo(
            chat_id=self._chat_id,
            video=self.video_file_url,
            timeout=10,
            duration=self.duration,
            caption=self.caption)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, None)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, self.thumb_from_url)
        self.assertEqual(video.mime_type, None)
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
        self.assertEqual(video.duration, 0)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, None)

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

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      timeout=10,
                                                      **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_video_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['video'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      timeout=10,
                                                      **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_video_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['duration'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      timeout=10,
                                                      **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_video(self):
        """Test for Message.reply_video"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_video(self.video_file)

        self.assertNotEqual(message.video.file_id, None)


if __name__ == '__main__':
    unittest.main()
