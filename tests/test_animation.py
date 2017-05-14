#!/usr/bin/env python
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
"""This module contains an object that represents Tests for Telegram Animation"""

import unittest
import sys

sys.path.append('.')

import telegram
from tests.base import BaseTest


class AnimationTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Animation."""

    def setUp(self):
        self.animation_file_id = 'CgADBAADFQEAAny4rAUgukhiTv2TWwI'
        self.thumb = telegram.PhotoSize.de_json({
            'height': 50,
            'file_size': 1613,
            'file_id': 'AAQEABPQUWQZAAT7gZuQAAH0bd93VwACAg',
            'width': 90
        }, self._bot)
        self.file_name = "game.gif.mp4"
        self.mime_type = "video/mp4"
        self.file_size = 4008

        self.json_dict = {
            'file_id': self.animation_file_id,
            'thumb': self.thumb.to_dict(),
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    def test_animation_de_json(self):
        animation = telegram.Animation.de_json(self.json_dict, self._bot)

        self.assertEqual(animation.file_id, self.animation_file_id)
        self.assertEqual(animation.thumb, self.thumb)
        self.assertEqual(animation.file_name, self.file_name)
        self.assertEqual(animation.mime_type, self.mime_type)
        self.assertEqual(animation.file_size, self.file_size)

    def test_animation_to_json(self):
        animation = telegram.Animation.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(animation.to_json()))

    def test_animation_to_dict(self):
        animation = telegram.Animation.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_dict(animation.to_dict()))
        self.assertEqual(animation['file_id'], self.animation_file_id)
        self.assertEqual(animation['thumb'], self.thumb)
        self.assertEqual(animation['file_name'], self.file_name)
        self.assertEqual(animation['mime_type'], self.mime_type)
        self.assertEqual(animation['file_size'], self.file_size)

    def test_equality(self):
        a = telegram.Animation(self.animation_file_id)
        b = telegram.Animation(self.animation_file_id)
        d = telegram.Animation("")
        e = telegram.Voice(self.animation_file_id, 0)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertIsNot(a, b)

        self.assertNotEqual(a, d)
        self.assertNotEqual(hash(a), hash(d))

        self.assertNotEqual(a, e)
        self.assertNotEqual(hash(a), hash(e))
