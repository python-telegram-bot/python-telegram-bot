#!/usr/bin/env python
# encoding: utf-8
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

"""This module contains a object that represents Tests for Telegram Bot"""

import os
import unittest
from datetime import datetime
import sys
sys.path.append('.')

import telegram
from tests.base import BaseTest


class BotTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Bot."""

    def testGetMe(self):
        '''Test the telegram.Bot getMe method'''
        print('Testing getMe')
        bot = self._bot.getMe()

        self.assertTrue(self.is_json(bot.to_json()))
        self.assertEqual(bot.id, 133505823)
        self.assertEqual(bot.first_name, 'PythonTelegramBot')
        self.assertEqual(bot.last_name, '')
        self.assertEqual(bot.username, 'PythonTelegramBot')
        self.assertEqual(bot.name, '@PythonTelegramBot')

    def testSendMessage(self):
        '''Test the telegram.Bot sendMessage method'''
        print('Testing sendMessage')
        message = self._bot.sendMessage(chat_id=self._chat_id,
                                        text='Моё судно на воздушной подушке полно угрей')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    def testGetUpdates(self):
        '''Test the telegram.Bot getUpdates method'''
        print('Testing getUpdates')
        updates = self._bot.getUpdates()

        if updates:
            self.assertTrue(self.is_json(updates[0].to_json()))
            self.assertTrue(isinstance(updates[0], telegram.Update))

    def testForwardMessage(self):
        '''Test the telegram.Bot forwardMessage method'''
        print('Testing forwardMessage')
        message = self._bot.forwardMessage(chat_id=self._chat_id,
                                           from_chat_id=self._chat_id,
                                           message_id=2398)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'teste')
        self.assertEqual(message.forward_from.username, 'leandrotoledo')
        self.assertTrue(isinstance(message.forward_date, datetime))

    def testSendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing sendPhoto - File')
        message = self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                                      caption='testSendPhoto',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 1451)
        self.assertEqual(message.caption, 'testSendPhoto')

    def testResendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing sendPhoto - Resend')
        message = self._bot.sendPhoto(photo='AgADAQADyKcxGx8j9Qdp6d-gpUsw4Gja1i8ABEVJsVqQk8LfJ3wAAgI',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_id, 'AgADAQADyKcxGx8j9Qdp6d-gpUsw4Gja1i8ABEVJsVqQk8LfJ3wAAgI')

    def testSendJPGURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendJPGURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.jpg&text=telegram',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 822)

    def testSendPNGURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendPNGURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.png&text=telegram',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 684)

    def testSendGIFURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendGIFURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 684)

    def testSendChatAction(self):
        '''Test the telegram.Bot sendChatAction method'''
        print('Testing sendChatAction - ChatAction.TYPING')

        self._bot.sendChatAction(action=telegram.ChatAction.TYPING,
                                 chat_id=self._chat_id)

    def testGetUserProfilePhotos(self):
        '''Test the telegram.Bot getUserProfilePhotos method'''
        print('Testing getUserProfilePhotos')
        upf = self._bot.getUserProfilePhotos(user_id=self._chat_id)

        self.assertTrue(self.is_json(upf.to_json()))
        self.assertEqual(upf.photos[0][0].file_size, 12421)

if __name__ == '__main__':
    unittest.main()
