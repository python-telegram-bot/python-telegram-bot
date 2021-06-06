#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import InlineKeyboardButton, LoginUrl


@pytest.fixture(scope='class')
def inline_keyboard_button():
    return InlineKeyboardButton(
        TestInlineKeyboardButton.text,
        url=TestInlineKeyboardButton.url,
        callback_data=TestInlineKeyboardButton.callback_data,
        switch_inline_query=TestInlineKeyboardButton.switch_inline_query,
        switch_inline_query_current_chat=TestInlineKeyboardButton.switch_inline_query_current_chat,
        callback_game=TestInlineKeyboardButton.callback_game,
        pay=TestInlineKeyboardButton.pay,
        login_url=TestInlineKeyboardButton.login_url,
    )


class TestInlineKeyboardButton:
    text = 'text'
    url = 'url'
    callback_data = 'callback data'
    switch_inline_query = 'switch_inline_query'
    switch_inline_query_current_chat = 'switch_inline_query_current_chat'
    callback_game = 'callback_game'
    pay = 'pay'
    login_url = LoginUrl("http://google.com")

    def test_slot_behaviour(self, inline_keyboard_button, recwarn, mro_slots):
        inst = inline_keyboard_button
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.text = 'should give warning', self.text
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_expected_values(self, inline_keyboard_button):
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query
        assert (
            inline_keyboard_button.switch_inline_query_current_chat
            == self.switch_inline_query_current_chat
        )
        assert inline_keyboard_button.callback_game == self.callback_game
        assert inline_keyboard_button.pay == self.pay
        assert inline_keyboard_button.login_url == self.login_url

    def test_to_dict(self, inline_keyboard_button):
        inline_keyboard_button_dict = inline_keyboard_button.to_dict()

        assert isinstance(inline_keyboard_button_dict, dict)
        assert inline_keyboard_button_dict['text'] == inline_keyboard_button.text
        assert inline_keyboard_button_dict['url'] == inline_keyboard_button.url
        assert inline_keyboard_button_dict['callback_data'] == inline_keyboard_button.callback_data
        assert (
            inline_keyboard_button_dict['switch_inline_query']
            == inline_keyboard_button.switch_inline_query
        )
        assert (
            inline_keyboard_button_dict['switch_inline_query_current_chat']
            == inline_keyboard_button.switch_inline_query_current_chat
        )
        assert inline_keyboard_button_dict['callback_game'] == inline_keyboard_button.callback_game
        assert inline_keyboard_button_dict['pay'] == inline_keyboard_button.pay
        assert (
            inline_keyboard_button_dict['login_url'] == inline_keyboard_button.login_url.to_dict()
        )  # NOQA: E127

    def test_de_json(self, bot):
        json_dict = {
            'text': self.text,
            'url': self.url,
            'callback_data': self.callback_data,
            'switch_inline_query': self.switch_inline_query,
            'switch_inline_query_current_chat': self.switch_inline_query_current_chat,
            'callback_game': self.callback_game,
            'pay': self.pay,
        }

        inline_keyboard_button = InlineKeyboardButton.de_json(json_dict, None)
        assert inline_keyboard_button.text == self.text
        assert inline_keyboard_button.url == self.url
        assert inline_keyboard_button.callback_data == self.callback_data
        assert inline_keyboard_button.switch_inline_query == self.switch_inline_query
        assert (
            inline_keyboard_button.switch_inline_query_current_chat
            == self.switch_inline_query_current_chat
        )
        assert inline_keyboard_button.callback_game == self.callback_game
        assert inline_keyboard_button.pay == self.pay

    def test_equality(self):
        a = InlineKeyboardButton('text', callback_data='data')
        b = InlineKeyboardButton('text', callback_data='data')
        c = InlineKeyboardButton('texts', callback_data='data')
        d = InlineKeyboardButton('text', callback_data='info')
        e = InlineKeyboardButton('text', url='http://google.com')
        f = LoginUrl("http://google.com")

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

    @pytest.mark.parametrize('callback_data', ['foo', 1, ('da', 'ta'), object()])
    def test_update_callback_data(self, callback_data):
        button = InlineKeyboardButton(text='test', callback_data='data')
        button_b = InlineKeyboardButton(text='test', callback_data='data')

        assert button == button_b
        assert hash(button) == hash(button_b)

        button.update_callback_data(callback_data)
        assert button.callback_data is callback_data
        assert button != button_b
        assert hash(button) != hash(button_b)

        button_b.update_callback_data(callback_data)
        assert button_b.callback_data is callback_data
        assert button == button_b
        assert hash(button) == hash(button_b)

        button.update_callback_data({})
        assert button.callback_data == {}
        with pytest.raises(TypeError, match='unhashable'):
            hash(button)
