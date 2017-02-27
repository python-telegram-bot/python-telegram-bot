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
"""This module contains an object that represents Tests for Telegram Audio"""

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class AudioTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Audio."""

    def setUp(self):
        self.audio_file = open('tests/data/telegram.mp3', 'rb')
        self.audio_file_id = 'CQADAQADDwADHyP1B6PSPq2HjX8kAg'
        self.audio_file_url = 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.mp3'
        self.duration = 4
        self.performer = 'Leandro Toledo'
        self.title = 'Teste'
        self.caption = "Test audio"
        self.mime_type = 'audio/mpeg'
        self.file_size = 28232

        self.json_dict = {
            'file_id': self.audio_file_id,
            'duration': self.duration,
            'performer': self.performer,
            'title': self.title,
            'caption': self.caption,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_required_args_only(self):
        message = self._bot.sendAudio(self._chat_id, self.audio_file)

        self.assertEqual(message.caption, None)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        # self.assertEqual(audio.duration, 4)
        self.assertEqual(audio.performer, None)
        self.assertEqual(audio.title, None)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_all_args(self):
        message = self._bot.sendAudio(
            self._chat_id,
            self.audio_file,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
            caption=self.caption,
            mime_type=self.mime_type,
            file_size=self.file_size)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_file(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio_file,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_file_custom_filename(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio_file,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
            caption=self.caption,
            filename='telegram_custom.mp3')

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_url_file(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id, audio=self.audio_file_url, duration=self.duration)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_mp3_url_file_with_caption(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio_file_url,
            duration=self.duration,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertTrue(isinstance(audio.file_id, str))
        self.assertNotEqual(audio.file_id, None)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_audio_resend(self):
        message = self._bot.sendAudio(
            chat_id=self._chat_id,
            audio=self.audio_file_id,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
            caption=self.caption)

        self.assertEqual(message.caption, self.caption)

        audio = message.audio

        self.assertEqual(audio.file_id, self.audio_file_id)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)

    def test_audio_de_json(self):
        audio = telegram.Audio.de_json(self.json_dict, self._bot)

        self.assertEqual(audio.file_id, self.audio_file_id)
        self.assertEqual(audio.duration, self.duration)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.mime_type, self.mime_type)
        self.assertEqual(audio.file_size, self.file_size)

    def test_audio_to_json(self):
        audio = telegram.Audio.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(audio.to_json()))

    def test_audio_to_dict(self):
        audio = telegram.Audio.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(audio.to_dict()))
        self.assertEqual(audio['file_id'], self.audio_file_id)
        self.assertEqual(audio['duration'], self.duration)
        self.assertEqual(audio['performer'], self.performer)
        self.assertEqual(audio['title'], self.title)
        self.assertEqual(audio['mime_type'], self.mime_type)
        self.assertEqual(audio['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_audio_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['audio'] = open(os.devnull, 'rb')

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendAudio(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_audio_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['audio'] = ''

        self.assertRaises(
            telegram.TelegramError,
            lambda: self._bot.sendAudio(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_error_audio_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        del (json_dict['duration'])

        self.assertRaises(
            TypeError,
            lambda: self._bot.sendAudio(chat_id=self._chat_id, **json_dict))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_audio(self):
        """Test for Message.reply_audio"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_audio(self.audio_file)

        self.assertNotEqual(message.audio.file_id, None)


if __name__ == '__main__':
    unittest.main()
