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
import json

import pytest

from telegram import


@pytest.fixture(scope='class')
def json_dict():
    return {
        'text': TestInlineKeyboardButton.text,
        'url': TestInlineKeyboardButton.url,
        'callback_data': TestInlineKeyboardButton.callback_data,
        'switch_inline_query': TestInlineKeyboardButton.switch_inline_query
    }


class TestInlineKeyboardButton:
    """This object represents Tests for Telegram KeyboardButton."""

    text = 'text'
    url = 'url'
    callback_data = 'callback data'
    switch_inline_query = ''

    def test_inline_keyboard_button_de_json(self):
        inline_keyboard_button = InlineKeyboardButton.de_json(json_dict, bot)

        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query

    def test_inline_keyboard_button_de_json_empty(self):
        inline_keyboard_button = InlineKeyboardButton.de_json(None, bot)

        assert inline_keyboard_button is False

    def test_inline_keyboard_button_de_list_empty(self):
        inline_keyboard_button = InlineKeyboardButton.de_list(None, bot)

        assert inline_keyboard_button is False

    def test_inline_keyboard_button_to_json(self):
        inline_keyboard_button = InlineKeyboardButton.de_json(json_dict, bot)

        json.loads(inline_keyboard_button.to_json())

    def test_inline_keyboard_button_to_dict(self):
        inline_keyboard_button = InlineKeyboardButton.de_json(json_dict,
                                                              bot).to_dict()

        assert isinstance(inline_keyboard_button, dict)
        assert json_dict == inline_keyboard_button
