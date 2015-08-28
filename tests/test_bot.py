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
        self._bot = bot
        print('Testing the Bot API class')

    def testGetMe(self):
        '''Test the telegram.Bot getMe method'''
        print('Testing getMe')
        bot = self._bot.getMe()
        self.assertTrue(self.is_json(bot.to_json()))
        self.assertEqual(120405045, bot.id)
        self.assertEqual('Toledo\'s Palace Bot', bot.first_name)
        self.assertEqual(None, bot.last_name)
        self.assertEqual('ToledosPalaceBot', bot.username)

    def testSendMessage(self):
        '''Test the telegram.Bot sendMessage method'''
        print('Testing sendMessage')
        message = self._bot.sendMessage(chat_id=12173560,
                                        text='Моё судно на воздушной подушке полно угрей')
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(u'Моё судно на воздушной подушке полно угрей', message.text)
        self.assertIsInstance(message.date, datetime)

    def testGetUpdates(self):
        '''Test the telegram.Bot getUpdates method'''
        print('Testing getUpdates')
        updates = self._bot.getUpdates()
        if updates:
            self.assertTrue(self.is_json(updates[0].to_json()))
            self.assertIsInstance(updates[0], telegram.Update)

    def testForwardMessage(self):
        '''Test the telegram.Bot forwardMessage method'''
        print('Testing forwardMessage')
        message = self._bot.forwardMessage(chat_id=12173560,
                                           from_chat_id=12173560,
                                           message_id=138)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual('Oi', message.text)
        self.assertEqual('leandrotoledo', message.forward_from.username)
        self.assertIsInstance(message.forward_date, datetime)

    def testSendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing sendPhoto - File')
        message = self._bot.sendPhoto(photo=open('tests/data/telegram.png', 'rb'),
                                      caption='testSendPhoto',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(1451, message.photo[0].file_size)
        self.assertEqual('testSendPhoto', message.caption)

    def testResendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing sendPhoto - Resend')
        message = self._bot.sendPhoto(photo='AgADAQADr6cxGzU8LQe6q0dMJD2rHYkP2ykABFymiQqJgjxRGGMAAgI',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual('AgADAQADr6cxGzU8LQe6q0dMJD2rHYkP2ykABFymiQqJgjxRGGMAAgI', message.photo[0].file_id)

    def testSendJPGURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendJPGURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.jpg&text=telegram',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(822, message.photo[0].file_size)

    def testSendPNGURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendPNGURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.png&text=telegram',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(684, message.photo[0].file_size)

    def testSendGIFURLPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print('Testing testSendGIFURLPhoto - URL')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(684, message.photo[0].file_size)

    def testSendAudio(self):
        '''Test the telegram.Bot sendAudio method'''
        print('Testing sendAudio - File')
        message = self._bot.sendAudio(audio=open('tests/data/telegram.mp3', 'rb'),
                                      chat_id=12173560,
                                      performer='Leandro Toledo',
                                      title='Teste')
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(28232, message.audio.file_size)
        self.assertEqual('Leandro Toledo', message.audio.performer)
        self.assertEqual('Teste', message.audio.title)

    def testResendAudio(self):
        '''Test the telegram.Bot sendAudio method'''
        print('Testing sendAudio - Resend')
        message = self._bot.sendAudio(audio='BQADAQADwwcAAjU8LQdBRsl3_qD2TAI',
                                      chat_id=12173560,
                                      performer='Leandro Toledo',   # Bug #39
                                      title='Teste')                # Bug #39
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual('BQADAQADwwcAAjU8LQdBRsl3_qD2TAI', message.audio.file_id)

    def testSendVoice(self):
        '''Test the telegram.Bot sendVoice method'''
        print('Testing sendVoice - File')
        message = self._bot.sendVoice(voice=open('tests/data/telegram.ogg', 'rb'),
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(9199, message.voice.file_size)

    def testResendVoice(self):
        '''Test the telegram.Bot sendVoice method'''
        print('Testing sendVoice - Resend')
        message = self._bot.sendVoice(voice='AwADAQADIQEAAvjAuQABSAXg_GhkhZcC',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual('AwADAQADIQEAAvjAuQABSAXg_GhkhZcC', message.voice.file_id)

    def testSendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - File')
        message = self._bot.sendDocument(document=open('tests/data/telegram.png', 'rb'),
                                         chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(12948, message.document.file_size)

    def testSendGIFURLDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - File')
        message = self._bot.sendPhoto(photo='http://dummyimage.com/600x400/000/fff.gif&text=telegram',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(684, message.photo[0].file_size)

    def testResendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print('Testing sendDocument - Resend')
        message = self._bot.sendDocument(document='BQADAQADHAADNTwtBxZxUGKyxYbYAg',
                                         chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual('BQADAQADHAADNTwtBxZxUGKyxYbYAg', message.document.file_id)

    def testSendVideo(self):
        '''Test the telegram.Bot sendVideo method'''
        print('Testing sendVideo - File')
        message = self._bot.sendVideo(video=open('tests/data/telegram.mp4', 'rb'),
                                      caption='testSendVideo',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(326534, message.video.file_size)
        self.assertEqual('testSendVideo', message.caption)

    def testResendVideo(self):
        '''Test the telegram.Bot sendVideo method'''
        print('Testing sendVideo - Resend')
        message = self._bot.sendVideo(video='BAADAQADIgEAAvjAuQABOuTB937fPTgC',
                                      chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(4, message.video.duration)

    def testResendSticker(self):
        '''Test the telegram.Bot sendSticker method'''
        print('Testing sendSticker - Resend')
        message = self._bot.sendSticker(sticker='BQADAQADHAADyIsGAAFZfq1bphjqlgI',
                                        chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(39518, message.sticker.file_size)

    def testSendLocation(self):
        '''Test the telegram.Bot sendLocation method'''
        print('Testing sendLocation')
        message = self._bot.sendLocation(latitude=-23.558873,
                                         longitude=-46.659732,
                                         chat_id=12173560)
        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(-23.558873, message.location.latitude)
        self.assertEqual(-46.659732, message.location.longitude)

    def testSendChatAction(self):
        '''Test the telegram.Bot sendChatAction method'''
        print('Testing sendChatAction - ChatAction.TYPING')
        self._bot.sendChatAction(action=telegram.ChatAction.TYPING,
                                 chat_id=12173560)

    def testGetUserProfilePhotos(self):
        '''Test the telegram.Bot getUserProfilePhotos method'''
        print('Testing getUserProfilePhotos')
        upf = self._bot.getUserProfilePhotos(user_id=12173560)
        self.assertTrue(self.is_json(upf.to_json()))
        self.assertEqual(6547, upf.photos[0][0].file_size)

unittest.main()
