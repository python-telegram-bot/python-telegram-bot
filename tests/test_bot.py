#!/usr/bin/env python
# encoding: utf-8
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
"""This module contains a object that represents Tests for Telegram Bot"""

import io
from datetime import datetime
import sys

from flaky import flaky

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest, timeout


class BotTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Bot."""

    @flaky(3, 1)
    @timeout(10)
    def testGetMe(self):
        bot = self._bot.getMe()

        self.assertTrue(self.is_json(bot.to_json()))
        self._testUserEqualsBot(bot)

    @flaky(3, 1)
    @timeout(10)
    def testSendMessage(self):
        message = self._bot.sendMessage(chat_id=self._chat_id,
                                        text='Моё судно на воздушной подушке полно угрей')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def testSilentSendMessage(self):
        message = self._bot.sendMessage(chat_id=self._chat_id,
                                        text='Моё судно на воздушной подушке полно угрей',
                                        disable_notification=True)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def testGetUpdates(self):
        updates = self._bot.getUpdates(timeout=1)

        if updates:
            self.assertTrue(self.is_json(updates[0].to_json()))
            self.assertTrue(isinstance(updates[0], telegram.Update))

    @flaky(3, 1)
    @timeout(10)
    def testForwardMessage(self):
        message = self._bot.forwardMessage(chat_id=self._chat_id,
                                           from_chat_id=self._chat_id,
                                           message_id=2398)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'teste')
        self.assertEqual(message.forward_from.username, 'leandrotoledo')
        self.assertTrue(isinstance(message.forward_date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def testSendPhoto(self):
        message = self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                                      caption='testSendPhoto',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 1451)
        self.assertEqual(message.caption, 'testSendPhoto')

    @flaky(3, 1)
    @timeout(10)
    def testSilentSendPhoto(self):
        message = self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                                      caption='testSendPhoto',
                                      chat_id=self._chat_id,
                                      disable_notification=True)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 1451)
        self.assertEqual(message.caption, 'testSendPhoto')

    @flaky(3, 1)
    @timeout(10)
    def testResendPhoto(self):
        message = self._bot.sendPhoto(
            photo='AgADAQAD1y0yGx8j9Qf8f_m3CKeS6Iy95y8ABI1ggfVJ4-UvwJcAAgI',
            chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_id,
                         'AgADAQAD1y0yGx8j9Qf8f_m3CKeS6Iy95y8ABI1ggfVJ4-UvwJcAAgI')

    @flaky(3, 1)
    @timeout(10)
    def testSendJPGURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.jpg&text=telegram',
            chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 822)

    @flaky(3, 1)
    @timeout(10)
    def testSendPNGURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram',
            chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 685)

    @flaky(3, 1)
    @timeout(10)
    def testSendGIFURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram',
            chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 685)

    @flaky(3, 1)
    @timeout(10)
    def testSendBufferedReaderPhoto(self):
        photo = open('tests/data/telegram.png', 'rb')
        br_photo = io.BufferedReader(io.BytesIO(photo.read()))
        message = self._bot.sendPhoto(photo=br_photo, chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 1451)

    @flaky(3, 1)
    @timeout(10)
    def testSendChatAction(self):
        self._bot.sendChatAction(action=telegram.ChatAction.TYPING, chat_id=self._chat_id)

    @flaky(3, 1)
    @timeout(10)
    def testGetUserProfilePhotos(self):
        upf = self._bot.getUserProfilePhotos(user_id=self._chat_id)

        self.assertTrue(self.is_json(upf.to_json()))
        self.assertEqual(upf.photos[0][0].file_size, 12421)

    def _test_invalid_token(self, token):
        self.assertRaisesRegexp(telegram.error.InvalidToken, 'Invalid token', telegram.Bot, token)

    def testInvalidToken1(self):
        self._test_invalid_token('123')

    def testInvalidToken2(self):
        self._test_invalid_token('12a:')

    def testInvalidToken3(self):
        self._test_invalid_token('12:')

    def testUnauthToken(self):
        with self.assertRaisesRegexp(telegram.error.Unauthorized, 'Unauthorized'):
            bot = telegram.Bot('1234:abcd1234')
            bot.getMe()

    def testInvalidSrvResp(self):
        with self.assertRaisesRegexp(telegram.TelegramError, 'Invalid server response'):
            # bypass the valid token check
            bot = telegram.Bot.__new__(telegram.Bot)
            bot.base_url = 'https://api.telegram.org/bot{0}'.format('12')

            bot.getMe()

    @flaky(3, 1)
    @timeout(10)
    def testLeaveChat(self):
        with self.assertRaisesRegexp(telegram.error.BadRequest, 'Chat not found'):
            chat = self._bot.leaveChat(-123456)

    @flaky(3, 1)
    @timeout(10)
    def testGetChat(self):
        chat = self._bot.getChat(self._group_id)

        self.assertTrue(self.is_json(chat.to_json()))
        self.assertEqual(chat.type, "group")
        self.assertEqual(chat.title, ">>> telegram.Bot() - Developers")
        self.assertEqual(chat.id, int(self._group_id))

    @flaky(3, 1)
    @timeout(10)
    def testGetChatAdministrators(self):
        admins = self._bot.getChatAdministrators(self._channel_id)
        self.assertTrue(isinstance(admins, list))
        self.assertTrue(self.is_json(admins[0].to_json()))

        for a in admins:
            self.assertTrue(a.status in ("administrator", "creator"))

        bot = [a.user for a in admins if a.user.id == 133505823][0]
        self._testUserEqualsBot(bot)

    @flaky(3, 1)
    @timeout(10)
    def testGetChatMembersCount(self):
        count = self._bot.getChatMembersCount(self._channel_id)
        self.assertTrue(isinstance(count, int))
        self.assertTrue(count > 3)

    @flaky(3, 1)
    @timeout(10)
    def testGetChatMember(self):
        chat_member = self._bot.getChatMember(self._channel_id, 133505823)
        bot = chat_member.user

        self.assertTrue(self.is_json(chat_member.to_json()))
        self.assertEqual(chat_member.status, "administrator")
        self._testUserEqualsBot(bot)

    def _testUserEqualsBot(self, user):
        """Tests if user is our trusty @PythonTelegramBot."""
        self.assertEqual(user.id, 133505823)
        self.assertEqual(user.first_name, 'PythonTelegramBot')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.username, 'PythonTelegramBot')
        self.assertEqual(user.name, '@PythonTelegramBot')


if __name__ == '__main__':
    unittest.main()
