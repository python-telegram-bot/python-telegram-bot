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
InputMessageContent"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InputMessageContentTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InputMessageContent."""

    def test_imc_de_json(self):
        imc = telegram.InputMessageContent.de_json(None, self._bot)

        self.assertFalse(imc)


if __name__ == '__main__':
    unittest.main()
