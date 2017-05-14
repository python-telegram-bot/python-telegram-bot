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
"""This module contains an object that represents Tests for Telegram
InlineQueryResultAudio"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultAudioTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultAudio."""

    def setUp(self):
        self._id = 'id'
        self.type = 'audio'
        self.audio_url = 'audio url'
        self.title = 'title'
        self.performer = 'performer'
        self.audio_duration = 'audio_duration'
        self.caption = 'caption'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self._id,
            'audio_url': self.audio_url,
            'title': self.title,
            'performer': self.performer,
            'audio_duration': self.audio_duration,
            'caption': self.caption,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_audio_de_json(self):
        audio = telegram.InlineQueryResultAudio.de_json(self.json_dict, self._bot)

        self.assertEqual(audio.type, self.type)
        self.assertEqual(audio.id, self._id)
        self.assertEqual(audio.audio_url, self.audio_url)
        self.assertEqual(audio.title, self.title)
        self.assertEqual(audio.performer, self.performer)
        self.assertEqual(audio.audio_duration, self.audio_duration)
        self.assertEqual(audio.caption, self.caption)
        self.assertDictEqual(audio.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(audio.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_audio_to_json(self):
        audio = telegram.InlineQueryResultAudio.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(audio.to_json()))

    def test_audio_to_dict(self):
        audio = telegram.InlineQueryResultAudio.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(audio))
        self.assertDictEqual(self.json_dict, audio)

    def test_equality(self):
        a = telegram.InlineQueryResultAudio(self._id, self.audio_url, self.title)
        b = telegram.InlineQueryResultAudio(self._id, self.title, self.title)
        c = telegram.InlineQueryResultAudio(self._id, "", self.title)
        d = telegram.InlineQueryResultAudio("", self.audio_url, self.title)
        e = telegram.InlineQueryResultArticle(self._id, "", "")

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
