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
"""This module contains a object that represents a Telegram MessageEntity."""

from telegram import TelegramObject


class MessageEntity(TelegramObject):
    """
    This object represents one special entity in a text message. For example,
    hashtags, usernames, URLs, etc.

    Args:
        type (str):
        offset (int):
        length (int):
        url (Optional[str]):
    """

    def __init__(self, type, offset, length, **kwargs):
        # Required
        self.type = type
        self.offset = offset
        self.length = length
        # Optionals
        self.url = kwargs.get('url')

    @staticmethod
    def de_json(data):
        data = super(MessageEntity, MessageEntity).de_json(data)

        return MessageEntity(**data)

    @staticmethod
    def de_list(data):
        """
        Args:
            data (list):

        Returns:
            List<telegram.MessageEntity>:
        """
        if not data:
            return list()

        entities = list()
        for entity in data:
            entities.append(MessageEntity.de_json(entity))

        return entities
