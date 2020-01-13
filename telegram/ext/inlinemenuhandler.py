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
"""This module contains the InlineMenuHandler."""

import re
from functools import partial
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler


class InlineMenuHandler(ConversationHandler):
    """
    A handler to display a menu with the help of :class:`telegram.InlineKeyboardMarkup` by managing
    a collection of data for the menus sites. Build on top of
    :class:`telegram.ext.ConversationHandler`.

    To build a menu, this handler needs a :obj:`dict` named :attr:`menus` containing the different
    menu steps. For each step, the corresponding dict value is a tuple of

        #. A description of the currently avaiable methods sent as the message text
        #. An array of tuples containing

           #. The button label
           #. the state this button leads to

        #. Optionally a callback function used to process the selected input

    All descriptions/labels may be subsituted by callbacks returning strings to adapt the output to
    the user input.

    The usual arguments ``update`` and ``context`` will be passed all callback functions.

    Note that the ``data`` field of the corresponding :class:`telegram.CallbackQuery` will be of
    the form ``menu <name> <state> <label>``, where ``<name>`` is the :attr:`name` of this
    conversation and only present if not ``None``, ``<state>`` is the string representation of the
    current state and ``<label>`` is the text of the pressed button.

    The top level menu is always the step :attr:`MAIN_MENU`. :attr:`menus` may also contain the
    keys :attr:`telegram.ext.ConversationHandler.TIMEOUT` and
    :attr:`telegram.ext.ConversationHandler.WAITING` which will then be used like in
    :class:`telegram.ext.ConversationHandler`. Finally, also the key
    :attr:`telegram.ext.ConversationHandler.END` may be present in :attr:`menus`. Use this to
    display a closing message and/or display a keyboard that can lead to another conversation. In
    the latter case, leave out info about the next state.
    If :attr:`telegram.ext.ConversationHandler.END` is not present, the menu message will be
    deleted.

    To start the menu, you have two options: A simple method is to use :attr:`start_command` to
    trigger the menu with a command. Another way is to set :attr:`map_to_parent` as for an ordinary
    :class:`telegram.ext.ConversationHandler`. You can than pass this handler to another
    :class:`telegram.ext.ConversationHandler` and use :attr:`start_pattern` to seemlessly integrate
    this menu into a higher level menu.

    Attributes:
        start_command (:obj:`str`): Optional. A command to start the conversation with.
        start_pattern (:obj:`str`): Optional. If set, the conversation will be started by a
            :class:`telegram.CallbackQuery` with this pattern as data.
        menus (Dict[:obj:`object`, (:obj:`str` | :obj:`callable`, \
            List[List[(:obj:`str` | :obj:`callable`, :obj:`obj`)]], :obj:`callable`)]):
            A :obj:`dict` that defines the different states of the menu a user can be in. Each
            state has a description, an array of buttons to send as
            :class:`telegram.InlineKeyboardMarkup` and optionally a callback function to process
            the user input. If you don't need a callback function, just leave out that argument.
        parse_mode (:obj:`str`): Optional. The :class:`telegram.ParseMode` to use to send the
            menu descriptions.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            ``False`` on :attr:`check_update`. The first handler which :attr:`check_update` method
            returns ``True`` will be used. If all return ``False``, the update is not handled.
        conversation_timeout (:obj:`float` | :obj:`datetime.timedelta`): Optional. When this
            handler is inactive more than this timeout (in seconds), it will be automatically
            ended. If this value is 0 or None (default), there will be no timeout. The last
            received update will be handled by ALL the handler's who's `check_update` method
            returns True that are in the state :attr:`ConversationHandler.TIMEOUT`.
        name (:obj:`str`): Optional The name for this inline menu handler. Required for
            persistence
        persistent (:obj:`bool`): Optional. If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`]): Optional. A :obj:`dict` that can be
            used to instruct a nested conversationhandler to transition into a mapped state on
            its parent conversationhandler in place of a specified nested state.

    Args:
        start_command (:obj:`str`, optional): A command to start the conversation with..
        start_pattern (:obj:`str`, optional): If set, the conversation will be started by a
            :class:`telegram.CallbackQuery` with this pattern as data.
        menus (Dict[:obj:`object`, (:obj:`str` | :obj:`callable`, \
            List[List[(:obj:`str` | :obj:`callable`, :obj:`obj`)]], :obj:`callable`)]):
            A :obj:`dict` that defines the different states of the menu a user can be in. Each
            state has a description, an array of buttons to send as
            :class:`telegram.InlineKeyboardMarkup` and optionally a callback function to process
            the user input.
        parse_mode (:obj:`str`, optional): The :class:`telegram.ParseMode` to use to send the
            menu descriptions.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            ``False`` on :attr:`check_update`. The first handler which :attr:`check_update` method
            returns ``True`` will be used. If all return ``False``, the update is not handled.
        conversation_timeout (:obj:`float` | :obj:`datetime.timedelta`, optional): When this
            handler is inactive more than this timeout (in seconds), it will be automatically
            ended. If this value is 0 or None (default), there will be no timeout. The last
            received update will be handled by ALL the handler's who's `check_update` method
            returns True that are in the state :attr:`ConversationHandler.TIMEOUT`.
        name (:obj:`str`, optional): The name for this inline menu handler. Required for
            persistence
        persistent (:obj:`bool`, optional): If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`], optional): A :obj:`dict` that can be
            used to instruct a nested conversationhandler to transition into a mapped state on
            its parent conversationhandler in place of a specified nested state.
    """
    MAIN_MENU = -4
    """:obj:`int`: Used as constant to handle state of the top level menu."""

    def __init__(self,
                 menus,
                 fallbacks,
                 start_command=None,
                 start_pattern=None,
                 parse_mode=None,
                 conversation_timeout=None,
                 name=None,
                 persistent=False,
                 map_to_parent=None):
        self._chat_id = None
        self._message_id = None
        self.start_command = start_command
        self.start_pattern = start_pattern
        self.parse_mode = parse_mode
        self.name = name

        # Build entry point
        start_command_handler = None
        if self.start_command:
            if (map_to_parent and self.start_pattern):
                raise ValueError('If start_command is set, start_pattern and map_to_parent will '
                                 'will be ignorerd.')
            start_command_handler = CommandHandler(
                command=self.start_command,
                callback=partial(
                    self._start_callback,
                    inline_menu_handler=self,
                )
            )
        elif not (map_to_parent and self.start_pattern):
            raise ValueError('Either start_command or both of map_to_parent and start_pattern '
                             'must be set.')
        else:
            start_command_handler = CallbackQueryHandler(
                pattern=re.compile('^{}$'.format(self.start_pattern)),
                callback=partial(
                    self._start_callback,
                    inline_menu_handler=self,
                )
            )
        entry_points = [start_command_handler]

        # Build handler for the states
        states = {}
        self._callback_query_handlers = {}
        for state in menus:
            if not (state is ConversationHandler.TIMEOUT or state is ConversationHandler.WAITING):
                states[state] = []
                self._callback_query_handlers[state] = []
                for row in menus[state][1]:
                    self._callback_query_handlers[state].append([])
                    for button in row:
                        handler = CallbackQueryHandler(
                            pattern=re.compile('^{}$'.format(self._data(state, button[0]))),
                            callback=partial(
                                self._update_callback,
                                inline_menu_handler=self,
                                new_state=button[1],
                                callback=menus[state][2] if len(menus[state]) == 3 else None
                            )
                        )
                        # Add handler to conversation
                        states[state].append(handler)
                        # Save handler to update pattern later on
                        self._callback_query_handlers[state][-1].append(handler)

        # Add TIMEOUT and WAITING handlers to conversation
        for state in [ConversationHandler.TIMEOUT, ConversationHandler.WAITING]:
            if state in menus:
                states[state] = menus[state]

        self.menus = menus

        # Initialize underlying ConversationHandler
        super(InlineMenuHandler, self).__init__(
            entry_points=entry_points,
            fallbacks=fallbacks,
            conversation_timeout=conversation_timeout,
            name=name,
            persistent=persistent,
            map_to_parent=map_to_parent,
            states=states
        )

    # Builds callback data
    def _data(self, state, label):
        if self.name:
            return '{} {} {} {}'.format('menu', self.name, state, label)
        else:
            return '{} {} {}'.format('menu', state, label)

    # Builds reply_markup
    def _reply_markup(self, update, context, state):
        buttons = []
        for idx, row in enumerate(self.menus[state][1]):
            # Skip empty rows
            if row:
                buttons.append([])
                for jdx, button in enumerate(row):
                    # In the END State no next state is given
                    label = button[0] if state is not self.END else button
                    if callable(label):
                        label = label(update, context)
                        # Update patterns in CallbackQueryHandlers if label is a callback
                        self._callback_query_handlers[state][idx][jdx].pattern = re.compile(
                            '^{}$'.format(self._data(state, label))
                        )
                    buttons[-1].append(
                        InlineKeyboardButton(
                            text=label,
                            callback_data=self._data(state, label)
                        )
                    )

        # If no Keyboard is set, return None
        if buttons:
            return InlineKeyboardMarkup(buttons)
        else:
            return None

    @staticmethod
    def _start_callback(update, context, inline_menu_handler):
        # Build description
        if callable(inline_menu_handler.menus[inline_menu_handler.MAIN_MENU][0]):
            description = inline_menu_handler.menus[inline_menu_handler.MAIN_MENU][0](
                update, context
            )
        else:
            description = inline_menu_handler.menus[inline_menu_handler.MAIN_MENU][0]

        kwargs = {
            'text': description,
            'parse_mode': inline_menu_handler.parse_mode,
            'reply_markup': inline_menu_handler._reply_markup(update, context,
                                                              inline_menu_handler.MAIN_MENU)
        }

        if update.callback_query:
            inline_menu_handler.message_id = update.callback_query.message.message_id
            inline_menu_handler.chat_id = update.callback_query.message.chat_id
            context.bot.edit_message_text(
                chat_id=inline_menu_handler.chat_id,
                message_id=inline_menu_handler.message_id,
                **kwargs
            )
        else:
            inline_menu_handler.chat_id = update.message.chat_id
            message = context.bot.send_message(
                chat_id=inline_menu_handler.chat_id,
                **kwargs
            )
            inline_menu_handler.message_id = message.message_id

        return inline_menu_handler.MAIN_MENU

    @staticmethod
    def _update_callback(update, context,
                         inline_menu_handler=None, new_state=None, callback=None):
        if (new_state == inline_menu_handler.END
                and not inline_menu_handler.menus.get(inline_menu_handler.END)):
            context.bot.delete_message(
                chat_id=inline_menu_handler.chat_id,
                message_id=inline_menu_handler.message_id,
            )
        else:
            if callable(inline_menu_handler.menus[new_state][0]):
                description = inline_menu_handler.menus[new_state][0](update, context)
            else:
                description = inline_menu_handler.menus[new_state][0]
            context.bot.edit_message_text(
                chat_id=inline_menu_handler.chat_id,
                message_id=inline_menu_handler.message_id,
                text=description,
                parse_mode=inline_menu_handler.parse_mode,
                reply_markup=inline_menu_handler._reply_markup(update, context, new_state)
            )
        if callback:
            callback(update, context)
        return new_state

    @property
    def chat_id(self):
        """:obj:`int`: The id of the chat this menu is displayed in."""
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._chat_id = int(value)

    @property
    def message_id(self):
        """:obj:`int`: The id of the message this menu is displayed as."""
        return self._message_id

    @message_id.setter
    def message_id(self, value):
        self._message_id = int(value)
