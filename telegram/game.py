#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents a Telegram Game."""

import sys

from telegram import MessageEntity, TelegramObject, Animation, PhotoSize


class Game(TelegramObject):
    """This object represents a Telegram Game.

    Attributes:
        title (str): Title of the game.
        description (str): Description of the game.
        photo (list[:class:`telegram.PhotoSize`]): List of photos that will be displayed in the
            game message in chats.

    Keyword Args:
        text (Optional[str]): Brief description of the game or high scores included in the game
            message. Can be automatically edited to include current high scores for the game when
            the bot calls setGameScore, or manually edited using editMessageText.
            0-4096 characters.
        text_entities (Optional[list[:class:`telegram.MessageEntity`]]): Special entities that
            appear in text, such as usernames, URLs, bot commands, etc.
        animation (Optional[:class:`telegram.Animation`]): Animation that will be displayed in the
            game message in chats. Upload via BotFather.

    """

    def __init__(self,
                 title,
                 description,
                 photo,
                 text='',
                 text_entities=None,
                 animation=None,
                 **kwargs):
        self.title = title
        self.description = description
        self.photo = photo
        self.text = text
        self.text_entities = text_entities
        self.animation = animation

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Game:

        """
        if not data:
            return None

        data['photo'] = PhotoSize.de_list(data.get('photo'), bot)
        data['text_entities'] = MessageEntity.de_list(data.get('text_entities'), bot)
        data['animation'] = Animation.de_json(data.get('animation'), bot)

        return Game(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(Game, self).to_dict()

        data['photo'] = [p.to_dict() for p in self.photo]
        data['text_entities'] = [x.to_dict() for x in self.text_entities]

        return data

    def parse_text_entity(self, entity):
        """
        Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (MessageEntity): The entity to extract the text from. It must be an entity that
                belongs to this message.

        Returns:
            str: The text of the given entity
        """
        # Is it a narrow build, if so we don't need to convert
        if sys.maxunicode == 0xffff:
            return self.text[entity.offset:entity.offset + entity.length]
        else:
            entity_text = self.text.encode('utf-16-le')
            entity_text = entity_text[entity.offset * 2:(entity.offset + entity.length) * 2]

        return entity_text.decode('utf-16-le')

    def parse_text_entities(self, types=None):
        """
        Returns a ``dict`` that maps :class:`telegram.MessageEntity` to ``str``.
        It contains entities from this message filtered by their ``type`` attribute as the key, and
        the text that each entity belongs to as the value of the ``dict``.

        Note:
            This method should always be used instead of the ``entities`` attribute, since it
            calculates the correct substring from the message text based on UTF-16 codepoints.
            See ``get_entity_text`` for more info.

        Args:
            types (Optional[list]): List of ``MessageEntity`` types as strings. If the ``type``
                attribute of an entity is contained in this list, it will be returned.
                Defaults to a list of all types. All types can be found as constants in
                :class:`telegram.MessageEntity`.

        Returns:
            dict[:class:`telegram.MessageEntity`, ``str``]: A dictionary of entities mapped to the
                text that belongs to them, calculated based on UTF-16 codepoints.
        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_text_entity(entity)
            for entity in self.text_entities if entity.type in types
        }
