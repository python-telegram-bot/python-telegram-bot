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
"""This module contains an object that represents Tests for Telegram
InlineQueryResultCachedVoice"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedVoiceTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram
    InlineQueryResultCachedVoice."""

    def setUp(self):
        self._id = 'id'
        self.type = 'voice'
        self.voice_file_id = 'voice file id'
        self.title = 'title'
        self.caption = 'caption'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self._id,
            'voice_file_id': self.voice_file_id,
            'title': self.title,
            'caption': self.caption,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_voice_de_json(self):
        voice = telegram.InlineQueryResultCachedVoice.de_json(self.json_dict, self._bot)

        self.assertEqual(voice.type, self.type)
        self.assertEqual(voice.id, self._id)
        self.assertEqual(voice.voice_file_id, self.voice_file_id)
        self.assertEqual(voice.title, self.title)
        self.assertEqual(voice.caption, self.caption)
        self.assertDictEqual(voice.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(voice.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_voice_to_json(self):
        voice = telegram.InlineQueryResultCachedVoice.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(voice.to_json()))

    def test_voice_to_dict(self):
        voice = telegram.InlineQueryResultCachedVoice.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(voice))
        self.assertDictEqual(self.json_dict, voice)

    def test_equality(self):
        a = telegram.InlineQueryResultCachedVoice(self._id, self.voice_file_id, self.title)
        b = telegram.InlineQueryResultCachedVoice(self._id, self.voice_file_id, self.title)
        c = telegram.InlineQueryResultCachedVoice(self._id, "", self.title)
        d = telegram.InlineQueryResultCachedVoice("", self.voice_file_id, self.title)
        e = telegram.InlineQueryResultCachedAudio(self._id, "", "")

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
