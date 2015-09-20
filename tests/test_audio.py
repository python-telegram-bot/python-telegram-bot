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

"""This module contains a object that represents Tests for Telegram Audio"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class AudioTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Audio."""

    def setUp(self):
        self.audio_file = open('tests/data/telegram.mp3', 'rb')
        self.audio_file_id = 'BQADAQADDwADHyP1B6PSPq2HjX8kAg'
        self.duration = 4
        self.performer = 'Leandro Toledo'
        self.title = 'Teste'
        self.mime_type = 'audio/mpeg'
        self.file_size = 28232

        self.json_dict = {
            'file_id': self.audio_file_id,
            'duration': self.duration,
            'performer': self.performer,
            'title': self.title,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    def test_send_audio_required_args_only(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendAudio - With required arguments only')

        message = self._bot.sendAudio(self._chat_id,
                                      self.audio_file)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, '')
        self.assertEqual(audio.duration, 4)
        self.assertEqual(audio.performer, '')
        self.assertEqual(audio.title, '')
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_send_audio_all_args(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendAudio - With all arguments')

        message = self._bot.sendAudio(self._chat_id,
                                      self.audio_file,
                                      duration=self.duration,
                                      performer=self.performer,
                                      title=self.title,
                                      mime_type=self.mime_type,
                                      file_size=self.file_size)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, '')
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_send_audio_mp3_file(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendAudio - MP3 File')

        message = self._bot.sendAudio(chat_id=self._chat_id,
                                      audio=self.audio_file,
                                      duration=self.duration,
                                      performer=self.performer,
                                      title=self.title)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, '')
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_send_audio_mp3_file_custom_filename(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendAudio - MP3 File with custom filename')

        message = self._bot.sendAudio(chat_id=self._chat_id,
                                      audio=self.audio_file,
                                      duration=self.duration,
                                      performer=self.performer,
                                      title=self.title,
                                      filename='telegram_custom.mp3')

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, '')
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_send_audio_resend(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendAudio - Resend by file_id')

        message = self._bot.sendAudio(chat_id=self._chat_id,
                                      audio=self.audio_file_id,
                                      duration=self.duration,
                                      performer=self.performer,
                                      title=self.title)

        audio = message.audio

        self.assertEqual(audio.file_id, self.audio_file_id)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)

    def test_audio_de_json(self):
        """Test Audio.de_json() method"""
        print('Testing Audio.de_json()')

        audio = telegram.Audio.de_json(self.json_dict)

        self.assertEqual(audio.file_id, self.audio_file_id)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_audio_to_json(self):
        """Test Audio.to_json() method"""
        print('Testing Audio.to_json()')

        audio = telegram.Audio.de_json(self.json_dict)

        self.assertTrue(self.is_json(audio.to_json()))

    def test_audio_to_dict(self):
        """Test Audio.to_dict() method"""
        print('Testing Audio.to_dict()')

        audio = telegram.Audio.de_json(self.json_dict)

        self.assertTrue(self.is_dict(audio.to_dict()))
        self.assertEqual(audio['file_id'], self.audio_file_id)
        self.assertEqual(audio['duration'], self.duration)
        self.assertEqual(audio['performer'], self.performer)
        self.assertEqual(audio['title'], self.title)
        self.assertEqual(audio['mime_type'], self.mime_type)
        self.assertEqual(audio['file_size'], self.file_size)

    def test_error_send_audio_empty_file(self):
        print('Testing bot.sendAudio - Null file')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['audio'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendAudio(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_send_audio_empty_file_id(self):
        print('Testing bot.sendAudio - Empty file_id')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['audio'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendAudio(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_audio_without_required_args(self):
        print('Testing bot.sendAudio - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        del(json_dict['duration'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendAudio(chat_id=self._chat_id,
                                                      **json_dict))

if __name__ == '__main__':
    unittest.main()
