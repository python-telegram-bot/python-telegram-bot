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
LabeledPrice"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class LabeledPriceTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram LabeledPrice."""

    def setUp(self):
        self.label = 'label'
        self.amount = 100

        self.json_dict = {'label': self.label, 'amount': self.amount}

    def test_labeledprice_de_json(self):
        labeledprice = telegram.LabeledPrice.de_json(self.json_dict, self._bot)

        self.assertEqual(labeledprice.label, self.label)
        self.assertEqual(labeledprice.amount, self.amount)

    def test_labeledprice_to_json(self):
        labeledprice = telegram.LabeledPrice.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(labeledprice.to_json()))

    def test_labeledprice_to_dict(self):
        labeledprice = telegram.LabeledPrice.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(labeledprice))
        self.assertDictEqual(self.json_dict, labeledprice)


if __name__ == '__main__':
    unittest.main()
