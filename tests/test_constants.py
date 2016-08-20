# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# by the python-telegram-bot contributors <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Test the Telegram constants."""

import sys
import unittest

from flaky import flaky

sys.path.append('.')

import telegram
from telegram.error import BadRequest
from tests.base import BaseTest, timeout


class ConstantsTest(BaseTest, unittest.TestCase):

    @flaky(3, 1)
    @timeout(10)
    def testMaxMessageLength(self):
        self._bot.sendMessage(chat_id=self._chat_id,
                              text='a' * telegram.constants.MAX_MESSAGE_LENGTH)

        try:
            self._bot.sendMessage(chat_id=self._chat_id,
                                  text='a' * (telegram.constants.MAX_MESSAGE_LENGTH + 1))
        except BadRequest as e:
            err = str(e)

        self.assertTrue("too long" in err)  # BadRequest: 'Message is too long'

    @flaky(3, 1)
    @timeout(10)
    def testMaxCaptionLength(self):
        self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                            caption='a' * telegram.constants.MAX_CAPTION_LENGTH,
                            chat_id=self._chat_id)

        try:
            self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                                caption='a' * (telegram.constants.MAX_CAPTION_LENGTH + 1),
                                chat_id=self._chat_id)
        except BadRequest as e:
            err = str(e)

        self.assertTrue("TOO_LONG" in err)  # BadRequest: 'MEDIA_CAPTION_TOO_LONG'


if __name__ == '__main__':
    unittest.main()
