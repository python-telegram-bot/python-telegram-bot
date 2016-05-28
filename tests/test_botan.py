#!/usr/bin/env python
"""This module contains an object that represents Tests for Botan analytics integration"""

import sys
import unittest
import os

from flaky import flaky

sys.path.append('.')

from telegram.contrib.botan import Botan
from tests.base import BaseTest


class MessageMock(object):
    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def to_json(self):
        return "{}"


@flaky(3, 1)
class BotanTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Botan analytics integration."""

    token = os.environ.get('BOTAN_TOKEN')

    def test_track(self):
        botan = Botan(self.token)
        message = MessageMock(self._chat_id)
        result = botan.track(message, 'named event')
        self.assertTrue(result)

    def test_track_fail(self):
        botan = Botan(self.token)
        botan.url_template = 'https://api.botan.io/traccc?token={token}&uid={uid}&name={name}'
        message = MessageMock(self._chat_id)
        result = botan.track(message, 'named event')
        self.assertFalse(result)

    def test_wrong_message(self):
        botan = Botan(self.token)
        message = MessageMock(self._chat_id)
        message = delattr(message, 'chat_id')
        result = botan.track(message, 'named event')
        self.assertFalse(result)

    def test_wrong_endpoint(self):
        botan = Botan(self.token)
        botan.url_template = 'https://api.botaaaaan.io/traccc?token={token}&uid={uid}&name={name}'
        message = MessageMock(self._chat_id)
        result = botan.track(message, 'named event')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
