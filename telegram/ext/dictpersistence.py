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
"""This module contains the DictPersistence class."""
from copy import deepcopy

from telegram.utils.helpers import decode_user_chat_data_from_json,\
    decode_conversations_from_json, encode_conversations_to_json

try:
    import ujson as json
except ImportError:
    import json
from collections import defaultdict
from telegram.ext import BasePersistence


class DictPersistence(BasePersistence):
    """Using python's dicts and json for making your bot persistent.

    Attributes:
        store_user_data (:obj:`bool`): Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Whether chat_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Whether bot_data should be saved by this
            persistence class.

    Args:
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is ``True``.
        store_chat_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is ``True``.
        store_bot_data (:obj:`bool`, optional): Whether bot_data should be saved by this
            persistence class. Default is ``True`` .
        user_data_json (:obj:`str`, optional): Json string that will be used to reconstruct
            user_data on creating this persistence. Default is ``""``.
        chat_data_json (:obj:`str`, optional): Json string that will be used to reconstruct
            chat_data on creating this persistence. Default is ``""``.
        bot_data_json (:obj:`str`, optional): Json string that will be used to reconstruct
            bot_data on creating this persistence. Default is ``""``.
        conversations_json (:obj:`str`, optional): Json string that will be used to reconstruct
            conversation on creating this persistence. Default is ``""``.
    """

    def __init__(self,
                 store_user_data=True,
                 store_chat_data=True,
                 store_bot_data=True,
                 user_data_json='',
                 chat_data_json='',
                 bot_data_json='',
                 conversations_json=''):
        super(DictPersistence, self).__init__(store_user_data=store_user_data,
                                              store_chat_data=store_chat_data,
                                              store_bot_data=store_bot_data)
        self._user_data = None
        self._chat_data = None
        self._bot_data = None
        self._conversations = None
        self._user_data_json = None
        self._chat_data_json = None
        self._bot_data_json = None
        self._conversations_json = None
        if user_data_json:
            try:
                self._user_data = decode_user_chat_data_from_json(user_data_json)
                self._user_data_json = user_data_json
            except (ValueError, AttributeError):
                raise TypeError("Unable to deserialize user_data_json. Not valid JSON")
        if chat_data_json:
            try:
                self._chat_data = decode_user_chat_data_from_json(chat_data_json)
                self._chat_data_json = chat_data_json
            except (ValueError, AttributeError):
                raise TypeError("Unable to deserialize chat_data_json. Not valid JSON")
        if bot_data_json:
            try:
                self._bot_data = json.loads(bot_data_json)
                self._bot_data_json = bot_data_json
            except (ValueError, AttributeError):
                raise TypeError("Unable to deserialize bot_data_json. Not valid JSON")
            if not isinstance(self._bot_data, dict):
                raise TypeError("bot_data_json must be serialized dict")

        if conversations_json:
            try:
                self._conversations = decode_conversations_from_json(conversations_json)
                self._conversations_json = conversations_json
            except (ValueError, AttributeError):
                raise TypeError("Unable to deserialize conversations_json. Not valid JSON")

    @property
    def user_data(self):
        """:obj:`dict`: The user_data as a dict"""
        return self._user_data

    @property
    def user_data_json(self):
        """:obj:`str`: The user_data serialized as a JSON-string."""
        if self._user_data_json:
            return self._user_data_json
        else:
            return json.dumps(self.user_data)

    @property
    def chat_data(self):
        """:obj:`dict`: The chat_data as a dict"""
        return self._chat_data

    @property
    def chat_data_json(self):
        """:obj:`str`: The chat_data serialized as a JSON-string."""
        if self._chat_data_json:
            return self._chat_data_json
        else:
            return json.dumps(self.chat_data)

    @property
    def bot_data(self):
        """:obj:`dict`: The bot_data as a dict"""
        return self._bot_data

    @property
    def bot_data_json(self):
        """:obj:`str`: The bot_data serialized as a JSON-string."""
        if self._bot_data_json:
            return self._bot_data_json
        else:
            return json.dumps(self.bot_data)

    @property
    def conversations(self):
        """:obj:`dict`: The conversations as a dict"""
        return self._conversations

    @property
    def conversations_json(self):
        """:obj:`str`: The conversations serialized as a JSON-string."""
        if self._conversations_json:
            return self._conversations_json
        else:
            return encode_conversations_to_json(self.conversations)

    def get_user_data(self):
        """Returns the user_data created from the ``user_data_json`` or an empty defaultdict.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.user_data:
            pass
        else:
            self._user_data = defaultdict(dict)
        return deepcopy(self.user_data)

    def get_chat_data(self):
        """Returns the chat_data created from the ``chat_data_json`` or an empty defaultdict.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.chat_data:
            pass
        else:
            self._chat_data = defaultdict(dict)
        return deepcopy(self.chat_data)

    def get_bot_data(self):
        """Returns the bot_data created from the ``bot_data_json`` or an empty dict.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.bot_data:
            pass
        else:
            self._bot_data = {}
        return deepcopy(self.bot_data)

    def get_conversations(self, name):
        """Returns the conversations created from the ``conversations_json`` or an empty
        defaultdict.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.conversations:
            pass
        else:
            self._conversations = {}
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        """Will update the conversations for the given handler.

        Args:
            name (:obj:`str`): The handlers name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """
        if self._conversations.setdefault(name, {}).get(key) == new_state:
            return
        self._conversations[name][key] = new_state
        self._conversations_json = None

    def update_user_data(self, user_id, data):
        """Will update the user_data (if changed).

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """
        if self._user_data is None:
            self._user_data = defaultdict(dict)
        if self._user_data.get(user_id) == data:
            return
        self._user_data[user_id] = data
        self._user_data_json = None

    def update_chat_data(self, chat_id, data):
        """Will update the chat_data (if changed).

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        if self._chat_data is None:
            self._chat_data = defaultdict(dict)
        if self._chat_data.get(chat_id) == data:
            return
        self._chat_data[chat_id] = data
        self._chat_data_json = None

    def update_bot_data(self, data):
        """Will update the bot_data (if changed).

        Args:
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.bot_data`.
        """
        if self._bot_data == data:
            return
        self._bot_data = data.copy()
        self._bot_data_json = None
