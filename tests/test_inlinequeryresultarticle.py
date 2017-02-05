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
InlineQueryResultArticle"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultArticleTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultArticle."""

    def setUp(self):
        self.id = 'id'
        self.type = 'article'
        self.title = 'title'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])
        self.url = 'url'
        self.hide_url = True
        self.description = 'description'
        self.thumb_url = 'thumb url'
        self.thumb_height = 10
        self.thumb_width = 15

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'title': self.title,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
            'url': self.url,
            'hide_url': self.hide_url,
            'description': self.description,
            'thumb_url': self.thumb_url,
            'thumb_height': self.thumb_height,
            'thumb_width': self.thumb_width
        }

    def test_article_de_json(self):
        article = telegram.InlineQueryResultArticle.de_json(self.json_dict, self._bot)

        self.assertEqual(article.type, self.type)
        self.assertEqual(article.id, self.id)
        self.assertEqual(article.title, self.title)
        self.assertDictEqual(article.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(article.reply_markup.to_dict(), self.reply_markup.to_dict())
        self.assertEqual(article.url, self.url)
        self.assertEqual(article.hide_url, self.hide_url)
        self.assertEqual(article.description, self.description)
        self.assertEqual(article.thumb_url, self.thumb_url)
        self.assertEqual(article.thumb_height, self.thumb_height)
        self.assertEqual(article.thumb_width, self.thumb_width)

    def test_article_to_json(self):
        article = telegram.InlineQueryResultArticle.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(article.to_json()))

    def test_article_to_dict(self):
        article = telegram.InlineQueryResultArticle.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(article))
        self.assertDictEqual(self.json_dict, article)


if __name__ == '__main__':
    unittest.main()
