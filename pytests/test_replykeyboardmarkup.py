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

from telegram import ReplyKeyboardMarkup, KeyboardButton

@pytest.fixture(scope='class')
def json_dict():
    return {
            'keyboard': [[TestReplyKeyboardMarkup.keyboard[0][0].to_dict(), TestReplyKeyboardMarkup.keyboard[0][1].to_dict()]],
            'resize_keyboard': TestReplyKeyboardMarkup.resize_keyboard,
            'one_time_keyboard': TestReplyKeyboardMarkup.one_time_keyboard,
            'selective': TestReplyKeyboardMarkup.selective,
        }

@pytest.fixture(scope='class')
def reply_keyboard_markup():
   return ReplyKeyboardMarkup(keyboard=[[TestReplyKeyboardMarkup.keyboard[0][0], resize_keyboard=TestReplyKeyboardMarkup.resize_keyboard, one_time_keyboard=TestReplyKeyboardMarkup.one_time_keyboard, selective=TestReplyKeyboardMarkup.selective)

class TestReplyKeyboardMarkup:
    """This object represents Tests for Telegram ReplyKeyboardMarkup."""

    keyboard = [[KeyboardButton('button1'), KeyboardButton('button2')]]
    resize_keyboard = True
    one_time_keyboard = True
    selective = True
    
    
    
    def test_send_message_with_reply_keyboard_markup(self):
        message = bot.sendMessage(
            chat_id,
            'Моё судно на воздушной подушке полно угрей',
            reply_markup=ReplyKeyboardMarkup.de_json(json_dict, bot))

        json.loads(message.to_json())
        assert message.text == u'Моё судно на воздушной подушке полно угрей'

    def test_reply_markup_empty_de_json_empty(self):
        reply_markup_empty = ReplyKeyboardMarkup.de_json(None, bot)

        assert reply_markup_empty is False

    def test_de_json(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.de_json(json_dict, bot)

        assert isinstance(reply_keyboard_markup.keyboard, list)
        assert isinstance(reply_keyboard_markup.keyboard[0][0], KeyboardButton)
        assert reply_keyboard_markup.resize_keyboard == self.resize_keyboard
        assert reply_keyboard_markup.one_time_keyboard == self.one_time_keyboard
        assert reply_keyboard_markup.selective == self.selective

    def test_to_json(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.de_json(json_dict, bot)

        json.loads(reply_keyboard_markup.to_json())

    def test_to_dict(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.de_json(json_dict, bot)

        assert isinstance(reply_keyboard_markup.keyboard, list)
        assert isinstance(reply_keyboard_markup.keyboard[0][0], KeyboardButton)
        assert reply_keyboard_markup['resize_keyboard'] == self.resize_keyboard
        assert reply_keyboard_markup['one_time_keyboard'] == self.one_time_keyboard
        assert reply_keyboard_markup['selective'] == self.selective


