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

"""
This module contains a object that represents Tests for MessageHandler.Filters
"""

import unittest
import sys
from datetime import datetime
sys.path.append('.')

from telegram import Update, Message, User, Chat
from telegram.ext import Filters
from tests.base import BaseTest


class FiltersTest(BaseTest, unittest.TestCase):
    """This object represents Tests for MessageHandler.Filters"""

    def setUp(self):
        self.message = Message(0, User(0, "Testuser"), datetime.now(),
                               Chat(0, 'private'))
        self.update = Update(0, message=self.message)

    def test_filters_text(self):
        self.message.text = 'test'
        self.assertTrue(Filters.text(self.update))
        self.message.text = '/test'
        self.assertFalse(Filters.text(self.update))

    def test_filters_command(self):
        self.message.text = 'test'
        self.assertFalse(Filters.text(self.update))
        self.message.text = '/test'
        self.assertTrue(Filters.text(self.update))

    def test_filters_audio(self):
        self.message.audio = 'test'
        self.assertTrue(Filters.audio(self.update))
        self.message.audio = None
        self.assertFalse(Filters.audio(self.update))

    def test_filters_document(self):
        self.message.document = 'test'
        self.assertTrue(Filters.document(self.update))
        self.message.document = None
        self.assertFalse(Filters.document(self.update))

    def test_filters_photo(self):
        self.message.photo = 'test'
        self.assertTrue(Filters.photo(self.update))
        self.message.photo = None
        self.assertFalse(Filters.photo(self.update))

    def test_filters_sticker(self):
        self.message.sticker = 'test'
        self.assertTrue(Filters.sticker(self.update))
        self.message.sticker = None
        self.assertFalse(Filters.sticker(self.update))

    def test_filters_video(self):
        self.message.video = 'test'
        self.assertTrue(Filters.video(self.update))
        self.message.video = None
        self.assertFalse(Filters.video(self.update))

    def test_filters_voice(self):
        self.message.voice = 'test'
        self.assertTrue(Filters.voice(self.update))
        self.message.voice = None
        self.assertFalse(Filters.voice(self.update))

    def test_filters_contact(self):
        self.message.contact = 'test'
        self.assertTrue(Filters.contact(self.update))
        self.message.contact = None
        self.assertFalse(Filters.contact(self.update))

    def test_filters_location(self):
        self.message.location = 'test'
        self.assertTrue(Filters.location(self.update))
        self.message.location = None
        self.assertFalse(Filters.location(self.update))

    def test_filters_venue(self):
        self.message.venue = 'test'
        self.assertTrue(Filters.venue(self.update))
        self.message.venue = None
        self.assertFalse(Filters.venue(self.update))

    def test_filters_status_update(self):
        self.assertFalse(Filters.status_update(self.update))

        self.message.new_chat_member = 'test'
        self.assertTrue(Filters.status_update(self.update))
        self.message.new_chat_member = None

        self.message.left_chat_member = 'test'
        self.assertTrue(Filters.status_update(self.update))
        self.message.left_chat_member = None

        self.message.new_chat_title = 'test'
        self.assertTrue(Filters.status_update(self.update))
        self.message.new_chat_title = ''

        self.message.new_chat_photo = 'test'
        self.assertTrue(Filters.status_update(self.update))
        self.message.new_chat_photo = None

        self.message.delete_chat_photo = True
        self.assertTrue(Filters.status_update(self.update))
        self.message.delete_chat_photo = False

        self.message.group_chat_created = True
        self.assertTrue(Filters.status_update(self.update))
        self.message.group_chat_created = False

        self.message.supergroup_chat_created = True
        self.assertTrue(Filters.status_update(self.update))
        self.message.supergroup_chat_created = False

        self.message.migrate_to_chat_id = 100
        self.assertTrue(Filters.status_update(self.update))
        self.message.migrate_to_chat_id = 0

        self.message.migrate_from_chat_id = 100
        self.assertTrue(Filters.status_update(self.update))
        self.message.migrate_from_chat_id = 0

        self.message.channel_chat_created = True
        self.assertTrue(Filters.status_update(self.update))
        self.message.channel_chat_created = False

        self.message.pinned_message = 'test'
        self.assertTrue(Filters.status_update(self.update))
        self.message.pinned_message = None

if __name__ == '__main__':
    unittest.main()
