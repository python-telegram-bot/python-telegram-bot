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
from typing import Any, Dict, Optional, Tuple, overload, Mapping, cast, TypeVar, MutableMapping

from telegram.ext import BasePersistence
from telegram.utils.types import ConversationDict, CD, UD, BD, IntDD  # pylint: disable=W0611
from .contextcustomizer import ContextCustomizer

UDM = TypeVar('UDM', bound=MutableMapping)
CDM = TypeVar('CDM', bound=MutableMapping)


class PicklePersistence(BasePersistence[UD, CD, BD, UDM, CDM]):
    """Using python's builtin pickle for making you bot persistent.

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
        context_customizer (:class:`telegram.ext.ContextCustomizer`, optional): Pass an instance
            of :class:`telegram.ext.ContextCustomizer` to customize the the types used in the
            ``context`` interface.

            Note:
                The types for :attr:`telegram.ext.ContextCustomizer.user_data_mapping` and
                :attr:`telegram.ext.ContextCustomizer.chat_data_mapping` must be subclasses of
                :class:`collections.abc.MutableMapping` and support instantiation via

                .. code:: python

                    chat/user_data_mapping(chat/user_data_type[, data])

                where ``data`` is of type ``chat/user_data_mapping``.

            If not passed, the defaults documented in
            :class:`telegram.ext.ContextCustomizer` will be used.

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
        context_customizer (:class:`telegram.ext.ContextCustomizer`): Container for the types used
            in the ``context`` interface.
    """

    @overload
    def __init__(
        self: 'PicklePersistence[Dict, Dict, Dict, IntDD[Dict], IntDD[Dict]]',
        filename: str,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        single_file: bool = True,
        on_flush: bool = False,
    ):
        ...

    @overload
    def __init__(
        self: 'PicklePersistence[UD, CD, BD, UDM, CDM]',
        filename: str,
        store_user_data: bool = True,
        store_chat_data: bool = True,
        store_bot_data: bool = True,
        single_file: bool = True,
        on_flush: bool = False,
        context_customizer: ContextCustomizer[Any, UD, CD, BD, UDM, CDM] = None,
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
        context_customizer: ContextCustomizer[Any, UD, CD, BD, UDM, CDM] = None,
    ):
        super().__init__(
            store_user_data=store_user_data,
            store_chat_data=store_chat_data,
            store_bot_data=store_bot_data,
        )
        self.filename = filename
        self.single_file = single_file
        self.on_flush = on_flush
        self.user_data: Optional[MutableMapping[int, UD]] = None
        self.chat_data: Optional[MutableMapping[int, CD]] = None
        self.bot_data: Optional[BD] = None
        self.conversations: Optional[Dict[str, Dict[Tuple, Any]]] = None
        self.context_customizer = cast(
            ContextCustomizer[Any, UD, CD, BD, UDM, CDM], context_customizer or ContextCustomizer()
        )

    def load_singlefile(self) -> None:
        try:
            filename = self.filename
            with open(self.filename, "rb") as file:
                data = pickle.load(file)
                self.user_data = (
                    self.context_customizer.user_data_mapping(  # type: ignore[call-arg]
                        self.context_customizer.user_data, data['user_data']
                    )
                )
                self.chat_data = (
                    self.context_customizer.chat_data_mapping(  # type: ignore[call-arg]
                        self.context_customizer.chat_data, data['chat_data']
                    )
                )
                # For backwards compatibility with files not containing bot data
                self.bot_data = data.get('bot_data', {})
                self.conversations = data['conversations']
        except IOError:
            self.conversations = dict()
            self.user_data = self.context_customizer.user_data_mapping(  # type: ignore[call-arg]
                self.context_customizer.user_data
            )
            self.chat_data = self.context_customizer.chat_data_mapping(  # type: ignore[call-arg]
                self.context_customizer.chat_data
            )
            self.bot_data = self.context_customizer.bot_data()
        except pickle.UnpicklingError as exc:
            raise TypeError(f"File {filename} does not contain valid pickle data") from exc
        except Exception as exc:
            raise TypeError(f"Something went wrong unpickling {filename}") from exc

    @staticmethod
    def load_file(filename: str) -> Any:
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except IOError:
            return None
        except pickle.UnpicklingError as exc:
            raise TypeError(f"File {filename} does not contain valid pickle data") from exc
        except Exception as exc:
            raise TypeError(f"Something went wrong unpickling {filename}") from exc

    def dump_singlefile(self) -> None:
        with open(self.filename, "wb") as file:
            data = {
                'conversations': self.conversations,
                'user_data': self.user_data,
                'chat_data': self.chat_data,
                'bot_data': self.bot_data,
            }
            pickle.dump(data, file)

    @staticmethod
    def dump_file(filename: str, data: Any) -> None:
        with open(filename, "wb") as file:
            pickle.dump(data, file)

    def get_user_data(self) -> Mapping[int, UD]:
        """Returns the user_data from the pickle file if it exists or an empty :obj:`defaultdict`.

        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.user_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_user_data"
            data = self.load_file(filename)
            if not data:
                data = self.context_customizer.user_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.user_data
                )
            else:
                data = self.context_customizer.user_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.user_data, data
                )
            self.user_data = data
        else:
            self.load_singlefile()
        return self.user_data  # type: ignore[return-value]

    def get_chat_data(self) -> Mapping[int, CD]:
        """Returns the chat_data from the pickle file if it exists or an empty :obj:`defaultdict`.

        Returns:
            :obj:`defaultdict`: The restored chat data.
        """
        if self.chat_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_chat_data"
            data = self.load_file(filename)
            if not data:
                data = self.context_customizer.chat_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.chat_data
                )
            else:
                data = self.context_customizer.chat_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.chat_data, data
                )
            self.chat_data = data
        else:
            self.load_singlefile()
        return self.chat_data  # type: ignore[return-value]

    def get_bot_data(self) -> BD:
        """Returns the bot_data from the pickle file if it exists or an empty :obj:`dict`.

        Returns:
            :obj:`dict`: The restored bot data.
        """
        if self.bot_data:
            pass
        elif not self.single_file:
            filename = f"{self.filename}_bot_data"
            data = self.load_file(filename)
            if not data:
                data = {}
            self.bot_data = data
        else:
            self.load_singlefile()
        return self.bot_data  # type: ignore[return-value]

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
            filename = f"{self.filename}_conversations"
            data = self.load_file(filename)
            if not data:
                data = {name: {}}
            self.conversations = data
        else:
            self.load_singlefile()
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
            self.conversations = dict()
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_conversations"
                self.dump_file(filename, self.conversations)
            else:
                self.dump_singlefile()

    def update_user_data(self, user_id: int, data: UD) -> None:
        """Will update the user_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """
        if self.user_data is None:
            self.user_data = cast(
                MutableMapping[int, UD],
                self.context_customizer.user_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.user_data
                ),
            )
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_user_data"
                self.dump_file(filename, self.user_data)
            else:
                self.dump_singlefile()

    def update_chat_data(self, chat_id: int, data: CD) -> None:
        """Will update the chat_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        if self.chat_data is None:
            self.chat_data = cast(
                MutableMapping[int, CD],
                self.context_customizer.chat_data_mapping(  # type: ignore[call-arg]
                    self.context_customizer.chat_data
                ),
            )
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_chat_data"
                self.dump_file(filename, self.chat_data)
            else:
                self.dump_singlefile()

    def update_bot_data(self, data: BD) -> None:
        """Will update the bot_data and depending on :attr:`on_flush` save the pickle file.

        Args:
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.bot_data`.
        """
        if self.bot_data == data:
            return
        self.bot_data = data
        if not self.on_flush:
            if not self.single_file:
                filename = f"{self.filename}_bot_data"
                self.dump_file(filename, self.bot_data)
            else:
                self.dump_singlefile()

    def flush(self) -> None:
        """Will save all data in memory to pickle file(s)."""
        if self.single_file:
            if self.user_data or self.chat_data or self.bot_data or self.conversations:
                self.dump_singlefile()
        else:
            if self.user_data:
                self.dump_file(f"{self.filename}_user_data", self.user_data)
            if self.chat_data:
                self.dump_file(f"{self.filename}_chat_data", self.chat_data)
            if self.bot_data:
                self.dump_file(f"{self.filename}_bot_data", self.bot_data)
            if self.conversations:
                self.dump_file(f"{self.filename}_conversations", self.conversations)
