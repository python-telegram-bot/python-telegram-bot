#!/usr/bin/env python
# pylint: disable=too-many-arguments
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""This module contains an object that represents a Telegram Bot with convenience extensions."""
from copy import copy
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    no_type_check,
)

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    InlineKeyboardMarkup,
    InputMedia,
    Message,
    MessageId,
    Poll,
    Update,
)
from telegram._utils.datetime import to_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.types import DVInput, JSONDict, ODVInput, ReplyMarkup
from telegram.ext._callbackdatacache import CallbackDataCache
from telegram.request import BaseRequest

if TYPE_CHECKING:
    from telegram import InlineQueryResult, MessageEntity
    from telegram.ext import Defaults

HandledTypes = TypeVar("HandledTypes", bound=Union[Message, CallbackQuery, Chat])


class ExtBot(Bot):
    """This object represents a Telegram Bot with convenience extensions.

    Warning:
        Not to be confused with :class:`telegram.Bot`.

    For the documentation of the arguments, methods and attributes, please see
    :class:`telegram.Bot`.

    .. versionadded:: 13.6

    Args:
        defaults (:class:`telegram.ext.Defaults`, optional): An object containing default values to
            be used if not set explicitly in the bot methods.
        arbitrary_callback_data (:obj:`bool` | :obj:`int`, optional): Whether to
            allow arbitrary objects as callback data for :class:`telegram.InlineKeyboardButton`.
            Pass an integer to specify the maximum number of objects cached in memory. For more
            details, please see our `wiki <https://github.com/python-telegram-bot\
                /python-telegram-bot/wiki/Arbitrary-callback_data>`_. Defaults to :obj:`False`.

    Attributes:
        arbitrary_callback_data (:obj:`bool` | :obj:`int`): Whether this bot instance
            allows to use arbitrary objects as callback data for
            :class:`telegram.InlineKeyboardButton`.
        callback_data_cache (:class:`telegram.ext.CallbackDataCache`): The cache for objects passed
            as callback data for :class:`telegram.InlineKeyboardButton`.

    """

    __slots__ = ("arbitrary_callback_data", "callback_data_cache", "_defaults")

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.telegram.org/bot",
        base_file_url: str = "https://api.telegram.org/file/bot",
        request: BaseRequest = None,
        get_updates_request: BaseRequest = None,
        private_key: bytes = None,
        private_key_password: bytes = None,
        defaults: "Defaults" = None,
        arbitrary_callback_data: Union[bool, int] = False,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            base_file_url=base_file_url,
            request=request,
            get_updates_request=get_updates_request,
            private_key=private_key,
            private_key_password=private_key_password,
        )
        self._defaults = defaults

        # set up callback_data
        if not isinstance(arbitrary_callback_data, bool):
            maxsize = cast(int, arbitrary_callback_data)
            self.arbitrary_callback_data = True
        else:
            maxsize = 1024
            self.arbitrary_callback_data = arbitrary_callback_data
        self.callback_data_cache: CallbackDataCache = CallbackDataCache(bot=self, maxsize=maxsize)

    @property
    def defaults(self) -> Optional["Defaults"]:
        """The :class:`telegram.ext.Defaults` used by this bot, if any."""
        # This is a property because defaults shouldn't be changed at runtime
        return self._defaults

    def _insert_defaults(self, data: Dict[str, object]) -> None:
        """Inserts the defaults values for optional kwargs for which tg.ext.Defaults provides
        convenience functionality, i.e. the kwargs with a tg.utils.helpers.DefaultValue default

        data is edited in-place. As timeout is not passed via the kwargs, it needs to be passed
        separately and gets returned.

        This can only work, if all kwargs that may have defaults are passed in data!
        """
        # if we have Defaults, we
        # 1) replace all DefaultValue instances with the relevant Defaults value. If there is none,
        #    we fall back to the default value of the bot method
        # 2) convert all datetime.datetime objects to timestamps wrt the correct default timezone
        # 3) set the correct parse_mode for all InputMedia objects
        for key, val in data.items():
            # 1)
            if isinstance(val, DefaultValue):
                data[key] = (
                    self.defaults.api_defaults.get(key, val.value)
                    if self.defaults
                    else DefaultValue.get_value(val)
                )

            # 2)
            elif isinstance(val, datetime):
                data[key] = to_timestamp(
                    val, tzinfo=self.defaults.tzinfo if self.defaults else None
                )

            # 3)
            elif isinstance(val, InputMedia) and val.parse_mode is DEFAULT_NONE:
                val.parse_mode = self.defaults.parse_mode if self.defaults else None
            elif key == "media" and isinstance(val, list):
                for media in val:
                    if media.parse_mode is DEFAULT_NONE:
                        media.parse_mode = self.defaults.parse_mode if self.defaults else None

    def _replace_keyboard(self, reply_markup: Optional[ReplyMarkup]) -> Optional[ReplyMarkup]:
        # If the reply_markup is an inline keyboard and we allow arbitrary callback data, let the
        # CallbackDataCache build a new keyboard with the data replaced. Otherwise return the input
        if isinstance(reply_markup, InlineKeyboardMarkup) and self.arbitrary_callback_data:
            return self.callback_data_cache.process_keyboard(reply_markup)

        return reply_markup

    def insert_callback_data(self, update: Update) -> None:
        """If this bot allows for arbitrary callback data, this inserts the cached data into all
        corresponding buttons within this update.

        Note:
            Checks :attr:`telegram.Message.via_bot` and :attr:`telegram.Message.from_user`
            to figure out if a) a reply markup exists and b) it was actually sent by this
            bot. If not, the message will be returned unchanged.

            Note that this will fail for channel posts, as :attr:`telegram.Message.from_user` is
            :obj:`None` for those! In the corresponding reply markups, the callback data will be
            replaced by :class:`telegram.ext.InvalidCallbackData`.

        Warning:
            *In place*, i.e. the passed :class:`telegram.Message` will be changed!

        Args:
            update (:class:`telegram.Update`): The update.

        """
        # The only incoming updates that can directly contain a message sent by the bot itself are:
        # * CallbackQueries
        # * Messages where the pinned_message is sent by the bot
        # * Messages where the reply_to_message is sent by the bot
        # * Messages where via_bot is the bot
        # Finally there is effective_chat.pinned message, but that's only returned in get_chat
        if update.callback_query:
            self._insert_callback_data(update.callback_query)
        # elif instead of if, as effective_message includes callback_query.message
        # and that has already been processed
        elif update.effective_message:
            self._insert_callback_data(update.effective_message)

    def _insert_callback_data(self, obj: HandledTypes) -> HandledTypes:
        if not self.arbitrary_callback_data:
            return obj

        if isinstance(obj, CallbackQuery):
            self.callback_data_cache.process_callback_query(obj)
            return obj  # type: ignore[return-value]

        if isinstance(obj, Message):
            if obj.reply_to_message:
                # reply_to_message can't contain further reply_to_messages, so no need to check
                self.callback_data_cache.process_message(obj.reply_to_message)
                if obj.reply_to_message.pinned_message:
                    # pinned messages can't contain reply_to_message, no need to check
                    self.callback_data_cache.process_message(obj.reply_to_message.pinned_message)
            if obj.pinned_message:
                # pinned messages can't contain reply_to_message, no need to check
                self.callback_data_cache.process_message(obj.pinned_message)

            # Finally, handle the message itself
            self.callback_data_cache.process_message(message=obj)
            return obj  # type: ignore[return-value]

        if isinstance(obj, Chat) and obj.pinned_message:
            self.callback_data_cache.process_message(obj.pinned_message)

        return obj

    async def _send_message(
        self,
        endpoint: str,
        data: JSONDict,
        reply_to_message_id: int = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[bool, Message]:
        # We override this method to call self._replace_keyboard and self._insert_callback_data.
        # This covers most methods that have a reply_markup
        result = await super()._send_message(
            endpoint=endpoint,
            data=data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=self._replace_keyboard(reply_markup),
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        if isinstance(result, Message):
            self._insert_callback_data(result)
        return result

    async def get_updates(
        self,
        offset: int = None,
        limit: int = None,
        timeout: float = None,
        allowed_updates: List[str] = None,
        *,
        read_timeout: float = 2,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[Update]:
        updates = await super().get_updates(
            offset=offset,
            limit=limit,
            timeout=timeout,
            allowed_updates=allowed_updates,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        for update in updates:
            self.insert_callback_data(update)

        return updates

    def _effective_inline_results(
        self,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        next_offset: str = None,
        current_offset: str = None,
    ) -> Tuple[Sequence["InlineQueryResult"], Optional[str]]:
        """This method is called by Bot.answer_inline_query to build the actual results list.
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
            # All currently existingInlineQueryResults have a reply_markup, but future ones
            # might not have. Better be save than sorry
            if not hasattr(result, "reply_markup"):
                results.append(result)
            else:
                # We build a new result in case the user wants to use the same object in
                # different places
                new_result = copy(result)
                markup = self._replace_keyboard(result.reply_markup)  # type: ignore[attr-defined]
                new_result.reply_markup = markup  # type: ignore[attr-defined]
                results.append(new_result)

        return results, next_offset

    @no_type_check  # mypy doesn't play too well with hasattr
    def _insert_defaults_for_ilq_results(self, res: "InlineQueryResult") -> None:
        """This method is called by Bot.answer_inline_query to replace `DefaultValue(obj)` with
        `obj`.
        Overriding this to call insert the actual desired default values.
        """
        if hasattr(res, "parse_mode") and res.parse_mode is DEFAULT_NONE:
            res.parse_mode = self.defaults.parse_mode if self.defaults else None
        if hasattr(res, "input_message_content") and res.input_message_content:
            if (
                hasattr(res.input_message_content, "parse_mode")
                and res.input_message_content.parse_mode is DEFAULT_NONE
            ):
                res.input_message_content.parse_mode = (
                    self.defaults.parse_mode if self.defaults else None
                )
            if (
                hasattr(res.input_message_content, "disable_web_page_preview")
                and res.input_message_content.disable_web_page_preview is DEFAULT_NONE
            ):
                res.input_message_content.disable_web_page_preview = (
                    self.defaults.disable_web_page_preview if self.defaults else None
                )

    async def stop_poll(
        self,
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Poll:
        # We override this method to call self._replace_keyboard
        return await super().stop_poll(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=self._replace_keyboard(reply_markup),
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple["MessageEntity", ...], List["MessageEntity"]] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> MessageId:
        # We override this method to call self._replace_keyboard
        return await super().copy_message(
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
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Chat:
        # We override this method to call self._insert_callback_data
        result = await super().get_chat(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return self._insert_callback_data(result)

    # updated camelCase aliases
    getChat = get_chat
    """Alias for :meth:`get_chat`"""
    copyMessage = copy_message
    """Alias for :meth:`copy_message`"""
    getUpdates = get_updates
    """Alias for :meth:`get_updates`"""
    stopPoll = stop_poll
    """Alias for :meth:`stop_poll`"""
