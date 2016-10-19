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
"""This module contains an object that represents Tests for Telegram Games"""

import sys
import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class GameTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Game."""

    def setUp(self):
        self.title = 'Python-telegram-bot Test Game'
        self.description = 'description'
        self.photo = [{'width': 640, 'height': 360, 'file_id': 'Blah', 'file_size': 0}]
        self.text = 'Other description'
        self.text_entities = [{'offset': 13, 'length': 17, 'type': telegram.MessageEntity.URL}]
        self.animation = {'file_id': 'Blah'}

        self.json_dict = {
            'title': self.title,
            'description': self.description,
            'photo': self.photo,
            'text': self.text,
            'text_entities': self.text_entities,
            'animation': self.animation
        }

    def test_game_de_json(self):
        game = telegram.Game.de_json(self.json_dict, self._bot)

        self.assertEqual(game.title, self.title)
        self.assertEqual(game.description, self.description)
        self.assertTrue(isinstance(game.photo[0], telegram.PhotoSize))
        self.assertEqual(game.text, self.text)
        self.assertTrue(isinstance(game.text_entities[0], telegram.MessageEntity))
        self.assertTrue(isinstance(game.animation, telegram.Animation))

    def test_game_to_json(self):
        game = telegram.Game.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(game.to_json()))

    def test_game_all_args(self):
        game = telegram.Game(
            title=self.title,
            description=self.description,
            photo=self.photo,
            text=self.text,
            text_entities=self.text_entities,
            animation=self.animation)

        self.assertEqual(game.title, self.title)
        self.assertEqual(game.description, self.description)
        self.assertEqual(game.photo, self.photo)
        self.assertEqual(game.text, self.text)
        self.assertEqual(game.text_entities, self.text_entities)
        self.assertEqual(game.animation, self.animation)

    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = telegram.MessageEntity(type=telegram.MessageEntity.URL, offset=13, length=17)
        game = telegram.Game(
            self.title, self.description, self.photo, text=text, text_entities=[entity])
        self.assertEqual(game.parse_text_entity(entity), 'http://google.com')

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = telegram.MessageEntity(type=telegram.MessageEntity.URL, offset=13, length=17)
        entity_2 = telegram.MessageEntity(type=telegram.MessageEntity.BOLD, offset=13, length=1)
        game = telegram.Game(
            self.title, self.description, self.photo, text=text, text_entities=[entity_2, entity])
        self.assertDictEqual(
            game.parse_text_entities(telegram.MessageEntity.URL), {entity: 'http://google.com'})
        self.assertDictEqual(game.parse_text_entities(),
                             {entity: 'http://google.com',
                              entity_2: 'h'})


class AnimationTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Animatiion."""

    def setUp(self):
        self.file_id = 'thisisafileid'
        self.thumb = {'width': 640, 'height': 360, 'file_id': 'Blah', 'file_size': 0}
        self.file_name = 'File name'
        self.mime_type = 'something/gif'
        self.file_size = 42

        self.json_dict = {
            'file_id': self.file_id,
            'thumb': self.thumb,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }

    def test_animation_de_json(self):
        animation = telegram.Animation.de_json(self.json_dict, self._bot)

        self.assertEqual(animation.file_id, self.file_id)
        self.assertTrue(isinstance(animation.thumb, telegram.PhotoSize))
        self.assertEqual(animation.file_name, self.file_name)
        self.assertEqual(animation.mime_type, self.mime_type)
        self.assertEqual(animation.file_size, self.file_size)

    def test_game_to_json(self):
        animation = telegram.Animation.de_json(self.json_dict, self._bot)

        self.assertTrue(self.is_json(animation.to_json()))
