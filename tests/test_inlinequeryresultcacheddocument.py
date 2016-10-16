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
InlineQueryResultCachedDocument"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultCachedDocumentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram
    InlineQueryResultCachedDocument."""

    def setUp(self):
        self.id = 'id'
        self.type = 'document'
        self.document_file_id = 'document file id'
        self.title = 'title'
        self.caption = 'caption'
        self.description = 'description'
        self.input_message_content = telegram.InputTextMessageContent('input_message_content')
        self.reply_markup = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton('reply_markup')]])
        self.json_dict = {
            'id': self.id,
            'type': self.type,
            'document_file_id': self.document_file_id,
            'title': self.title,
            'caption': self.caption,
            'description': self.description,
            'input_message_content': self.input_message_content.to_dict(),
            'reply_markup': self.reply_markup.to_dict(),
        }

    def test_document_de_json(self):
        document = telegram.InlineQueryResultCachedDocument.de_json(self.json_dict, self._bot)

        self.assertEqual(document.id, self.id)
        self.assertEqual(document.type, self.type)
        self.assertEqual(document.document_file_id, self.document_file_id)
        self.assertEqual(document.title, self.title)
        self.assertEqual(document.caption, self.caption)
        self.assertEqual(document.description, self.description)
        self.assertDictEqual(document.input_message_content.to_dict(),
                             self.input_message_content.to_dict())
        self.assertDictEqual(document.reply_markup.to_dict(), self.reply_markup.to_dict())

    def test_document_to_json(self):
        document = telegram.InlineQueryResultCachedDocument.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(document.to_json()))

    def test_document_to_dict(self):
        document = telegram.InlineQueryResultCachedDocument.de_json(self.json_dict,
                                                                    self._bot).to_dict()

        self.assertTrue(self.is_dict(document))
        self.assertDictEqual(self.json_dict, document)


if __name__ == '__main__':
    unittest.main()
