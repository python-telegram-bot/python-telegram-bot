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
"""This module contains the BasePersistence class."""


class BasePersistence(object):
    def __init__(self, store_user_data=False, store_chat_data=False):
        """
        Args:
            store_user_data (:obj:`bool`): Whether user_data should be saved by this
                persistence class.
            store_chat_data (:obj:`bool`): Whether user_data should be saved by this
                persistence class
        """
        self.store_user_data = store_user_data
        self.store_chat_data = store_chat_data

    def get_user_data(self):
        """"
        Returns:
            :obj:'defaultdict`: The restored user data.
        """
        raise NotImplementedError

    def get_chat_data(self):
        """"
        Returns:
            :obj:'defaultdict`: The restored chat data.
        """
        raise NotImplementedError

    def get_conversations(self, name):
        """"
        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:'dict`: The restored conversations for the handler.
        """
        raise NotImplementedError

    def update_conversation(self, conversations):
        """"
        Args:
            conversation (:obj:'dict`): The :attr:`telegram.ext.ConversationHandler.conversations`
                dict to store.
        """
        raise NotImplementedError

    def update_user_data(self, user_data):
        """"
        Args:
            user_data (:obj:'defaultdict`): The :attr:`telegram.ext.dispatcher.user_data`
                defaultdict to store.
        """
        raise NotImplementedError

    def update_chat_data(self, chat_data):
        """"
        Args:
            chat_data (:obj:'defaultdict`): The :attr:`telegram.ext.dispatcher.chat_data`
                defaultdict to store.
        """
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError
