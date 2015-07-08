#!/usr/bin/env python
# encoding: utf-8

import os
import telegram
import unittest


@unittest.skipIf(not os.environ.get('TOKEN'), "No tokens provided")
class BotTest(unittest.TestCase):
    def setUp(self):
        bot = telegram.Bot(token=os.environ.get('TOKEN'))
        self._bot = bot
        print 'Testing the Bot API class'

    def testGetMe(self):
        '''Test the telegram.Bot getMe method'''
        print 'Testing getMe'
        user = self._bot.getMe()
        self.assertEqual(120405045, user.id)
        self.assertEqual('Toledo\'s Palace Bot', user.first_name)
        self.assertEqual(None, user.last_name)
        self.assertEqual('ToledosPalaceBot', user.username)

    def testSendMessage(self):
        '''Test the telegram.Bot sendMessage method'''
        print 'Testing sendMessage'
        message = self._bot.sendMessage(chat_id=12173560,
                                        text=u'Моё судно на воздушной подушке полно угрей'.encode('utf8'))
        self.assertEqual(u'Моё судно на воздушной подушке полно угрей', message.text)

    def testGetUpdates(self):
        '''Test the telegram.Bot getUpdates method'''
        print 'Testing getUpdates'
        updates = self._bot.getUpdates()
        self.assertEqual(129566520, updates[0].update_id)

    def testForwardMessage(self):
        '''Test the telegram.Bot forwardMessage method'''
        print 'Testing forwardMessage'
        message = self._bot.forwardMessage(chat_id=12173560,
                                           from_chat_id=12173560,
                                           message_id=138)
        self.assertEqual(u'Oi', message.text)
        self.assertEqual(u'leandrotoledo', message.forward_from.username)

    def testSendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print 'Testing sendPhoto - File'
        message = self._bot.sendPhoto(photo=open('tests/telegram.png', 'rb'),
                                      chat_id=12173560)
        self.assertEqual(12948, message.photo[2].file_size)

    def testResendPhoto(self):
        '''Test the telegram.Bot sendPhoto method'''
        print 'Testing sendPhoto - Resend'
        message = self._bot.sendPhoto(photo=str('AgAD_v___6-nMRs1PC0HuqtHTCQ9qx0AFAI'),
                                      chat_id=12173560)
        self.assertEqual(u'AgAD_v___6-nMRs1PC0HuqtHTCQ9qx0AFAI', message.photo[2].file_id)

    def testSendAudio(self):
        '''Test the telegram.Bot sendAudio method'''
        print 'Testing sendAudio - File'
        message = self._bot.sendAudio(audio=open('tests/telegram.ogg', 'rb'),
                                      chat_id=12173560)
        self.assertEqual(9199, message.audio.file_size)

    def testResendAudio(self):
        '''Test the telegram.Bot sendAudio method'''
        print 'Testing sendAudio - Resend'
        message = self._bot.sendAudio(audio=str('AwADAQADIQEAAvjAuQABSAXg_GhkhZcC'),
                                      chat_id=12173560)
        self.assertEqual(u'AwADAQADIQEAAvjAuQABSAXg_GhkhZcC', message.audio.file_id)

    def testSendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print 'Testing sendDocument - File'
        message = self._bot.sendDocument(document=open('tests/telegram.png', 'rb'),
                                         chat_id=12173560)
        self.assertEqual(12948, message.document.file_size)

    def testResendDocument(self):
        '''Test the telegram.Bot sendDocument method'''
        print 'Testing sendDocument - Resend'
        message = self._bot.sendDocument(document=str('BQADAQADHAADNTwtBxZxUGKyxYbYAg'),
                                         chat_id=12173560)
        self.assertEqual(u'BQADAQADHAADNTwtBxZxUGKyxYbYAg', message.document.file_id)

    def testResendSticker(self):
        '''Test the telegram.Bot sendSticker method'''
        print 'Testing sendSticker - Resend'
        message = self._bot.sendSticker(sticker=str('BQADAQADHAADyIsGAAFZfq1bphjqlgI'),
                                        chat_id=12173560)
        self.assertEqual(39518, message.sticker.file_size)

    def testResendVideo(self):
        '''Test the telegram.Bot sendVideo method'''
        print 'Testing sendVideo - Resend'
        message = self._bot.sendVideo(video=str('BAADAQADIgEAAvjAuQABOuTB937fPTgC'),
                                      chat_id=12173560)
        self.assertEqual(4, message.video.duration)

    def testSendLocation(self):
        '''Test the telegram.Bot sendLocation method'''
        print 'Testing sendLocation'
        message = self._bot.sendLocation(latitude=-23.558873,
                                         longitude=-46.659732,
                                         chat_id=12173560)
        self.assertEqual(-23.558873, message.location.latitude)
        self.assertEqual(-46.659732, message.location.longitude)
