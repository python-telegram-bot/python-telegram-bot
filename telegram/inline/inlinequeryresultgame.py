#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""This module contains the classes that represent Telegram InlineQueryResultGame."""

from telegram import InlineQueryResult


class InlineQueryResultGame(InlineQueryResult):
    """Represents a Game.

    Attributes:
        type (:obj:`str`): 'game'.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        game_short_name (:obj:`str`): Short name of the game.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        game_short_name (:obj:`str`): Short name of the game.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, id, game_short_name, reply_markup=None, **kwargs):
        # Required
        super(InlineQueryResultGame, self).__init__('game', id)
        self.id = id
        self.game_short_name = game_short_name

        self.reply_markup = reply_markup
