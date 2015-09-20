#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents Tests for Telegram Video"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class VideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Video."""

    def setUp(self):
        self.video_file = open('tests/data/telegram.mp4', 'rb')
        self.video_file_id = 'BAADAQADXwADHyP1BwJFTcmY2RYCAg'
        self.width = 360
        self.height = 640
        self.duration = 4
        self.thumb = telegram.PhotoSize.de_json({})
        self.mime_type = 'video/mp4'
        self.file_size = 326534

        # caption is part of sendVideo method but not Video object
        self.caption = u'VideoTest - Caption'

        self.json_dict = {
            'file_id': self.video_file_id,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumb': self.thumb,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    def test_send_video_required_args_only(self):
        """Test telegram.Bot sendVideo method"""
        print('Testing bot.sendVideo - With required arguments only')

        message = self._bot.sendVideo(self._chat_id,
                                      self.video_file)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, '')
        self.assertEqual(video.width, 0)
        self.assertEqual(video.height, 0)
        self.assertEqual(video.duration, 0)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, '')
        self.assertEqual(video.file_size, self.file_size)

    def test_send_video_all_args(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendVideo - With all arguments')

        message = self._bot.sendVideo(self._chat_id,
                                      self.video_file,
                                      duration=self.duration,
                                      caption=self.caption)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, '')
        self.assertEqual(video.width, 0)
        self.assertEqual(video.height, 0)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, '')
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    def test_send_video_mp4_file(self):
        """Test telegram.Bot sendVideo method"""
        print('Testing bot.sendVideo - MP4 File')

        message = self._bot.sendVideo(chat_id=self._chat_id,
                                      video=self.video_file,
                                      duration=self.duration,
                                      caption=self.caption)

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, '')
        self.assertEqual(video.width, 0)
        self.assertEqual(video.height, 0)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, '')
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    def test_send_video_mp4_file_with_custom_filename(self):
        """Test telegram.Bot sendVideo method"""
        print('Testing bot.sendVideo - MP4 File with custom filename')

        message = self._bot.sendVideo(chat_id=self._chat_id,
                                      video=self.video_file,
                                      duration=self.duration,
                                      caption=self.caption,
                                      filename='telegram_custom.mp4')

        video = message.video

        self.assertTrue(isinstance(video.file_id, str))
        self.assertNotEqual(video.file_id, '')
        self.assertEqual(video.width, 0)
        self.assertEqual(video.height, 0)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, '')
        self.assertEqual(video.file_size, self.file_size)

        self.assertEqual(message.caption, self.caption)

    def test_send_video_resend(self):
        """Test telegram.Bot sendVideo method"""
        print('Testing bot.sendVideo - Resend by file_id')

        message = self._bot.sendVideo(chat_id=self._chat_id,
                                      video=self.video_file_id,
                                      duration=self.duration,
                                      caption=self.caption)

        video = message.video

        self.assertEqual(video.file_id, self.video_file_id)
        self.assertEqual(video.duration, 0)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, '')

        self.assertEqual(message.caption, self.caption)

    def test_video_de_json(self):
        """Test Video.de_json() method"""
        print('Testing Video.de_json()')

        video = telegram.Video.de_json(self.json_dict)

        self.assertEqual(video.file_id, self.video_file_id)
        self.assertEqual(video.width, self.width)
        self.assertEqual(video.height, self.height)
        self.assertEqual(video.duration, self.duration)
        self.assertEqual(video.thumb, None)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.file_size, self.file_size)

    def test_video_to_json(self):
        """Test Video.to_json() method"""
        print('Testing Video.to_json()')

        video = telegram.Video.de_json(self.json_dict)

        self.assertTrue(self.is_json(video.to_json()))

    def test_video_to_dict(self):
        """Test Video.to_dict() method"""
        print('Testing Video.to_dict()')

        video = telegram.Video.de_json(self.json_dict)

        self.assertTrue(self.is_dict(video.to_dict()))
        self.assertEqual(video['file_id'], self.video_file_id)
        self.assertEqual(video['width'], self.width)
        self.assertEqual(video['height'], self.height)
        self.assertEqual(video['duration'], self.duration)
        self.assertEqual(video['mime_type'], self.mime_type)
        self.assertEqual(video['file_size'], self.file_size)

    def test_error_send_video_empty_file(self):
        print('Testing bot.sendVideo - Null file')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['video'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_send_video_empty_file_id(self):
        print('Testing bot.sendVideo - Empty file_id')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['video'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_video_without_required_args(self):
        print('Testing bot.sendVideo - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        del(json_dict['duration'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendVideo(chat_id=self._chat_id,
                                                      **json_dict))

if __name__ == '__main__':
    unittest.main()
