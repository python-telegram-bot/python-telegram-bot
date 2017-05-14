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
"""This module contains an object that represents Tests for Telegram ChatMember"""

import unittest
import sys

sys.path.append('.')

import telegram
from tests.base import BaseTest


class ChatMemberTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram ChatMember."""

    def setUp(self):
        self.user = {'id': 1, 'first_name': 'User'}
        self.status = telegram.ChatMember.CREATOR

        self.json_dict = {'user': self.user, 'status': self.status}

    def test_chatmember_de_json(self):
        chatmember = telegram.ChatMember.de_json(self.json_dict, self._bot)

        self.assertEqual(chatmember.user.to_dict(), self.user)
        self.assertEqual(chatmember.status, self.status)

    def test_chatmember_to_json(self):
        chatmember = telegram.ChatMember.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(chatmember.to_json()))

    def test_chatmember_to_dict(self):
        chatmember = telegram.ChatMember.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(chatmember.to_dict()))
        self.assertEqual(chatmember['user'].to_dict(), self.user)
        self.assertEqual(chatmember['status'], self.status)

    def test_equality(self):
        a = telegram.ChatMember(telegram.User(1, ""), telegram.ChatMember.ADMINISTRATOR)
        b = telegram.ChatMember(telegram.User(1, ""), telegram.ChatMember.ADMINISTRATOR)
        d = telegram.ChatMember(telegram.User(2, ""), telegram.ChatMember.ADMINISTRATOR)
        d2 = telegram.ChatMember(telegram.User(1, ""), telegram.ChatMember.CREATOR)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, d2)
        self.assertNotEqual(hash(a), hash(d2))
