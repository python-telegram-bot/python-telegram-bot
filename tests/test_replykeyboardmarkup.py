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

import pytest
from flaky import flaky

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup


@pytest.fixture(scope='class')
def reply_keyboard_markup():
    return ReplyKeyboardMarkup(
        TestReplyKeyboardMarkup.keyboard,
        resize_keyboard=TestReplyKeyboardMarkup.resize_keyboard,
        one_time_keyboard=TestReplyKeyboardMarkup.one_time_keyboard,
        selective=TestReplyKeyboardMarkup.selective,
    )


class TestReplyKeyboardMarkup:
    keyboard = [[KeyboardButton('button1'), KeyboardButton('button2')]]
    resize_keyboard = True
    one_time_keyboard = True
    selective = True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_with_reply_keyboard_markup(self, bot, chat_id, reply_keyboard_markup):
        message = bot.send_message(chat_id, 'Text', reply_markup=reply_keyboard_markup)

        assert message.text == 'Text'

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_with_data_markup(self, bot, chat_id):
        message = bot.send_message(chat_id, 'text 2', reply_markup={'keyboard': [['1', '2']]})

        assert message.text == 'text 2'

    def test_from_button(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.from_button(
            KeyboardButton(text='button1')
        ).keyboard
        assert len(reply_keyboard_markup) == 1
        assert len(reply_keyboard_markup[0]) == 1

        reply_keyboard_markup = ReplyKeyboardMarkup.from_button('button1').keyboard
        assert len(reply_keyboard_markup) == 1
        assert len(reply_keyboard_markup[0]) == 1

    def test_from_row(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.from_row(
            [KeyboardButton(text='button1'), KeyboardButton(text='button2')]
        ).keyboard
        assert len(reply_keyboard_markup) == 1
        assert len(reply_keyboard_markup[0]) == 2

        reply_keyboard_markup = ReplyKeyboardMarkup.from_row(['button1', 'button2']).keyboard
        assert len(reply_keyboard_markup) == 1
        assert len(reply_keyboard_markup[0]) == 2

    def test_from_column(self):
        reply_keyboard_markup = ReplyKeyboardMarkup.from_column(
            [KeyboardButton(text='button1'), KeyboardButton(text='button2')]
        ).keyboard
        assert len(reply_keyboard_markup) == 2
        assert len(reply_keyboard_markup[0]) == 1
        assert len(reply_keyboard_markup[1]) == 1

        reply_keyboard_markup = ReplyKeyboardMarkup.from_column(['button1', 'button2']).keyboard
        assert len(reply_keyboard_markup) == 2
        assert len(reply_keyboard_markup[0]) == 1
        assert len(reply_keyboard_markup[1]) == 1

    def test_add_button(self):
        reply_keyboard_markup = ReplyKeyboardMarkup().add_button(
            KeyboardButton(text='button1')
        ).keyboard
        assert len(reply_keyboard_markup) == 1
        assert len(reply_keyboard_markup[0]) == 1
        reply_keyboard_markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text='button2'), KeyboardButton(text='button3')],
                [KeyboardButton(text='button4'), KeyboardButton(text='button5')],
                [KeyboardButton(text='button6')]
            ]
        ).add_button(
            KeyboardButton(text='button7')
        ).add_button(
            KeyboardButton(text='button8'), from_row=0, column=1
        ).add_button(
            KeyboardButton(text='button9'), from_row=1, column=-2
        ).add_button(
            KeyboardButton(text='button10'), from_row=2, column=-100
        ).add_button(
            KeyboardButton(text='button11'), column=100
        ).keyboard
        assert len(reply_keyboard_markup) == 3
        assert len(reply_keyboard_markup[0]) == 3
        assert len(reply_keyboard_markup[1]) == 3
        assert len(reply_keyboard_markup[2]) == 4
        assert reply_keyboard_markup[2][2].text == 'button7'
        assert reply_keyboard_markup[0][1].text == 'button8'
        assert reply_keyboard_markup[1][-3].text == 'button9'
        assert reply_keyboard_markup[2][0].text == 'button10'
        assert reply_keyboard_markup[2][-1].text == 'button11'

    def test_add_row(self):
        reply_keyboard_markup = ReplyKeyboardMarkup().add_row().keyboard
        assert len(reply_keyboard_markup) == 2
        assert len(reply_keyboard_markup[0]) == 0
        assert len(reply_keyboard_markup[1]) == 0
        reply_keyboard_markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text='button1'), KeyboardButton(text='button2')],
                [KeyboardButton(text='button3'), KeyboardButton(text='button4')]
            ]
        ).add_row(
            button_row=[KeyboardButton(text='button5')], index=1
        ).keyboard
        assert len(reply_keyboard_markup) == 3
        assert reply_keyboard_markup[1][0].text == 'button5'

    def test_add_from_markup(self):
        reply_keyboard_markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text='button1'), KeyboardButton(text='button2')],
                [KeyboardButton(text='button3')]
            ]
        ).add_from_markup(
            ReplyKeyboardMarkup(
                [
                    [KeyboardButton(text='button4'), KeyboardButton(text='button5')]
                ]
            )
        ).add_from_markup(
            ReplyKeyboardMarkup(
                [
                    [KeyboardButton(text='button6'), KeyboardButton(text='button7')],
                    [KeyboardButton(text='button8')]
                ]
            ),
            index=0
        ).keyboard
        assert len(reply_keyboard_markup) == 5
        assert reply_keyboard_markup[0][0].text == 'button6'
        assert reply_keyboard_markup[-1][0].text == 'button4'

    def test_expected_values(self, reply_keyboard_markup):
        assert isinstance(reply_keyboard_markup.keyboard, list)
        assert isinstance(reply_keyboard_markup.keyboard[0][0], KeyboardButton)
        assert isinstance(reply_keyboard_markup.keyboard[0][1], KeyboardButton)
        assert reply_keyboard_markup.resize_keyboard == self.resize_keyboard
        assert reply_keyboard_markup.one_time_keyboard == self.one_time_keyboard
        assert reply_keyboard_markup.selective == self.selective

    def test_to_dict(self, reply_keyboard_markup):
        reply_keyboard_markup_dict = reply_keyboard_markup.to_dict()

        assert isinstance(reply_keyboard_markup_dict, dict)
        assert (
            reply_keyboard_markup_dict['keyboard'][0][0]
            == reply_keyboard_markup.keyboard[0][0].to_dict()
        )
        assert (
            reply_keyboard_markup_dict['keyboard'][0][1]
            == reply_keyboard_markup.keyboard[0][1].to_dict()
        )
        assert (
            reply_keyboard_markup_dict['resize_keyboard'] == reply_keyboard_markup.resize_keyboard
        )
        assert (
            reply_keyboard_markup_dict['one_time_keyboard']
            == reply_keyboard_markup.one_time_keyboard
        )
        assert reply_keyboard_markup_dict['selective'] == reply_keyboard_markup.selective

    def test_equality(self):
        a = ReplyKeyboardMarkup.from_column(['button1', 'button2', 'button3'])
        b = ReplyKeyboardMarkup.from_column(
            [KeyboardButton(text) for text in ['button1', 'button2', 'button3']]
        )
        c = ReplyKeyboardMarkup.from_column(['button1', 'button2'])
        d = ReplyKeyboardMarkup.from_column(['button1', 'button2', 'button3.1'])
        e = ReplyKeyboardMarkup([['button1', 'button1'], ['button2'], ['button3.1']])
        f = InlineKeyboardMarkup.from_column(['button1', 'button2', 'button3'])

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert a != f
        assert hash(a) != hash(f)
