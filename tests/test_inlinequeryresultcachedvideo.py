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
InlineQueryResultCachedVideo"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedVideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram
    InlineQueryResultCachedVideo."""

    def setUp(self):
        self._id = 'id'
        self.type = 'video'
        self.video_file_id = 'video file id'
        self.title = 'title'
        self.caption = 'caption'
        self.description = 'description'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self._id,
            'video_file_id': self.video_file_id,
            'title': self.title,
            'caption': self.caption,
            'description': self.description,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_video_de_json(self):
        video = telegram.InlineQueryResultCachedVideo.de_json(self.json_dict, self._bot)

        self.assertEqual(video.type, self.type)
        self.assertEqual(video.id, self._id)
        self.assertEqual(video.video_file_id, self.video_file_id)
        self.assertEqual(video.title, self.title)
        self.assertEqual(video.description, self.description)
        self.assertEqual(video.caption, self.caption)
        self.assertDictEqual(video.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(video.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_video_to_json(self):
        video = telegram.InlineQueryResultCachedVideo.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(video.to_json()))

    def test_video_to_dict(self):
        video = telegram.InlineQueryResultCachedVideo.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(video))
        self.assertDictEqual(self.json_dict, video)

    def test_equality(self):
        a = telegram.InlineQueryResultCachedVideo(self._id, self.video_file_id, self.title)
        b = telegram.InlineQueryResultCachedVideo(self._id, self.video_file_id, self.title)
        c = telegram.InlineQueryResultCachedVideo(self._id, "", self.title)
        d = telegram.InlineQueryResultCachedVideo("", self.video_file_id, self.title)
        e = telegram.InlineQueryResultCachedVoice(self._id, "", "")

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
