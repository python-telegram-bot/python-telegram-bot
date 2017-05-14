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
InlineQueryResultPhoto"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultPhotoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultPhoto."""

    def setUp(self):
        self._id = 'id'
        self.type = 'photo'
        self.photo_url = 'photo url'
        self.photo_width = 10
        self.photo_height = 15
        self.thumb_url = 'thumb url'
        self.title = 'title'
        self.description = 'description'
        self.caption = 'caption'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])

        self.json_dict = {
            'type': self.type,
            'id': self._id,
            'photo_url': self.photo_url,
            'photo_width': self.photo_width,
            'photo_height': self.photo_height,
            'thumb_url': self.thumb_url,
            'title': self.title,
            'description': self.description,
            'caption': self.caption,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_photo_de_json(self):
        photo = telegram.InlineQueryResultPhoto.de_json(self.json_dict, self._bot)

        self.assertEqual(photo.type, self.type)
        self.assertEqual(photo.id, self._id)
        self.assertEqual(photo.photo_url, self.photo_url)
        self.assertEqual(photo.photo_width, self.photo_width)
        self.assertEqual(photo.photo_height, self.photo_height)
        self.assertEqual(photo.thumb_url, self.thumb_url)
        self.assertEqual(photo.title, self.title)
        self.assertEqual(photo.description, self.description)
        self.assertEqual(photo.caption, self.caption)
        self.assertDictEqual(photo.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(photo.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_photo_to_json(self):
        photo = telegram.InlineQueryResultPhoto.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(photo.to_json()))

    def test_photo_to_dict(self):
        photo = telegram.InlineQueryResultPhoto.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(photo))
        self.assertDictEqual(self.json_dict, photo)

    def test_equality(self):
        a = telegram.InlineQueryResultPhoto(self._id, self.photo_url, self.thumb_url)
        b = telegram.InlineQueryResultPhoto(self._id, self.photo_url, self.thumb_url)
        c = telegram.InlineQueryResultPhoto(self._id, "", self.thumb_url)
        d = telegram.InlineQueryResultPhoto("", self.photo_url, self.thumb_url)
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
