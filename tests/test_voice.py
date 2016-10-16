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
"""This module contains an object that represents Tests for Telegram Voice"""

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class VoiceTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Voice."""

    def setUp(self):
        self.voice_file = open('tests/data/telegram.ogg', 'rb')
        self.voice_file_id = 'AwADAQADTgADHyP1B_mbw34svXPHAg'
        self.voice_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.ogg'
        self.duration = 3
        self.caption = "Test voice"
        self.mime_type = 'audio/ogg'
        self.file_size = 9199

        self.json_dict = {
            'file_id': self.voice_file_id,
            'duration': self.duration,
            'caption': self.caption,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_required_args_only(self):
        message = self._bot.sendVoice(self._chat_id, self.voice_file)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_all_args(self):
        message = self._bot.sendVoice(
            self._chat_id,
            self.voice_file,
            duration=self.duration,
            caption=self.caption,
            mime_type=self.mime_type,
            file_size=self.file_size)

        self.assertEqual(message.caption, self.caption)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_ogg_file(self):
        message = self._bot.sendVoice(
            chat_id=self._chat_id,
            voice=self.voice_file,
            duration=self.duration,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_ogg_file_with_custom_filename(self):
        message = self._bot.sendVoice(
            chat_id=self._chat_id,
            voice=self.voice_file,
            duration=self.duration,
            caption=self.caption,
            filename='telegram_custom.ogg')

        self.assertEqual(message.caption, self.caption)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_ogg_url_file(self):
        message = self._bot.sendVoice(
            chat_id=self._chat_id, voice=self.voice_file_url, duration=self.duration)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_ogg_url_file_with_caption(self):
        message = self._bot.sendVoice(
            chat_id=self._chat_id,
            voice=self.voice_file_url,
            duration=self.duration,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        voice = message.voice

        self.assertTrue(isinstance(voice.file_id, str))
        self.assertNotEqual(voice.file_id, '')
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_voice_resend(self):
        message = self._bot.sendVoice(
            chat_id=self._chat_id,
            voice=self.voice_file_id,
            duration=self.duration,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        voice = message.voice

        self.assertEqual(voice.file_id, self.voice_file_id)
        self.assertEqual(voice.duration, 0)
        self.assertEqual(voice.mime_type, self.mime_type)

    def test_voice_de_json(self):
        voice = telegram.Voice.de_json(self.json_dict, self._bot)

        self.assertEqual(voice.file_id, self.voice_file_id)
        self.assertEqual(voice.duration, self.duration)
        self.assertEqual(voice.mime_type, self.mime_type)
        self.assertEqual(voice.file_size, self.file_size)

    def test_voice_to_json(self):
        voice = telegram.Voice.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(voice.to_json()))

    def test_voice_to_dict(self):
        voice = telegram.Voice.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(voice.to_dict()))
        self.assertEqual(voice['file_id'], self.voice_file_id)
        self.assertEqual(voice['duration'], self.duration)
        self.assertEqual(voice['mime_type'], self.mime_type)
        self.assertEqual(voice['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_voice_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['voice'] = open(os.devnull, 'rb')

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendVoice(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_voice_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['voice'] = ''

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendVoice(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_voice_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['duration'])

        self.assertRaises(
            TypeError,
            lambda: self._bot.sendVoice(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_voice(self):
        """Test for Message.reply_voice"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_voice(self.voice_file)

        self.assertNotEqual(message.voice.file_id, '')


if __name__ == '__main__':
    unittest.main()
