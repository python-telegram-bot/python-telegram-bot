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


import os
import sys
sys.path.append('.')
import json
import telegram
import unittest
from datetime import datetime


class BotTest(unittest.TestCase):
    @staticmethod
    def is_json(string):
        try:
            json.loads(string)
        except ValueError:
            return False
        return True

    def setUp(self):
        bot = telegram.Bot(token=os.environ.get('TOKEN'))
        chat_id = os.environ.get('CHAT_ID')

        self._bot = bot
        self._chat_id = chat_id

        print('Testing the Bot API class')

    def testGetMe(self):
        '''Test the telegram.Bot getMe method'''
        print('Testing getMe')
        bot = self._bot.getMe()

        self.assertTrue(self.is_json(bot.to_json()))
        self.assertEqual(bot.id, 133505823)
        self.assertEqual(bot.first_name, 'Toledo\'s Palace Bot')
        self.assertEqual(bot.last_name, '')
        self.assertEqual(bot.username, 'ToledosPalaceBot')
        self.assertEqual(bot.name, '@ToledosPalaceBot')

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
                                           message_id=138)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Oi')
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
        message = self._bot.sendPhoto(photo='AgADAQADr6cxGzU8LQe6q0dMJD2rHYkP2ykABFymiQqJgjxRGGMAAgI',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_id, 'AgADAQADr6cxGzU8LQe6q0dMJD2rHYkP2ykABFymiQqJgjxRGGMAAgI')

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

    def testSendVoice(self):
        '''Test the telegram.Bot sendVoice method'''
        print('Testing sendVoice - File')
        message = self._bot.sendVoice(voice=open('tests/data/telegram.ogg', 'rb'),
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.voice.file_size, 9199)

    def testResendVoice(self):
        '''Test the telegram.Bot sendVoice method'''
        print('Testing sendVoice - Resend')
        message = self._bot.sendVoice(voice='AwADAQADIQEAAvjAuQABSAXg_GhkhZcC',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.voice.file_id, 'AwADAQADIQEAAvjAuQABSAXg_GhkhZcC')

    def testSendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - File')
        message = self._bot.sendDocument(document=open('tests/data/telegram.png', 'rb'),
                                         chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.document.file_size, 12948)
        self.assertTrue(isinstance(message.document.thumb, telegram.PhotoSize))

    def testSendGIFURLDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - File')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.photo[0].file_size, 684)

    def testResendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - Resend')
        message = self._bot.sendDocument(document='BQADAQADHAADNTwtBxZxUGKyxYbYAg',
                                         chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.document.file_id, 'BQADAQADHAADNTwtBxZxUGKyxYbYAg')
        self.assertTrue(isinstance(message.document.thumb, telegram.PhotoSize))

    def testSendVideo(self):
        '''Test the telegram.Bot sendVideo method'''
        print('Testing sendVideo - File')
        message = self._bot.sendVideo(video=open('tests/data/telegram.mp4', 'rb'),
                                      caption='testSendVideo',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.video.file_size, 326534)
        self.assertEqual(message.caption, 'testSendVideo')
        if message.video.thumb:
            self.assertTrue(isinstance(message.video.thumb, telegram.PhotoSize))

    def testResendVideo(self):
        '''Test the telegram.Bot sendVideo method'''
        print('Testing sendVideo - Resend')
        message = self._bot.sendVideo(video='BAADAQADIgEAAvjAuQABOuTB937fPTgC',
                                      chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.video.duration, 4)
        self.assertTrue(isinstance(message.video.thumb, telegram.PhotoSize))

    def testResendSticker(self):
        '''Test the telegram.Bot sendSticker method'''
        print('Testing sendSticker - Resend')
        message = self._bot.sendSticker(sticker='BQADAQADHAADyIsGAAFZfq1bphjqlgI',
                                        chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.sticker.file_size, 39518)
        self.assertTrue(isinstance(message.sticker.thumb, telegram.PhotoSize))

    def testSendLocation(self):
        '''Test the telegram.Bot sendLocation method'''
        print('Testing sendLocation')
        message = self._bot.sendLocation(latitude=-23.558873,
                                         longitude=-46.659732,
                                         chat_id=self._chat_id)

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.location.latitude, -23.558873)
        self.assertEqual(message.location.longitude, -46.659732)

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
        self.assertEqual(upf.photos[0][0].file_size, 6547)

unittest.main()
