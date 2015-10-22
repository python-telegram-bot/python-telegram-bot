#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents Tests for Telegram Emoji"""

import os
import unittest
import sys
sys.path.append('.')

import telegram
from telegram.emoji import Emoji
from tests.base import BaseTest


class EmojiTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Emoji."""

    def test_emoji(self):
        """Test Emoji class"""
        print('Testing Emoji class')
        
        for attr in dir(Emoji):
            if attr[0] != '_':  # TODO: dirty way to filter out functions
                self.assertTrue(type(getattr(Emoji, attr)) is str)


if __name__ == '__main__':
    unittest.main()
