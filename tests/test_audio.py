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
"""This module contains an object that represents Tests for Telegram Audio"""

import os
import unittest

from flaky import flaky

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot


class AudioTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Audio."""

    @classmethod
    def setUpClass(cls):
        cls.caption = "Test audio"
        cls.performer = 'Leandro Toledo'
        cls.title = 'Teste'
        cls.audio_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.mp3'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])

        audio_file = open('tests/data/telegram.mp3', 'rb')
        audio = cls._bot.send_audio(cls._chat_id, audio=audio_file, timeout=10).audio
        cls.audio = audio

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.audio, telegram.Audio)
        assert isinstance(cls.audio.file_id, str)
        assert cls.audio.file_id is not ''

    def setUp(self):
        self.audio_file = open('tests/data/telegram.mp3', 'rb')
        self.json_dict = {
            'file_id': self.audio.file_id,
            'duration': self.audio.duration,
            'performer': self.performer,
            'title': self.title,
            'caption': self.caption,
            'mime_type': self.audio.mime_type,
            'file_size': self.audio.file_size
        }

    def test_expected_values(self):
        self.assertEqual(self.audio.duration, 3)
        self.assertEqual(self.audio.performer, None)
        self.assertEqual(self.audio.title, None)
        self.assertEqual(self.audio.mime_type, 'audio/mpeg')
        self.assertEqual(self.audio.file_size, 122920)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_all_args(self):
        message = self._bot.sendAudio(
            self._chat_id,
            self.audio_file,
            caption=self.caption,
            duration=self.audio.duration,
            performer=self.performer,
            title=self.title,
            disable_notification=False)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertIsInstance(audio, telegram.Audio)
        self.assertIsInstance(audio.file_id, str)
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.audio.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.audio.mime_type)
        self.assertEqual(audio.file_size, self.audio.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_audio(self):
        new_file = self._bot.getFile(self.audio.file_id)

        self.assertEqual(new_file.file_size, self.audio.file_size)
        self.assertEqual(new_file.file_id, self.audio.file_id)
        self.assertTrue(new_file.file_path.startswith('https://'))

        new_file.download('telegram.mp3')

        self.assertTrue(os.path.isfile('telegram.mp3'))

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_url_file(self):
        message = self._bot.sendAudio(chat_id=self._chat_id, audio=self.audio_file_url)

        audio = message.audio

        self.assertIsInstance(audio, telegram.Audio)
        self.assertIsInstance(audio.file_id, str)
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.audio.duration)
        self.assertEqual(audio.mime_type, self.audio.mime_type)
        self.assertEqual(audio.file_size, self.audio.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_url_file_with_caption(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio_file_url,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertIsInstance(audio, telegram.Audio)
        self.assertIsInstance(audio.file_id, str)
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.audio.duration)
        self.assertEqual(audio.mime_type, self.audio.mime_type)
        self.assertEqual(audio.file_size, self.audio.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_resend(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio.file_id)

        audio = message.audio

        self.assertEqual(audio, self.audio)

    def test_audio_de_json(self):
        audio = telegram.Audio.de_json(self.json_dict, self._bot)

        self.assertIsInstance(audio, telegram.Audio)
        self.assertEqual(audio.file_id, self.audio.file_id)
        self.assertEqual(audio.duration, self.audio.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.audio.mime_type)
        self.assertEqual(audio.file_size, self.audio.file_size)

    def test_audio_to_json(self):
        self.assertTrue(self.is_json(self.audio.to_json()))

    def test_audio_to_dict(self):
        audio = self.audio.to_dict()

        self.assertTrue(self.is_dict(audio))
        self.assertEqual(audio['file_id'], self.audio.file_id)
        self.assertEqual(audio['duration'], self.audio.duration)
        self.assertEqual(audio['mime_type'], self.audio.mime_type)
        self.assertEqual(audio['file_size'], self.audio.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_audio_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['audio'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendAudio(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_audio_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['audio'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendAudio(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_audio_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['duration'])

        with self.assertRaises(TypeError):
            self._bot.sendAudio(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_audio(self):
        """Test for Message.reply_audio"""
        message = self._bot.sendMessage(self._chat_id, '.')
        audio = message.reply_audio(self.audio_file).audio

        self.assertIsInstance(audio, telegram.Audio)
        self.assertIsInstance(audio.file_id, str)
        self.assertNotEqual(audio.file_id, None)

    def test_equality(self):
        a = telegram.Audio(self.audio.file_id, self.audio.duration)
        b = telegram.Audio(self.audio.file_id, self.audio.duration)
        c = telegram.Audio(self.audio.file_id, 0)
        d = telegram.Audio("", self.audio.duration)
        e = telegram.Voice(self.audio.file_id, self.audio.duration)

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
