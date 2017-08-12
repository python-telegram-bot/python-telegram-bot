#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
    """
    This object represents a game. Use BotFather to create and edit games, their short names will
    act as unique identifiers.

    Attributes:
        title (:obj:`str`): Title of the game.
        description (:obj:`str`): Description of the game.
        photo (List[:class:`telegram.PhotoSize`]): Photo that will be displayed in the game message
            in chats.
        text (:obj:`str`): Optional. Brief description of the game or high scores included in the
            game message. Can be automatically edited to include current high scores for the game
            when the bot calls set_game_score, or manually edited using edit_message_text.
        text_entities (List[:class:`telegram.MessageEntity`]): Optional. Special entities that
            appear in text, such as usernames, URLs, bot commands, etc.
        animation (:class:`telegram.Animation`): Optional. Animation that will be displayed in the
            game message in chats. Upload via BotFather.

    Args:
        title (:obj:`str`): Title of the game.
        description (:obj:`str`): Description of the game.
        photo (List[:class:`telegram.PhotoSize`]): Photo that will be displayed in the game message
            in chats.
        text (:obj:`str`, optional): Brief description of the game or high scores included in the
            game message. Can be automatically edited to include current high scores for the game
            when the bot calls set_game_score, or manually edited using edit_message_text.
            0-4096 characters. Also found as ``telegram.constants.MAX_MESSAGE_LENGTH``.
        text_entities (List[:class:`telegram.MessageEntity`], optional): Special entities that
            appear in text, such as usernames, URLs, bot commands, etc.
        animation (:class:`telegram.Animation`, optional): Animation that will be displayed in the
            game message in chats. Upload via BotFather.

    """

    def __init__(self,
                 title,
                 description,
                 photo,
                 text=None,
                 text_entities=None,
                 animation=None,
                 **kwargs):
        self.title = title
        self.description = description
        self.photo = photo
        self.text = text
        self.text_entities = text_entities or list()
        self.animation = animation

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Game, cls).de_json(data, bot)

        data['photo'] = PhotoSize.de_list(data.get('photo'), bot)
        data['text_entities'] = MessageEntity.de_list(data.get('text_entities'), bot)
        data['animation'] = Animation.de_json(data.get('animation'), bot)

        return cls(**data)

    def to_dict(self):
        data = super(Game, self).to_dict()

        data['photo'] = [p.to_dict() for p in self.photo]
        if self.text_entities:
            data['text_entities'] = [x.to_dict() for x in self.text_entities]

        return data

    def parse_text_entity(self, entity):
        """Returns the text from a given :class:`telegram.MessageEntity`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to this message.

        Returns:
            :obj:`str`: The text of the given entity.

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
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this message filtered by their ``type`` attribute as the key, and
        the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`text_entities` attribute, since
            it calculates the correct substring from the message text based on UTF-16 codepoints.
            See :attr:`parse_text_entity` for more info.

        Args:
            types (List[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            Dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        """
        if types is None:
            types = MessageEntity.ALL_TYPES

        return {
            entity: self.parse_text_entity(entity)
            for entity in self.text_entities if entity.type in types
        }
