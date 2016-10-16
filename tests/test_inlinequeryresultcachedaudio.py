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
InlineQueryResultCachedAudio"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedAudioTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram
    InlineQueryResultCachedAudio."""

    def setUp(self):
        self.id = 'id'
        self.type = 'audio'
        self.audio_file_id = 'audio file id'
        self.caption = 'caption'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'audio_file_id': self.audio_file_id,
            'caption': self.caption,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_audio_de_json(self):
        audio = telegram.InlineQueryResultCachedAudio.de_json(self.json_dict, self._bot)

        self.assertEqual(audio.type, self.type)
        self.assertEqual(audio.id, self.id)
        self.assertEqual(audio.audio_file_id, self.audio_file_id)
        self.assertEqual(audio.caption, self.caption)
        self.assertDictEqual(audio.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(audio.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_audio_to_json(self):
        audio = telegram.InlineQueryResultCachedAudio.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(audio.to_json()))

    def test_audio_to_dict(self):
        audio = telegram.InlineQueryResultCachedAudio.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(audio))
        self.assertDictEqual(self.json_dict, audio)


if __name__ == '__main__':
    unittest.main()
