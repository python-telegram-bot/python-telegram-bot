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
"""This module contains the PicklePersistence class."""
import pickle
from collections import defaultdict
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    overload,
    cast,
    DefaultDict,
)

from telegram.ext import BasePersistence
from .utils.types import UD, CD, BD, ConversationDict, CDCData
from .contexttypes import ContextTypes


class PicklePersistence(BasePersistence[UD, CD, BD]):
    """Using python's builtin pickle for making your bot persistent.

    Warning:
        :class:`PicklePersistence` will try to replace :class:`telegram.Bot` instances by
        :attr:`REPLACED_BOT` and insert the bot set with
        :meth:`telegram.ext.BasePersistence.set_bot` upon loading of the data. This is to ensure
        that changes to the bot apply to the saved objects, too. If you change the bots token, this
        may lead to e.g. ``Chat not found`` errors. For the limitations on replacing bots see
        :meth:`telegram.ext.BasePersistence.replace_bot` and
        :meth:`telegram.ext.BasePersistence.insert_bot`.

    Args:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is :obj:`False` this will be used as a prefix.
        store_user_data (:obj:`bool`, optional): Whether user_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_chat_data (:obj:`bool`, optional): Whether chat_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_bot_data (:obj:`bool`, optional): Whether bot_data should be saved by this
            persistence class. Default is :obj:`True`.
        store_callback_data (:obj:`bool`, optional): Whether callback_data should be saved by this
            persistence class. Default is :obj:`False`.

            .. versionadded:: 13.6
        single_file (:obj:`bool`, optional): When :obj:`False` will store 5 separate files of
            `filename_user_data`, `filename_chat_data`, `filename_bot_data`, `filename_chat_data`,
            `filename_callback_data` and `filename_conversations`. Default is :obj:`True`.
        on_flush (:obj:`bool`, optional): When :obj:`True` will only save to file when
            :meth:`flush` is called and keep data in memory until that happens. When
            :obj:`False` will store data on any transaction *and* on call to :meth:`flush`.
            Default is :obj:`False`.
        context_types (:class:`telegram.ext.ContextTypes`, optional): Pass an instance
            of :class:`telegram.ext.ContextTypes` to customize the types used in the
            ``context`` interface. If not passed, the defaults documented in
            :class:`telegram.ext.ContextTypes` will be used.

            .. versionadded:: 13.6

    Attributes:
        filename (:obj:`str`): The filename for storing the pickle files. When :attr:`single_file`
            is :obj:`False` this will be used as a prefix.
        store_user_data (:obj:`bool`): Optional. Whether user_data should be saved by this
            persistence class.
        store_chat_data (:obj:`bool`): Optional. Whether chat_data should be saved by this
            persistence class.
        store_bot_data (:obj:`bool`): Optional. Whether bot_data should be saved by this
            persistence class.
        store_callback_data (:obj:`bool`): Optional. Whether callback_data be saved by this
            persistence class.

            .. versionadded:: 13.6
        single_file (:obj:`bool`): Optional. When :obj:`False` will store 5 separate files of
            `filename_user_data`, `filename_chat_data`, `filename_bot_data`, `filename_chat_data`,
            `filename_callback_data` and `filename_conversations`. Default is :obj:`True`.
        on_flush (:obj:`bool`, optional): When :obj:`True` will only save to file when
            :meth:`flush` is called and keep data in memory until that happens. When
            :obj:`False` will store data on any transaction *and* on call to :meth:`flush`.
            Default is :obj:`False`.
        context_types (:class:`telegram.ext.ContextTypes`): Container for the types used
            in the ``context`` interface.

            .. versionadded:: 13.6
    """

    __slots__ = (
        'filename',
        'single_file',
        'on_flush',
        'user_data',
        'chat_data',
        'bot_data',
        'callback_data',
        'conversations',
        'context_types',
    )

    @overload
    def __init__(
        self: 'PicklePersistence[Dict, Dict, Dict]',
        filename: str,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        single_file: bool = True,
        on_flush: bool = False,
        store_callback_data: bool = False,
    ):
        ...

    @overload
    def __init__(
        self: 'PicklePersistence[UD, CD, BD]',
        filename: str,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        single_file: bool = True,
        on_flush: bool = False,
        store_callback_data: bool = False,
        context_types: ContextTypes[Any, UD, CD, BD] = None,
    ):
        ...

    def __init__(
        self,
        filename: str,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        single_file: bool = True,
        on_flush: bool = False,
        store_callback_data: bool = False,
        context_types: ContextTypes[Any, UD, CD, BD] = None,
    ):
        super().__init__(
            store_user_data=store_user_data,
            store_chat_data=store_chat_data,
            store_bot_data=store_bot_data,
            store_callback_data=store_callback_data,
        )
        self.filename = filename
        self.single_file = single_file
        self.on_flush = on_flush
        self.user_data: Optional[DefaultDict[int, UD]] = None
        self.chat_data: Optional[DefaultDict[int, CD]] = None
        self.bot_data: Optional[BD] = None
        self.callback_data: Optional[CDCData] = None
        self.conversations: Optional[Dict[str, Dict[Tuple, object]]] = None
        self.context_types = cast(ContextTypes[Any, UD, CD, BD], context_types or ContextTypes())

    def _load_singlefile(self) -> None:
        try:
            filename = self.filename
            with open(self.filename, "rb") as file:
                data = pickle.load(file)
                self.user_data = defaultdict(self.context_types.user_data, data['user_data'])
                self.chat_data = defaultdict(self.context_types.chat_data, data['chat_data'])
                # For backwards compatibility with files not containing bot data
                self.bot_data = data.get('bot_data', self.context_types.bot_data())
                self.callback_data = data.get('callback_data', {})
                self.conversations = data['conversations']
        except OSError:
            self.conversations = {}
            self.user_data = defaultdict(self.context_types.user_data)
            self.chat_data = defaultdict(self.context_types.chat_data)
            self.bot_data = self.context_types.bot_data()
            self.callback_data = None
        except pickle.UnpicklingError as exc:
            raise TypeError(f"File {filename} does not contain valid pickle data") from exc
        except Exception as exc:
            raise TypeError(f"Something went wrong unpickling {filename}") from exc

    @staticmethod
    def _load_file(filename: str) -> Any:
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except OSError:
            return None
        except pickle.UnpicklingError as exc:
            raise TypeError(f"File {filename} does not contain valid pickle data") from exc
        except Exception as exc:
            raise TypeError(f"Something went wrong unpickling {filename}") from exc

    def _dump_singlefile(self) -> None:
        with open(self.filename, "wb") as file:
            data = {
                'conversations': self.conversations,
                'user_data': self.user_data,
                'chat_data': self.chat_data,
                'bot_data': self.bot_data,
                'callback_data': self.callback_data,
            }
            pickle.dump(data, file)

    @staticmethod
    def _dump_file(filename: str, data: object) -> None:
        with open(filename, "wb") as file:
            pickle.dump(data, file)

    def get_user_data(self) -> DefaultDict[int, UD]:
        """Returns the user_data from the pickle file if it exists or an empty :obj:`defaultdict`.

        Returns:
            DefaultDict[:obj:`int`, :class:`telegram.ext.utils.types.UD`]: The restored user data.
        """
        if self.user_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_user_data"
            data = self._load_file(filename)
            if not data:
                data = defaultdict(self.context_types.user_data)
            else:
                data = defaultdict(self.context_types.user_data, data)
            self.user_data = data
        else:
            self._load_singlefile()
        return self.user_data  # type: ignore[return-value]

    def get_chat_data(self) -> DefaultDict[int, CD]:
        """Returns the chat_data from the pickle file if it exists or an empty :obj:`defaultdict`.

        Returns:
            DefaultDict[:obj:`int`, :class:`telegram.ext.utils.types.CD`]: The restored chat data.
        """
        if self.chat_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_chat_data"
            data = self._load_file(filename)
            if not data:
                data = defaultdict(self.context_types.chat_data)
            else:
                data = defaultdict(self.context_types.chat_data, data)
            self.chat_data = data
        else:
            self._load_singlefile()
        return self.chat_data  # type: ignore[return-value]

    def get_bot_data(self) -> BD:
        """Returns the bot_data from the pickle file if it exists or an empty object of type
        :class:`telegram.ext.utils.types.BD`.

        Returns:
            :class:`telegram.ext.utils.types.BD`: The restored bot data.
        """
        if self.bot_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_bot_data"
            data = self._load_file(filename)
            if not data:
                data = self.context_types.bot_data()
            self.bot_data = data
        else:
            self._load_singlefile()
        return self.bot_data  # type: ignore[return-value]

    def get_callback_data(self) -> Optional[CDCData]:
        """Returns the callback data from the pickle file if it exists or :obj:`None`.

        .. versionadded:: 13.6

        Returns:
            Optional[:class:`telegram.ext.utils.types.CDCData`]: The restored meta data or
                :obj:`None`, if no data was stored.
        """
        if self.callback_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_callback_data"
            data = self._load_file(filename)
            if not data:
                data = None
            self.callback_data = data
        else:
            self._load_singlefile()
        if self.callback_data is None:
            return None
        return self.callback_data[0], self.callback_data[1].copy()

    def get_conversations(self, name: str) -> ConversationDict:
        """Returns the conversations from the pickle file if it exists or an empty dict.

        Args:
            name (:obj:`str`): The handlers name.

        Returns:
            :obj:`dict`: The restored conversations for the handler.
        """
        if self.conversations:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_conversations"
            data = self._load_file(filename)
            if not data:
                data = {name: {}}
            self.conversations = data
        else:
            self._load_singlefile()
        return self.conversations.get(name, {}).copy()  # type: ignore[union-attr]

    def update_conversation(
        self, name: str, key: Tuple[int, ...], new_state: Optional[object]
    ) -> None:
        """Will update the conversations for the given handler and depending on :attr:`on_flush`
        save the pickle file.

        Args:
            name (:obj:`str`): The handler's name.
            key (:obj:`tuple`): The key the state is changed for.
            new_state (:obj:`tuple` | :obj:`any`): The new state for the given key.
        """
        if not self.conversations:
            self.conversations = {}
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_conversations"
                self._dump_file(filename, self.conversations)
            else:
                self._dump_singlefile()

    def update_user_data(self, user_id: int, data: UD) -> None:
        """Will update the user_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:class:`telegram.ext.utils.types.UD`): The
                :attr:`telegram.ext.dispatcher.user_data` ``[user_id]``.
        """
        if self.user_data is None:
            self.user_data = defaultdict(self.context_types.user_data)
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_user_data"
                self._dump_file(filename, self.user_data)
            else:
                self._dump_singlefile()

    def update_chat_data(self, chat_id: int, data: CD) -> None:
        """Will update the chat_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:class:`telegram.ext.utils.types.CD`): The
                :attr:`telegram.ext.dispatcher.chat_data` ``[chat_id]``.
        """
        if self.chat_data is None:
            self.chat_data = defaultdict(self.context_types.chat_data)
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_chat_data"
                self._dump_file(filename, self.chat_data)
            else:
                self._dump_singlefile()

    def update_bot_data(self, data: BD) -> None:
        """Will update the bot_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            data (:class:`telegram.ext.utils.types.BD`): The
                :attr:`telegram.ext.dispatcher.bot_data`.
        """
        if self.bot_data == data:
            return
        self.bot_data = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_bot_data"
                self._dump_file(filename, self.bot_data)
            else:
                self._dump_singlefile()

    def update_callback_data(self, data: CDCData) -> None:
        """Will update the callback_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.

        .. versionadded:: 13.6

        Args:
            data (:class:`telegram.ext.utils.types.CDCData`:): The relevant data to restore
                :attr:`telegram.ext.dispatcher.bot.callback_data`.
        """
        if self.callback_data == data:
            return
        self.callback_data = (data[0], data[1].copy())
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_callback_data"
                self._dump_file(filename, self.callback_data)
            else:
                self._dump_singlefile()

    def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_user_data`
        """

    def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_chat_data`
        """

    def refresh_bot_data(self, bot_data: BD) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_bot_data`
        """

    def flush(self) -> None:
        """Will save all data in memory to pickle file(s)."""
        if self.single_file:
            if (
                self.user_data
                or self.chat_data
                or self.bot_data
                or self.callback_data
                or self.conversations
            ):
                self._dump_singlefile()
        else:
            if self.user_data:
                self._dump_file(f"{self.filename}_user_data", self.user_data)
            if self.chat_data:
                self._dump_file(f"{self.filename}_chat_data", self.chat_data)
            if self.bot_data:
                self._dump_file(f"{self.filename}_bot_data", self.bot_data)
            if self.callback_data:
                self._dump_file(f"{self.filename}_callback_data", self.callback_data)
            if self.conversations:
                self._dump_file(f"{self.filename}_conversations", self.conversations)
