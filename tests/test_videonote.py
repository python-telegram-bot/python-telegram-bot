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
"""This module contains an object that represents Tests for Telegram VideoNote"""
import numbers
import sys
import unittest
import os

from flaky import flaky

from tests.bots import get_bot

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class VideoNoteTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram VideoNote."""

    @classmethod
    def setUpClass(cls):
        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])
        videonote_file = open('tests/data/telegram2.mp4', 'rb')
        video_note = cls._bot.send_video_note(cls._chat_id, video_note=videonote_file, timeout=10).video_note
        cls.videonote_file_id = video_note.file_id
        cls.duration = video_note.duration
        cls.length = video_note.length
        cls.thumb = video_note.thumb
        cls.file_size = video_note.file_size

    def setUp(self):
        self.videonote_file = open('tests/data/telegram2.mp4', 'rb')
        self.json_dict = {
            'file_id': self.videonote_file_id,
            'duration': self.duration,
            'length': self.length,
            'thumb': self.thumb.to_dict(),
            'file_size': self.file_size
        }

    @flaky(3, 1)
    @timeout(10)
    def test_send_videonote_required_args_only(self):
        # obsolete, testen in setUpClass
        self.assertEqual(True, True)

    @flaky(3, 1)
    @timeout(10)
    def test_send_videonote_all_args(self):
        message = self._bot.sendVideoNote(
            self._chat_id,
            self.videonote_file,
            timeout=10,
            duration=self.duration,
            length=self.length,
            disable_notification=False)

        videonote = message.video_note

        self.assertTrue(isinstance(videonote.file_id, str))
        self.assertNotEqual(videonote.file_id, None)
        self.assertEqual(videonote.length, self.length)
        self.assertEqual(videonote.duration, self.duration)
        self.assertEqual(videonote.thumb, self.thumb)
        self.assertEqual(videonote.file_size, self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_videonote_resend(self):
        message = self._bot.sendVideoNote(
            chat_id=self._chat_id,
            video_note=self.videonote_file_id,
            timeout=10
        )

        videonote = message.video_note

        self.assertEqual(videonote.file_id, self.videonote_file_id)
        self.assertEqual(videonote.length, self.length)
        self.assertEqual(videonote.duration, self.duration)
        self.assertEqual(videonote.thumb, self.thumb)
        self.assertEqual(videonote.file_size, self.file_size)

    def test_videonote_de_json(self):
        videonote = telegram.VideoNote.de_json(self.json_dict, self._bot)

        self.assertEqual(videonote.file_id, self.videonote_file_id)
        self.assertEqual(videonote.duration, self.duration)
        self.assertEqual(videonote.thumb, self.thumb)
        self.assertEqual(videonote.length, self.length)
        self.assertEqual(videonote.file_size, self.file_size)

    def test_videonote_to_json(self):
        videonote = telegram.VideoNote.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(videonote.to_json()))

    def test_videonote_to_dict(self):
        videonote = telegram.VideoNote.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(videonote.to_dict()))
        self.assertEqual(videonote['file_id'], self.videonote_file_id)
        self.assertEqual(videonote['duration'], self.duration)
        self.assertEqual(videonote['length'], self.length)
        self.assertEqual(videonote['file_size'], self.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_videonote_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['video_note'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendVideoNote(chat_id=self._chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_videonote_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['video_note'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendVideoNote(chat_id=self._chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_videonote(self):
        """Test for Message.reply_videonote"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_video_note(self.videonote_file)

        self.assertNotEqual(message.video_note.file_id, None)

    def test_equality(self):
        a = telegram.VideoNote(self.videonote_file_id, self.length, self.duration)
        b = telegram.VideoNote(self.videonote_file_id, self.length, self.duration)
        c = telegram.VideoNote(self.videonote_file_id, 0, 0, 0)
        d = telegram.VideoNote("", self.length, self.duration)
        e = telegram.Voice(self.videonote_file_id, self.duration)

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
