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
"""This module contains an object that represents Tests for Telegram Bot"""

import io
import re
from datetime import datetime
import time
import sys
import unittest

from flaky import flaky

sys.path.append('.')

import telegram
from telegram.error import BadRequest
from tests.base import BaseTest, timeout

BASE_TIME = time.time()
HIGHSCORE_DELTA = 1450000000


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
        message = self._bot.sendMessage(
            chat_id=self._chat_id, text='Моё судно на воздушной подушке полно угрей')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def testSilentSendMessage(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id,
            text='Моё судно на воздушной подушке полно угрей',
            disable_notification=True)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def test_sendMessage_no_web_page_preview(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id,
            text='Моё судно на воздушной подушке полно угрей',
            disable_web_page_preview=True)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')

    @flaky(3, 1)
    @timeout(10)
    def testGetUpdates(self):
        self._bot.delete_webhook()  # make sure there is no webhook set if webhook tests failed
        updates = self._bot.getUpdates(timeout=1)

        if updates:
            self.assertTrue(self.is_json(updates[0].to_json()))
            self.assertTrue(isinstance(updates[0], telegram.Update))

    @flaky(3, 1)
    @timeout(10)
    def testForwardMessage(self):
        message = self._bot.forwardMessage(
            chat_id=self._chat_id, from_chat_id=self._chat_id, message_id=2398)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'teste')
        self.assertEqual(message.forward_from.username, 'leandrotoledo')
        self.assertTrue(isinstance(message.forward_date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def testSendPhoto(self):
        message = self._bot.sendPhoto(
            photo=open('tests/data/telegram.png', 'rb'),
            caption='testSendPhoto',
            chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 1451)
        self.assertEqual(message.caption, 'testSendPhoto')

    @flaky(3, 1)
    @timeout(10)
    def testSilentSendPhoto(self):
        message = self._bot.sendPhoto(
            photo=open('tests/data/telegram.png', 'rb'),
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
            photo='AgADAQAD1y0yGx8j9Qf8f_m3CKeS6Iy95y8ABI1ggfVJ4-UvwJcAAgI', chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_id,
                         'AgADAQAD1y0yGx8j9Qf8f_m3CKeS6Iy95y8ABI1ggfVJ4-UvwJcAAgI')

    @flaky(3, 1)
    @timeout(10)
    def testSendJPGURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.jpg&text=telegram', chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 813)

    @flaky(3, 1)
    @timeout(10)
    def testSendPNGURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 670)

    @flaky(3, 1)
    @timeout(10)
    def testSendGIFURLPhoto(self):
        message = self._bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram', chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 670)

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
    def testSendGame(self):
        game_short_name = 'python_telegram_bot_test_game'
        message = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.game.description, 'This is a test game for python-telegram-bot.')
        self.assertEqual(message.game.animation.file_id, 'CgADAQADKwIAAvjAuQABozciVqhFDO0C')
        self.assertEqual(message.game.photo[0].file_size, 851)

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

    @flaky(3, 1)
    @timeout(10)
    def test_get_one_user_profile_photo(self):
        upf = self._bot.getUserProfilePhotos(user_id=self._chat_id, offset=0)
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

    def testInvalidToken4(self):
        # white spaces are invalid
        self._test_invalid_token('1234:abcd1234\n')
        self._test_invalid_token(' 1234:abcd1234')
        self._test_invalid_token(' 1234:abcd1234\r')
        self._test_invalid_token('1234:abcd 1234')

    def testUnauthToken(self):
        with self.assertRaisesRegexp(telegram.error.Unauthorized, 'Unauthorized'):
            bot = telegram.Bot('1234:abcd1234')
            bot.getMe()

    def testInvalidSrvResp(self):
        with self.assertRaisesRegexp(telegram.error.InvalidToken, 'Invalid token'):
            # bypass the valid token check
            newbot_cls = type(
                'NoTokenValidateBot', (telegram.Bot,), dict(_validate_token=lambda x, y: None))
            bot = newbot_cls('0xdeadbeef')
            bot.base_url = 'https://api.telegram.org/bot{0}'.format('12')

            bot.getMe()

    @flaky(3, 1)
    @timeout(10)
    def testLeaveChat(self):
        regex = re.compile('chat not found', re.IGNORECASE)
        with self.assertRaisesRegexp(telegram.error.BadRequest, regex):
            chat = self._bot.leaveChat(-123456)

        with self.assertRaisesRegexp(telegram.error.NetworkError, regex):
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

    @flaky(3, 1)
    @timeout(10)
    def test_forward_channel_message(self):
        text = 'test forward message'
        msg = self._bot.sendMessage(self._channel_id, text)
        self.assertEqual(text, msg.text)
        fwdmsg = msg.forward(self._chat_id)
        self.assertEqual(text, fwdmsg.text)
        self.assertEqual(fwdmsg.forward_from_message_id, msg.message_id)

    @flaky(3, 1)
    @timeout(10)
    def test_set_webhook_get_webhook_info(self):
        url = 'https://python-telegram-bot.org/test/webhook'
        max_connections = 7
        allowed_updates = ['message']
        self._bot.set_webhook(url, max_connections=7, allowed_updates=['message'])
        info = self._bot.getWebhookInfo()
        self._bot.delete_webhook()
        self.assertEqual(url, info.url)
        self.assertEqual(max_connections, info.max_connections)
        self.assertListEqual(allowed_updates, info.allowed_updates)

    @flaky(3, 1)
    @timeout(10)
    def test_delete_webhook(self):
        url = 'https://python-telegram-bot.org/test/webhook'
        self._bot.set_webhook(url)
        self._bot.delete_webhook()
        info = self._bot.getWebhookInfo()
        self.assertEqual(info.url, '')

    @flaky(3, 1)
    @timeout(10)
    def test_set_game_score1(self):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        message = self._bot.set_game_score(
            user_id=self._chat_id,
            score=int(BASE_TIME) - HIGHSCORE_DELTA,
            chat_id=game.chat_id,
            message_id=game.message_id)

        self.assertTrue(self.is_json(game.to_json()))
        self.assertEqual(message.game.description, game.game.description)
        self.assertEqual(message.game.animation.file_id, game.game.animation.file_id)
        self.assertEqual(message.game.photo[0].file_size, game.game.photo[0].file_size)
        self.assertNotEqual(message.game.text, game.game.text)

    @flaky(3, 1)
    @timeout(10)
    def test_set_game_score2(self):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        score = int(BASE_TIME) - HIGHSCORE_DELTA + 1

        message = self._bot.set_game_score(
            user_id=self._chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            disable_edit_message=True)

        self.assertTrue(self.is_json(game.to_json()))
        self.assertEqual(message.game.description, game.game.description)
        self.assertEqual(message.game.animation.file_id, game.game.animation.file_id)
        self.assertEqual(message.game.photo[0].file_size, game.game.photo[0].file_size)
        self.assertEqual(message.game.text, game.game.text)

    @flaky(3, 1)
    @timeout(10)
    def test_set_game_score3(self):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 1

        with self.assertRaises(BadRequest) as cm:
            self._bot.set_game_score(
                user_id=self._chat_id,
                score=score,
                chat_id=game.chat_id,
                message_id=game.message_id)

        self.assertTrue('BOT_SCORE_NOT_MODIFIED' in str(cm.exception.message).upper())

    @flaky(3, 1)
    @timeout(10)
    def test_set_game_score4(self):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 2

        message = self._bot.set_game_score(
            user_id=self._chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            force=True)

        self.assertTrue(self.is_json(game.to_json()))
        self.assertEqual(message.game.description, game.game.description)
        self.assertEqual(message.game.animation.file_id, game.game.animation.file_id)
        self.assertEqual(message.game.photo[0].file_size, game.game.photo[0].file_size)

        # For some reason the returned message does not contain the updated score. need to fetch
        # the game again...
        game2 = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)
        self.assertIn(str(score), game2.game.text)

    @flaky(3, 1)
    @timeout(10)
    def test_set_game_score_too_low_score(self):
        # We need a game to set the score for
        game_short_name = 'python_telegram_bot_test_game'
        game = self._bot.sendGame(game_short_name=game_short_name, chat_id=self._chat_id)

        with self.assertRaises(BadRequest):
            self._bot.set_game_score(
                user_id=self._chat_id, score=100, chat_id=game.chat_id, message_id=game.message_id)

    def _testUserEqualsBot(self, user):
        """Tests if user is our trusty @PythonTelegramBot."""
        self.assertEqual(user.id, 133505823)
        self.assertEqual(user.first_name, 'PythonTelegramBot')
        self.assertEqual(user.last_name, None)
        self.assertEqual(user.username, 'PythonTelegramBot')
        self.assertEqual(user.name, '@PythonTelegramBot')

    @flaky(3, 1)
    @timeout(10)
    def test_info(self):
        # tests the Bot.info decorator and associated funcs
        self.assertEqual(self._bot.id, 133505823)
        self.assertEqual(self._bot.first_name, 'PythonTelegramBot')
        self.assertEqual(self._bot.last_name, None)
        self.assertEqual(self._bot.username, 'PythonTelegramBot')
        self.assertEqual(self._bot.name, '@PythonTelegramBot')

    @flaky(3, 1)
    @timeout(10)
    def test_send_contact(self):
        # test disabled due to telegram servers annoyances repeatedly returning:
        # "Flood control exceeded. Retry in 2036 seconds"
        return
        phone = '+3-54-5445445'
        name = 'name'
        last = 'last'
        message = self._bot.send_contact(self._chat_id, phone, name, last)
        self.assertEqual(phone.replace('-', ''), message.contact.phone_number)
        self.assertEqual(name, message.contact.first_name)
        self.assertEqual(last, message.contact.last_name)


if __name__ == '__main__':
    unittest.main()
