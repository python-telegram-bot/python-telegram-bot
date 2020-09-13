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
"""This module contains the PicklePersistence class."""
import pickle
from collections import defaultdict
from copy import deepcopy

from telegram.ext import BasePersistence

from typing import DefaultDict, Dict, Any, Tuple, Optional
from telegram.utils.types import ConversationDict


class PicklePersistence(BasePersistence):
    """Using python's builtin pickle for making you bot persistent.

    Warning:
        :class:`PicklePersistence` will try to replace :class:`telegram.Bot` instances by
        :attr:`REPLACED_BOT` and insert the bot set with
        :meth:`telegram.ext.BasePersistence.set_bot` upon loading of the data. This is to ensure
        that changes to the bot apply to the saved objects, too. If you change the bots token, this
        may lead to e.g. ``Chat not found`` errors. For the limitations on replacing bots see
        :meth:`telegram.ext.BasePersistence.replace_bot` and
        :meth:`telegram.ext.BasePersistence.insert_bot`.

    Attributes:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is :obj:`False` this will be used as a prefix.
        store_user_data (:obj:`bool`): Optional. Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether user_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Optional. Whether bot_data should be saved by this
            persistence class.
        single_file (:obj:`bool`): Optional. When :obj:`False` will store 3 separate files of
            `filename_user_data`, `filename_chat_data` and `filename_conversations`. Default is
            :obj:`True`.
        on_flush (:obj:`bool`, optional): When :obj:`True` will only save to file when
            :meth:`flush` is called and keep data in memory until that happens. When
            :obj:`False` will store data on any transaction *and* on call to :meth:`flush`.
            Default is :obj:`False`.

    Args:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is :obj:`False` this will be used as a prefix.
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_chat_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_bot_data (:obj:`bool`, optional): Whether bot_data should be saved by this
            persistence class. Default is :obj:`True` .
        single_file (:obj:`bool`, optional): When :obj:`False` will store 3 separate files of
            `filename_user_data`, `filename_chat_data` and `filename_conversations`. Default is
            :obj:`True`.
        on_flush (:obj:`bool`, optional): When :obj:`True` will only save to file when
            :meth:`flush` is called and keep data in memory until that happens. When
            :obj:`False` will store data on any transaction *and* on call to :meth:`flush`.
            Default is :obj:`False`.
    """

    def __init__(self,
                 filename: str,
                 store_user_data: bool = True,
                 store_chat_data: bool = True,
                 store_bot_data: bool = True,
                 single_file: bool = True,
                 on_flush: bool = False):
        super().__init__(store_user_data=store_user_data,
                         store_chat_data=store_chat_data,
                         store_bot_data=store_bot_data)
        self.filename = filename
        self.single_file = single_file
        self.on_flush = on_flush
        self.user_data: Optional[DefaultDict[int, Dict]] = None
        self.chat_data: Optional[DefaultDict[int, Dict]] = None
        self.bot_data: Optional[Dict] = None
        self.conversations: Optional[Dict[str, Dict[Tuple, Any]]] = None

    def load_singlefile(self) -> None:
        try:
            filename = self.filename
            with open(self.filename, "rb") as f:
                data = pickle.load(f)
                self.user_data = defaultdict(dict, data['user_data'])
                self.chat_data = defaultdict(dict, data['chat_data'])
                # For backwards compatibility with files not containing bot data
                self.bot_data = data.get('bot_data', {})
                self.conversations = data['conversations']
        except IOError:
            self.conversations = dict()
            self.user_data = defaultdict(dict)
            self.chat_data = defaultdict(dict)
            self.bot_data = {}
        except pickle.UnpicklingError:
            raise TypeError("File {} does not contain valid pickle data".format(filename))
        except Exception:
            raise TypeError("Something went wrong unpickling {}".format(filename))

    def load_file(self, filename: str) -> Any:
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except IOError:
            return None
        except pickle.UnpicklingError:
            raise TypeError("File {} does not contain valid pickle data".format(filename))
        except Exception:
            raise TypeError("Something went wrong unpickling {}".format(filename))

    def dump_singlefile(self) -> None:
        with open(self.filename, "wb") as f:
            data = {'conversations': self.conversations, 'user_data': self.user_data,
                    'chat_data': self.chat_data, 'bot_data': self.bot_data}
            pickle.dump(data, f)

    def dump_file(self, filename: str, data: Any) -> None:
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """Returns the user_data from the pickle file if it exists or an empty :obj:`defaultdict`.

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
        return deepcopy(self.user_data)  # type: ignore[arg-type]

    def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        """Returns the chat_data from the pickle file if it exists or an empty :obj:`defaultdict`.

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
        return deepcopy(self.chat_data)  # type: ignore[arg-type]

    def get_bot_data(self) -> Dict[Any, Any]:
        """Returns the bot_data from the pickle file if it exists or an empty :obj:`dict`.

        Returns:
            :obj:`dict`: The restored bot data.
        """
        if self.bot_data:
            pass
        elif not self.single_file:
            filename = "{}_bot_data".format(self.filename)
            data = self.load_file(filename)
            if not data:
                data = {}
            self.bot_data = data
        else:
            self.load_singlefile()
        return deepcopy(self.bot_data)  # type: ignore[arg-type]

    def get_conversations(self, name: str) -> ConversationDict:
        """Returns the conversations from the pickle file if it exsists or an empty dict.

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
        return self.conversations.get(name, {}).copy()  # type: ignore[union-attr]

    def update_conversation(self,
                            name: str, key: Tuple[int, ...],
                            new_state: Optional[object]) -> None:
        """Will update the conversations for the given handler and depending on :attr:`on_flush`
        save the pickle file.

        Args:
            name (:obj:`str`): The handler's name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """
        if not self.conversations:
            self.conversations = dict()
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_conversations".format(self.filename)
                self.dump_file(filename, self.conversations)
            else:
                self.dump_singlefile()

    def update_user_data(self, user_id: int, data: Dict) -> None:
        """Will update the user_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """
        if self.user_data is None:
            self.user_data = defaultdict(dict)
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_user_data".format(self.filename)
                self.dump_file(filename, self.user_data)
            else:
                self.dump_singlefile()

    def update_chat_data(self, chat_id: int, data: Dict) -> None:
        """Will update the chat_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        if self.chat_data is None:
            self.chat_data = defaultdict(dict)
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_chat_data".format(self.filename)
                self.dump_file(filename, self.chat_data)
            else:
                self.dump_singlefile()

    def update_bot_data(self, data: Dict) -> None:
        """Will update the bot_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.bot_data`.
        """
        if self.bot_data == data:
            return
        self.bot_data = data.copy()
        if not self.on_flush:
            if not self.single_file:
                filename = "{}_bot_data".format(self.filename)
                self.dump_file(filename, self.bot_data)
            else:
                self.dump_singlefile()

    def flush(self) -> None:
        """ Will save all data in memory to pickle file(s).
        """
        if self.single_file:
            if self.user_data or self.chat_data or self.bot_data or self.conversations:
                self.dump_singlefile()
        else:
            if self.user_data:
                self.dump_file("{}_user_data".format(self.filename), self.user_data)
            if self.chat_data:
                self.dump_file("{}_chat_data".format(self.filename), self.chat_data)
            if self.bot_data:
                self.dump_file("{}_bot_data".format(self.filename), self.bot_data)
            if self.conversations:
                self.dump_file("{}_conversations".format(self.filename), self.conversations)
