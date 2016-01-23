#!/usr/bin/env python

"""This module contains a object that represents Tests for Botan analytics integration"""

import os
import unittest
import sys
sys.path.append('.')

from telegram.utils.botan import Botan
from tests.base import BaseTest

class MessageMock(object):
    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

class BotanTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Botan analytics integration."""

    token = os.environ.get('BOTAN_TOKEN')

    def test_track(self):
        """Test sending event to botan"""
        print('Test sending event to botan')
        botan = Botan(self.token)
        message = MessageMock(self._chat_id)
        result = botan.track(message, 'named event')
        self.assertTrue(result)


    def test_track_fail(self):
        """Test fail when sending event to botan"""
        print('Test fail when sending event to botan')
        botan = Botan(self.token)
        botan.url_template = 'https://api.botan.io/traccc?token={token}&uid={uid}&name={name}'
        message = MessageMock(self._chat_id)
        result = botan.track(message, 'named event')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
