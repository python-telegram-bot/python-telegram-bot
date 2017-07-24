#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""This module contains an object that represents Tests for Telegram Sticker"""

import os
import unittest

from flaky import flaky
from future.utils import PY2

import telegram
from tests.base import BaseTest, timeout
from tests.bots import get_bot


class StickerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Sticker."""

    @classmethod
    def setUpClass(cls):
        cls.emoji = '💪'
        # cls.sticker_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.webp"
        # Serving sticker from gh since our server sends wrong content_type
        cls.sticker_file_url = "https://github.com/python-telegram-bot/python-telegram-bot/blob/master/tests/data/telegram.webp?raw=true"  # noqa

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = telegram.Bot(bot_info['token'])

        sticker_file = open('tests/data/telegram.webp', 'rb')
        sticker = cls._bot.send_sticker(cls._chat_id, sticker=sticker_file, timeout=10).sticker
        cls.sticker = sticker
        cls.thumb = sticker.thumb

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.sticker, telegram.Sticker)
        assert isinstance(cls.sticker.file_id, str)
        assert cls.sticker.file_id is not ''
        assert isinstance(cls.thumb, telegram.PhotoSize)
        assert isinstance(cls.thumb.file_id, str)
        assert cls.thumb.file_id is not ''

    def setUp(self):
        self.sticker_file = open('tests/data/telegram.webp', 'rb')
        self.json_dict = {
            'file_id': self.sticker.file_id,
            'width': self.sticker.width,
            'height': self.sticker.height,
            'thumb': self.thumb.to_dict(),
            'emoji': self.emoji,
            'file_size': self.sticker.file_size
        }

    def test_expected_values(self):
        self.assertEqual(self.sticker.width, 510)
        self.assertEqual(self.sticker.height, 512)
        self.assertEqual(self.sticker.file_size, 39518)
        self.assertEqual(self.thumb.width, 90)
        self.assertEqual(self.thumb.height, 90)
        self.assertEqual(self.thumb.file_size, 3672)

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_all_args(self):
        message = self._bot.sendSticker(chat_id=self._chat_id, sticker=self.sticker.file_id, disable_notification=False)
        sticker = message.sticker

        self.assertEqual(sticker, self.sticker)

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_sticker(self):
        new_file = self._bot.getFile(self.sticker.file_id)

        self.assertEqual(new_file.file_size, self.sticker.file_size)
        self.assertEqual(new_file.file_id, self.sticker.file_id)
        self.assertTrue(new_file.file_path.startswith('https://'))

        new_file.download('telegram.webp')

        self.assertTrue(os.path.isfile('telegram.webp'))

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_resend(self):
        message = self._bot.sendSticker(chat_id=self._chat_id, sticker=self.sticker.file_id)

        sticker = message.sticker

        self.assertEqual(sticker.file_id, self.sticker.file_id)
        self.assertEqual(sticker.width, self.sticker.width)
        self.assertEqual(sticker.height, self.sticker.height)
        self.assertIsInstance(sticker.thumb, telegram.PhotoSize)
        self.assertEqual(sticker.file_size, self.sticker.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_sticker_on_server_emoji(self):
        server_file_id = "CAADAQADHAADyIsGAAFZfq1bphjqlgI"
        message = self._bot.sendSticker(chat_id=self._chat_id, sticker=server_file_id)
        sticker = message.sticker
        if PY2:
            self.assertEqual(sticker.emoji, self.emoji.decode('utf-8'))
        else:
            self.assertEqual(sticker.emoji, self.emoji)

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_from_url(self):
        message = self._bot.sendSticker(chat_id=self._chat_id, sticker=self.sticker_file_url)
        sticker = message.sticker

        self.assertIsInstance(sticker, telegram.Sticker)
        self.assertIsInstance(sticker.file_id, str)
        self.assertNotEqual(sticker.file_id, '')
        self.assertEqual(sticker.file_size, self.sticker.file_size)
        self.assertEqual(sticker.height, self.sticker.height)
        self.assertEqual(sticker.width, self.sticker.width)
        thumb = sticker.thumb
        self.assertIsInstance(thumb, telegram.PhotoSize)
        self.assertIsInstance(thumb.file_id, str)
        self.assertNotEqual(thumb.file_id, '')
        self.assertEqual(thumb.file_size, self.thumb.file_size)
        self.assertEqual(thumb.width, self.thumb.width)
        self.assertEqual(thumb.height, self.thumb.height)

    def test_sticker_de_json(self):
        sticker = telegram.Sticker.de_json(self.json_dict, self._bot)

        self.assertEqual(sticker.file_id, self.sticker.file_id)
        self.assertEqual(sticker.width, self.sticker.width)
        self.assertEqual(sticker.height, self.sticker.height)
        self.assertIsInstance(sticker.thumb, telegram.PhotoSize)
        self.assertEqual(sticker.emoji, self.emoji)
        self.assertEqual(sticker.file_size, self.sticker.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_send_sticker_with_sticker(self):
        message = self._bot.send_sticker(sticker=self.sticker, chat_id=self._chat_id)
        sticker = message.sticker

        self.assertEqual(sticker, self.sticker)


    def test_sticker_to_json(self):
        self.assertTrue(self.is_json(self.sticker.to_json()))

    def test_sticker_to_dict(self):
        sticker = self.sticker.to_dict()

        self.is_dict(sticker)
        self.assertEqual(sticker['file_id'], self.sticker.file_id)
        self.assertEqual(sticker['width'], self.sticker.width)
        self.assertEqual(sticker['height'], self.sticker.height)
        self.assertIsInstance(sticker['thumb'], dict)
        self.assertEqual(sticker['file_size'], self.sticker.file_size)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_sticker_empty_file(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['sticker'] = open(os.devnull, 'rb')

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendSticker(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_sticker_empty_file_id(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])
        json_dict['sticker'] = ''

        with self.assertRaises(telegram.TelegramError):
            self._bot.sendSticker(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_sticker_without_required_args(self):
        json_dict = self.json_dict

        del (json_dict['file_id'])

        with self.assertRaises(TypeError):
            self._bot.sendSticker(chat_id=self._chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_sticker(self):
        """Test for Message.reply_sticker"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_sticker(self.sticker.file_id)

        self.assertNotEqual(message.sticker.file_id, '')

    def test_equality(self):
        a = telegram.Sticker(self.sticker.file_id, self.sticker.width, self.sticker.height)
        b = telegram.Sticker(self.sticker.file_id, self.sticker.width, self.sticker.height)
        c = telegram.Sticker(self.sticker.file_id, 0, 0)
        d = telegram.Sticker("", self.sticker.width, self.sticker.height)
        e = telegram.PhotoSize(self.sticker.file_id, self.sticker.width, self.sticker.height)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertEqual(a, c)
        self.assertEqual(hash(a), hash(c))

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))


