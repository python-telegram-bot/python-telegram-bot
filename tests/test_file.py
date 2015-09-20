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

"""This module contains a object that represents Tests for Telegram File"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class FileTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram File."""

    def setUp(self):
        self.audio_file_id = 'BQADAQADDwADHyP1B6PSPq2HjX8kAg'
        self.document_file_id = 'BQADAQADpAADHyP1B04ipZxJTe2BAg'
        self.sticker_file_id = 'BQADAQADHAADyIsGAAFZfq1bphjqlgI'
        self.video_file_id = 'BAADAQADXwADHyP1BwJFTcmY2RYCAg'
        self.voice_file_id = 'AwADAQADTgADHyP1B_mbw34svXPHAg'


        self.json_dict = {
            'file_id': self.audio_file_id,
            'file_path': 'https://api.telegram.org/file/bot133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0/document/file_3',
            'file_size': 28232
        }

    def test_get_and_download_file_audio(self):
        """Test telegram.Bot getFile method - Audio"""
        print('Testing bot.getFile - With Audio.file_id')

        newFile = self._bot.getFile(self.audio_file_id)

        self.assertEqual(newFile.file_size, 28232)
        self.assertEqual(newFile.file_id, self.audio_file_id)
        self.assertTrue(newFile.file_path.startswith('https://'))

        newFile.download('telegram.mp3')

        self.assertTrue(os.path.isfile('telegram.mp3'))

    def test_get_and_download_file_document(self):
        """Test telegram.Bot getFile method - Document"""
        print('Testing bot.getFile - With Document.file_id')

        newFile = self._bot.getFile(self.document_file_id)

        self.assertEqual(newFile.file_size, 12948)
        self.assertEqual(newFile.file_id, self.document_file_id)
        self.assertTrue(newFile.file_path.startswith('https://'))

        newFile.download('telegram.png')

        self.assertTrue(os.path.isfile('telegram.png'))

    def test_get_and_download_file_sticker(self):
        """Test telegram.Bot getFile method - Sticker"""
        print('Testing bot.getFile - With Sticker.file_id')

        newFile = self._bot.getFile(self.sticker_file_id)

        self.assertEqual(newFile.file_size, 39518)
        self.assertEqual(newFile.file_id, self.sticker_file_id)
        self.assertTrue(newFile.file_path.startswith('https://'))

        newFile.download('telegram.webp')

        self.assertTrue(os.path.isfile('telegram.webp'))

    def test_get_and_download_file_video(self):
        """Test telegram.Bot getFile method - Video"""
        print('Testing bot.getFile - With Video.file_id')

        newFile = self._bot.getFile(self.video_file_id)

        self.assertEqual(newFile.file_size, 326534)
        self.assertEqual(newFile.file_id, self.video_file_id)
        self.assertTrue(newFile.file_path.startswith('https://'))

        newFile.download('telegram.mp4')

        self.assertTrue(os.path.isfile('telegram.mp4'))

    def test_get_and_download_file_voice(self):
        """Test telegram.Bot getFile method - Voice"""
        print('Testing bot.getFile - With Voice.file_id')

        newFile = self._bot.getFile(self.voice_file_id)

        self.assertEqual(newFile.file_size, 9199)
        self.assertEqual(newFile.file_id, self.voice_file_id)
        self.assertTrue(newFile.file_path.startswith('https://'))

        newFile.download('telegram.ogg')

        self.assertTrue(os.path.isfile('telegram.ogg'))

    def test_file_de_json(self):
        """Test File.de_json() method"""
        print('Testing File.de_json()')

        newFile = telegram.File.de_json(self.json_dict)

        self.assertEqual(newFile.file_id, self.json_dict['file_id'])
        self.assertEqual(newFile.file_path, self.json_dict['file_path'])
        self.assertEqual(newFile.file_size, self.json_dict['file_size'])

    def test_file_to_json(self):
        """Test File.to_json() method"""
        print('Testing File.to_json()')

        newFile = telegram.File.de_json(self.json_dict)

        self.assertTrue(self.is_json(newFile.to_json()))

    def test_file_to_dict(self):
        """Test File.to_dict() method"""
        print('Testing File.to_dict()')

        newFile = telegram.File.de_json(self.json_dict)

        self.assertTrue(self.is_dict(newFile.to_dict()))
        self.assertEqual(newFile['file_id'], self.json_dict['file_id'])
        self.assertEqual(newFile['file_path'], self.json_dict['file_path'])
        self.assertEqual(newFile['file_size'], self.json_dict['file_size'])

    def test_error_get_empty_file_id(self):
        print('Testing bot.getFile - Null file_id')

        json_dict = self.json_dict

        json_dict['file_id'] = ''
        del(json_dict['file_path'])
        del(json_dict['file_size'])

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.getFile(**json_dict))

    def test_error_file_without_required_args(self):
        print('Testing bot.getFile - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        del(json_dict['file_path'])
        del(json_dict['file_size'])

        self.assertRaises(TypeError,
                          lambda: self._bot.getFile(**json_dict))

if __name__ == '__main__':
    unittest.main()
