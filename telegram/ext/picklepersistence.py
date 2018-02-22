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
"""This module contains the BasePersistence class."""
import pickle
from collections import defaultdict

from telegram.ext import BasePersistence


class PicklePersistence(BasePersistence):
    """Using python's builtin pickle for making you bot persistent.

    Attributes:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is false this will be used as a prefix.
        store_user_data (:obj:`bool`): Optional. Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether user_data should be saved by this
            persistence class.
        single_file (:obj:`bool`): Optional. When ``False`` will store 3 sperate files of
            `filename_user_data`, `filename_chat_data` and `filename_conversations`. Default is
            ``True``.
        on_flush (:obj:`bool`): Optional. When ``True`` will only save to file when :meth:`flush`
            is called and keep data in memory until that happens. When False will store data on any
            transaction. Default is ``False``.

    Args:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is false this will be used as a prefix.
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is ``True``.
        store_chat_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is ``True``.
        single_file (:obj:`bool`, optional): When ``False`` will store 3 sperate files of
            `filename_user_data`, `filename_chat_data` and `filename_conversations`. Default is
            ``True``.
        on_flush (:obj:`bool`, optional): When ``True`` will only save to file when :meth:`flush`
            is called and keep data in memory until that happens. When False will store data on any
            transaction. Default is ``False``.
    """

    def __init__(self, filename, store_user_data=True, store_chat_data=True, singe_file=True,
                 on_flush=False):
        self.filename = filename
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data
        self.single_file = singe_file
        self.on_flush = on_flush
        self.user_data = None
        self.chat_data = None
        self.conversations = None

    def load_singlefile(self):
        try:
            filename = self.filename
            with open(self.filename, "rb") as f:
                all = pickle.load(f)
                self.user_data = defaultdict(dict, all['user_data'])
                self.chat_data = defaultdict(dict, all['chat_data'])
                self.conversations = all['conversations']
        except FileNotFoundError:
            self.conversations = {}
            self.user_data = defaultdict(dict)
            self.chat_data = defaultdict(dict)
        except pickle.UnpicklingError:
            raise TypeError("File {} does not contain valid pickle data".format(filename))

    def load_file(self, filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
        except pickle.UnpicklingError:
            raise TypeError("File {} does not contain valid pickle data".format(filename))

    def dump_singlefile(self):
        with open(self.filename, "wb") as f:
            all = {'conversations': self.conversations, 'user_data': self.user_data,
                   'chat_data': self.chat_data}
            pickle.dump(all, f)

    def dump_file(self, filename, data):
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def get_user_data(self):
        """Returns the user_data from the pickle file if it exsists or an empty defaultdict.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.user_data:
            pass
        elif not self.single_file:
            filename = "{}_user_data".format(self.filename)
            data = self.load_file(filename)
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.user_data = data
        else:
            self.load_singlefile()
        return self.user_data.copy()

    def get_chat_data(self):
        """Returns the chat_data from the pickle file if it exsists or an empty defaultdict.

        Returns:
            :obj:`defaultdict`: The restored chat data.
        """
        if self.chat_data:
            pass
        elif not self.single_file:
            filename = "{}_chat_data".format(self.filename)
            data = self.load_file(filename)
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.chat_data = data
        else:
            self.load_singlefile()
        return self.chat_data.copy()

    def get_conversations(self, name):
        """Returns the conversations from the pickle file if it exsists or an empty defaultdict.

        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """
        if self.conversations:
            pass
        elif not self.single_file:
            filename = "{}_conversations".format(self.filename)
            data = self.load_file(filename)
            if not data:
                data = {name: {}}
            self.conversations = data
        else:
            self.load_singlefile()
        return self.conversations.get(name, {}).copy()

    def update_conversations(self, name, conversations):
        """Will update the conversations for the given handler and depending on :attr:`on_flush`
        save the pickle file.

        Args:
            name (:obj:`str`): The handlers name.
            conversations (:obj:`dict`): The :attr:`telegram.ext.ConversationHandler.conversations`
                dict to store.
        """
        if self.conversations[name] == conversations:
            return
        self.conversations[name] = conversations
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_conversations".format(self.filename)
                self.dump_file(filename, self.conversations)
            else:
                self.dump_singlefile()

    def update_user_data(self, user_data):
        """Will update the user_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.

        Args:
            user_data (:obj:`defaultdict`): The :attr:`telegram.ext.Dispatcher.user_data`
                defaultdict to store.
        """
        if self.user_data == user_data:
            return
        self.user_data = user_data
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_user_data".format(self.filename)
                self.dump_file(filename, self.user_data)
            else:
                self.dump_singlefile()

    def update_chat_data(self, chat_data):
        """Will update the chat_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.

        Args:
            chat_data (:obj:`defaultdict`): The :attr:`telegram.ext.Dispatcher.chat_data`
                defaultdict to store.
        """
        if self.chat_data == chat_data:
            return
        self.chat_data = chat_data
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_chat_data".format(self.filename)
                self.dump_file(filename, self.chat_data)
            else:
                self.dump_singlefile()

    def flush(self):
        """If :attr:`on_flush` is set to ``True``. Will save all data in memory to pickle file(s). If
        it's ``False`` will just pass.
        """
        if not self.on_flush:
            pass
        else:
            if self.single_file:
                self.dump_singlefile()
            else:
                self.dump_file("{}_user_data".format(self.filename), self.user_data)
                self.dump_file("{}_chat_data".format(self.filename), self.chat_data)
                self.dump_file("{}_conversations".format(self.filename), self.conversations)