class TestStickerSet(BaseTest, unittest.TestCase):
    # TODO: Implement bot tests for StickerSet
    # It's hard to test creation when we can't delete sticker sets
    def setUp(self):
        self.name = 'test_by_{0}'.format(self._bot.username)
        self.title = 'Test stickers'
        self.contains_masks = False
        self.stickers = [telegram.Sticker('file_id', 512, 512)]

        self.json_dict = {
            'name': self.name,
            'title': self.title,
            'contains_masks': self.contains_masks,
            'stickers': [x.to_dict() for x in self.stickers]
        }

    def test_sticker_set_de_json(self):
        sticker_set = telegram.StickerSet.de_json(self.json_dict, self._bot)

        self.assertEqual(sticker_set.name, self.name)
        self.assertEqual(sticker_set.title, self.title)
        self.assertEqual(sticker_set.contains_masks, self.contains_masks)
        self.assertEqual(sticker_set.stickers, self.stickers)

    def test_sticker_set_to_json(self):
        sticker_set = telegram.StickerSet.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(sticker_set.to_json()))

    def test_sticker_set_to_dict(self):
        sticker_set = telegram.StickerSet.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(sticker_set))
        self.assertDictEqual(self.json_dict, sticker_set)

    def test_equality(self):
        a = telegram.StickerSet(self.name, self.title, self.contains_masks, self.stickers)
        b = telegram.StickerSet(self.name, self.title, self.contains_masks, self.stickers)
        c = telegram.StickerSet(self.name, None, None, None)
        d = telegram.StickerSet('blah', self.title, self.contains_masks, self.stickers)
        e = telegram.Audio(self.name, 0, None, None)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertEqual(a, c)
        self.assertEqual(hash(a), hash(c))

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))


class TestMaskPosition(BaseTest, unittest.TestCase):
    def setUp(self):
        self.point = telegram.MaskPosition.EYES
        self.x_shift = -1
        self.y_shift = 1
        self.scale = 2

        self.json_dict = {
            'point': self.point,
            'x_shift': self.x_shift,
            'y_shift': self.y_shift,
            'scale': self.scale
        }

    def test_mask_position_de_json(self):
        mask_position = telegram.MaskPosition.de_json(self.json_dict, self._bot)

        self.assertEqual(mask_position.point, self.point)
        self.assertEqual(mask_position.x_shift, self.x_shift)
        self.assertEqual(mask_position.y_shift, self.y_shift)
        self.assertEqual(mask_position.scale, self.scale)

    def test_mask_positiont_to_json(self):
        mask_position = telegram.MaskPosition.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(mask_position.to_json()))

    def test_mask_position_to_dict(self):
        mask_position = telegram.MaskPosition.de_json(self.json_dict, self._bot).to_dict()

        self.assertTrue(self.is_dict(mask_position))
        self.assertDictEqual(self.json_dict, mask_position)


if __name__ == '__main__':
    unittest.main()
