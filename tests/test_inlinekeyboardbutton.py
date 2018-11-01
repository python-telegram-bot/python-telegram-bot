#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import pytest

from telegram import InlineKeyboardButton


@pytest.fixture(scope='class')
def inline_keyboard_button():
    return InlineKeyboardButton(TestInlineKeyboardButton.text,
                                url=TestInlineKeyboardButton.url,
                                callback_data=TestInlineKeyboardButton.callback_data,
                                switch_inline_query=TestInlineKeyboardButton.switch_inline_query,
                                switch_inline_query_current_chat=TestInlineKeyboardButton
                                .switch_inline_query_current_chat,
                                callback_game=TestInlineKeyboardButton.callback_game,
                                pay=TestInlineKeyboardButton.pay)


class TestInlineKeyboardButton(object):
    text = 'text'
    url = 'url'
    callback_data = 'callback data'
    switch_inline_query = 'switch_inline_query'
    switch_inline_query_current_chat = 'switch_inline_query_current_chat'
    callback_game = 'callback_game'
    pay = 'pay'

    def test_expected_values(self, inline_keyboard_button):
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query
        assert (inline_keyboard_button.switch_inline_query_current_chat
                == self.switch_inline_query_current_chat)
        assert inline_keyboard_button.callback_game == self.callback_game
        assert inline_keyboard_button.pay == self.pay

    def test_to_dict(self, inline_keyboard_button):
        inline_keyboard_button_dict = inline_keyboard_button.to_dict()

        assert isinstance(inline_keyboard_button_dict, dict)
        assert inline_keyboard_button_dict['text'] == inline_keyboard_button.text
        assert inline_keyboard_button_dict['url'] == inline_keyboard_button.url
        assert inline_keyboard_button_dict['callback_data'] == inline_keyboard_button.callback_data
        assert (inline_keyboard_button_dict['switch_inline_query']
                == inline_keyboard_button.switch_inline_query)
        assert (inline_keyboard_button_dict['switch_inline_query_current_chat']
                == inline_keyboard_button.switch_inline_query_current_chat)
        assert inline_keyboard_button_dict['callback_game'] == inline_keyboard_button.callback_game
        assert inline_keyboard_button_dict['pay'] == inline_keyboard_button.pay
