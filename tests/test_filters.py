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
This module contains an object that represents Tests for Filters for use with MessageHandler.
"""

import sys
import unittest
from datetime import datetime
import functools

sys.path.append('.')

from telegram import Message, User, Chat, MessageEntity
from telegram.ext import Filters, BaseFilter
from tests.base import BaseTest


class FiltersTest(BaseTest, unittest.TestCase):
    """This object represents Tests for MessageHandler.Filters"""

    def setUp(self):
        self.message = Message(0, User(0, "Testuser"), datetime.now(), Chat(0, 'private'))
        self.e = functools.partial(MessageEntity, offset=0, length=0)

    def test_filters_text(self):
        self.message.text = 'test'
        self.assertTrue(Filters.text(self.message))
        self.message.text = '/test'
        self.assertFalse(Filters.text(self.message))

    def test_filters_command(self):
        self.message.text = 'test'
        self.assertFalse(Filters.command(self.message))
        self.message.text = '/test'
        self.assertTrue(Filters.command(self.message))

    def test_filters_reply(self):
        another_message = Message(1, User(1, "TestOther"), datetime.now(), Chat(0, 'private'))
        self.message.text = 'test'
        self.assertFalse(Filters.reply(self.message))
        self.message.reply_to_message = another_message
        self.assertTrue(Filters.reply(self.message))

    def test_filters_audio(self):
        self.message.audio = 'test'
        self.assertTrue(Filters.audio(self.message))
        self.message.audio = None
        self.assertFalse(Filters.audio(self.message))

    def test_filters_document(self):
        self.message.document = 'test'
        self.assertTrue(Filters.document(self.message))
        self.message.document = None
        self.assertFalse(Filters.document(self.message))

    def test_filters_photo(self):
        self.message.photo = 'test'
        self.assertTrue(Filters.photo(self.message))
        self.message.photo = None
        self.assertFalse(Filters.photo(self.message))

    def test_filters_sticker(self):
        self.message.sticker = 'test'
        self.assertTrue(Filters.sticker(self.message))
        self.message.sticker = None
        self.assertFalse(Filters.sticker(self.message))

    def test_filters_video(self):
        self.message.video = 'test'
        self.assertTrue(Filters.video(self.message))
        self.message.video = None
        self.assertFalse(Filters.video(self.message))

    def test_filters_voice(self):
        self.message.voice = 'test'
        self.assertTrue(Filters.voice(self.message))
        self.message.voice = None
        self.assertFalse(Filters.voice(self.message))

    def test_filters_contact(self):
        self.message.contact = 'test'
        self.assertTrue(Filters.contact(self.message))
        self.message.contact = None
        self.assertFalse(Filters.contact(self.message))

    def test_filters_location(self):
        self.message.location = 'test'
        self.assertTrue(Filters.location(self.message))
        self.message.location = None
        self.assertFalse(Filters.location(self.message))

    def test_filters_venue(self):
        self.message.venue = 'test'
        self.assertTrue(Filters.venue(self.message))
        self.message.venue = None
        self.assertFalse(Filters.venue(self.message))

    def test_filters_game(self):
        self.message.game = 'test'
        self.assertTrue(Filters.game(self.message))
        self.message.game = None
        self.assertFalse(Filters.game(self.message))

    def test_filters_status_update(self):
        self.assertFalse(Filters.status_update(self.message))

        self.message.new_chat_member = 'test'
        self.assertTrue(Filters.status_update(self.message))
        self.message.new_chat_member = None

        self.message.left_chat_member = 'test'
        self.assertTrue(Filters.status_update(self.message))
        self.message.left_chat_member = None

        self.message.new_chat_title = 'test'
        self.assertTrue(Filters.status_update(self.message))
        self.message.new_chat_title = ''

        self.message.new_chat_photo = 'test'
        self.assertTrue(Filters.status_update(self.message))
        self.message.new_chat_photo = None

        self.message.delete_chat_photo = True
        self.assertTrue(Filters.status_update(self.message))
        self.message.delete_chat_photo = False

        self.message.group_chat_created = True
        self.assertTrue(Filters.status_update(self.message))
        self.message.group_chat_created = False

        self.message.supergroup_chat_created = True
        self.assertTrue(Filters.status_update(self.message))
        self.message.supergroup_chat_created = False

        self.message.migrate_to_chat_id = 100
        self.assertTrue(Filters.status_update(self.message))
        self.message.migrate_to_chat_id = 0

        self.message.migrate_from_chat_id = 100
        self.assertTrue(Filters.status_update(self.message))
        self.message.migrate_from_chat_id = 0

        self.message.channel_chat_created = True
        self.assertTrue(Filters.status_update(self.message))
        self.message.channel_chat_created = False

        self.message.pinned_message = 'test'
        self.assertTrue(Filters.status_update(self.message))
        self.message.pinned_message = None

    def test_entities_filter(self):
        self.message.entities = [self.e(MessageEntity.MENTION)]
        self.assertTrue(Filters.entity(MessageEntity.MENTION)(self.message))

        self.message.entities = []
        self.assertFalse(Filters.entity(MessageEntity.MENTION)(self.message))

        self.message.entities = [self.e(MessageEntity.BOLD)]
        self.assertFalse(Filters.entity(MessageEntity.MENTION)(self.message))

        self.message.entities = [self.e(MessageEntity.BOLD), self.e(MessageEntity.MENTION)]
        self.assertTrue(Filters.entity(MessageEntity.MENTION)(self.message))

    def test_and_filters(self):
        self.message.text = 'test'
        self.message.forward_date = True
        self.assertTrue((Filters.text & Filters.forwarded)(self.message))
        self.message.text = '/test'
        self.assertFalse((Filters.text & Filters.forwarded)(self.message))
        self.message.text = 'test'
        self.message.forward_date = None
        self.assertFalse((Filters.text & Filters.forwarded)(self.message))

        self.message.text = 'test'
        self.message.forward_date = True
        self.message.entities = [self.e(MessageEntity.MENTION)]
        self.assertTrue((Filters.text & Filters.forwarded & Filters.entity(MessageEntity.MENTION))(
            self.message))
        self.message.entities = [self.e(MessageEntity.BOLD)]
        self.assertFalse((Filters.text & Filters.forwarded & Filters.entity(MessageEntity.MENTION)
                         )(self.message))

    def test_or_filters(self):
        self.message.text = 'test'
        self.assertTrue((Filters.text | Filters.status_update)(self.message))
        self.message.group_chat_created = True
        self.assertTrue((Filters.text | Filters.status_update)(self.message))
        self.message.text = None
        self.assertTrue((Filters.text | Filters.status_update)(self.message))
        self.message.group_chat_created = False
        self.assertFalse((Filters.text | Filters.status_update)(self.message))

    def test_and_or_filters(self):
        self.message.text = 'test'
        self.message.forward_date = True
        self.assertTrue((Filters.text & (Filters.forwarded | Filters.entity(MessageEntity.MENTION))
                        )(self.message))
        self.message.forward_date = False
        self.assertFalse((Filters.text & (Filters.forwarded | Filters.entity(MessageEntity.MENTION)
                                         ))(self.message))
        self.message.entities = [self.e(MessageEntity.MENTION)]
        self.assertTrue((Filters.text & (Filters.forwarded | Filters.entity(MessageEntity.MENTION))
                        )(self.message))

        self.assertRegexpMatches(
            str((Filters.text & (Filters.forwarded | Filters.entity(MessageEntity.MENTION)))),
            r"<telegram.ext.filters.MergedFilter consisting of <telegram.ext.filters.(Filters.)?_"
            r"Text object at .*?> and <telegram.ext.filters.MergedFilter consisting of "
            r"<telegram.ext.filters.(Filters.)?_Forwarded object at .*?> or "
            r"<telegram.ext.filters.(Filters.)?entity object at .*?>>>")

    def test_faulty_custom_filter(self):

        class _CustomFilter(BaseFilter):
            pass

        custom = _CustomFilter()

        with self.assertRaises(NotImplementedError):
            (custom & Filters.text)(self.message)


if __name__ == '__main__':
    unittest.main()
