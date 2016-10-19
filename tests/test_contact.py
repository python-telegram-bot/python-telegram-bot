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
"""This module contains an object that represents Tests for Telegram Contact"""

import unittest
import sys

from flaky import flaky

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ContactTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Contact."""

    def setUp(self):
        self.phone_number = '+11234567890'
        self.first_name = 'Leandro Toledo'
        self.last_name = ''
        self.user_id = 0

        self.json_dict = {
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_id': self.user_id
        }

    def test_contact_de_json(self):
        contact = telegram.Contact.de_json(self.json_dict, self._bot)

        self.assertEqual(contact.phone_number, self.phone_number)
        self.assertEqual(contact.first_name, self.first_name)
        self.assertEqual(contact.last_name, self.last_name)
        self.assertEqual(contact.user_id, self.user_id)

    def test_contact_to_json(self):
        contact = telegram.Contact.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(contact.to_json()))

    def test_contact_to_dict(self):
        contact = telegram.Contact.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(contact.to_dict()))
        self.assertEqual(contact['phone_number'], self.phone_number)
        self.assertEqual(contact['first_name'], self.first_name)
        self.assertEqual(contact['last_name'], self.last_name)
        self.assertEqual(contact['user_id'], self.user_id)


''' Commented out, because it would cause "Too Many Requests (429)" errors.
    @flaky(3, 1)
    def test_reply_contact(self):
        """Test for Message.reply_contact"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_contact(self.phone_number, self.first_name)

        self.assertEqual(message.contact.phone_number, self.phone_number)
        self.assertEqual(message.contact.first_name, self.first_name)
'''

if __name__ == '__main__':
    unittest.main()
