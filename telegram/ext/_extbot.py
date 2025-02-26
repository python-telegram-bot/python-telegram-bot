#!/usr/bin/env python
# pylint: disable=too-many-arguments
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
import datetime as dtm
from collections.abc import Sequence
from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast,
    no_type_check,
    overload,
)
from uuid import uuid4

from telegram import (
    Animation,
    Audio,
    Bot,
    BotCommand,
    BotCommandScope,
    BotDescription,
    BotName,
    BotShortDescription,
    BusinessConnection,
    CallbackQuery,
    ChatAdministratorRights,
    ChatFullInfo,
    ChatInviteLink,
    ChatMember,
    ChatPermissions,
    ChatPhoto,
    Contact,
    Document,
    File,
    ForumTopic,
    GameHighScore,
    Gift,
    Gifts,
    InlineKeyboardMarkup,
    InlineQueryResultsButton,
    InputMedia,
    InputPollOption,
    LinkPreviewOptions,
    Location,
    MaskPosition,
    MenuButton,
    Message,
    MessageId,
    PhotoSize,
    Poll,
    PreparedInlineMessage,
    ReactionType,
    ReplyParameters,
    SentWebAppMessage,
    StarTransactions,
    Sticker,
    StickerSet,
    TelegramObject,
    Update,
    User,
    UserChatBoosts,
    UserProfilePhotos,
    Venue,
    Video,
    VideoNote,
    Voice,
    WebhookInfo,
)
from telegram._utils.datetime import to_timestamp
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.logging import get_logger
from telegram._utils.repr import build_repr_with_selected_attrs
from telegram._utils.types import (
    BaseUrl,
    CorrectOptionID,
    FileInput,
    JSONDict,
    ODVInput,
    ReplyMarkup,
    TimePeriod,
)
from telegram.ext._callbackdatacache import CallbackDataCache
from telegram.ext._utils.types import RLARGS
from telegram.request import BaseRequest
from telegram.warnings import PTBUserWarning

if TYPE_CHECKING:
    from telegram import (
        InlineQueryResult,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        InputPaidMedia,
        InputSticker,
        LabeledPrice,
        MessageEntity,
        PassportElementError,
        ShippingOption,
    )
    from telegram.ext import BaseRateLimiter, Defaults

HandledTypes = TypeVar("HandledTypes", bound=Union[Message, CallbackQuery, ChatFullInfo])
KT = TypeVar("KT", bound=ReplyMarkup)


