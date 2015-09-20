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

"""This module contains a object that represents Tests for Telegram Voice"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class VoiceTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Voice."""

    def setUp(self):
        self.voice_file = open('tests/data/telegram.ogg', 'rb')
        self.voice_file_id = 'AwADAQADTgADHyP1B_mbw34svXPHAg'
        self.duration = 0
        self.mime_type = 'audio/ogg'
        self.file_size = 9199

        self.json_dict = {
            'file_id': self.voice_file_id,
            'duration': self.duration,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    def test_send_voice_required_args_only(self):
        """Test telegram.Bot sendVoice method"""
        print('Testing bot.sendVoice - With required arguments only')

        message = self._bot.sendVoice(self._chat_id,
                                      self.voice_file)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_send_voice_all_args(self):
        """Test telegram.Bot sendAudio method"""
        print('Testing bot.sendVoice - With all arguments')

        message = self._bot.sendVoice(self._chat_id,
                                      self.voice_file,
                                      self.duration,
                                      mime_type=self.mime_type,
                                      file_size=self.file_size)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_send_voice_ogg_file(self):
        """Test telegram.Bot sendVoice method"""
        print('Testing bot.sendVoice - Ogg File')

        message = self._bot.sendVoice(chat_id=self._chat_id,
                                      voice=self.voice_file,
                                      duration=self.duration)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_send_voice_ogg_file_with_custom_filename(self):
        """Test telegram.Bot sendVoice method"""
        print('Testing bot.sendVoice - Ogg File with custom filename')

        message = self._bot.sendVoice(chat_id=self._chat_id,
                                      voice=self.voice_file,
                                      duration=self.duration,
                                      filename='telegram_custom.ogg')

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_send_voice_resend(self):
        """Test telegram.Bot sendVoice method"""
        print('Testing bot.sendVoice - Resend by file_id')

        message = self._bot.sendVoice(chat_id=self._chat_id,
                                      voice=self.voice_file_id,
                                      duration=self.duration)

        voice = message.voice

        self.assertEqual(voice.file_id, self.voice_file_id)
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)

    def test_voice_de_json(self):
        """Test Voice.de_json() method"""
        print('Testing Voice.de_json()')

        voice = telegram.Voice.de_json(self.json_dict)

        self.assertEqual(voice.file_id, self.voice_file_id)
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_voice_to_json(self):
        """Test Voice.to_json() method"""
        print('Testing Voice.to_json()')

        voice = telegram.Voice.de_json(self.json_dict)

        self.assertTrue(self.is_json(voice.to_json()))

    def test_voice_to_dict(self):
        """Test Voice.to_dict() method"""
        print('Testing Voice.to_dict()')

        voice = telegram.Voice.de_json(self.json_dict)

        self.assertTrue(self.is_dict(voice.to_dict()))
        self.assertEqual(voice['file_id'], self.voice_file_id)
        self.assertEqual(voice['duration'], self.duration)
        self.assertEqual(voice['mime_type'], self.mime_type)
        self.assertEqual(voice['file_size'], self.file_size)

    def test_error_send_voice_empty_file(self):
        print('Testing bot.sendVoice - Null file')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['voice'] = open(os.devnull, 'rb')

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVoice(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_send_voice_empty_file_id(self):
        print('Testing bot.sendVoice - Empty file_id')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        json_dict['voice'] = ''

        self.assertRaises(telegram.TelegramError,
                          lambda: self._bot.sendVoice(chat_id=self._chat_id,
                                                      **json_dict))

    def test_error_voice_without_required_args(self):
        print('Testing bot.sendVoice - Without required arguments')

        json_dict = self.json_dict

        del(json_dict['file_id'])
        del(json_dict['duration'])

        self.assertRaises(TypeError,
                          lambda: self._bot.sendVoice(chat_id=self._chat_id,
                                                      **json_dict))

if __name__ == '__main__':
    unittest.main()
