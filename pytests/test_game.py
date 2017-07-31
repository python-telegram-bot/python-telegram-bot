#!/usr/bin/env python
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
import pytest

from telegram import

class GameTest:
    """This object represents Tests for Telegram Game."""

    def setUp(self):
        self.title = 'Python-telegram-bot Test Game'
        self.description = 'description'
        self.photo = [{'width': 640, 'height': 360, 'file_id': 'Blah', 'file_size': 0}]
        self.text = 'Other description'
        self.text_entities = [{'offset': 13, 'length': 17, 'type': MessageEntity.URL}]
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
        game = Game.de_json(self.json_dict, self._bot)

        assert game.title == self.title
        assert game.description == self.description
        assert isinstance(game.photo[0], PhotoSize) is True
        assert game.text == self.text
        assert isinstance(game.text_entities[0], MessageEntity) is True
        assert isinstance(game.animation, Animation) is True

    def test_game_to_json(self):
        game = Game.de_json(self.json_dict, self._bot)

        json.loads(game.to_json())

    def test_game_all_args(self):
        game = Game(
            title=self.title,
            description=self.description,
            photo=self.photo,
            text=self.text,
            text_entities=self.text_entities,
            animation=self.animation)

        assert game.title == self.title
        assert game.description == self.description
        assert game.photo == self.photo
        assert game.text == self.text
        assert game.text_entities == self.text_entities
        assert game.animation == self.animation

    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        game = Game(
            self.title, self.description, self.photo, text=text, text_entities=[entity])
        assert game.parse_text_entity(entity) == 'http://google.com'

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        game = Game(
            self.title, self.description, self.photo, text=text, text_entities=[entity_2, entity])
        self.assertDictEqual(
            game.parse_text_entities(MessageEntity.URL), {entity: 'http://google.com'})
        self.assertDictEqual(game.parse_text_entities(),
                             {entity: 'http://google.com',
                              entity_2: 'h'})
