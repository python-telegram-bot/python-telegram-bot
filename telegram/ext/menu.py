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
from collections import defaultdict, OrderedDict
from itertools import chain
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Handler

try:
    str_type = basestring  # noqa
except NameError:
    str_type = str


def id_from_update(update):
    if update.callback_query.message:
        return update.callback_query.message.chat_id, update.callback_query.message.message_id
    return update.callback_query.inline_message_id


class Menu(object):
    _buttons = None
    text = ''
    buttons = None
    data = None
    default_data = None
    root_menu = None  # Populated in MenuHandler
    stack = None  # Only used in root menu assigned in MenuHandler

    def callback(self, bot, update, add_to_stack=True):
        if add_to_stack:
            self.root_menu.stack[id_from_update(update)].append(self)

        try:
            return update.callback_query.edit_message_text(self.get_text(update),
                                                           reply_markup=self.keyboard(update))
        except BadRequest as e:
            if 'Message is not modified' in e.message:
                update.callback_query.answer()
            else:
                raise

    def start(self, bot, update):
        # user_ and chat_data is only needed if we wanna do stuff that need state (ie.
        # ToggleButtons)
        return update.message.reply_text(self.get_text(update), reply_markup=self.keyboard(update))

    def keyboard(self, update):
        return InlineKeyboardMarkup([[x.keyboard_button(update) for x in y] for y in
                                     self.get_buttons(update)])  # noqa

    def get_buttons(self, update):
        if self._buttons is None:
            if callable(self.buttons):
                self._buttons = self.buttons(update)  # noqa pylint: disable=not-callable
            else:
                self._buttons = self.buttons
        return self._buttons

    def get_text(self, update):
        if callable(self.text):
            return self.text(update)  # noqa pylint: disable=not-callable
        else:
            return self.text


class Button(Handler):
    def __init__(self,
                 text=None,
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
                 pass_menu_data=False,
                 uuid=None):
        self._text = text

        if callback is not None and menu is not None:
            raise RuntimeError
        self.callback = callback
        if menu is not None:
            self.callback = menu.callback
        self.menu = menu

        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game

        self.uuid = uuid
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.pass_menu_data = pass_menu_data

        self.parent_menu = None

        super(Button, self).__init__(
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

    def check_update(self, update):
        # Since it's not registered using Dispatcher.add_handler this really doesn't matter
        return None

    def collect_optional_args(self, dispatcher, update=None):
        optional_args = super(Button, self).collect_optional_args(dispatcher, update)

        if self.pass_menu_data:
            menu_data = self.parent_menu.root_menu.default_data.copy()
            menu_data.update(self.parent_menu.root_menu.data[id_from_update(update)])
            optional_args['menu_data'] = menu_data

        return optional_args

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)

        return self.callback(dispatcher.bot, update, **optional_args)

    def keyboard_button(self, update):
        return InlineKeyboardButton(self.text(update), self.url, self.uuid,
                                    self.switch_inline_query,
                                    self.switch_inline_query_current_chat,
                                    self.callback_game)

    def text(self, update):
        return self._text

    def post_init(self):
        pass


class BackButton(Button):
    def __init__(self, text, uuid=None):
        super(BackButton, self).__init__(text, callback=self._callback, uuid=uuid)

    def _callback(self, bot, update):
        stack = self.parent_menu.root_menu.stack[id_from_update(update)]
        try:
            stack.pop()
            last_menu = stack.pop()
        except IndexError:
            last_menu = self.parent_menu.root_menu
        last_menu.callback(bot, update)


class ToggleButton(Button):
    def __init__(self, name, text=None, states=None, default=None, uuid=None):
        self.name = name
        if (text is None and states is None) or (text is not None and states is not None):
            raise RuntimeError
        if text is not None:
            states = (False, text), (True, '\u2714' + text)
        if default is None:
            default = states[0][0]
        self.default = default
        self.states = OrderedDict(states)

        super(ToggleButton, self).__init__(callback=self._callback, uuid=uuid)

    def post_init(self):
        self.parent_menu.root_menu.default_data[self.name] = self.default

    def _callback(self, bot, update):
        data = self.parent_menu.root_menu.data[id_from_update(update)]

        current = data.get(self.name, self.default)
        keys = list(self.states.keys())
        index = keys.index(current) + 1
        if index > len(keys) - 1:
            index = 0
        data[self.name] = keys[index]

        return self.parent_menu.callback(bot, update, add_to_stack=False)

    def text(self, update):
        data = self.parent_menu.root_menu.data[id_from_update(update)]
        return self.states[data.get(self.name, self.default)]


class RadioButton(Button):
    def __init__(self, name, value, text, enabled=False, uuid=None):
        self.value = value
        self.name = name

        super(RadioButton, self).__init__(callback=self._callback, uuid=uuid)

        if isinstance(text, str_type):
            self._text = ('\u26aa' + text, '\U0001f518' + text)
        else:
            self._text = text

        self.enabled = enabled

    def post_init(self):
        default_data = self.parent_menu.root_menu.default_data
        if self.name in default_data:
            if default_data[self.name] is not None:
                return
        if self.enabled is True:
            default_data[self.name] = self.value
        else:
            default_data[self.name] = None

    def _callback(self, bot, update):
        data = self.parent_menu.root_menu.data[id_from_update(update)]
        data[self.name] = self.value

        return self.parent_menu.callback(bot, update, add_to_stack=False)

    def text(self, update):
        data = self.parent_menu.root_menu.data[id_from_update(update)]
        value = data.get(self.name)
        if (value is None and self.enabled) or value == self.value:
            return self._text[1]  # True
        return self._text[0]  # False


class MenuHandler(Handler):
    def __init__(self, menu):
        self.menu = menu
        self.buttons = {}

        menu.data = defaultdict(dict)
        menu.default_data = dict()
        menu.stack = defaultdict(list)

        self.collect_buttons(self.menu)

        super(MenuHandler, self).__init__(
            pass_update_queue=None,
            pass_job_queue=None,
            pass_user_data=None,
            pass_chat_data=None)

    def collect_buttons(self, menu):
        menu.root_menu = self.menu
        for button in chain.from_iterable(menu.get_buttons(None)):
            button.parent_menu = menu
            button.post_init()
            if button.uuid not in self.buttons and (button.callback is not None or
                                                    button.menu is not None):
                self.buttons[button.uuid] = button
                if button.menu is not None:
                    self.collect_buttons(button.menu)

    def check_update(self, update):
        return update.callback_query and update.callback_query.data in self.buttons

    def handle_update(self, update, dispatcher):
        # Let the button handle it
        return self.buttons[update.callback_query.data].handle_update(update, dispatcher)


def make_menu(name, text, buttons):
    if callable(text):
        def _text(self, update):
            return text(update)
    else:
        _text = text
    if callable(buttons):
        def _buttons(self, update):
            return buttons(update)
    else:
        _buttons = buttons
    return type(name, (Menu,), dict(text=_text, buttons=_buttons))()
