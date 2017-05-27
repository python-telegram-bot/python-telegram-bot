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
"""This module contains objects helps with creating menus for telegram bots."""

# pylint: disable=not-callable

import uuid
from collections import defaultdict
from itertools import chain

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Handler

try:
    str_type = str
except NameError:
    str_type = basestring  # noqa pylint: disable=undefined-variable


class Menu(object):
    _instance = None
    _buttons = None
    text = ''
    buttons = None
    data = {}
    root_menu = None  # populated in menuhandler
    stack = None  # Only used in root menu assigned in menuhandler

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Menu, cls).__new__(cls)
        return cls._instance

    def callback(self, bot, update, user_data, chat_data):
        _id = (update.callback_query.message.chat_id, update.callback_query.message.message_id
               ) if update.callback_query.message else update.callback_query.inline_message_id
        self.root_menu().stack[_id].append(self)
        try:
            return update.callback_query.edit_message_text(self.get_text(update),
                                                           reply_markup=self.keyboard(user_data,
                                                                                      chat_data))
        except BadRequest as e:
            if 'Message is not modified' in e.message:
                update.callback_query.answer()
            else:
                raise

    @classmethod
    def start(cls, bot, update, user_data=None, chat_data=None):
        # user_ and chat_data is only needed if we wanna do stuff that need state (ie.
        # ToggleButtons)
        return update.message.reply_text(cls().get_text(update), reply_markup=cls().keyboard(
            user_data, chat_data))

    def keyboard(self, user_data, chat_data):
        return InlineKeyboardMarkup([[x.keyboard_button(user_data, chat_data) for x in y] for y in
                                     self.get_buttons()])  # noqa

    def get_buttons(self):
        if self._buttons is None:
            if callable(self.buttons):
                self._buttons = self.buttons()  # noqa
            else:
                self._buttons = self.buttons
        return self._buttons

    def get_text(self, update):
        if callable(self.text):
            return self.text(update)  # noqa
        else:
            return self.text


class Button(Handler):
    def __init__(self,
                 text,
                 callback=None,
                 menu=None,
                 url=None,
                 callback_data=None,
                 switch_inline_query=None,
                 switch_inline_query_current_chat=None,
                 callback_game=None,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 name=None):
        self._text = text

        if callback is not None and menu is not None:
            raise RuntimeError
        self.callback = callback
        if menu is not None:
            self.callback = menu().callback
            pass_user_data = True
            pass_chat_data = True
        self.menu = menu

        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game

        self.name = name
        if self.name is None:
            self.name = str(uuid.uuid4())

        self.parent_menu = None
        self.root_menu = None

        super(Button, self).__init__(
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

    def check_update(self, update):
        # Since it's not registered using Dispatcher.add_handler this really doesn't matter
        return None

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)

        return self.callback(dispatcher.bot, update, **optional_args)

    def keyboard_button(self, user_data, chat_data):
        return InlineKeyboardButton(self.text(user_data, chat_data), self.url, self.name,
                                    self.switch_inline_query,
                                    self.switch_inline_query_current_chat,
                                    self.callback_game)

    def text(self, user_data, chat_data):
        return self._text


class BackButton(Button):
    def __init__(self, text, name=None):
        super(BackButton, self).__init__(text, callback=self._callback,
                                         pass_user_data=True, pass_chat_data=True, name=name)

    def _callback(self, bot, update, user_data, chat_data):
        _id = (update.callback_query.message.chat_id, update.callback_query.message.message_id
               ) if update.callback_query.message else update.callback_query.inline_message_id

        stack = self.parent_menu().root_menu().stack[_id]
        try:
            stack.pop()
            last_menu = stack.pop()
        except IndexError:
            last_menu = self.parent_menu().root_menu()
        last_menu.callback(bot, update, user_data, chat_data)


class MenuHandler(Handler):
    def __init__(self, menu):
        self.menu = menu
        self.buttons = {}
        self.collect_buttons(self.menu)

        menu.stack = defaultdict(list)

        super(MenuHandler, self).__init__(
            pass_update_queue=None,
            pass_job_queue=None,
            pass_user_data=None,
            pass_chat_data=None)

    def collect_buttons(self, menu):
        menu.root_menu = self.menu
        for button in chain.from_iterable(menu().get_buttons()):
            button.parent_menu = menu
            if button.name not in self.buttons and (button.callback is not None or
                                                    button.menu is not None):
                self.buttons[button.name] = button
                if button.menu is not None:
                    self.collect_buttons(button.menu)

    def check_update(self, update):
        return update.callback_query and update.callback_query.data in self.buttons

    def handle_update(self, update, dispatcher):
        # Let the button handle it
        return self.buttons[update.callback_query.data].handle_update(update, dispatcher)