class ExtBot(Bot, Generic[RLARGS]):
    """This object represents a Telegram Bot with convenience extensions.

    Warning:
        Not to be confused with :class:`telegram.Bot`.

    For the documentation of the arguments, methods and attributes, please see
    :class:`telegram.Bot`.

    All API methods of this class have an additional keyword argument ``rate_limit_args``.
    This can be used to pass additional information to the rate limiter, specifically to
    :paramref:`telegram.ext.BaseRateLimiter.process_request.rate_limit_args`.

    This class is a :class:`~typing.Generic` class and accepts one type variable that specifies
    the generic type of the :attr:`rate_limiter` used by the bot. Use :obj:`None` if no rate
    limiter is used.

    Warning:
        * The keyword argument ``rate_limit_args`` can `not` be used, if :attr:`rate_limiter`
          is :obj:`None`.
        * The method :meth:`~telegram.Bot.get_updates` is the only method that does not have the
          additional argument, as this method will never be rate limited.

    Examples:
        :any:`Arbitrary Callback Data Bot <examples.arbitrarycallbackdatabot>`

    .. seealso:: :wiki:`Arbitrary callback_data <Arbitrary-callback_data>`

    .. versionadded:: 13.6

    .. versionchanged:: 20.0
        Removed the attribute ``arbitrary_callback_data``. You can instead use
        :attr:`bot.callback_data_cache.maxsize <telegram.ext.CallbackDataCache.maxsize>` to
        access the size of the cache.

    .. versionchanged:: 20.5
        Removed deprecated methods ``set_sticker_set_thumb`` and ``setStickerSetThumb``.

    Args:
        defaults (:class:`telegram.ext.Defaults`, optional): An object containing default values to
            be used if not set explicitly in the bot methods.
        arbitrary_callback_data (:obj:`bool` | :obj:`int`, optional): Whether to
            allow arbitrary objects as callback data for :class:`telegram.InlineKeyboardButton`.
            Pass an integer to specify the maximum number of objects cached in memory.
            Defaults to :obj:`False`.

            .. seealso:: :wiki:`Arbitrary callback_data <Arbitrary-callback_data>`
        rate_limiter (:class:`telegram.ext.BaseRateLimiter`, optional): A rate limiter to use for
            limiting the number of requests made by the bot per time interval.

            .. versionadded:: 20.0

    """

    __slots__ = ("_callback_data_cache", "_defaults", "_rate_limiter")

    _LOGGER = get_logger(__name__, class_name="ExtBot")

    # using object() would be a tiny bit safer, but a string plays better with the typing setup
    __RL_KEY = uuid4().hex

    @overload
    def __init__(
        self: "ExtBot[None]",
        token: str,
        base_url: BaseUrl = "https://api.telegram.org/bot",
        base_file_url: BaseUrl = "https://api.telegram.org/file/bot",
        request: Optional[BaseRequest] = None,
        get_updates_request: Optional[BaseRequest] = None,
        private_key: Optional[bytes] = None,
        private_key_password: Optional[bytes] = None,
        defaults: Optional["Defaults"] = None,
        arbitrary_callback_data: Union[bool, int] = False,
        local_mode: bool = False,
    ): ...

    @overload
    def __init__(
        self: "ExtBot[RLARGS]",
        token: str,
        base_url: BaseUrl = "https://api.telegram.org/bot",
        base_file_url: BaseUrl = "https://api.telegram.org/file/bot",
        request: Optional[BaseRequest] = None,
        get_updates_request: Optional[BaseRequest] = None,
        private_key: Optional[bytes] = None,
        private_key_password: Optional[bytes] = None,
        defaults: Optional["Defaults"] = None,
        arbitrary_callback_data: Union[bool, int] = False,
        local_mode: bool = False,
        rate_limiter: Optional["BaseRateLimiter[RLARGS]"] = None,
    ): ...

    def __init__(
        self,
        token: str,
        base_url: BaseUrl = "https://api.telegram.org/bot",
        base_file_url: BaseUrl = "https://api.telegram.org/file/bot",
        request: Optional[BaseRequest] = None,
        get_updates_request: Optional[BaseRequest] = None,
        private_key: Optional[bytes] = None,
        private_key_password: Optional[bytes] = None,
        defaults: Optional["Defaults"] = None,
        arbitrary_callback_data: Union[bool, int] = False,
        local_mode: bool = False,
        rate_limiter: Optional["BaseRateLimiter[RLARGS]"] = None,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            base_file_url=base_file_url,
            request=request,
            get_updates_request=get_updates_request,
            private_key=private_key,
            private_key_password=private_key_password,
            local_mode=local_mode,
        )
        with self._unfrozen():
            self._defaults: Optional[Defaults] = defaults
            self._rate_limiter: Optional[BaseRateLimiter] = rate_limiter
            self._callback_data_cache: Optional[CallbackDataCache] = None

            # set up callback_data
            if arbitrary_callback_data is False:
                return

            if not isinstance(arbitrary_callback_data, bool):
                maxsize = cast(int, arbitrary_callback_data)
            else:
                maxsize = 1024

            self._callback_data_cache = CallbackDataCache(bot=self, maxsize=maxsize)

    def __repr__(self) -> str:
        """Give a string representation of the bot in the form ``ExtBot[token=...]``.

        As this class doesn't implement :meth:`object.__str__`, the default implementation
        will be used, which is equivalent to :meth:`__repr__`.

        Returns:
            :obj:`str`
        """
        return build_repr_with_selected_attrs(self, token=self.token)

    @classmethod
    def _warn(
        cls,
        message: Union[str, PTBUserWarning],
        category: type[Warning] = PTBUserWarning,
        stacklevel: int = 0,
    ) -> None:
        """We override this method to add one more level to the stacklevel, so that the warning
        points to the user's code, not to the PTB code.
        """
        super()._warn(message=message, category=category, stacklevel=stacklevel + 2)

    @property
    def callback_data_cache(self) -> Optional[CallbackDataCache]:
        """:class:`telegram.ext.CallbackDataCache`: Optional. The cache for
        objects passed as callback data for :class:`telegram.InlineKeyboardButton`.

        Examples:
            :any:`Arbitrary Callback Data Bot <examples.arbitrarycallbackdatabot>`

        .. versionchanged:: 20.0
           * This property is now read-only.
           * This property is now optional and can be :obj:`None` if
             :paramref:`~telegram.ext.ExtBot.arbitrary_callback_data` is set to :obj:`False`.
        """
        return self._callback_data_cache

    async def initialize(self) -> None:
        """See :meth:`telegram.Bot.initialize`. Also initializes the
        :paramref:`ExtBot.rate_limiter` (if set)
        by calling :meth:`telegram.ext.BaseRateLimiter.initialize`.
        """
        # Initialize before calling super, because super calls get_me
        if self.rate_limiter:
            await self.rate_limiter.initialize()
        await super().initialize()

    async def shutdown(self) -> None:
        """See :meth:`telegram.Bot.shutdown`. Also shuts down the
        :paramref:`ExtBot.rate_limiter` (if set) by
        calling :meth:`telegram.ext.BaseRateLimiter.shutdown`.
        """
        # Shut down the rate limiter before shutting down the request objects!
        if self.rate_limiter:
            await self.rate_limiter.shutdown()
        await super().shutdown()

    @classmethod
    def _merge_api_rl_kwargs(
        cls, api_kwargs: Optional[JSONDict], rate_limit_args: Optional[RLARGS]
    ) -> Optional[JSONDict]:
        """Inserts the `rate_limit_args` into `api_kwargs` with the special key `__RL_KEY` so
        that we can extract them later without having to modify the `telegram.Bot` class.
        """
        if not rate_limit_args:
            return api_kwargs
        if api_kwargs is None:
            api_kwargs = {}
        api_kwargs[cls.__RL_KEY] = rate_limit_args
        return api_kwargs

    @classmethod
    def _extract_rl_kwargs(cls, data: Optional[JSONDict]) -> Optional[RLARGS]:
        """Extracts the `rate_limit_args` from `data` if it exists."""
        if not data:
            return None
        return data.pop(cls.__RL_KEY, None)

    async def _do_post(
        self,
        endpoint: str,
        data: JSONDict,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> Union[bool, JSONDict, list[JSONDict]]:
        """Order of method calls is: Bot.some_method -> Bot._post -> Bot._do_post.
        So we can override Bot._do_post to add rate limiting.
        """
        rate_limit_args = self._extract_rl_kwargs(data)
        if not self.rate_limiter and rate_limit_args is not None:
            raise ValueError(
                "`rate_limit_args` can only be used if a `ExtBot.rate_limiter` is set."
            )

        # getting updates should not be rate limited!
        if endpoint == "getUpdates" or not self.rate_limiter:
            return await super()._do_post(
                endpoint=endpoint,
                data=data,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                read_timeout=read_timeout,
            )

        kwargs = {
            "read_timeout": read_timeout,
            "write_timeout": write_timeout,
            "connect_timeout": connect_timeout,
            "pool_timeout": pool_timeout,
        }
        self._LOGGER.debug(
            "Passing request through rate limiter of type %s with rate_limit_args %s",
            type(self.rate_limiter),
            rate_limit_args,
        )
        return await self.rate_limiter.process_request(
            callback=super()._do_post,
            args=(endpoint, data),
            kwargs=kwargs,
            endpoint=endpoint,
            data=data,
            rate_limit_args=rate_limit_args,
        )

    @property
    def defaults(self) -> Optional["Defaults"]:
        """The :class:`telegram.ext.Defaults` used by this bot, if any."""
        # This is a property because defaults shouldn't be changed at runtime
        return self._defaults

    @property
    def rate_limiter(self) -> Optional["BaseRateLimiter[RLARGS]"]:
        """The :class:`telegram.ext.BaseRateLimiter` used by this bot, if any.

        .. versionadded:: 20.0
        """
        # This is a property because the rate limiter shouldn't be changed at runtime
        return self._rate_limiter

    def _merge_lpo_defaults(
        self, lpo: ODVInput[LinkPreviewOptions]
    ) -> Optional[LinkPreviewOptions]:
        # This is a standalone method because both _insert_defaults and
        # _insert_defaults_for_ilq_results need this logic
        #
        # If Defaults.LPO is set, and LPO is passed in the bot method we should fuse
        # them, giving precedence to passed values.
        # Defaults.LPO(True, "google.com", True) & LPO=LPO(True, ..., False) ->
        # LPO(True, "google.com", False)
        if self.defaults is None or (defaults_lpo := self.defaults.link_preview_options) is None:
            return DefaultValue.get_value(lpo)
        return LinkPreviewOptions(
            **{
                attr: (
                    getattr(defaults_lpo, attr)
                    # only use the default value
                    # if the value was explicitly passed to the LPO object
                    if isinstance(orig_attr := getattr(lpo, attr), DefaultValue)
                    else orig_attr
                )
                for attr in defaults_lpo.__slots__
            }
        )

    def _insert_defaults(self, data: dict[str, object]) -> None:
        """Inserts the defaults values for optional kwargs for which tg.ext.Defaults provides
        convenience functionality, i.e. the kwargs with a tg.utils.helpers.DefaultValue default

        data is edited in-place. As timeout is not passed via the kwargs, it needs to be passed
        separately and gets returned.

        This can only work, if all kwargs that may have defaults are passed in data!
        """
        if self.defaults is None:
            # If we have no defaults to insert, the behavior is the same as in `tg.Bot`
            super()._insert_defaults(data)
            return

        # if we have Defaults, we
        # 1) replace all DefaultValue instances with the relevant Defaults value. If there is none,
        #    we fall back to the default value of the bot method
        # 2) convert all datetime.datetime objects to timestamps wrt the correct default timezone
        # 3) set the correct parse_mode for all InputMedia objects
        # 4) handle the LinkPreviewOptions case (see below)
        # 5) handle the ReplyParameters case (see below)
        # 6) handle text_parse_mode in InputPollOption
        for key, val in data.items():
            # 1)
            if isinstance(val, DefaultValue):
                data[key] = self.defaults.api_defaults.get(key, val.value)

            # 2)
            elif isinstance(val, dtm.datetime):
                data[key] = to_timestamp(val, tzinfo=self.defaults.tzinfo)

            # 3)
            elif isinstance(val, InputMedia) and val.parse_mode is DEFAULT_NONE:
                # Copy object as not to edit it in-place
                copied_val = copy(val)
                with copied_val._unfrozen():
                    copied_val.parse_mode = self.defaults.parse_mode
                data[key] = copied_val
            elif key == "media" and isinstance(val, Sequence):
                # Copy objects as not to edit them in-place
                copy_list = [copy(media) for media in val]
                for media in copy_list:
                    if media.parse_mode is DEFAULT_NONE:
                        with media._unfrozen():
                            media.parse_mode = self.defaults.parse_mode

                data[key] = copy_list

            # 4) LinkPreviewOptions:
            elif isinstance(val, LinkPreviewOptions):
                data[key] = self._merge_lpo_defaults(val)

            # 5)
            # Similar to LinkPreviewOptions, but only two of the arguments of RPs have a default
            elif isinstance(val, ReplyParameters) and (
                (defaults_aswr := self.defaults.allow_sending_without_reply) is not None
                or self.defaults.quote_parse_mode is not None
            ):
                new_value = copy(val)
                with new_value._unfrozen():
                    new_value.allow_sending_without_reply = (
                        defaults_aswr
                        if isinstance(val.allow_sending_without_reply, DefaultValue)
                        else val.allow_sending_without_reply
                    )
                    new_value.quote_parse_mode = (
                        self.defaults.quote_parse_mode
                        if isinstance(val.quote_parse_mode, DefaultValue)
                        else val.quote_parse_mode
                    )

                data[key] = new_value

            # 6)
            elif isinstance(val, Sequence) and all(
                isinstance(obj, InputPollOption) for obj in val
            ):
                new_val = []
                for option in val:
                    if not isinstance(option.text_parse_mode, DefaultValue):
                        new_val.append(option)
                    else:
                        new_option = copy(option)
                        with new_option._unfrozen():
                            new_option.text_parse_mode = self.defaults.text_parse_mode
                        new_val.append(new_option)
                data[key] = new_val

    def _replace_keyboard(self, reply_markup: Optional[KT]) -> Optional[KT]:
        # If the reply_markup is an inline keyboard and we allow arbitrary callback data, let the
        # CallbackDataCache build a new keyboard with the data replaced. Otherwise return the input
        if isinstance(reply_markup, InlineKeyboardMarkup) and self.callback_data_cache is not None:
            # for some reason mypy doesn't understand that IKB is a subtype of Optional[KT]
            return self.callback_data_cache.process_keyboard(  # type: ignore[return-value]
                reply_markup
            )

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
        if self.callback_data_cache is None:
            return obj

        if isinstance(obj, CallbackQuery):
            self.callback_data_cache.process_callback_query(obj)
            return obj  # type: ignore[return-value]

        if isinstance(obj, Message):
            if obj.reply_to_message:
                # reply_to_message can't contain further reply_to_messages, so no need to check
                self.callback_data_cache.process_message(obj.reply_to_message)
                if isinstance(obj.reply_to_message.pinned_message, Message):
                    # pinned messages can't contain reply_to_message, no need to check
                    self.callback_data_cache.process_message(obj.reply_to_message.pinned_message)
            if isinstance(obj.pinned_message, Message):
                # pinned messages can't contain reply_to_message, no need to check
                self.callback_data_cache.process_message(obj.pinned_message)

            # Finally, handle the message itself
            self.callback_data_cache.process_message(message=obj)
            return obj  # type: ignore[return-value]

        if isinstance(obj, ChatFullInfo) and obj.pinned_message:
            self.callback_data_cache.process_message(obj.pinned_message)

        return obj

    async def _send_message(
        self,
        endpoint: str,
        data: JSONDict,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        link_preview_options: ODVInput["LinkPreviewOptions"] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Any:
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
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            link_preview_options=link_preview_options,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )
        if isinstance(result, Message):
            self._insert_callback_data(result)
        return result

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[Sequence[str]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> tuple[Update, ...]:
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
        next_offset: Optional[str] = None,
        current_offset: Optional[str] = None,
    ) -> tuple[Sequence["InlineQueryResult"], Optional[str]]:
        """This method is called by Bot.answer_inline_query to build the actual results list.
        Overriding this to call self._replace_keyboard suffices
        """
        effective_results, next_offset = super()._effective_inline_results(
            results=results, next_offset=next_offset, current_offset=current_offset
        )

        # Process arbitrary callback
        if self.callback_data_cache is None:
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
                with new_result._unfrozen():
                    markup = self._replace_keyboard(result.reply_markup)
                    new_result.reply_markup = markup

                results.append(new_result)

        return results, next_offset

    @no_type_check  # mypy doesn't play too well with hasattr
    def _insert_defaults_for_ilq_results(self, res: "InlineQueryResult") -> "InlineQueryResult":
        """This method is called by Bot.answer_inline_query to replace `DefaultValue(obj)` with
        `obj`.
        Overriding this to call insert the actual desired default values.
        """
        if self.defaults is None:
            # If we have no defaults to insert, the behavior is the same as in `tg.Bot`
            return super()._insert_defaults_for_ilq_results(res)

        # Copy the objects that need modification to avoid modifying the original object
        copied = False
        if hasattr(res, "parse_mode") and res.parse_mode is DEFAULT_NONE:
            res = copy(res)
            with res._unfrozen():
                copied = True
                res.parse_mode = self.defaults.parse_mode
        if hasattr(res, "input_message_content") and res.input_message_content:
            if (
                hasattr(res.input_message_content, "parse_mode")
                and res.input_message_content.parse_mode is DEFAULT_NONE
            ):
                if not copied:
                    res = copy(res)
                    copied = True
                with res.input_message_content._unfrozen():
                    res.input_message_content.parse_mode = self.defaults.parse_mode
            if hasattr(res.input_message_content, "link_preview_options"):
                if not copied:
                    res = copy(res)
                with res.input_message_content._unfrozen():
                    if res.input_message_content.link_preview_options is DEFAULT_NONE:
                        res.input_message_content.link_preview_options = (
                            self.defaults.link_preview_options
                        )
                    else:
                        # merge the existing options with the defaults
                        res.input_message_content.link_preview_options = self._merge_lpo_defaults(
                            res.input_message_content.link_preview_options
                        )

        return res

    async def do_api_request(
        self,
        endpoint: str,
        api_kwargs: Optional[JSONDict] = None,
        return_type: Optional[type[TelegramObject]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Any:
        return await super().do_api_request(
            endpoint=endpoint,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            return_type=return_type,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

    async def stop_poll(
        self,
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Poll:
        # We override this method to call self._replace_keyboard
        return await super().stop_poll(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=self._replace_keyboard(reply_markup),
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        show_caption_above_media: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> MessageId:
        # We override this method to call self._replace_keyboard
        return await super().copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            video_start_timestamp=video_start_timestamp,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=self._replace_keyboard(reply_markup),
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            show_caption_above_media=show_caption_above_media,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def copy_messages(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        remove_caption: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple["MessageId", ...]:
        # We override this method to call self._replace_keyboard
        return await super().copy_messages(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            remove_caption=remove_caption,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatFullInfo:
        # We override this method to call self._insert_callback_data
        result = await super().get_chat(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )
        return self._insert_callback_data(result)

    async def add_sticker_to_set(
        self,
        user_id: int,
        name: str,
        sticker: "InputSticker",
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().add_sticker_to_set(
            user_id=user_id,
            name=name,
            sticker=sticker,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[TimePeriod] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().answer_callback_query(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        cache_time: Optional[TimePeriod] = None,
        is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        button: Optional[InlineQueryResultsButton] = None,
        *,
        current_offset: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().answer_inline_query(
            inline_query_id=inline_query_id,
            results=results,
            cache_time=cache_time,
            is_personal=is_personal,
            next_offset=next_offset,
            current_offset=current_offset,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            button=button,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def save_prepared_inline_message(
        self,
        user_id: int,
        result: "InlineQueryResult",
        allow_user_chats: Optional[bool] = None,
        allow_bot_chats: Optional[bool] = None,
        allow_group_chats: Optional[bool] = None,
        allow_channel_chats: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> PreparedInlineMessage:
        return await super().save_prepared_inline_message(
            user_id=user_id,
            result=result,
            allow_user_chats=allow_user_chats,
            allow_bot_chats=allow_bot_chats,
            allow_group_chats=allow_group_chats,
            allow_channel_chats=allow_channel_chats,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            error_message=error_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def answer_shipping_query(
        self,
        shipping_query_id: str,
        ok: bool,
        shipping_options: Optional[Sequence["ShippingOption"]] = None,
        error_message: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().answer_shipping_query(
            shipping_query_id=shipping_query_id,
            ok=ok,
            shipping_options=shipping_options,
            error_message=error_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def answer_web_app_query(
        self,
        web_app_query_id: str,
        result: "InlineQueryResult",
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> SentWebAppMessage:
        return await super().answer_web_app_query(
            web_app_query_id=web_app_query_id,
            result=result,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def approve_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().approve_chat_join_request(
            chat_id=chat_id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def ban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        until_date: Optional[Union[int, dtm.datetime]] = None,
        revoke_messages: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().ban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            revoke_messages=revoke_messages,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def ban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().ban_chat_sender_chat(
            chat_id=chat_id,
            sender_chat_id=sender_chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def create_chat_invite_link(
        self,
        chat_id: Union[str, int],
        expire_date: Optional[Union[int, dtm.datetime]] = None,
        member_limit: Optional[int] = None,
        name: Optional[str] = None,
        creates_join_request: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatInviteLink:
        return await super().create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expire_date,
            member_limit=member_limit,
            name=name,
            creates_join_request=creates_join_request,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: Optional[str],
        currency: str,
        prices: Sequence["LabeledPrice"],
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Sequence[int]] = None,
        provider_data: Optional[Union[str, object]] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        subscription_period: Optional[TimePeriod] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> str:
        return await super().create_invoice_link(
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            provider_data=provider_data,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            subscription_period=subscription_period,
            business_connection_id=business_connection_id,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def create_new_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        stickers: Sequence["InputSticker"],
        sticker_type: Optional[str] = None,
        needs_repainting: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().create_new_sticker_set(
            user_id=user_id,
            name=name,
            title=title,
            stickers=stickers,
            sticker_type=sticker_type,
            needs_repainting=needs_repainting,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def decline_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().decline_chat_join_request(
            chat_id=chat_id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_chat_photo(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_chat_photo(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_chat_sticker_set(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_forum_topic(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_message(
            chat_id=chat_id,
            message_id=message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_messages(
        self,
        chat_id: Union[str, int],
        message_ids: Sequence[int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_my_commands(
        self,
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_my_commands(
            scope=scope,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_sticker_from_set(
        self,
        sticker: Union[str, "Sticker"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_sticker_from_set(
            sticker=sticker,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_webhook(
        self,
        drop_pending_updates: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_webhook(
            drop_pending_updates=drop_pending_updates,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        expire_date: Optional[Union[int, dtm.datetime]] = None,
        member_limit: Optional[int] = None,
        name: Optional[str] = None,
        creates_join_request: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatInviteLink:
        return await super().edit_chat_invite_link(
            chat_id=chat_id,
            invite_link=invite_link,
            expire_date=expire_date,
            member_limit=member_limit,
            name=name,
            creates_join_request=creates_join_request,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        name: Optional[str] = None,
        icon_custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().edit_forum_topic(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            name=name,
            icon_custom_emoji_id=icon_custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_general_forum_topic(
        self,
        chat_id: Union[str, int],
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().edit_general_forum_topic(
            chat_id=chat_id,
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_message_caption(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        show_caption_above_media: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            show_caption_above_media=show_caption_above_media,
        )

    async def edit_message_live_location(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        live_period: Optional[TimePeriod] = None,
        business_connection_id: Optional[str] = None,
        *,
        location: Optional[Location] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().edit_message_live_location(
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            latitude=latitude,
            longitude=longitude,
            reply_markup=reply_markup,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            live_period=live_period,
            location=location,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_message_media(
        self,
        media: "InputMedia",
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().edit_message_media(
            media=media,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=reply_markup,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_message_reply_markup(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=reply_markup,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        entities: Optional[Sequence["MessageEntity"]] = None,
        link_preview_options: ODVInput["LinkPreviewOptions"] = DEFAULT_NONE,
        business_connection_id: Optional[str] = None,
        *,
        disable_web_page_preview: Optional[bool] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            entities=entities,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            link_preview_options=link_preview_options,
        )

    async def export_chat_invite_link(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> str:
        return await super().export_chat_invite_link(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().forward_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            video_start_timestamp=video_start_timestamp,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def forward_messages(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[MessageId, ...]:
        return await super().forward_messages(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_chat_administrators(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[ChatMember, ...]:
        return await super().get_chat_administrators(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatMember:
        return await super().get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_chat_member_count(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> int:
        return await super().get_chat_member_count(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_chat_menu_button(
        self,
        chat_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> MenuButton:
        return await super().get_chat_menu_button(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_file(
        self,
        file_id: Union[
            str, Animation, Audio, ChatPhoto, Document, PhotoSize, Sticker, Video, VideoNote, Voice
        ],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> File:
        return await super().get_file(
            file_id=file_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_forum_topic_icon_stickers(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[Sticker, ...]:
        return await super().get_forum_topic_icon_stickers(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_game_high_scores(
        self,
        user_id: int,
        chat_id: Optional[int] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[GameHighScore, ...]:
        return await super().get_game_high_scores(
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_me(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> User:
        return await super().get_me(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_my_commands(
        self,
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[BotCommand, ...]:
        return await super().get_my_commands(
            scope=scope,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_my_default_administrator_rights(
        self,
        for_channels: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatAdministratorRights:
        return await super().get_my_default_administrator_rights(
            for_channels=for_channels,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_sticker_set(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> StickerSet:
        return await super().get_sticker_set(
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_custom_emoji_stickers(
        self,
        custom_emoji_ids: Sequence[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> tuple[Sticker, ...]:
        return await super().get_custom_emoji_stickers(
            custom_emoji_ids=custom_emoji_ids,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_user_profile_photos(
        self,
        user_id: int,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> UserProfilePhotos:
        return await super().get_user_profile_photos(
            user_id=user_id,
            offset=offset,
            limit=limit,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_webhook_info(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> WebhookInfo:
        return await super().get_webhook_info(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def leave_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().leave_chat(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def log_out(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().log_out(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def close(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().close(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def close_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().close_forum_topic(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def close_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().close_general_forum_topic(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def create_forum_topic(
        self,
        chat_id: Union[str, int],
        name: str,
        icon_color: Optional[int] = None,
        icon_custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ForumTopic:
        return await super().create_forum_topic(
            chat_id=chat_id,
            name=name,
            icon_color=icon_color,
            icon_custom_emoji_id=icon_custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def reopen_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().reopen_general_forum_topic(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def hide_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().hide_general_forum_topic(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unhide_general_forum_topic(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unhide_general_forum_topic(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def pin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().pin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            business_connection_id=business_connection_id,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def promote_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        is_anonymous: Optional[bool] = None,
        can_manage_chat: Optional[bool] = None,
        can_manage_video_chats: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
        can_post_stories: Optional[bool] = None,
        can_edit_stories: Optional[bool] = None,
        can_delete_stories: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().promote_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
            is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_manage_video_chats=can_manage_video_chats,
            can_manage_topics=can_manage_topics,
            can_post_stories=can_post_stories,
            can_edit_stories=can_edit_stories,
            can_delete_stories=can_delete_stories,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def reopen_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().reopen_forum_topic(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def restrict_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        permissions: ChatPermissions,
        until_date: Optional[Union[int, dtm.datetime]] = None,
        use_independent_chat_permissions: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_date,
            use_independent_chat_permissions=use_independent_chat_permissions,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def revoke_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatInviteLink:
        return await super().revoke_chat_invite_link(
            chat_id=chat_id,
            invite_link=invite_link,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def send_animation(
        self,
        chat_id: Union[int, str],
        animation: Union[FileInput, "Animation"],
        duration: Optional[TimePeriod] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_animation(
            chat_id=chat_id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
            reply_parameters=reply_parameters,
            filename=filename,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            business_connection_id=business_connection_id,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_audio(
        self,
        chat_id: Union[int, str],
        audio: Union[FileInput, "Audio"],
        duration: Optional[TimePeriod] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_audio(
            chat_id=chat_id,
            audio=audio,
            duration=duration,
            performer=performer,
            business_connection_id=business_connection_id,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
            reply_parameters=reply_parameters,
            filename=filename,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str,
        message_thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().send_chat_action(
            chat_id=chat_id,
            business_connection_id=business_connection_id,
            action=action,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def send_contact(
        self,
        chat_id: Union[int, str],
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        vcard: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        contact: Optional[Contact] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_contact(
            chat_id=chat_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            vcard=vcard,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            contact=contact,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            business_connection_id=business_connection_id,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_dice(
        self,
        chat_id: Union[int, str],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        emoji: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_dice(
            chat_id=chat_id,
            disable_notification=disable_notification,
            business_connection_id=business_connection_id,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            emoji=emoji,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[FileInput, "Document"],
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: Optional[bool] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            business_connection_id=business_connection_id,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
            reply_parameters=reply_parameters,
            filename=filename,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_game(
        self,
        chat_id: int,
        game_short_name: str,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_game(
            chat_id=chat_id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            business_connection_id=business_connection_id,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_invoice(
        self,
        chat_id: Union[int, str],
        title: str,
        description: str,
        payload: str,
        provider_token: Optional[str],
        currency: str,
        prices: Sequence["LabeledPrice"],
        start_parameter: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        provider_data: Optional[Union[str, object]] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Sequence[int]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            start_parameter=start_parameter,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_location(
        self,
        chat_id: Union[int, str],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        live_period: Optional[TimePeriod] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        location: Optional[Location] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_location(
            chat_id=chat_id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            live_period=live_period,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            location=location,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            business_connection_id=business_connection_id,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_media_group(
        self,
        chat_id: Union[int, str],
        media: Sequence[
            Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
    ) -> tuple[Message, ...]:
        return await super().send_media_group(
            chat_id=chat_id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            caption=caption,
            business_connection_id=business_connection_id,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        message_thread_id: Optional[int] = None,
        link_preview_options: ODVInput["LinkPreviewOptions"] = DEFAULT_NONE,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        disable_web_page_preview: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            business_connection_id=business_connection_id,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            link_preview_options=link_preview_options,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[FileInput, "PhotoSize"],
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            reply_parameters=reply_parameters,
            filename=filename,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_poll(
        self,
        chat_id: Union[int, str],
        question: str,
        options: Sequence[Union[str, "InputPollOption"]],
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[CorrectOptionID] = None,
        is_closed: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        explanation: Optional[str] = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: Optional[TimePeriod] = None,
        close_date: Optional[Union[int, dtm.datetime]] = None,
        explanation_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        question_parse_mode: ODVInput[str] = DEFAULT_NONE,
        question_entities: Optional[Sequence["MessageEntity"]] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            type=type,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
            business_connection_id=business_connection_id,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            question_parse_mode=question_parse_mode,
            question_entities=question_entities,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_sticker(
        self,
        chat_id: Union[int, str],
        sticker: Union[FileInput, "Sticker"],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        emoji: Optional[str] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_sticker(
            chat_id=chat_id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            business_connection_id=business_connection_id,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            emoji=emoji,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_venue(
        self,
        chat_id: Union[int, str],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        title: Optional[str] = None,
        address: Optional[str] = None,
        foursquare_id: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        foursquare_type: Optional[str] = None,
        google_place_id: Optional[str] = None,
        google_place_type: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        venue: Optional[Venue] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_venue(
            chat_id=chat_id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            foursquare_type=foursquare_type,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            business_connection_id=business_connection_id,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            venue=venue,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[FileInput, "Video"],
        duration: Optional[TimePeriod] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: Optional[bool] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        cover: Optional[FileInput] = None,
        start_timestamp: Optional[int] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_video(
            chat_id=chat_id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
            cover=cover,
            start_timestamp=start_timestamp,
            filename=filename,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_video_note(
        self,
        chat_id: Union[int, str],
        video_note: Union[FileInput, "VideoNote"],
        duration: Optional[TimePeriod] = None,
        length: Optional[int] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_video_note(
            chat_id=chat_id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
            reply_parameters=reply_parameters,
            filename=filename,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_voice(
        self,
        chat_id: Union[int, str],
        voice: Union[FileInput, "Voice"],
        duration: Optional[TimePeriod] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_voice(
            chat_id=chat_id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            filename=filename,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def set_chat_administrator_custom_title(
        self,
        chat_id: Union[int, str],
        user_id: int,
        custom_title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_administrator_custom_title(
            chat_id=chat_id,
            user_id=user_id,
            custom_title=custom_title,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_description(
        self,
        chat_id: Union[str, int],
        description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_description(
            chat_id=chat_id,
            description=description,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_user_emoji_status(
        self,
        user_id: int,
        emoji_status_custom_emoji_id: Optional[str] = None,
        emoji_status_expiration_date: Optional[Union[int, dtm.datetime]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_user_emoji_status(
            user_id=user_id,
            emoji_status_custom_emoji_id=emoji_status_custom_emoji_id,
            emoji_status_expiration_date=emoji_status_expiration_date,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_menu_button(
        self,
        chat_id: Optional[int] = None,
        menu_button: Optional[MenuButton] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_menu_button(
            chat_id=chat_id,
            menu_button=menu_button,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_permissions(
        self,
        chat_id: Union[str, int],
        permissions: ChatPermissions,
        use_independent_chat_permissions: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_permissions(
            chat_id=chat_id,
            permissions=permissions,
            use_independent_chat_permissions=use_independent_chat_permissions,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_photo(
        self,
        chat_id: Union[str, int],
        photo: FileInput,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_photo(
            chat_id=chat_id,
            photo=photo,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        sticker_set_name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_sticker_set(
            chat_id=chat_id,
            sticker_set_name=sticker_set_name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_chat_title(
        self,
        chat_id: Union[str, int],
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_chat_title(
            chat_id=chat_id,
            title=title,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_game_score(
        self,
        user_id: int,
        score: int,
        chat_id: Optional[int] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        force: Optional[bool] = None,
        disable_edit_message: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().set_game_score(
            user_id=user_id,
            score=score,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            force=force,
            disable_edit_message=disable_edit_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_my_commands(
        self,
        commands: Sequence[Union[BotCommand, tuple[str, str]]],
        scope: Optional[BotCommandScope] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_my_commands(
            commands=commands,
            scope=scope,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_my_default_administrator_rights(
        self,
        rights: Optional[ChatAdministratorRights] = None,
        for_channels: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_my_default_administrator_rights(
            rights=rights,
            for_channels=for_channels,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_passport_data_errors(
        self,
        user_id: int,
        errors: Sequence["PassportElementError"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_passport_data_errors(
            user_id=user_id,
            errors=errors,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_position_in_set(
        self,
        sticker: Union[str, "Sticker"],
        position: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_position_in_set(
            sticker=sticker,
            position=position,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_set_thumbnail(
        self,
        name: str,
        user_id: int,
        format: str,  # pylint: disable=redefined-builtin
        thumbnail: Optional[FileInput] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_set_thumbnail(
            name=name,
            user_id=user_id,
            thumbnail=thumbnail,
            format=format,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[FileInput] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[Sequence[str]] = None,
        ip_address: Optional[str] = None,
        drop_pending_updates: Optional[bool] = None,
        secret_token: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_webhook(
            url=url,
            certificate=certificate,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            ip_address=ip_address,
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def stop_message_live_location(
        self,
        chat_id: Optional[Union[str, int]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Union[Message, bool]:
        return await super().stop_message_live_location(
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=reply_markup,
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        only_if_banned: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            only_if_banned=only_if_banned,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unban_chat_sender_chat(
            chat_id=chat_id,
            sender_chat_id=sender_chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unpin_all_chat_messages(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unpin_all_chat_messages(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unpin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unpin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            business_connection_id=business_connection_id,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unpin_all_forum_topic_messages(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unpin_all_forum_topic_messages(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def unpin_all_general_forum_topic_messages(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().unpin_all_general_forum_topic_messages(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def upload_sticker_file(
        self,
        user_id: int,
        sticker: FileInput,
        sticker_format: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> File:
        return await super().upload_sticker_file(
            user_id=user_id,
            sticker=sticker,
            sticker_format=sticker_format,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_my_description(
        self,
        description: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_my_description(
            description=description,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_my_short_description(
        self,
        short_description: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_my_short_description(
            short_description=short_description,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_my_description(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> BotDescription:
        return await super().get_my_description(
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_my_short_description(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> BotShortDescription:
        return await super().get_my_short_description(
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_my_name(
        self,
        name: Optional[str] = None,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_my_name(
            name=name,
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_my_name(
        self,
        language_code: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> BotName:
        return await super().get_my_name(
            language_code=language_code,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_custom_emoji_sticker_set_thumbnail(
        self,
        name: str,
        custom_emoji_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_custom_emoji_sticker_set_thumbnail(
            name=name,
            custom_emoji_id=custom_emoji_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_set_title(
        self,
        name: str,
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_set_title(
            name=name,
            title=title,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def delete_sticker_set(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().delete_sticker_set(
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_emoji_list(
        self,
        sticker: Union[str, "Sticker"],
        emoji_list: Sequence[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_emoji_list(
            sticker=sticker,
            emoji_list=emoji_list,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_keywords(
        self,
        sticker: Union[str, "Sticker"],
        keywords: Optional[Sequence[str]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_keywords(
            sticker=sticker,
            keywords=keywords,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_sticker_mask_position(
        self,
        sticker: Union[str, "Sticker"],
        mask_position: Optional[MaskPosition] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_sticker_mask_position(
            sticker=sticker,
            mask_position=mask_position,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_user_chat_boosts(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> UserChatBoosts:
        return await super().get_user_chat_boosts(
            chat_id=chat_id,
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def set_message_reaction(
        self,
        chat_id: Union[str, int],
        message_id: int,
        reaction: Optional[Union[Sequence[Union[ReactionType, str]], ReactionType, str]] = None,
        is_big: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=reaction,
            is_big=is_big,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_business_connection(
        self,
        business_connection_id: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> BusinessConnection:
        return await super().get_business_connection(
            business_connection_id=business_connection_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def replace_sticker_in_set(
        self,
        user_id: int,
        name: str,
        old_sticker: Union[str, "Sticker"],
        sticker: "InputSticker",
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().replace_sticker_in_set(
            user_id=user_id,
            name=name,
            old_sticker=old_sticker,
            sticker=sticker,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def refund_star_payment(
        self,
        user_id: int,
        telegram_payment_charge_id: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_star_transactions(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> StarTransactions:
        return await super().get_star_transactions(
            offset=offset,
            limit=limit,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_user_star_subscription(
        self,
        user_id: int,
        telegram_payment_charge_id: str,
        is_canceled: bool,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().edit_user_star_subscription(
            user_id=user_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            is_canceled=is_canceled,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def send_paid_media(
        self,
        chat_id: Union[str, int],
        star_count: int,
        media: Sequence["InputPaidMedia"],
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        show_caption_above_media: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        reply_parameters: Optional["ReplyParameters"] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        business_connection_id: Optional[str] = None,
        payload: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: Optional[int] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Message:
        return await super().send_paid_media(
            chat_id=chat_id,
            star_count=star_count,
            media=media,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
            business_connection_id=business_connection_id,
            payload=payload,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def create_chat_subscription_invite_link(
        self,
        chat_id: Union[str, int],
        subscription_period: TimePeriod,
        subscription_price: int,
        name: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatInviteLink:
        return await super().create_chat_subscription_invite_link(
            chat_id=chat_id,
            subscription_period=subscription_period,
            subscription_price=subscription_price,
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def edit_chat_subscription_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        name: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> ChatInviteLink:
        return await super().edit_chat_subscription_invite_link(
            chat_id=chat_id,
            invite_link=invite_link,
            name=name,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def get_available_gifts(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> Gifts:
        return await super().get_available_gifts(
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def send_gift(
        self,
        user_id: Optional[int] = None,
        gift_id: Union[str, Gift] = None,  # type: ignore
        text: Optional[str] = None,
        text_parse_mode: ODVInput[str] = DEFAULT_NONE,
        text_entities: Optional[Sequence["MessageEntity"]] = None,
        pay_for_upgrade: Optional[bool] = None,
        chat_id: Optional[Union[str, int]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().send_gift(
            user_id=user_id,
            chat_id=chat_id,
            gift_id=gift_id,
            text=text,
            text_parse_mode=text_parse_mode,
            text_entities=text_entities,
            pay_for_upgrade=pay_for_upgrade,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def verify_chat(
        self,
        chat_id: Union[int, str],
        custom_description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().verify_chat(
            chat_id=chat_id,
            custom_description=custom_description,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def verify_user(
        self,
        user_id: int,
        custom_description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().verify_user(
            user_id=user_id,
            custom_description=custom_description,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def remove_chat_verification(
        self,
        chat_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().remove_chat_verification(
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    async def remove_user_verification(
        self,
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        rate_limit_args: Optional[RLARGS] = None,
    ) -> bool:
        return await super().remove_user_verification(
            user_id=user_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args),
        )

    # updated camelCase aliases
    getMe = get_me
    sendMessage = send_message
    deleteMessage = delete_message
    deleteMessages = delete_messages
    forwardMessage = forward_message
    forwardMessages = forward_messages
    sendPhoto = send_photo
    sendAudio = send_audio
    sendDocument = send_document
    sendSticker = send_sticker
    sendVideo = send_video
    sendAnimation = send_animation
    sendVoice = send_voice
    sendVideoNote = send_video_note
    sendMediaGroup = send_media_group
    sendLocation = send_location
    editMessageLiveLocation = edit_message_live_location
    stopMessageLiveLocation = stop_message_live_location
    sendVenue = send_venue
    sendContact = send_contact
    sendGame = send_game
    sendChatAction = send_chat_action
    answerInlineQuery = answer_inline_query
    savePreparedInlineMessage = save_prepared_inline_message
    getUserProfilePhotos = get_user_profile_photos
    getFile = get_file
    banChatMember = ban_chat_member
    banChatSenderChat = ban_chat_sender_chat
    unbanChatMember = unban_chat_member
    unbanChatSenderChat = unban_chat_sender_chat
    answerCallbackQuery = answer_callback_query
    editMessageText = edit_message_text
    editMessageCaption = edit_message_caption
    editMessageMedia = edit_message_media
    editMessageReplyMarkup = edit_message_reply_markup
    getUpdates = get_updates
    setWebhook = set_webhook
    deleteWebhook = delete_webhook
    leaveChat = leave_chat
    getChat = get_chat
    getChatAdministrators = get_chat_administrators
    getChatMember = get_chat_member
    setChatStickerSet = set_chat_sticker_set
    deleteChatStickerSet = delete_chat_sticker_set
    getChatMemberCount = get_chat_member_count
    getWebhookInfo = get_webhook_info
    setGameScore = set_game_score
    getGameHighScores = get_game_high_scores
    sendInvoice = send_invoice
    answerShippingQuery = answer_shipping_query
    answerPreCheckoutQuery = answer_pre_checkout_query
    answerWebAppQuery = answer_web_app_query
    restrictChatMember = restrict_chat_member
    promoteChatMember = promote_chat_member
    setChatPermissions = set_chat_permissions
    setChatAdministratorCustomTitle = set_chat_administrator_custom_title
    exportChatInviteLink = export_chat_invite_link
    createChatInviteLink = create_chat_invite_link
    editChatInviteLink = edit_chat_invite_link
    revokeChatInviteLink = revoke_chat_invite_link
    approveChatJoinRequest = approve_chat_join_request
    declineChatJoinRequest = decline_chat_join_request
    setChatPhoto = set_chat_photo
    deleteChatPhoto = delete_chat_photo
    setChatTitle = set_chat_title
    setChatDescription = set_chat_description
    setUserEmojiStatus = set_user_emoji_status
    pinChatMessage = pin_chat_message
    unpinChatMessage = unpin_chat_message
    unpinAllChatMessages = unpin_all_chat_messages
    getStickerSet = get_sticker_set
    getCustomEmojiStickers = get_custom_emoji_stickers
    uploadStickerFile = upload_sticker_file
    createNewStickerSet = create_new_sticker_set
    addStickerToSet = add_sticker_to_set
    setStickerPositionInSet = set_sticker_position_in_set
    deleteStickerFromSet = delete_sticker_from_set
    setStickerSetThumbnail = set_sticker_set_thumbnail
    setPassportDataErrors = set_passport_data_errors
    sendPoll = send_poll
    stopPoll = stop_poll
    sendDice = send_dice
    getMyCommands = get_my_commands
    setMyCommands = set_my_commands
    deleteMyCommands = delete_my_commands
    logOut = log_out
    copyMessage = copy_message
    copyMessages = copy_messages
    getChatMenuButton = get_chat_menu_button
    setChatMenuButton = set_chat_menu_button
    getMyDefaultAdministratorRights = get_my_default_administrator_rights
    setMyDefaultAdministratorRights = set_my_default_administrator_rights
    createInvoiceLink = create_invoice_link
    getForumTopicIconStickers = get_forum_topic_icon_stickers
    createForumTopic = create_forum_topic
    editForumTopic = edit_forum_topic
    closeForumTopic = close_forum_topic
    reopenForumTopic = reopen_forum_topic
    deleteForumTopic = delete_forum_topic
    unpinAllForumTopicMessages = unpin_all_forum_topic_messages
    editGeneralForumTopic = edit_general_forum_topic
    closeGeneralForumTopic = close_general_forum_topic
    reopenGeneralForumTopic = reopen_general_forum_topic
    hideGeneralForumTopic = hide_general_forum_topic
    unhideGeneralForumTopic = unhide_general_forum_topic
    setMyDescription = set_my_description
    getMyDescription = get_my_description
    setMyShortDescription = set_my_short_description
    getMyShortDescription = get_my_short_description
    setCustomEmojiStickerSetThumbnail = set_custom_emoji_sticker_set_thumbnail
    setStickerSetTitle = set_sticker_set_title
    deleteStickerSet = delete_sticker_set
    setStickerEmojiList = set_sticker_emoji_list
    setStickerKeywords = set_sticker_keywords
    setStickerMaskPosition = set_sticker_mask_position
    setMyName = set_my_name
    getMyName = get_my_name
    unpinAllGeneralForumTopicMessages = unpin_all_general_forum_topic_messages
    getUserChatBoosts = get_user_chat_boosts
    setMessageReaction = set_message_reaction
    getBusinessConnection = get_business_connection
    replaceStickerInSet = replace_sticker_in_set
    refundStarPayment = refund_star_payment
    getStarTransactions = get_star_transactions
    editUserStarSubscription = edit_user_star_subscription
    createChatSubscriptionInviteLink = create_chat_subscription_invite_link
    editChatSubscriptionInviteLink = edit_chat_subscription_invite_link
    sendPaidMedia = send_paid_media
    getAvailableGifts = get_available_gifts
    sendGift = send_gift
    verifyChat = verify_chat
    verifyUser = verify_user
    removeChatVerification = remove_chat_verification
    removeUserVerification = remove_user_verification
