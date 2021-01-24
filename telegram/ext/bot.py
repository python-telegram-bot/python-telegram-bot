#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=E0611,E0213,E1102,C0103,E1101,R0913,R0904
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
# pylint: disable=C0112
"""This module contains an object that represents a Telegram Bot with convenience extensions."""
from copy import copy
from typing import Union, cast, List, Callable, Optional, Tuple

import telegram.bot
from telegram import (
    ReplyMarkup,
    Message,
    InlineKeyboardMarkup,
    Poll,
    MessageEntity,
    MessageId,
    InlineQueryResult,
    Update,
)
from telegram.ext.utils.callbackdatacache import CallbackDataCache
from telegram.utils.request import Request
from telegram.utils.types import JSONDict
from .defaults import Defaults


class Bot(telegram.bot.Bot):
    """This object represents a Telegram Bot with convenience extensions.

    For the documentation of the arguments, methods and attributes, please see
    :class:`telegram.Bot`.

    Args:
        defaults (:class:`telegram.ext.Defaults`, optional): An object containing default values to
            be used if not set explicitly in the bot methods.
        arbitrary_callback_data (:obj:`bool` | :obj:`int`, optional): Whether to
            allow arbitrary objects as callback data for :class:`telegram.InlineKeyboardButton`.
            Pass an integer to specify the maximum number objects cached in memory. For more info,
            please see our wiki. Defaults to :obj:`False`.

    """

    def __init__(
        self,
        token: str,
        base_url: str = None,
        base_file_url: str = None,
        request: Request = None,
        private_key: bytes = None,
        private_key_password: bytes = None,
        defaults: Defaults = None,
        arbitrary_callback_data: Union[bool, int] = False,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            base_file_url=base_file_url,
            request=request,
            private_key=private_key,
            private_key_password=private_key_password,
            defaults=defaults,
        )

        # set up callback_data
        if not isinstance(arbitrary_callback_data, bool):
            maxsize = cast(int, arbitrary_callback_data)
            self.arbitrary_callback_data = True
        else:
            maxsize = 1024
            self.arbitrary_callback_data = arbitrary_callback_data
        self.callback_data: CallbackDataCache = CallbackDataCache(maxsize=maxsize)

    def _replace_keyboard(self, reply_markup: Optional[ReplyMarkup]) -> Optional[ReplyMarkup]:
        # If the reply_markup is an inline keyboard and we allow arbitrary callback data, let the
        # CallbackDataCache build a new keyboard with the data replaced. Otherwise return the input
        if isinstance(reply_markup, ReplyMarkup):
            if self.arbitrary_callback_data and isinstance(reply_markup, InlineKeyboardMarkup):
                return self.callback_data.process_keyboard(reply_markup)

        return reply_markup

    def _message(
        self,
        endpoint: str,
        data: JSONDict,
        reply_to_message_id: Union[str, int] = None,
        disable_notification: bool = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: bool = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Union[bool, Message]:
        # We override this method to call self._replace_keyboard. This covers most methods that
        # have a reply_markup
        return super()._message(
            endpoint=endpoint,
            data=data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=self._replace_keyboard(reply_markup),
            allow_sending_without_reply=allow_sending_without_reply,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def get_updates(
        self,
        offset: int = None,
        limit: int = 100,
        timeout: float = 0,
        read_latency: float = 2.0,
        allowed_updates: List[str] = None,
        api_kwargs: JSONDict = None,
    ) -> List[Update]:
        """"""  # hide from docs
        updates = super().get_updates(
            offset=offset,
            limit=limit,
            timeout=timeout,
            read_latency=read_latency,
            allowed_updates=allowed_updates,
            api_kwargs=api_kwargs,
        )

        for update in updates:
            if update.callback_query:
                self.callback_data.process_callback_query(update.callback_query)

        return updates

    def _effective_inline_results(
        self,
        results: Union[
            List[InlineQueryResult], Callable[[int], Optional[List[InlineQueryResult]]]
        ],
        next_offset: str = None,
        current_offset: str = None,
    ) -> Tuple[List[InlineQueryResult], Optional[str]]:
        """
        This method is called by Bot.answer_inline_query to build the actual results list.
        Overriding this to call self._replace_keyboard suffices
        """
        effective_results, next_offset = super()._effective_inline_results(
            results=results, next_offset=next_offset, current_offset=current_offset
        )

        # Process arbitrary callback
        if not self.arbitrary_callback_data:
            return effective_results, next_offset
        results = []
        for result in effective_results:
            # Not all InlineQueryResults have a reply_markup, so we need to check
            if not hasattr(result, 'reply_markup'):
                results.append(result)
            else:
                # We build a new result in case the user wants to use the same object in
                # different places
                new_result = copy(result)
                markup = self._replace_keyboard(result.reply_markup)  # type: ignore[attr-defined]
                new_result.reply_markup = markup  # type: ignore[attr-defined]
                results.append(new_result)

        return results, next_offset

    def stop_poll(
        self,
        chat_id: Union[int, str],
        message_id: Union[int, str],
        reply_markup: InlineKeyboardMarkup = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> Poll:
        """"""  # hide from decs
        # We override this method to call self._replace_keyboard
        return super().stop_poll(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=self._replace_keyboard(reply_markup),
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: Union[str, int],
        caption: str = None,
        parse_mode: str = None,
        caption_entities: Union[Tuple[MessageEntity, ...], List[MessageEntity]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Union[int, str] = None,
        allow_sending_without_reply: bool = False,
        reply_markup: ReplyMarkup = None,
        timeout: float = None,
        api_kwargs: JSONDict = None,
    ) -> MessageId:
        """"""  # hide from docs
        # We override this method to call self._replace_keyboard
        return super().copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=self._replace_keyboard(reply_markup),
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
