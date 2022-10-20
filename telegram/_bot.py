#!/usr/bin/env python
# pylint: disable=no-self-argument, not-callable, no-member, too-many-arguments
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
"""This module contains an object that represents a Telegram Bot."""
import asyncio
import functools
import logging
import pickle
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    no_type_check,
)

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    CRYPTO_INSTALLED = True
except ImportError:
    default_backend = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    CRYPTO_INSTALLED = False

from telegram._botcommand import BotCommand
from telegram._botcommandscope import BotCommandScope
from telegram._chat import Chat
from telegram._chatadministratorrights import ChatAdministratorRights
from telegram._chatinvitelink import ChatInviteLink
from telegram._chatmember import ChatMember
from telegram._chatpermissions import ChatPermissions
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.chatphoto import ChatPhoto
from telegram._files.contact import Contact
from telegram._files.document import Document
from telegram._files.file import File
from telegram._files.inputmedia import InputMedia
from telegram._files.location import Location
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import MaskPosition, Sticker, StickerSet
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._files.videonote import VideoNote
from telegram._files.voice import Voice
from telegram._games.gamehighscore import GameHighScore
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._menubutton import MenuButton
from telegram._message import Message
from telegram._messageid import MessageId
from telegram._passport.passportelementerrors import PassportElementError
from telegram._payment.shippingoption import ShippingOption
from telegram._poll import Poll
from telegram._sentwebappmessage import SentWebAppMessage
from telegram._telegramobject import TelegramObject
from telegram._update import Update
from telegram._user import User
from telegram._userprofilephotos import UserProfilePhotos
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.files import is_local_file, parse_file_input
from telegram._utils.types import DVInput, FileInput, JSONDict, ODVInput, ReplyMarkup
from telegram._webhookinfo import WebhookInfo
from telegram.constants import InlineQueryLimit
from telegram.error import InvalidToken
from telegram.request import BaseRequest, RequestData
from telegram.request._httpxrequest import HTTPXRequest
from telegram.request._requestparameter import RequestParameter

if TYPE_CHECKING:
    from telegram import (
        InlineQueryResult,
        InputFile,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        LabeledPrice,
        MessageEntity,
    )

BT = TypeVar("BT", bound="Bot")


class Bot(TelegramObject, AbstractAsyncContextManager):
    """This object represents a Telegram Bot.

    Instances of this class can be used as asyncio context managers, where

    .. code:: python

        async with bot:
            # code

    is roughly equivalent to

    .. code:: python

        try:
            await bot.initialize()
            # code
        finally:
            await request_object.shutdown()

    Note:
        * Most bot methods have the argument ``api_kwargs`` which allows passing arbitrary keywords
          to the Telegram API. This can be used to access new features of the API before they are
          incorporated into PTB. However, this is not guaranteed to work, i.e. it will fail for
          passing files.
        * Bots should not be serialized since if you for e.g. change the bots token, then your
          serialized instance will not reflect that change. Trying to pickle a bot instance will
          raise :exc:`pickle.PicklingError`.

    .. seealso:: :attr:`telegram.ext.Application.bot`,
        :attr:`telegram.ext.CallbackContext.bot`,
        :attr:`telegram.ext.Updater.bot`

    .. versionadded:: 13.2
        Objects of this class are comparable in terms of equality. Two objects of this class are
        considered equal, if their :attr:`bot` is equal.

    .. versionchanged:: 20.0

        * Removed the deprecated methods ``kick_chat_member``, ``kickChatMember``,
          ``get_chat_members_count`` and ``getChatMembersCount``.
        * Removed the deprecated property ``commands``.
        * Removed the deprecated ``defaults`` parameter. If you want to use
          :class:`telegram.ext.Defaults`, please use the subclass :class:`telegram.ext.ExtBot`
          instead.
        * Attempting to pickle a bot instance will now raise :exc:`pickle.PicklingError`.
        * The following are now keyword-only arguments in Bot methods:
          ``location``, ``filename``, ``venue``, ``contact``,
          ``{read, write, connect, pool}_timeout``, ``api_kwargs``. Use a named argument for those,
          and notice that some positional arguments changed position as a result.
        * For uploading files, file paths are now always accepted. If :paramref:`local_mode` is
          :obj:`False`, the file contents will be read in binary mode and uploaded. Otherwise,
          the file path will be passed in the
          `file URI scheme <https://en.wikipedia.org/wiki/File_URI_scheme>`_.

    Args:
        token (:obj:`str`): Bot's unique authentication token.
        base_url (:obj:`str`, optional): Telegram Bot API service URL.
        base_file_url (:obj:`str`, optional): Telegram Bot API file URL.
        request (:class:`telegram.request.BaseRequest`, optional): Pre initialized
            :class:`telegram.request.BaseRequest` instances. Will be used for all bot methods
            *except* for :meth:`get_updates`. If not passed, an instance of
            :class:`telegram.request.HTTPXRequest` will be used.
        get_updates_request (:class:`telegram.request.BaseRequest`, optional): Pre initialized
            :class:`telegram.request.BaseRequest` instances. Will be used exclusively for
            :meth:`get_updates`. If not passed, an instance of
            :class:`telegram.request.HTTPXRequest` will be used.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.
        local_mode (:obj:`bool`, optional): Set to :obj:`True`, if the :paramref:`base_url` is
            the URI of a `Local Bot API Server <https://core.telegram.org/bots/api#using-a-local\
            -bot-api-server>`_ that runs with the ``--local`` flag. Currently, the only effect of
            this is that files are uploaded using their local path in the
            `file URI scheme <https://en.wikipedia.org/wiki/File_URI_scheme>`_.
            Defaults to :obj:`False`.

            .. versionadded:: 20.0.

    .. include:: inclusions/bot_methods.rst

    """

    __slots__ = (
        "_token",
        "_base_url",
        "_base_file_url",
        "_private_key",
        "_bot_user",
        "_request",
        "_logger",
        "_initialized",
        "_local_mode",
    )

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.telegram.org/bot",
        base_file_url: str = "https://api.telegram.org/file/bot",
        request: BaseRequest = None,
        get_updates_request: BaseRequest = None,
        private_key: bytes = None,
        private_key_password: bytes = None,
        local_mode: bool = False,
    ):
        super().__init__(api_kwargs=None)
        if not token:
            raise InvalidToken("You must pass the token you received from https://t.me/Botfather!")
        self._token = token

        self._base_url = base_url + self._token
        self._base_file_url = base_file_url + self._token
        self._local_mode = local_mode
        self._bot_user: Optional[User] = None
        self._private_key = None
        self._logger = logging.getLogger(__name__)
        self._initialized = False

        self._request: Tuple[BaseRequest, BaseRequest] = (
            HTTPXRequest() if get_updates_request is None else get_updates_request,
            HTTPXRequest() if request is None else request,
        )

        if private_key:
            if not CRYPTO_INSTALLED:
                raise RuntimeError(
                    "To use Telegram Passports, PTB must be installed via `pip install "
                    "python-telegram-bot[passport]`."
                )
            self._private_key = serialization.load_pem_private_key(
                private_key, password=private_key_password, backend=default_backend()
            )

    @property
    def token(self) -> str:
        """:obj:`str`: Bot's unique authentication token.

        .. versionadded:: 20.0
        """
        return self._token

    @property
    def base_url(self) -> str:
        """:obj:`str`: Telegram Bot API service URL, built from :paramref:`Bot.base_url` and
        :paramref:`Bot.token`.

        .. versionadded:: 20.0
        """
        return self._base_url

    @property
    def base_file_url(self) -> str:
        """:obj:`str`: Telegram Bot API file URL, built from :paramref:`Bot.base_file_url` and
        :paramref:`Bot.token`.

        .. versionadded:: 20.0
        """
        return self._base_file_url

    @property
    def local_mode(self) -> bool:
        """:obj:`bool`: Whether this bot is running in local mode.

        .. versionadded:: 20.0
        """
        return self._local_mode

    # Proper type hints are difficult because:
    # 1. cryptography doesn't have a nice base class, so it would get lengthy
    # 2. we can't import cryptography if it's not installed
    @property
    def private_key(self) -> Optional[Any]:
        """Deserialized private key for decryption of telegram passport data.

        .. versionadded:: 20.0
        """
        return self._private_key

    def __reduce__(self) -> NoReturn:
        """Called by pickle.dumps(). Serializing bots is unadvisable, so we forbid pickling."""
        raise pickle.PicklingError("Bot objects cannot be pickled!")

    # TODO: After https://youtrack.jetbrains.com/issue/PY-50952 is fixed, we can revisit this and
    # consider adding Paramspec from typing_extensions to properly fix this. Currently a workaround
    def _log(func: Any):  # type: ignore[no-untyped-def] # skipcq: PY-D0003
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        async def decorator(*args, **kwargs):  # type: ignore[no-untyped-def]
            logger.debug("Entering: %s", func.__name__)
            result = await func(*args, **kwargs)
            logger.debug(result)
            logger.debug("Exiting: %s", func.__name__)
            return result

        return decorator

    def _parse_file_input(
        self,
        file_input: Union[FileInput, "TelegramObject"],
        tg_type: Type["TelegramObject"] = None,
        filename: str = None,
        attach: bool = False,
    ) -> Union[str, "InputFile", Any]:
        return parse_file_input(
            file_input=file_input,
            tg_type=tg_type,
            filename=filename,
            attach=attach,
            local_mode=self._local_mode,
        )

    def _insert_defaults(self, data: Dict[str, object]) -> None:  # skipcq: PYL-R0201
        """This method is here to make ext.Defaults work. Because we need to be able to tell
        e.g. `send_message(chat_id, text)` from `send_message(chat_id, text, parse_mode=None)`, the
        default values for `parse_mode` etc are not `None` but `DEFAULT_NONE`. While this *could*
        be done in ExtBot instead of Bot, shortcuts like `Message.reply_text` need to work for both
        Bot and ExtBot, so they also have the `DEFAULT_NONE` default values.

        This makes it necessary to convert `DefaultValue(obj)` to `obj` at some point between
        `Message.reply_text` and the request to TG. Doing this here in a centralized manner is a
        rather clean and minimally invasive solution, i.e. the link between tg and tg.ext is as
        small as possible.
        See also _insert_defaults_for_ilq
        ExtBot overrides this method to actually insert default values.

        If in the future we come up with a better way of making `Defaults` work, we can cut this
        link as well.
        """
        # We
        # 1) set the correct parse_mode for all InputMedia objects
        # 2) replace all DefaultValue instances with the corresponding normal value.
        for key, val in data.items():
            # 1)
            if isinstance(val, InputMedia):
                val.parse_mode = DefaultValue.get_value(val.parse_mode)
            elif key == "media" and isinstance(val, list):
                for media in val:
                    media.parse_mode = DefaultValue.get_value(media.parse_mode)
            # 2)
            else:
                data[key] = DefaultValue.get_value(val)

    async def _post(
        self,
        endpoint: str,
        data: JSONDict = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[bool, JSONDict, None]:
        if data is None:
            data = {}

        if api_kwargs:
            data.update(api_kwargs)

        # Insert is in-place, so no return value for data
        self._insert_defaults(data)

        # Drop any None values because Telegram doesn't handle them well
        data = {key: value for key, value in data.items() if value is not None}

        return await self._do_post(
            endpoint=endpoint,
            data=data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

    async def _do_post(
        self,
        endpoint: str,
        data: JSONDict,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> Union[bool, JSONDict, None]:
        # This also converts datetimes into timestamps.
        # We don't do this earlier so that _insert_defaults (see above) has a chance to convert
        # to the default timezone in case this is called by ExtBot
        request_data = RequestData(
            parameters=[RequestParameter.from_input(key, value) for key, value in data.items()],
        )

        if endpoint == "getUpdates":
            request = self._request[0]
        else:
            request = self._request[1]

        return await request.post(
            url=f"{self._base_url}/{endpoint}",
            request_data=request_data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

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
        if reply_to_message_id is not None:
            data["reply_to_message_id"] = reply_to_message_id

        # We don't check if (DEFAULT_)None here, so that _post is able to insert the defaults
        # correctly, if necessary
        data["disable_notification"] = disable_notification
        data["allow_sending_without_reply"] = allow_sending_without_reply
        data["protect_content"] = protect_content

        if reply_markup is not None:
            data["reply_markup"] = reply_markup

        result = await self._post(
            endpoint,
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        if result is True:
            return result

        return Message.de_json(result, self)  # type: ignore[return-value, arg-type]

    async def initialize(self) -> None:
        """Initialize resources used by this class. Currently calls :meth:`get_me` to
        cache :attr:`bot` and calls :meth:`telegram.request.BaseRequest.initialize` for
        the request objects used by this bot.

        .. seealso:: :meth:`shutdown`

        .. versionadded:: 20.0
        """
        if self._initialized:
            self._logger.debug("This Bot is already initialized.")
            return

        await asyncio.gather(self._request[0].initialize(), self._request[1].initialize())
        # Since the bot is to be initialized only once, we can also use it for
        # verifying the token passed and raising an exception if it's invalid.
        try:
            await self.get_me()
        except InvalidToken as exc:
            raise InvalidToken(f"The token `{self._token}` was rejected by the server.") from exc
        self._initialized = True

    async def shutdown(self) -> None:
        """Stop & clear resources used by this class. Currently just calls
        :meth:`telegram.request.BaseRequest.shutdown` for the request objects used by this bot.

        .. seealso:: :meth:`initialize`

        .. versionadded:: 20.0
        """
        if not self._initialized:
            self._logger.debug("This Bot is already shut down. Returning.")
            return

        await asyncio.gather(self._request[0].shutdown(), self._request[1].shutdown())
        self._initialized = False

    async def __aenter__(self: BT) -> BT:
        try:
            await self.initialize()
            return self
        except Exception as exc:
            await self.shutdown()
            raise exc

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Make sure not to return `True` so that exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__
        await self.shutdown()

    @property
    def request(self) -> BaseRequest:
        """The :class:`~telegram.request.BaseRequest` object used by this bot.

        Warning:
            Requests to the Bot API are made by the various methods of this class. This attribute
            should *not* be used manually.
        """
        return self._request[1]

    @property
    def bot(self) -> User:
        """:class:`telegram.User`: User instance for the bot as returned by :meth:`get_me`.

        Warning:
            This value is the cached return value of :meth:`get_me`. If the bots profile is
            changed during runtime, this value won't reflect the changes until :meth:`get_me` is
            called again.

        .. seealso:: :meth:`initialize`
        """
        if self._bot_user is None:
            raise RuntimeError(
                f"{self.__class__.__name__} is not properly initialized. Call "
                f"`{self.__class__.__name__}.initialize` before accessing this property."
            )
        return self._bot_user

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """:obj:`int`: Unique identifier for this bot. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.id

    @property
    def first_name(self) -> str:
        """:obj:`str`: Bot's first name. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.first_name

    @property
    def last_name(self) -> str:
        """:obj:`str`: Optional. Bot's last name. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.last_name  # type: ignore

    @property
    def username(self) -> str:
        """:obj:`str`: Bot's username. Shortcut for the corresponding attribute of
        :attr:`bot`.
        """
        return self.bot.username  # type: ignore

    @property
    def link(self) -> str:
        """:obj:`str`: Convenience property. Returns the t.me link of the bot."""
        return f"https://t.me/{self.username}"

    @property
    def can_join_groups(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_join_groups` attribute. Shortcut for the
        corresponding attribute of :attr:`bot`.
        """
        return self.bot.can_join_groups  # type: ignore

    @property
    def can_read_all_group_messages(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_read_all_group_messages` attribute.
        Shortcut for the corresponding attribute of :attr:`bot`.
        """
        return self.bot.can_read_all_group_messages  # type: ignore

    @property
    def supports_inline_queries(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.supports_inline_queries` attribute.
        Shortcut for the corresponding attribute of :attr:`bot`.
        """
        return self.bot.supports_inline_queries  # type: ignore

    @property
    def name(self) -> str:
        """:obj:`str`: Bot's @username. Shortcut for the corresponding attribute of :attr:`bot`."""
        return f"@{self.username}"

    @_log
    async def get_me(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> User:
        """A simple method for testing your bot's auth token. Requires no parameters.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance representing that bot if the
            credentials are valid, :obj:`None` otherwise.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        result = await self._post(
            "getMe",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        self._bot_user = User.de_json(result, self)  # type: ignore[arg-type]
        return self._bot_user  # type: ignore[return-value]

    @_log
    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send text messages.

        .. seealso:: :attr:`telegram.Message.reply_text`, :attr:`telegram.Chat.send_message`,
            :attr:`telegram.User.send_message`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            text (:obj:`str`): Text of the message to be sent. Max
                :tg-const:`telegram.constants.MessageLimit.TEXT_LENGTH` characters after entities
                parsing.
            parse_mode (:obj:`str`): Send Markdown or HTML, if you want Telegram apps to show bold,
                italic, fixed-width text or inline URLs in your bot's message. See the constants in
                :class:`telegram.constants.ParseMode` for the available modes.
            entities (List[:class:`telegram.MessageEntity`], optional): List of special entities
                that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of sent messages from
                forwarding and saving.

                .. versionadded:: 13.10
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        if entities:
            data["entities"] = entities

        return await self._send_message(  # type: ignore[return-value]
            "sendMessage",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete a message, including service messages, with the following
        limitations:

        - A message can only be deleted if it was sent less than 48 hours ago.
        - A dice message in a private chat can only be deleted if it was sent more than 24
          hours ago.
        - Bots can delete outgoing messages in private chats, groups, and supergroups.
        - Bots can delete incoming messages in private chats.
        - Bots granted :attr:`~telegram.ChatMemberAdministrator.can_post_messages` permissions
          can delete outgoing messages in channels.
        - If the bot is an administrator of a group, it can delete any message there.
        - If the bot has :attr:`~telegram.ChatMemberAdministrator.can_delete_messages`
          permission in a supergroup or a channel, it can delete any message there.

        .. seealso:: :meth:`telegram.Message.delete`,
            :meth:`telegram.CallbackQuery.delete_message`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of the message to delete.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "message_id": message_id}
        result = await self._post(
            "deleteMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to forward messages of any kind. Service messages can't be forwarded.

        Note:
            Since the release of Bot API 5.5 it can be impossible to forward messages from
            some chats. Use the attributes :attr:`telegram.Message.has_protected_content` and
            :attr:`telegram.Chat.has_protected_content` to check this.

            As a workaround, it is still possible to use :meth:`copy_message`. However, this
            behaviour is undocumented and might be changed by Telegram.

        .. seealso:: :attr:`telegram.Message.forward`, :attr:`telegram.Chat.forward_to`,
            :attr:`telegram.Chat.forward_from`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format ``@channelusername``).
            message_id (:obj:`int`): Message identifier in the chat specified in from_chat_id.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if chat_id:
            data["chat_id"] = chat_id
        if from_chat_id:
            data["from_chat_id"] = from_chat_id
        if message_id:
            data["message_id"] = message_id
        return await self._send_message(  # type: ignore[return-value]
            "forwardMessage",
            data,
            disable_notification=disable_notification,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[FileInput, "PhotoSize"],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send photos.

        .. seealso:: :attr:`telegram.Message.reply_photo`, :attr:`telegram.Chat.send_photo`,
            :attr:`telegram.User.send_photo`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            photo (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.PhotoSize`): Photo to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Photo caption (may also be used when resending photos
                by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the photo, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "photo": self._parse_file_input(photo, PhotoSize, filename=filename),
            "parse_mode": parse_mode,
        }

        if caption:
            data["caption"] = caption

        if caption_entities:
            data["caption_entities"] = caption_entities

        return await self._send_message(  # type: ignore[return-value]
            "sendPhoto",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_audio(
        self,
        chat_id: Union[int, str],
        audio: Union[FileInput, "Audio"],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display them in the
        music player. Your audio must be in the .mp3 or .m4a format.

        Bots can currently send audio files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        For sending voice messages, use the :meth:`send_voice` method instead.

        .. seealso:: :attr:`telegram.Message.reply_audio`, :attr:`telegram.Chat.send_audio`,
            :attr:`telegram.User.send_audio`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            audio (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Audio`): Audio file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Audio` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Audio caption,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            duration (:obj:`int`, optional): Duration of sent audio in seconds.
            performer (:obj:`str`, optional): Performer.
            title (:obj:`str`, optional): Track name.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the audio, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "audio": self._parse_file_input(audio, Audio, filename=filename),
            "parse_mode": parse_mode,
        }

        if duration:
            data["duration"] = duration
        if performer:
            data["performer"] = performer
        if title:
            data["title"] = title
        if caption:
            data["caption"] = caption

        if caption_entities:
            data["caption_entities"] = caption_entities
        if thumb:
            data["thumb"] = self._parse_file_input(thumb, attach=True)

        return await self._send_message(  # type: ignore[return-value]
            "sendAudio",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[FileInput, "Document"],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send general files.

        Bots can currently send files of any type of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        .. seealso:: :attr:`telegram.Message.reply_document`, :attr:`telegram.Chat.send_document`,
            :attr:`telegram.User.send_document`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            document (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Document`): File to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Document` object to send.

                Note:
                    Sending by URL will currently only work ``GIF``, ``PDF`` & ``ZIP`` files.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Document caption (may also be used when resending
                documents by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            disable_content_type_detection (:obj:`bool`, optional): Disables automatic server-side
                content type detection for files uploaded using multipart/form-data.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the document, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "document": self._parse_file_input(document, Document, filename=filename),
            "parse_mode": parse_mode,
        }

        if caption:
            data["caption"] = caption

        if caption_entities:
            data["caption_entities"] = caption_entities
        if disable_content_type_detection is not None:
            data["disable_content_type_detection"] = disable_content_type_detection
        if thumb:
            data["thumb"] = self._parse_file_input(thumb, attach=True)

        return await self._send_message(  # type: ignore[return-value]
            "sendDocument",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_sticker(
        self,
        chat_id: Union[int, str],
        sticker: Union[FileInput, "Sticker"],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send static ``.WEBP``, animated ``.TGS``, or video ``.WEBM`` stickers.

        .. seealso:: :attr:`telegram.Message.reply_sticker`, :attr:`telegram.Chat.send_sticker`,
            :attr:`telegram.User.send_sticker`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Sticker`): Sticker to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Sticker` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "sticker": self._parse_file_input(sticker, Sticker)}
        return await self._send_message(  # type: ignore[return-value]
            "sendSticker",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[FileInput, "Video"],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send video files, Telegram clients support mp4 videos
        (other formats may be sent as Document).

        Bots can currently send video files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        Note:
            :paramref:`thumb` will be ignored for small video files, for which Telegram can
            easily generate thumbnails. However, this behaviour is undocumented and might be
            changed by Telegram.

        .. seealso:: :attr:`telegram.Message.reply_video`, :attr:`telegram.Chat.send_video`,
            :attr:`telegram.User.send_video`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            video (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Video`): Video file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Video` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            width (:obj:`int`, optional): Video width.
            height (:obj:`int`, optional): Video height.
            caption (:obj:`str`, optional): Video caption (may also be used when resending videos
                by file_id), 0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH`
                characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            supports_streaming (:obj:`bool`, optional): Pass :obj:`True`, if the uploaded video is
                suitable for streaming.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the video, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "video": self._parse_file_input(video, Video, filename=filename),
            "parse_mode": parse_mode,
        }

        if duration:
            data["duration"] = duration
        if caption:
            data["caption"] = caption
        if caption_entities:
            data["caption_entities"] = caption_entities
        if supports_streaming:
            data["supports_streaming"] = supports_streaming
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        if thumb:
            data["thumb"] = self._parse_file_input(thumb, attach=True)

        return await self._send_message(  # type: ignore[return-value]
            "sendVideo",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_video_note(
        self,
        chat_id: Union[int, str],
        video_note: Union[FileInput, "VideoNote"],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        thumb: FileInput = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        As of v.4.0, Telegram clients support rounded square mp4 videos of up to 1 minute long.
        Use this method to send video messages.

        Note:
            :paramref:`thumb` will be ignored for small video files, for which Telegram can
            easily generate thumbnails. However, this behaviour is undocumented and might be
            changed by Telegram.

        .. seealso:: :attr:`telegram.Message.reply_video_note`,
            :attr:`telegram.Chat.send_video_note`,
            :attr:`telegram.User.send_video_note`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            video_note (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.VideoNote`): Video note to send.
                Pass a file_id as String to send a video note that exists on the Telegram
                servers (recommended) or upload a new video using multipart/form-data.
                |uploadinput|
                Lastly you can pass an existing :class:`telegram.VideoNote` object to send.
                Sending video notes by a URL is currently unsupported.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            length (:obj:`int`, optional): Video width and height, i.e. diameter of the video
                message.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.
            thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the video note, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "video_note": self._parse_file_input(video_note, VideoNote, filename=filename),
        }

        if duration is not None:
            data["duration"] = duration
        if length is not None:
            data["length"] = length
        if thumb:
            data["thumb"] = self._parse_file_input(thumb, attach=True)

        return await self._send_message(  # type: ignore[return-value]
            "sendVideoNote",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_animation(
        self,
        chat_id: Union[int, str],
        animation: Union[FileInput, "Animation"],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound).
        Bots can currently send animation files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD` in size, this limit may be
        changed in the future.

        Note:
            :paramref:`thumb` will be ignored for small files, for which Telegram can easily
            generate thumbnails. However, this behaviour is undocumented and might be changed
            by Telegram.

        .. seealso:: :attr:`telegram.Message.reply_animation`,
            :attr:`telegram.Chat.send_animation`,
            :attr:`telegram.User.send_animation`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            animation (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Animation`): Animation to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Animation` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            duration (:obj:`int`, optional): Duration of sent animation in seconds.
            width (:obj:`int`, optional): Animation width.
            height (:obj:`int`, optional): Animation height.
            thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstring|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

            caption (:obj:`str`, optional): Animation caption (may also be used when resending
                animations by file_id),
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "animation": self._parse_file_input(animation, Animation, filename=filename),
            "parse_mode": parse_mode,
        }

        if duration:
            data["duration"] = duration
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        if thumb:
            data["thumb"] = self._parse_file_input(thumb, attach=True)
        if caption:
            data["caption"] = caption
        if caption_entities:
            data["caption_entities"] = caption_entities

        return await self._send_message(  # type: ignore[return-value]
            "sendAnimation",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_voice(
        self,
        chat_id: Union[int, str],
        voice: Union[FileInput, "Voice"],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        filename: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display the file
        as a playable voice message. For this to work, your audio must be in an ``.ogg`` file
        encoded with OPUS (other formats may be sent as Audio or Document). Bots can currently
        send voice messages of up to :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_UPLOAD`
        in size, this limit may be changed in the future.

        Note:
            To use this method, the file must have the type :mimetype:`audio/ogg` and be no more
            than ``1MB`` in size. ``1-20MB`` voice notes will be sent as files.

        .. seealso:: :attr:`telegram.Message.reply_voice`, :attr:`telegram.Chat.send_voice`,
            :attr:`telegram.User.send_voice`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            voice (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Voice`): Voice file to send.
                |fileinput|
                Lastly you can pass an existing :class:`telegram.Voice` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            caption (:obj:`str`, optional): Voice message caption,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            duration (:obj:`int`, optional): Duration of the voice message in seconds.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            filename (:obj:`str`, optional): Custom file name for the voice, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "voice": self._parse_file_input(voice, Voice, filename=filename),
            "parse_mode": parse_mode,
        }

        if duration:
            data["duration"] = duration
        if caption:
            data["caption"] = caption

        if caption_entities:
            data["caption_entities"] = caption_entities

        return await self._send_message(  # type: ignore[return-value]
            "sendVoice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_media_group(
        self,
        chat_id: Union[int, str],
        media: List[
            Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[Message]:
        """Use this method to send a group of photos or videos as an album.

        .. seealso:: :attr:`telegram.Message.reply_media_group`,
            :attr:`telegram.Chat.send_media_group`,
            :attr:`telegram.User.send_media_group`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            media (List[:class:`telegram.InputMediaAudio`, :class:`telegram.InputMediaDocument`, \
                :class:`telegram.InputMediaPhoto`, :class:`telegram.InputMediaVideo`]): An array
                describing messages to be sent, must include 2–10 items.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to ``20``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "media": media,
            "disable_notification": disable_notification,
            "allow_sending_without_reply": allow_sending_without_reply,
            "protect_content": protect_content,
        }

        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        result = await self._post(
            "sendMediaGroup",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return Message.de_list(result, self)  # type: ignore

    @_log
    async def send_location(
        self,
        chat_id: Union[int, str],
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        live_period: int = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        location: Location = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send point on the map.

        Note:
            You can either supply a :paramref:`latitude` and :paramref:`longitude` or a
            :paramref:`location`.

        .. seealso:: :attr:`telegram.Message.reply_location`,  :attr:`telegram.Chat.send_location`,
            :attr:`telegram.User.send_location`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            horizontal_accuracy (:obj:`int`, optional): The radius of uncertainty for the location,
                measured in meters;
                0-:tg-const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`.
            live_period (:obj:`int`, optional): Period in seconds for which the location will be
                updated, should be between 60 and 86400.
            heading (:obj:`int`, optional): For live locations, a direction in which the user is
                moving, in degrees. Must be between 1 and
                :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
            proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance
                for proximity alerts about approaching another chat member, in meters. Must be
                between 1 and :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                    original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            location (:class:`telegram.Location`, optional): The location to send.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if not ((latitude is not None and longitude is not None) or location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument."
            )

        if not (latitude is not None or longitude is not None) ^ bool(location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument. Not both."
            )

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data: JSONDict = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}

        if live_period:
            data["live_period"] = live_period
        if horizontal_accuracy:
            data["horizontal_accuracy"] = horizontal_accuracy
        if heading:
            data["heading"] = heading
        if proximity_alert_radius:
            data["proximity_alert_radius"] = proximity_alert_radius

        return await self._send_message(  # type: ignore[return-value]
            "sendLocation",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_live_location(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        latitude: float = None,
        longitude: float = None,
        reply_markup: InlineKeyboardMarkup = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        *,
        location: Location = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Use this method to edit live location messages sent by the bot or via the bot
        (for inline bots). A location can be edited until its :attr:`telegram.Location.live_period`
        expires or editing is explicitly disabled by a call to :meth:`stop_message_live_location`.

        Note:
            You can either supply a :paramref:`latitude` and :paramref:`longitude` or a
            :paramref:`location`.

        .. seealso:: :attr:`telegram.Message.edit_live_location`,
            :attr:`telegram.CallbackQuery.edit_message_live_location`

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the
                location, measured in meters;
                0-:tg-const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`.
            heading (:obj:`int`, optional): Direction in which the user is moving, in degrees. Must
                be between 1 and :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
            proximity_alert_radius (:obj:`int`, optional): Maximum distance for proximity alerts
                about approaching another chat member, in meters. Must be between 1 and
                :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard.

        Keyword Args:
            location (:class:`telegram.Location`, optional): The location to send.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.
        """
        # The location parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if not (all([latitude, longitude]) or location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument."
            )
        if not (latitude is not None or longitude is not None) ^ bool(location):
            raise ValueError(
                "Either location or latitude and longitude must be passed as argument. Not both."
            )

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data: JSONDict = {"latitude": latitude, "longitude": longitude}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        if horizontal_accuracy:
            data["horizontal_accuracy"] = horizontal_accuracy
        if heading:
            data["heading"] = heading
        if proximity_alert_radius:
            data["proximity_alert_radius"] = proximity_alert_radius

        return await self._send_message(
            "editMessageLiveLocation",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def stop_message_live_location(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Use this method to stop updating a live location message sent by the bot or via the bot
        (for inline bots) before live_period expires.

        .. seealso:: :attr:`telegram.Message.stop_live_location`
            :attr:`telegram.CallbackQuery.stop_message_live_location`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Required if inline_message_id is not specified.
                Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message with live location to stop.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.
        """
        data: JSONDict = {}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id

        return await self._send_message(
            "stopMessageLiveLocation",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_venue(
        self,
        chat_id: Union[int, str],
        latitude: float = None,
        longitude: float = None,
        title: str = None,
        address: str = None,
        foursquare_id: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        foursquare_type: str = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        venue: Venue = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send information about a venue.

        Note:
            * You can either supply :paramref:`venue`, or :paramref:`latitude`,
              :paramref:`longitude`, :paramref:`title` and :paramref:`address` and optionally
              :paramref:`foursquare_id` and :paramref:`foursquare_type` or optionally
              :paramref:`google_place_id` and :paramref:`google_place_type`.
            * Foursquare details and Google Place details are mutually exclusive. However, this
              behaviour is undocumented and might be changed by Telegram.

        .. seealso:: :attr:`telegram.Message.reply_venue`, :attr:`telegram.Chat.send_venue`,
            :attr:`telegram.User.send_venue`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            latitude (:obj:`float`, optional): Latitude of venue.
            longitude (:obj:`float`, optional): Longitude of venue.
            title (:obj:`str`, optional): Name of the venue.
            address (:obj:`str`, optional): Address of the venue.
            foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue.
            foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
                "food/icecream".)
            google_place_id (:obj:`str`, optional): Google Places identifier of the venue.
            google_place_type (:obj:`str`, optional): Google Places type of the venue. (See
                `supported types \
                <https://developers.google.com/maps/documentation/places/web-service/supported_types>`_.)
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            venue (:class:`telegram.Venue`, optional): The venue to send.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        # The venue parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if not (venue or all([latitude, longitude, address, title])):
            raise ValueError(
                "Either venue or latitude, longitude, address and title must be "
                "passed as arguments."
            )
        if not bool(venue) ^ any([latitude, longitude, address, title]):
            raise ValueError(
                "Either venue or latitude, longitude, address and title must be "
                "passed as arguments. Not both."
            )

        if isinstance(venue, Venue):
            latitude = venue.location.latitude
            longitude = venue.location.longitude
            address = venue.address
            title = venue.title
            foursquare_id = venue.foursquare_id
            foursquare_type = venue.foursquare_type
            google_place_id = venue.google_place_id
            google_place_type = venue.google_place_type

        data: JSONDict = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "title": title,
        }

        if foursquare_id:
            data["foursquare_id"] = foursquare_id
        if foursquare_type:
            data["foursquare_type"] = foursquare_type
        if google_place_id:
            data["google_place_id"] = google_place_id
        if google_place_type:
            data["google_place_type"] = google_place_type

        return await self._send_message(  # type: ignore[return-value]
            "sendVenue",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_contact(
        self,
        chat_id: Union[int, str],
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        vcard: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        contact: Contact = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send phone contacts.

        Note:
            You can either supply :paramref:`contact` or :paramref:`phone_number` and
            :paramref:`first_name` with optionally :paramref:`last_name` and optionally
            :paramref:`vcard`.

        .. seealso:: :attr:`telegram.Message.reply_contact`,  :attr:`telegram.Chat.send_contact`,
            :attr:`telegram.User.send_contact`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            phone_number (:obj:`str`, optional): Contact's phone number.
            first_name (:obj:`str`, optional): Contact's first name.
            last_name (:obj:`str`, optional): Contact's last name.
            vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
                0-2048 bytes.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            contact (:class:`telegram.Contact`, optional): The contact to send.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        # The contact parameter is a convenience functionality added by us, so enforcing the
        # mutual exclusivity here is nothing that Telegram would handle anyway
        if (not contact) and (not all([phone_number, first_name])):
            raise ValueError(
                "Either contact or phone_number and first_name must be passed as arguments."
            )
        if not bool(contact) ^ any([phone_number, first_name]):
            raise ValueError(
                "Either contact or phone_number and first_name must be passed as arguments. "
                "Not both."
            )

        if isinstance(contact, Contact):
            phone_number = contact.phone_number
            first_name = contact.first_name
            last_name = contact.last_name
            vcard = contact.vcard

        data: JSONDict = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "first_name": first_name,
        }

        if last_name:
            data["last_name"] = last_name
        if vcard:
            data["vcard"] = vcard

        return await self._send_message(  # type: ignore[return-value]
            "sendContact",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_game(
        self,
        chat_id: Union[int, str],
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: InlineKeyboardMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send a game.

        .. seealso:: :attr:`telegram.Message.reply_game`, :attr:`telegram.Chat.send_game`,
            :attr:`telegram.User.send_game`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat.
            game_short_name (:obj:`str`): Short name of the game, serves as the unique identifier
                for the game. Set up your games via `@BotFather <https://t.me/BotFather>`_.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                inline keyboard. If empty, one ‘Play game_title’ button will be
                shown. If not empty, the first button must launch the game.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "game_short_name": game_short_name}

        return await self._send_message(  # type: ignore[return-value]
            "sendGame",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status). Telegram only recommends using this method when
        a response from the bot will take a noticeable amount of time to arrive.

        .. seealso:: :attr:`telegram.Message.reply_chat_action`, :attr:`telegram.Chat.send_action`,
            :attr:`telegram.User.send_chat_action`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            action(:obj:`str`): Type of action to broadcast. Choose one, depending on what the user
                is about to receive. For convenience look at the constants in
                :class:`telegram.constants.ChatAction`.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`:  On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "action": action}
        result = await self._post(
            "sendChatAction",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    def _effective_inline_results(  # skipcq: PYL-R0201
        self,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        next_offset: str = None,
        current_offset: str = None,
    ) -> Tuple[Sequence["InlineQueryResult"], Optional[str]]:
        """
        Builds the effective results from the results input.
        We make this a stand-alone method so tg.ext.ExtBot can wrap it.

        Returns:
            Tuple of 1. the effective results and 2. correct the next_offset

        """
        if current_offset is not None and next_offset is not None:
            raise ValueError("`current_offset` and `next_offset` are mutually exclusive!")

        if current_offset is not None:
            # Convert the string input to integer
            if current_offset == "":
                current_offset_int = 0
            else:
                current_offset_int = int(current_offset)

            # for now set to empty string, stating that there are no more results
            # might change later
            next_offset = ""

            if callable(results):
                callable_output = results(current_offset_int)
                if not callable_output:
                    effective_results: Sequence["InlineQueryResult"] = []
                else:
                    effective_results = callable_output
                    # the callback *might* return more results on the next call, so we increment
                    # the page count
                    next_offset = str(current_offset_int + 1)
            else:
                if len(results) > (current_offset_int + 1) * InlineQueryLimit.RESULTS:
                    # we expect more results for the next page
                    next_offset_int = current_offset_int + 1
                    next_offset = str(next_offset_int)
                    effective_results = results[
                        current_offset_int
                        * InlineQueryLimit.RESULTS : next_offset_int
                        * InlineQueryLimit.RESULTS
                    ]
                else:
                    effective_results = results[current_offset_int * InlineQueryLimit.RESULTS :]
        else:
            effective_results = results  # type: ignore[assignment]

        return effective_results, next_offset

    @no_type_check  # mypy doesn't play too well with hasattr
    def _insert_defaults_for_ilq_results(self, res: "InlineQueryResult") -> None:
        """The reason why this method exists is similar to the description of _insert_defaults
        The reason why we do this in rather than in _insert_defaults is because converting
        DEFAULT_NONE to NONE *before* calling to_dict() makes it way easier to drop None entries
        from the json data.
        """
        if hasattr(res, "parse_mode"):
            res.parse_mode = DefaultValue.get_value(res.parse_mode)
        if hasattr(res, "input_message_content") and res.input_message_content:
            if hasattr(res.input_message_content, "parse_mode"):
                res.input_message_content.parse_mode = DefaultValue.get_value(
                    res.input_message_content.parse_mode
                )
            if hasattr(res.input_message_content, "disable_web_page_preview"):
                res.input_message_content.disable_web_page_preview = DefaultValue.get_value(
                    res.input_message_content.disable_web_page_preview
                )

    @_log
    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: Union[
            Sequence["InlineQueryResult"], Callable[[int], Optional[Sequence["InlineQueryResult"]]]
        ],
        cache_time: int = None,
        is_personal: bool = None,
        next_offset: str = None,
        switch_pm_text: str = None,
        switch_pm_parameter: str = None,
        *,
        current_offset: str = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to send answers to an inline query. No more than
        :tg-const:`telegram.InlineQuery.MAX_RESULTS` results per query are allowed.

        Warning:
            In most use cases :paramref:`current_offset` should not be passed manually. Instead of
            calling this method directly, use the shortcut :meth:`telegram.InlineQuery.answer` with
            :paramref:`telegram.InlineQuery.answer.auto_pagination` set to :obj:`True`, which will
            take care of passing the correct value.

        .. seealso:: :attr:`telegram.InlineQuery.answer`

        Args:
            inline_query_id (:obj:`str`): Unique identifier for the answered query.
            results (List[:class:`telegram.InlineQueryResult`] | Callable): A list of results for
                the inline query. In case :paramref:`current_offset` is passed,
                :paramref:`results` may also be
                a callable that accepts the current page index starting from 0. It must return
                either a list of :class:`telegram.InlineQueryResult` instances or :obj:`None` if
                there are no more results.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the inline query may be cached on the server. Defaults to ``300``.
            is_personal (:obj:`bool`, optional): Pass :obj:`True`, if results may be cached on
                the server side only for the user that sent the query. By default,
                results may be returned to any user who sends the same query.
            next_offset (:obj:`str`, optional): Pass the offset that a client should send in the
                next query with the same text to receive more results. Pass an empty string if
                there are no more results or if you don't support pagination. Offset length can't
                exceed 64 bytes.
            switch_pm_text (:obj:`str`, optional): If passed, clients will display a button with
                specified text that switches the user to a private chat with the bot and sends the
                bot a start message with the parameter :paramref:`switch_pm_parameter`.
            switch_pm_parameter (:obj:`str`, optional): Deep-linking parameter for the
                :guilabel:`/start` message sent to the bot when user presses the switch button.
                1-:tg-const:`telegram.InlineQuery.MAX_SWITCH_PM_TEXT_LENGTH` characters,
                only ``A-Z``, ``a-z``, ``0-9``, ``_`` and ``-`` are allowed.

        Keyword Args:
            current_offset (:obj:`str`, optional): The :attr:`telegram.InlineQuery.offset` of
                the inline query to answer. If passed, PTB will automatically take care of
                the pagination for you, i.e. pass the correct :paramref:`next_offset` and truncate
                the results list/get the results from the callable you passed.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Example:
            An inline bot that sends YouTube videos can ask the user to connect the bot to their
            YouTube account to adapt search results accordingly. To do this, it displays a
            'Connect your YouTube account' button above the results, or even before showing any.
            The user presses the button, switches to a private chat with the bot and, in doing so,
            passes a start parameter that instructs the bot to return an oauth link. Once done, the
            bot can offer a switch_inline button so that the user can easily return to the chat
            where they wanted to use the bot's inline capabilities.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        effective_results, next_offset = self._effective_inline_results(
            results=results, next_offset=next_offset, current_offset=current_offset
        )

        # Apply defaults
        for result in effective_results:
            self._insert_defaults_for_ilq_results(result)

        data: JSONDict = {"inline_query_id": inline_query_id, "results": effective_results}

        if cache_time or cache_time == 0:
            data["cache_time"] = cache_time
        if is_personal:
            data["is_personal"] = is_personal
        if next_offset is not None:
            data["next_offset"] = next_offset
        if switch_pm_text:
            data["switch_pm_text"] = switch_pm_text
        if switch_pm_parameter:
            data["switch_pm_parameter"] = switch_pm_parameter

        return await self._post(  # type: ignore[return-value]
            "answerInlineQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_user_profile_photos(
        self,
        user_id: Union[str, int],
        offset: int = None,
        limit: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> UserProfilePhotos:
        """Use this method to get a list of profile pictures for a user.

        .. seealso:: :meth:`telegram.User.get_profile_photos`

        Args:
            user_id (:obj:`int`): Unique identifier of the target user.
            offset (:obj:`int`, optional): Sequential number of the first photo to be returned.
                By default, all photos are returned.
            limit (:obj:`int`, optional): Limits the number of photos to be retrieved. Values
                between 1-100 are accepted. Defaults to ``100``.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.UserProfilePhotos`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id}

        if offset is not None:
            data["offset"] = offset
        if limit:
            data["limit"] = limit

        result = await self._post(
            "getUserProfilePhotos",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return UserProfilePhotos.de_json(result, self)  # type: ignore[arg-type,return-value]

    @_log
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
        api_kwargs: JSONDict = None,
    ) -> File:
        """
        Use this method to get basic info about a file and prepare it for downloading. For the
        moment, bots can download files of up to
        :tg-const:`telegram.constants.FileSizeLimit.FILESIZE_DOWNLOAD` in size. The file can then
        be downloaded
        with :meth:`telegram.File.download`. It is guaranteed that the link will be
        valid for at least 1 hour. When the link expires, a new one can be requested by
        calling get_file again.

        Note:
             This function may not preserve the original file name and MIME type.
             You should save the file's MIME type and name (if available) when the File object
             is received.

        Args:
            file_id (:obj:`str` | :class:`telegram.Animation` | :class:`telegram.Audio` |         \
                     :class:`telegram.ChatPhoto` | :class:`telegram.Document` |                   \
                     :class:`telegram.PhotoSize` | :class:`telegram.Sticker` |                    \
                     :class:`telegram.Video` | :class:`telegram.VideoNote` |                      \
                     :class:`telegram.Voice`):
                Either the file identifier or an object that has a file_id attribute
                to get file information about.

         Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        try:
            file_id = file_id.file_id  # type: ignore[union-attr]
        except AttributeError:
            pass

        data: JSONDict = {"file_id": file_id}

        result = await self._post(
            "getFile",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        if result.get("file_path") and not is_local_file(  # type: ignore[union-attr]
            result["file_path"]  # type: ignore[index]
        ):
            result[  # type: ignore[index]
                "file_path"
            ] = f"{self._base_file_url}/{result['file_path']}"  # type: ignore[index]

        return File.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def ban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        until_date: Union[int, datetime] = None,
        revoke_messages: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to ban a user from a group, supergroup or a channel. In the case of
        supergroups and channels, the user will not be able to return to the group on their own
        using invite links, etc., unless unbanned first. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        .. seealso:: :attr:`telegram.Chat.ban_member`

         .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the user will
                be unbanned, unix time. If user is banned for more than 366 days or less than 30
                seconds from the current time they are considered to be banned forever. Applied
                for supergroups and channels only.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            revoke_messages (:obj:`bool`, optional): Pass :obj:`True` to delete all messages from
                the chat for the user that is being removed. If :obj:`False`, the user will be able
                to see messages in the group that were sent before the user was removed.
                Always :obj:`True` for supergroups and channels.

                .. versionadded:: 13.4

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        if until_date is not None:
            data["until_date"] = until_date

        if revoke_messages is not None:
            data["revoke_messages"] = revoke_messages

        result = await self._post(
            "banChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def ban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to ban a channel chat in a supergroup or a channel. Until the chat is
        unbanned, the owner of the banned chat won't be able to send messages on behalf of **any of
        their channels**. The bot must be an administrator in the supergroup or channel for this
        to work and must have the appropriate administrator rights.

        .. seealso:: :attr:`telegram.Chat.ban_chat`, :attr:`telegram.Chat.ban_sender_chat`

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}

        result = await self._post(
            "banChatSenderChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def unban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        only_if_banned: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to unban a previously kicked user in a supergroup or channel.

        The user will *not* return to the group or channel automatically, but will be able to join
        via link, etc. The bot must be an administrator for this to work. By default, this method
        guarantees that after the call the user is not a member of the chat, but will be able to
        join it. So if the user is a member of the chat they will also be *removed* from the chat.
        If you don't want this, use the parameter :paramref:`only_if_banned`.

        .. seealso:: :attr:`telegram.Chat.unban_member`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            only_if_banned (:obj:`bool`, optional): Do nothing if the user is not banned.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        if only_if_banned is not None:
            data["only_if_banned"] = only_if_banned

        result = await self._post(
            "unbanChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def unban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to unban a previously banned channel in a supergroup or channel.
        The bot must be an administrator for this to work and must have the
        appropriate administrator rights.

        .. seealso:: :attr:`telegram.Chat.unban_chat`

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}

        result = await self._post(
            "unbanChatSenderChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str = None,
        show_alert: bool = None,
        url: str = None,
        cache_time: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to send answers to callback queries sent from inline keyboards. The answer
        will be displayed to the user as a notification at the top of the chat screen or as an
        alert.
        Alternatively, the user can be redirected to the specified Game URL. For this option to
        work, you must first create a game for your bot via `@BotFather <https://t.me/BotFather>`_
        and accept the terms. Otherwise, you may use links like t.me/your_bot?start=XXXX that open
        your bot with a parameter.

        .. seealso:: :attr:`telegram.CallbackQuery.answer`

        Args:
            callback_query_id (:obj:`str`): Unique identifier for the query to be answered.
            text (:obj:`str`, optional): Text of the notification. If not specified, nothing will
                be shown to the user, 0-:tg-const:`telegram.CallbackQuery.MAX_ANSWER_TEXT_LENGTH`
                characters.
            show_alert (:obj:`bool`, optional): If :obj:`True`, an alert will be shown by the
                client instead of a notification at the top of the chat screen. Defaults to
                :obj:`False`.
            url (:obj:`str`, optional): URL that will be opened by the user's client. If you have
                created a Game and accepted the conditions via
                `@BotFather <https://t.me/BotFather>`_, specify the URL that
                opens your game - note that this will only work if the query comes from a callback
                game button. Otherwise, you may use links like t.me/your_bot?start=XXXX that open
                your bot with a parameter.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the callback query may be cached client-side. Defaults to 0.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"callback_query_id": callback_query_id}

        if text:
            data["text"] = text
        if show_alert:
            data["show_alert"] = show_alert
        if url:
            data["url"] = url
        if cache_time is not None:
            data["cache_time"] = cache_time

        result = await self._post(
            "answerCallbackQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def edit_message_text(
        self,
        text: str,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: InlineKeyboardMarkup = None,
        entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit text and game messages.

        Note:
            |editreplymarkup|.

        .. seealso:: :attr:`telegram.Message.edit_text`,
            :attr:`telegram.CallbackQuery.edit_message_text`

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``)
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            text (:obj:`str`): New text of the message,
                1-:tg-const:`telegram.constants.MessageLimit.TEXT_LENGTH` characters after entities
                parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in your bot's message. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            entities (List[:class:`telegram.MessageEntity`], optional): List of special entities
                that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        if entities:
            data["entities"] = [me.to_dict() for me in entities]

        return await self._send_message(
            "editMessageText",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_caption(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        caption: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit captions of messages.

        Note:
            |editreplymarkup|

        .. seealso:: :attr:`telegram.Message.edit_caption`,
            :attr:`telegram.CallbackQuery.edit_message_caption`

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``)
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            caption (:obj:`str`, optional): New caption of the message,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`parse_mode`.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"parse_mode": parse_mode}

        if caption:
            data["caption"] = caption
        if caption_entities:
            data["caption_entities"] = caption_entities
        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id

        return await self._send_message(
            "editMessageCaption",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_media(
        self,
        media: "InputMedia",
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit animation, audio, document, photo, or video messages. If a message
        is part of a message album, then it can be edited only to an audio for audio albums, only
        to a document for document albums and to a photo or a video otherwise. When an inline
        message is edited, a new file can't be uploaded; use a previously uploaded file via its
        :attr:`~telegram.File.file_id` or specify a URL.

        Note:
            |editreplymarkup|

        .. seealso:: :attr:`telegram.Message.edit_media`,
            :attr:`telegram.CallbackQuery.edit_message_media`

        Args:
            media (:class:`telegram.InputMedia`): An object for a new media content
                of the message.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited Message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"media": media}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id

        return await self._send_message(
            "editMessageMedia",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def edit_message_reply_markup(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot
        (for inline bots).

        Note:
            |editreplymarkup|

        .. seealso:: :attr:`telegram.Message.edit_reply_markup`,
            :attr:`telegram.CallbackQuery.edit_message_reply_markup`

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id

        return await self._send_message(
            "editMessageReplyMarkup",
            data,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
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
        """Use this method to receive incoming updates using long polling.

        Note:
            1. This method will not work if an outgoing webhook is set up.
            2. In order to avoid getting duplicate updates, recalculate offset after each
               server response.
            3. To take full advantage of this library take a look at :class:`telegram.ext.Updater`

        Args:
            offset (:obj:`int`, optional): Identifier of the first update to be returned. Must be
                greater by one than the highest among the identifiers of previously received
                updates. By default, updates starting with the earliest unconfirmed update are
                returned. An update is considered confirmed as soon as this method is called with
                an offset higher than its :attr:`telegram.Update.update_id`. The negative offset
                can be specified to retrieve updates starting from -offset update from the end of
                the updates queue. All previous updates will forgotten.
            limit (:obj:`int`, optional): Limits the number of updates to be retrieved. Values
                between 1-100 are accepted. Defaults to ``100``.
            timeout (:obj:`int`, optional): Timeout in seconds for long polling. Defaults to ``0``,
                i.e. usual short polling. Should be positive, short polling should be used for
                testing purposes only.
            allowed_updates (List[:obj:`str`]), optional): A list the types of
                updates you want your bot to receive. For example, specify ["message",
                "edited_channel_post", "callback_query"] to only receive updates of these types.
                See :class:`telegram.Update` for a complete list of available update types.
                Specify an empty list to receive all updates except
                :attr:`telegram.Update.chat_member` (default). If not specified, the previous
                setting will be used. Please note that this parameter doesn't affect updates
                created before the call to the get_updates, so unwanted updates may be received for
                a short period of time.

        Keyword Args:
            read_timeout (:obj:`float`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                ``2``. :paramref:`timeout` will be added to this value.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.Update`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"timeout": timeout}

        if offset:
            data["offset"] = offset
        if limit:
            data["limit"] = limit
        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates

        # Ideally we'd use an aggressive read timeout for the polling. However,
        # * Short polling should return within 2 seconds.
        # * Long polling poses a different problem: the connection might have been dropped while
        #   waiting for the server to return and there's no way of knowing the connection had been
        #   dropped in real time.
        result = cast(
            List[JSONDict],
            await self._post(
                "getUpdates",
                data,
                read_timeout=read_timeout + timeout if timeout else read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
        )

        if result:
            self._logger.debug("Getting updates: %s", [u["update_id"] for u in result])
        else:
            self._logger.debug("No new updates found.")

        return Update.de_list(result, self)  # type: ignore[return-value]

    @_log
    async def set_webhook(
        self,
        url: str,
        certificate: FileInput = None,
        max_connections: int = None,
        allowed_updates: List[str] = None,
        ip_address: str = None,
        drop_pending_updates: bool = None,
        secret_token: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, Telegram will send an HTTPS POST request to the
        specified url, containing An Update. In case of an unsuccessful request,
        Telegram will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook was set by you, you can specify secret data in
        the parameter :paramref:`secret_token`. If specified, the request will contain a header
        ``X-Telegram-Bot-Api-Secret-Token`` with the secret token as content.

        Note:
            1. You will not be able to receive updates using :meth:`get_updates` for long as an
               outgoing webhook is set up.
            2. To use a self-signed certificate, you need to upload your public key certificate
               using :paramref:`certificate` parameter. Please upload as
               :class:`~telegram.InputFile`, sending a String will not work.
            3. Ports currently supported for Webhooks:
               :attr:`telegram.constants.SUPPORTED_WEBHOOK_PORTS`.

            If you're having any trouble setting up webhooks, please check out this `guide to
            Webhooks`_.

        Args:
            url (:obj:`str`): HTTPS url to send updates to. Use an empty string to remove webhook
                integration.
            certificate (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`):
                Upload your public key certificate so that the root
                certificate in use can be checked. See our `self-signed guide <https://github.com/\
                python-telegram-bot/python-telegram-bot/wiki/Webhooks#creating-a-self-signed-\
                certificate-using-openssl>`_ for details. |uploadinputnopath|
            ip_address (:obj:`str`, optional): The fixed IP address which will be used to send
                webhook requests instead of the IP address resolved through DNS.
            max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
                connections to the webhook for update delivery, 1-100. Defaults to ``40``. Use
                lower values to limit the load on your bot's server, and higher values to increase
                your bot's throughput.
            allowed_updates (List[:obj:`str`], optional): A list the types of
                updates you want your bot to receive. For example, specify ["message",
                "edited_channel_post", "callback_query"] to only receive updates of these types.
                See :class:`telegram.Update` for a complete list of available update types.
                Specify an empty list to receive all updates except
                :attr:`telegram.Update.chat_member` (default). If not specified, the previous
                setting will be used. Please note that this parameter doesn't affect updates
                created before the call to the set_webhook, so unwanted updates may be received for
                a short period of time.
            drop_pending_updates (:obj:`bool`, optional): Pass :obj:`True` to drop all pending
                updates.
            secret_token (:obj:`str`, optional): A secret token to be sent in a header
                ``X-Telegram-Bot-Api-Secret-Token`` in every webhook request,
                :tg-const:`telegram.constants.WebhookLimit.MIN_SECRET_TOKEN_LENGTH`-
                :tg-const:`telegram.constants.WebhookLimit.MAX_SECRET_TOKEN_LENGTH` characters.
                Only characters ``A-Z``, ``a-z``, ``0-9``, ``_`` and ``-`` are allowed.
                The header is useful to ensure that the request comes from a webhook set by you.

                .. versionadded:: 20.0

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        .. _`guide to Webhooks`: https://core.telegram.org/bots/webhooks

        """
        data: JSONDict = {"url": url}

        if certificate:
            data["certificate"] = self._parse_file_input(certificate)
        if max_connections is not None:
            data["max_connections"] = max_connections
        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates
        if ip_address:
            data["ip_address"] = ip_address
        if drop_pending_updates:
            data["drop_pending_updates"] = drop_pending_updates
        if secret_token is not None:
            data["secret_token"] = secret_token

        result = await self._post(
            "setWebhook",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def delete_webhook(
        self,
        drop_pending_updates: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to remove webhook integration if you decide to switch back to
        :meth:`get_updates()`.

        Args:
            drop_pending_updates (:obj:`bool`, optional): Pass :obj:`True` to drop all pending
                updates.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {}

        if drop_pending_updates:
            data["drop_pending_updates"] = drop_pending_updates

        result = await self._post(
            "deleteWebhook",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def leave_chat(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method for your bot to leave a group, supergroup or channel.

        .. seealso:: :attr:`telegram.Chat.leave`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        result = await self._post(
            "leaveChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
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
        """
        Use this method to get up to date information about the chat (current name of the user for
        one-on-one conversations, current username of a user, group or channel, etc.).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Chat`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        result = await self._post(
            "getChat",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return Chat.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def get_chat_administrators(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[ChatMember]:
        """
        Use this method to get a list of administrators in a chat.

        .. seealso:: :attr:`telegram.Chat.get_administrators`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.ChatMember`]: On success, returns a list of ``ChatMember``
            objects that contains information about all chat administrators except
            other bots. If the chat is a group or a supergroup and no administrators were
            appointed, only the creator will be returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "getChatAdministrators",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return ChatMember.de_list(result, self)  # type: ignore

    @_log
    async def get_chat_member_count(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> int:
        """Use this method to get the number of members in a chat.

        .. seealso:: :attr:`telegram.Chat.get_member_count`

        .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`int`: Number of members in the chat.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "getChatMemberCount",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def get_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatMember:
        """Use this method to get information about a member of a chat.

        .. seealso:: :attr:`telegram.Chat.get_member`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatMember`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}
        result = await self._post(
            "getChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return ChatMember.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def set_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        sticker_set_name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to set a new group sticker set for a supergroup.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights. Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned
        in :meth:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            sticker_set_name (:obj:`str`): Name of the sticker set to be set as the group
                sticker set.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {"chat_id": chat_id, "sticker_set_name": sticker_set_name}
        result = await self._post(
            "setChatStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def delete_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to delete a group sticker set from a supergroup. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned in
        :meth:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
             :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "deleteChatStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    async def get_webhook_info(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> WebhookInfo:
        """Use this method to get current webhook status. Requires no parameters.

        If the bot is using :meth:`get_updates`, will return an object with the
        :attr:`telegram.WebhookInfo.url` field empty.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.WebhookInfo`

        """
        result = await self._post(
            "getWebhookInfo",
            None,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return WebhookInfo.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        force: bool = None,
        disable_edit_message: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to set the score of the specified user in a game message.

        .. seealso::`telegram.CallbackQuery.set_game_score`

        Args:
            user_id (:obj:`int`): User identifier.
            score (:obj:`int`): New score, must be non-negative.
            force (:obj:`bool`, optional): Pass :obj:`True`, if the high score is allowed to
                decrease. This can be useful when fixing mistakes or banning cheaters.
            disable_edit_message (:obj:`bool`, optional): Pass :obj:`True`, if the game message
                should not be automatically edited to include the current scoreboard.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: The edited message. If the message is not an inline message
            , :obj:`True`.

        Raises:
            :class:`telegram.error.TelegramError`: If the new score is not greater than the user's
                current score in the chat and force is :obj:`False`.

        """
        data: JSONDict = {"user_id": user_id, "score": score}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        if force is not None:
            data["force"] = force
        if disable_edit_message is not None:
            data["disable_edit_message"] = disable_edit_message

        return await self._send_message(
            "setGameScore",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_game_high_scores(
        self,
        user_id: Union[int, str],
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[GameHighScore]:
        """
        Use this method to get data for high score tables. Will return the score of the specified
        user and several of their neighbors in a game.

        Note:
            This method will currently return scores for the target user, plus two of their
            closest neighbors on each side. Will also return the top three users if the user and
            his neighbors are not among them. Please note that this behavior is subject to change.

        .. seealso:: :attr:`telegram.CallbackQuery.get_game_high_scores`

        Args:
            user_id (:obj:`int`): Target user id.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.GameHighScore`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id}

        if chat_id:
            data["chat_id"] = chat_id
        if message_id:
            data["message_id"] = message_id
        if inline_message_id:
            data["inline_message_id"] = inline_message_id

        result = await self._post(
            "getGameHighScores",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return GameHighScore.de_list(result, self)  # type: ignore

    @_log
    async def send_invoice(
        self,
        chat_id: Union[int, str],
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List["LabeledPrice"],
        start_parameter: str = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        is_flexible: bool = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: InlineKeyboardMarkup = None,
        provider_data: Union[str, object] = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """Use this method to send invoices.

        Warning:
            As of API 5.2 :paramref:`start_parameter` is an optional argument and therefore the
            order of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. seealso:: :attr:`telegram.Message.reply_invoice`, :attr:`telegram.Chat.send_invoice`,
            :attr:`telegram.User.send_invoice`

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :paramref:`start_parameter` is optional.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            title (:obj:`str`): Product name. :tg-const:`telegram.Invoice.MIN_TITLE_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_TITLE_LENGTH` characters.
            description (:obj:`str`): Product description.
                :tg-const:`telegram.Invoice.MIN_DESCRIPTION_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_DESCRIPTION_LENGTH` characters.
            payload (:obj:`str`): Bot-defined invoice payload.
                :tg-const:`telegram.Invoice.MIN_PAYLOAD_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_PAYLOAD_LENGTH` bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via
                `@BotFather <https://t.me/BotFather>`_.
            currency (:obj:`str`): Three-letter ISO 4217 currency code, see `more on currencies
                <https://core.telegram.org/bots/payments#supported-currencies>`_.
            prices (List[:class:`telegram.LabeledPrice`)]: Price breakdown, a list
                of components (e.g. product price, tax, discount, delivery cost, delivery tax,
                bonus, etc.).
            max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the
                *smallest* units of the currency (integer, **not** float/double). For example, for
                a maximum tip of US$ 1.45 pass ``max_tip_amount = 145``. See the exp parameter in
                `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
                shows the number of digits past the decimal point for each currency (2 for the
                majority of currencies). Defaults to ``0``.

                .. versionadded:: 13.5
            suggested_tip_amounts (List[:obj:`int`], optional): An array of
                suggested amounts of tips in the *smallest* units of the currency (integer, **not**
                float/double). At most 4 suggested tip amounts can be specified. The suggested tip
                amounts must be positive, passed in a strictly increased order and must not exceed
                :paramref:`max_tip_amount`.

                .. versionadded:: 13.5
            start_parameter (:obj:`str`, optional): Unique deep-linking parameter. If left empty,
                *forwarded copies* of the sent message will have a *Pay* button, allowing
                multiple users to pay directly from the forwarded message, using the same invoice.
                If non-empty, forwarded copies of the sent message will have a *URL* button with a
                deep link to the bot (instead of a *Pay* button), with the value used as the
                start parameter.

                .. versionchanged:: 13.5
                    As of Bot API 5.2, this parameter is optional.
            provider_data (:obj:`str` | :obj:`object`, optional): data about the
                invoice, which will be shared with the payment provider. A detailed description of
                required fields should be provided by the payment provider. When an object is
                passed, it will be encoded as JSON.
            photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a
                photo of the goods or a marketing image for a service. People like it better when
                they see what they are paying for.
            photo_size (:obj:`str`, optional): Photo size.
            photo_width (:obj:`int`, optional): Photo width.
            photo_height (:obj:`int`, optional): Photo height.
            need_name (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's full
                name to complete the order.
            need_phone_number (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
                phone number to complete the order.
            need_email (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's email
                to complete the order.
            need_shipping_address (:obj:`bool`, optional): Pass :obj:`True`, if you require the
                user's shipping address to complete the order.
            send_phone_number_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's
                phone number should be sent to provider.
            send_email_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's email
                address should be sent to provider.
            is_flexible (:obj:`bool`, optional): Pass :obj:`True`, if the final price depends on
                the shipping method.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for an
                inline keyboard. If empty, one 'Pay total price' button will be
                shown. If not empty, the first button must be a Pay button.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": prices,
        }
        if max_tip_amount is not None:
            data["max_tip_amount"] = max_tip_amount
        if suggested_tip_amounts is not None:
            data["suggested_tip_amounts"] = suggested_tip_amounts
        if start_parameter is not None:
            data["start_parameter"] = start_parameter
        if provider_data is not None:
            data["provider_data"] = provider_data
        if photo_url is not None:
            data["photo_url"] = photo_url
        if photo_size is not None:
            data["photo_size"] = photo_size
        if photo_width is not None:
            data["photo_width"] = photo_width
        if photo_height is not None:
            data["photo_height"] = photo_height
        if need_name is not None:
            data["need_name"] = need_name
        if need_phone_number is not None:
            data["need_phone_number"] = need_phone_number
        if need_email is not None:
            data["need_email"] = need_email
        if need_shipping_address is not None:
            data["need_shipping_address"] = need_shipping_address
        if is_flexible is not None:
            data["is_flexible"] = is_flexible
        if send_phone_number_to_provider is not None:
            data["send_phone_number_to_provider"] = send_phone_number_to_provider
        if send_email_to_provider is not None:
            data["send_email_to_provider"] = send_email_to_provider

        return await self._send_message(  # type: ignore[return-value]
            "sendInvoice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def answer_shipping_query(  # pylint: disable=invalid-name
        self,
        shipping_query_id: str,
        ok: bool,
        shipping_options: List[ShippingOption] = None,
        error_message: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        If you sent an invoice requesting a shipping address and the parameter
        :paramref:`send_invoice.is_flexible` was specified, the Bot API will send an
        :class:`telegram.Update` with a :attr:`telegram.Update.shipping_query` field to the bot.
        Use this method to reply to shipping queries.

        .. seealso:: :attr:`telegram.ShippingQuery.answer`

        Args:
            shipping_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify :obj:`True` if delivery to the specified address is possible
                and :obj:`False` if there are any problems (for example, if delivery to the
                specified address is not possible).
            shipping_options (List[:class:`telegram.ShippingOption`]), optional]: Required if ok is
                :obj:`True`. An array of available shipping options.
            error_message (:obj:`str`, optional): Required if ok is :obj:`False`. Error message in
                human readable form that explains why it is impossible to complete the order (e.g.
                "Sorry, delivery to your desired address is unavailable"). Telegram will display
                this message to the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"shipping_query_id": shipping_query_id, "ok": ok}

        if shipping_options is not None:
            data["shipping_options"] = [option.to_dict() for option in shipping_options]
        if error_message is not None:
            data["error_message"] = error_message

        result = await self._post(
            "answerShippingQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def answer_pre_checkout_query(  # pylint: disable=invalid-name
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Once the user has confirmed their payment and shipping details, the Bot API sends the final
        confirmation in the form of an :class:`telegram.Update` with the field
        :attr:`telegram.Update.pre_checkout_query`. Use this method to respond to such pre-checkout
        queries.

        Note:
            The Bot API must receive an answer within 10 seconds after the pre-checkout
            query was sent.

        .. seealso:: :attr:`telegram.PreCheckoutQuery.answer`

        Args:
            pre_checkout_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify :obj:`True` if everything is alright
                (goods are available, etc.) and the bot is ready to proceed with the order. Use
                :obj:`False` if there are any problems.
            error_message (:obj:`str`, optional): Required if ok is :obj:`False`. Error message
                in human readable form that explains the reason for failure to proceed with
                the checkout (e.g. "Sorry, somebody just bought the last of our amazing black
                T-shirts while you were busy filling out your payment details. Please choose a
                different color or garment!"). Telegram will display this message to the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"pre_checkout_query_id": pre_checkout_query_id, "ok": ok}

        if error_message is not None:
            data["error_message"] = error_message

        result = await self._post(
            "answerPreCheckoutQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def answer_web_app_query(
        self,
        web_app_query_id: str,
        result: "InlineQueryResult",
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> SentWebAppMessage:
        """Use this method to set the result of an interaction with a Web App and send a
        corresponding message on behalf of the user to the chat from which the query originated.

        .. versionadded:: 20.0

        Args:
            web_app_query_id (:obj:`str`): Unique identifier for the query to be answered.
            result (:class:`telegram.InlineQueryResult`): An object describing the message to be
                sent.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.SentWebAppMessage`: On success, a sent
            :class:`telegram.SentWebAppMessage` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"web_app_query_id": web_app_query_id, "result": result}

        api_result = await self._post(
            "answerWebAppQuery",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return SentWebAppMessage.de_json(api_result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def restrict_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        permissions: ChatPermissions,
        until_date: Union[int, datetime] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to restrict a user in a supergroup. The bot must be an administrator in
        the supergroup for this to work and must have the appropriate admin rights. Pass
        :obj:`True` for all boolean parameters to lift restrictions from a user.

        .. seealso:: :meth:`telegram.ChatPermissions.all_permissions`,
            :attr:`telegram.Chat.restrict_member`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when restrictions
                will be lifted for the user, unix time. If user is restricted for more than 366
                days or less than 30 seconds from the current time, they are considered to be
                restricted forever.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            permissions (:class:`telegram.ChatPermissions`): An object for new user
                permissions.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": permissions,
        }

        if until_date is not None:
            data["until_date"] = until_date

        result = await self._post(
            "restrictChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def promote_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        can_change_info: bool = None,
        can_post_messages: bool = None,
        can_edit_messages: bool = None,
        can_delete_messages: bool = None,
        can_invite_users: bool = None,
        can_restrict_members: bool = None,
        can_pin_messages: bool = None,
        can_promote_members: bool = None,
        is_anonymous: bool = None,
        can_manage_chat: bool = None,
        can_manage_video_chats: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to promote or demote a user in a supergroup or a channel. The bot must be
        an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass :obj:`False` for all boolean parameters to demote a user.

        .. seealso:: :attr:`telegram.Chat.promote_member`

        .. versionchanged:: 20.0
           The argument ``can_manage_voice_chats`` was renamed to
           :paramref:`can_manage_video_chats` in accordance to Bot API 6.0.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            is_anonymous (:obj:`bool`, optional): Pass :obj:`True`, if the administrator's presence
                in the chat is hidden.
            can_manage_chat (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                access the chat event log, chat statistics, message statistics in channels, see
                channel members, see anonymous administrators in supergroups and ignore slow mode.
                Implied by any other administrator privilege.

                .. versionadded:: 13.4

            can_manage_video_chats (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can manage video chats.

                .. versionadded:: 20.0

            can_change_info (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                change chat title, photo and other settings.
            can_post_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                create channel posts, channels only.
            can_edit_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                edit messages of other users and can pin messages, channels only.
            can_delete_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                delete messages of other users.
            can_invite_users (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                invite new users to the chat.
            can_restrict_members (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can restrict, ban or unban chat members.
            can_pin_messages (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                pin messages, supergroups only.
            can_promote_members (:obj:`bool`, optional): Pass :obj:`True`, if the administrator can
                add new administrators with a subset of his own privileges or demote administrators
                that he has promoted, directly or indirectly (promoted by administrators that were
                appointed by him).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        if is_anonymous is not None:
            data["is_anonymous"] = is_anonymous
        if can_change_info is not None:
            data["can_change_info"] = can_change_info
        if can_post_messages is not None:
            data["can_post_messages"] = can_post_messages
        if can_edit_messages is not None:
            data["can_edit_messages"] = can_edit_messages
        if can_delete_messages is not None:
            data["can_delete_messages"] = can_delete_messages
        if can_invite_users is not None:
            data["can_invite_users"] = can_invite_users
        if can_restrict_members is not None:
            data["can_restrict_members"] = can_restrict_members
        if can_pin_messages is not None:
            data["can_pin_messages"] = can_pin_messages
        if can_promote_members is not None:
            data["can_promote_members"] = can_promote_members
        if can_manage_chat is not None:
            data["can_manage_chat"] = can_manage_chat
        if can_manage_video_chats is not None:
            data["can_manage_video_chats"] = can_manage_video_chats

        result = await self._post(
            "promoteChatMember",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def set_chat_permissions(
        self,
        chat_id: Union[str, int],
        permissions: ChatPermissions,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to set default chat permissions for all members. The bot must be an
        administrator in the group or a supergroup for this to work and must have the
        :attr:`telegram.ChatMemberAdministrator.can_restrict_members` admin rights.

        .. seealso:: :attr:`telegram.Chat.set_permissions`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username of
                the target supergroup (in the format `@supergroupusername`).
            permissions (:class:`telegram.ChatPermissions`): New default chat permissions.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "permissions": permissions}
        result = await self._post(
            "setChatPermissions",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def set_chat_administrator_custom_title(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        custom_title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to set a custom title for administrators promoted by the bot in a
        supergroup. The bot must be an administrator for this to work.

        .. seealso:: :attr:`telegram.Chat.set_administrator_custom_title`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username of
                the target supergroup (in the format `@supergroupusername`).
            user_id (:obj:`int`): Unique identifier of the target administrator.
            custom_title (:obj:`str`): New custom title for the administrator; 0-16 characters,
                emoji are not allowed.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id, "custom_title": custom_title}

        result = await self._post(
            "setChatAdministratorCustomTitle",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def export_chat_invite_link(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> str:
        """
        Use this method to generate a new primary invite link for a chat; any previously generated
        link is revoked. The bot must be an administrator in the chat for this to work and must
        have the appropriate admin rights.

        Note:
            Each administrator in a chat generates their own invite links. Bots can't use invite
            links generated by other administrators. If you want your bot to work with invite
            links, it will need to generate its own link using :meth:`export_chat_invite_link` or
            by calling the :meth:`get_chat` method. If your bot needs to generate a new primary
            invite link replacing its previous one, use :attr:`export_chat_invite_link` again.

        .. seealso:: :attr:`telegram.Chat.export_invite_link`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`str`: New invite link on success.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "exportChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def create_chat_invite_link(
        self,
        chat_id: Union[str, int],
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        name: str = None,
        creates_join_request: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatInviteLink:
        """
        Use this method to create an additional invite link for a chat. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        The link can be revoked using the method :meth:`revoke_chat_invite_link`.

        .. seealso:: :attr:`telegram.Chat.create_invite_link`

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire. Integer input will be interpreted as Unix timestamp.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link;
                1-:tg-const:`telegram.constants.ChatInviteLinkLimit.MEMBER_LIMIT`.
            name (:obj:`str`, optional): Invite link name;
                0-:tg-const:`telegram.constants.ChatInviteLinkLimit.NAME_LENGTH` characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, :paramref:`member_limit` can't be specified.

                .. versionadded:: 13.8

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        if expire_date is not None:
            data["expire_date"] = expire_date

        if member_limit is not None:
            data["member_limit"] = member_limit

        if name is not None:
            data["name"] = name

        if creates_join_request is not None:
            data["creates_join_request"] = creates_join_request

        result = await self._post(
            "createChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def edit_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        name: str = None,
        creates_join_request: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatInviteLink:
        """
        Use this method to edit a non-primary invite link created by the bot. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.

        Note:
            Though not stated explicitly in the official docs, Telegram changes not only the
            optional parameters that are explicitly passed, but also replaces all other optional
            parameters to the default values. However, since not documented, this behaviour may
            change unbeknown to PTB.

        .. seealso:: :attr:`telegram.Chat.edit_invite_link`

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            invite_link (:obj:`str` | :obj:`telegram.ChatInviteLink`): The invite link to edit.

                .. versionchanged:: 20.0
                    Now also accepts :obj:`telegram.ChatInviteLink` instances.
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link;
                1-:tg-const:`telegram.constants.ChatInviteLinkLimit.MEMBER_LIMIT`.
            name (:obj:`str`, optional): Invite link name;
                0-:tg-const:`telegram.constants.ChatInviteLinkLimit.NAME_LENGTH` characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, :paramref:`member_limit` can't be specified.

                .. versionadded:: 13.8

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        link = invite_link.invite_link if isinstance(invite_link, ChatInviteLink) else invite_link
        data: JSONDict = {"chat_id": chat_id, "invite_link": link}

        if expire_date is not None:
            data["expire_date"] = expire_date

        if member_limit is not None:
            data["member_limit"] = member_limit

        if name is not None:
            data["name"] = name

        if creates_join_request is not None:
            data["creates_join_request"] = creates_join_request

        result = await self._post(
            "editChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def revoke_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: Union[str, "ChatInviteLink"],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatInviteLink:
        """
        Use this method to revoke an invite link created by the bot. If the primary link is
        revoked, a new link is automatically generated. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        .. seealso:: :attr:`telegram.Chat.revoke_invite_link`

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            invite_link (:obj:`str` | :obj:`telegram.ChatInviteLink`): The invite link to revoke.

                .. versionchanged:: 20.0
                    Now also accepts :obj:`telegram.ChatInviteLink` instances.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        link = invite_link.invite_link if isinstance(invite_link, ChatInviteLink) else invite_link
        data: JSONDict = {"chat_id": chat_id, "invite_link": link}

        result = await self._post(
            "revokeChatInviteLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def approve_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to approve a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. seealso:: :attr:`telegram.Chat.approve_join_request`,
            :attr:`telegram.ChatJoinRequest.approve`, :attr:`telegram.User.approve_join_request`

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        result = await self._post(
            "approveChatJoinRequest",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def decline_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to decline a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. seealso:: :attr:`telegram.Chat.decline_join_request`,
            :attr:`telegram.ChatJoinRequest.decline`, :attr:`telegram.User.decline_join_request`

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"chat_id": chat_id, "user_id": user_id}

        result = await self._post(
            "declineChatJoinRequest",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def set_chat_photo(
        self,
        chat_id: Union[str, int],
        photo: FileInput,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to set a new profile photo for the chat.

        Photos can't be changed for private chats. The bot must be an administrator in the chat
        for this to work and must have the appropriate admin rights.

        .. seealso:: :attr:`telegram.Chat.set_photo`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            photo (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path`): New chat photo.
                |uploadinput|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "photo": self._parse_file_input(photo)}
        result = await self._post(
            "setChatPhoto",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def delete_chat_photo(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete a chat photo. Photos can't be changed for private chats. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        .. seealso:: :attr:`telegram.Chat.delete_photo`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        result = await self._post(
            "deleteChatPhoto",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def set_chat_title(
        self,
        chat_id: Union[str, int],
        title: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to change the title of a chat. Titles can't be changed for private chats.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights.

        .. seealso:: :attr:`telegram.Chat.set_title`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            title (:obj:`str`): New chat title, 1-255 characters.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "title": title}
        result = await self._post(
            "setChatTitle",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def set_chat_description(
        self,
        chat_id: Union[str, int],
        description: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to change the description of a group, a supergroup or a channel. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        .. seealso:: :attr:`telegram.Chat.set_description`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            description (:obj:`str`, optional): New chat description, 0-255 characters.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        if description is not None:
            data["description"] = description
        result = await self._post(
            "setChatDescription",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def pin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to add a message to the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` admin
        right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages` admin
        right in a channel.

        .. seealso:: :attr:`telegram.Chat.pin_message`, :attr:`telegram.User.pin_message`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of a message to pin.
            disable_notification (:obj:`bool`, optional): Pass :obj:`True`, if it is not necessary
                to send a notification to all chat members about the new pinned message.
                Notifications are always disabled in channels and private chats.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        }

        return await self._post(  # type: ignore[return-value]
            "pinChatMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to remove a message from the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages` admin
        right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages` admin
        right in a channel.

        .. seealso:: :attr:`telegram.Chat.unpin_message`, :attr:`telegram.User.unpin_message`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Identifier of a message to unpin. If not specified,
                the most recent pinned message (by sending date) will be unpinned.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}

        if message_id is not None:
            data["message_id"] = message_id

        return await self._post(  # type: ignore[return-value]
            "unpinChatMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def unpin_all_chat_messages(
        self,
        chat_id: Union[str, int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this
        to work and must have the :paramref:`~telegram.ChatAdministratorRights.can_pin_messages`
        admin right in a supergroup or :attr:`~telegram.ChatMemberAdministrator.can_edit_messages`
        admin right in a channel.

        .. seealso:: :attr:`telegram.Chat.unpin_all_messages`,
            :attr:`telegram.User.unpin_all_messages`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        return await self._post(  # type: ignore[return-value]
            "unpinAllChatMessages",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_sticker_set(
        self,
        name: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> StickerSet:
        """Use this method to get a sticker set.

        Args:
            name (:obj:`str`): Name of the sticker set.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.StickerSet`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name}
        result = await self._post(
            "getStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return StickerSet.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def get_custom_emoji_stickers(
        self,
        custom_emoji_ids: List[str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[Sticker]:
        # skipcq: FLK-D207
        """
        Use this method to get information about emoji stickers by their identifiers.

        Args:
            custom_emoji_ids (List[:obj:`str`]): List of custom emoji identifiers.
                At most :tg-const:`telegram.constants.CustomEmojiStickerLimit.\
CUSTOM_EMOJI_IDENTIFIER_LIMIT` custom emoji identifiers can be specified.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.Sticker`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"custom_emoji_ids": custom_emoji_ids}
        result = await self._post(
            "getCustomEmojiStickers",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return Sticker.de_list(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def upload_sticker_file(
        self,
        user_id: Union[str, int],
        png_sticker: FileInput,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> File:
        """
        Use this method to upload a ``.PNG`` file with a sticker for later use in
        :meth:`create_new_sticker_set` and :meth:`add_sticker_to_set` methods (can be used multiple
        times).

        Args:
            user_id (:obj:`int`): User identifier of sticker file owner.
            png_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`):
                **PNG** image with the sticker, must be up to 512 kilobytes in size,
                dimensions must not exceed 512px, and either width or height must be exactly 512px.
                |uploadinput|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.File`: On success, the uploaded File is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "png_sticker": self._parse_file_input(png_sticker)}
        result = await self._post(
            "uploadStickerFile",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return File.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def create_new_sticker_set(
        self,
        user_id: Union[str, int],
        name: str,
        title: str,
        emojis: str,
        png_sticker: FileInput = None,
        mask_position: MaskPosition = None,
        tgs_sticker: FileInput = None,
        webm_sticker: FileInput = None,
        sticker_type: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to create new sticker set owned by a user.
        The bot will be able to edit the created sticker set.
        You must use exactly one of the fields :paramref:`png_sticker`, :paramref:`tgs_sticker`,
        or :paramref:`webm_sticker`.

        Warning:
            As of API 4.7 :paramref:`png_sticker` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 20.0
            The parameter ``contains_masks`` has been removed. Use :paramref:`sticker_type`
            instead.

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Short name of sticker set, to be used in t.me/addstickers/ URLs
                (e.g., animals). Can contain only english letters, digits and underscores.
                Must begin with a letter, can't contain consecutive underscores and
                must end in "_by_<bot username>". <bot_username> is case insensitive.
                1-64 characters.
            title (:obj:`str`): Sticker set title, 1-64 characters.
            png_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **PNG** image with the sticker,
                must be up to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px.
                |fileinput|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            tgs_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **TGS** animation with the sticker. |uploadinput|
                See https://core.telegram.org/stickers#animated-sticker-requirements for technical
                requirements.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            webm_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`,\
                optional): **WEBM** video with the sticker. |uploadinput|
                See https://core.telegram.org/stickers#video-sticker-requirements for
                technical requirements.

                .. versionadded:: 13.11

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.

            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should be placed on faces.
            sticker_type (:obj:`str`, optional): Type of stickers in the set, pass
                :attr:`telegram.Sticker.REGULAR` or :attr:`telegram.Sticker.MASK`. Custom emoji
                sticker sets can't be created via the Bot API at the moment. By default, a
                regular sticker set is created.

                .. versionadded:: 20.0

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "name": name, "title": title, "emojis": emojis}

        if png_sticker is not None:
            data["png_sticker"] = self._parse_file_input(png_sticker)
        if tgs_sticker is not None:
            data["tgs_sticker"] = self._parse_file_input(tgs_sticker)
        if webm_sticker is not None:
            data["webm_sticker"] = self._parse_file_input(webm_sticker)
        if mask_position is not None:
            data["mask_position"] = mask_position
        if sticker_type is not None:
            data["sticker_type"] = sticker_type

        result = await self._post(
            "createNewStickerSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def add_sticker_to_set(
        self,
        user_id: Union[str, int],
        name: str,
        emojis: str,
        png_sticker: FileInput = None,
        mask_position: MaskPosition = None,
        tgs_sticker: FileInput = None,
        webm_sticker: FileInput = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = 20,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to add a new sticker to a set created by the bot.
        You **must** use exactly one of the fields :paramref:`png_sticker`, :paramref:`tgs_sticker`
        or :paramref:`webm_sticker`. Animated stickers can be added to animated sticker sets and
        only to them. Animated sticker sets can have up to 50 stickers. Static sticker sets can
        have up to 120 stickers.

        Warning:
            As of API 4.7 :paramref:`png_sticker` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.

            name (:obj:`str`): Sticker set name.
            png_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **PNG** image with the sticker,
                must be up to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px.
                |fileinput|

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            tgs_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **TGS** animation with the sticker. |uploadinput|
                See https://core.telegram.org/stickers#animated-sticker-requirements for technical
                requirements.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            webm_sticker (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`,\
                optional): **WEBM** video with the sticker. |uploadinput|
                See https://core.telegram.org/stickers#video-sticker-requirements for
                technical requirements.

                .. versionadded:: 13.11

                .. versionchanged:: 20.0
                    File paths as input is also accepted for bots *not* running in
                    :paramref:`~telegram.Bot.local_mode`.
            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should be placed on faces.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "name": name, "emojis": emojis}

        if png_sticker is not None:
            data["png_sticker"] = self._parse_file_input(png_sticker)
        if tgs_sticker is not None:
            data["tgs_sticker"] = self._parse_file_input(tgs_sticker)
        if webm_sticker is not None:
            data["webm_sticker"] = self._parse_file_input(webm_sticker)
        if mask_position is not None:
            data["mask_position"] = mask_position

        result = await self._post(
            "addStickerToSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def set_sticker_position_in_set(
        self,
        sticker: str,
        position: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to move a sticker in a set created by the bot to a specific position.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            position (:obj:`int`): New sticker position in the set, zero-based.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"sticker": sticker, "position": position}
        result = await self._post(
            "setStickerPositionInSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def delete_sticker_from_set(
        self,
        sticker: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to delete a sticker from a set created by the bot.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"sticker": sticker}
        result = await self._post(
            "deleteStickerFromSet",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def set_sticker_set_thumb(
        self,
        name: str,
        user_id: Union[str, int],
        thumb: FileInput = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to set the thumbnail of a sticker set. Animated thumbnails can be set
        for animated sticker sets only. Video thumbnails can be set only for video sticker sets
        only.

        Args:
            name (:obj:`str`): Sticker set name
            user_id (:obj:`int`): User identifier of created sticker set owner.
            thumb (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): A **PNG** image with the thumbnail, must
                be up to 128 kilobytes in size and have width and height exactly 100px, or a
                **TGS** animation with the thumbnail up to 32 kilobytes in size; see
                https://core.telegram.org/stickers#animated-sticker-requirements for animated
                sticker technical requirements, or a **WEBM** video with the thumbnail up to 32
                kilobytes in size; see
                https://core.telegram.org/stickers#video-sticker-requirements for video sticker
                technical requirements.
                |fileinput|
                Animated sticker set thumbnails can't be uploaded via HTTP URL.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"name": name, "user_id": user_id}
        if thumb is not None:
            data["thumb"] = self._parse_file_input(thumb)

        result = await self._post(
            "setStickerSetThumb",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def set_passport_data_errors(
        self,
        user_id: Union[str, int],
        errors: List[PassportElementError],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Informs a user that some of the Telegram Passport elements they provided contains errors.
        The user will not be able to re-submit their Passport to you until the errors are fixed
        (the contents of the field for which you returned the error must change).

        Use this if the data submitted by the user doesn't satisfy the standards your service
        requires for any reason. For example, if a birthday date seems invalid, a submitted
        document is blurry, a scan shows evidence of tampering, etc. Supply some details in the
        error message to make sure the user knows how to correct the issues.

        Args:
            user_id (:obj:`int`): User identifier
            errors (List[:class:`PassportElementError`]): An array describing the
                errors.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"user_id": user_id, "errors": errors}
        result = await self._post(
            "setPassportDataErrors",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]

    @_log
    async def send_poll(
        self,
        chat_id: Union[int, str],
        question: str,
        options: List[str],
        is_anonymous: bool = None,
        type: str = None,  # pylint: disable=redefined-builtin
        allows_multiple_answers: bool = None,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Union[List["MessageEntity"], Tuple["MessageEntity", ...]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send a native poll.

        .. seealso:: :attr:`telegram.Message.reply_poll`, :attr:`telegram.Chat.send_poll`,
            :attr:`telegram.User.send_poll`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            question (:obj:`str`): Poll question, 1-:tg-const:`telegram.Poll.MAX_QUESTION_LENGTH`
                characters.
            options (List[:obj:`str`]): List of answer options,
                2-:tg-const:`telegram.Poll.MAX_OPTION_NUMBER` strings
                1-:tg-const:`telegram.Poll.MAX_OPTION_LENGTH` characters each.
            is_anonymous (:obj:`bool`, optional): :obj:`True`, if the poll needs to be anonymous,
                defaults to :obj:`True`.
            type (:obj:`str`, optional): Poll type, :tg-const:`telegram.Poll.QUIZ` or
                :tg-const:`telegram.Poll.REGULAR`, defaults to :tg-const:`telegram.Poll.REGULAR`.
            allows_multiple_answers (:obj:`bool`, optional): :obj:`True`, if the poll allows
                multiple answers, ignored for polls in quiz mode, defaults to :obj:`False`.
            correct_option_id (:obj:`int`, optional): 0-based identifier of the correct answer
                option, required for polls in quiz mode.
            explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
                answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most
                2 line feeds after entities parsing.
            explanation_parse_mode (:obj:`str`, optional): Mode for parsing entities in the
                explanation. See the constants in :class:`telegram.constants.ParseMode` for the
                available modes.
            explanation_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :paramref:`explanation_parse_mode`.
            open_period (:obj:`int`, optional): Amount of time in seconds the poll will be active
                after creation, 5-600. Can't be used together with :paramref:`close_date`.
            close_date (:obj:`int` | :obj:`datetime.datetime`, optional): Point in time (Unix
                timestamp) when the poll will be automatically closed. Must be at least 5 and no
                more than 600 seconds in the future. Can't be used together with
                :paramref:`open_period`.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used, which is UTC unless :attr:`telegram.ext.Defaults.tzinfo` is
                used.
            is_closed (:obj:`bool`, optional): Pass :obj:`True`, if the poll needs to be
                immediately closed. This can be useful for poll preview.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "explanation_parse_mode": explanation_parse_mode,
        }

        if not is_anonymous:
            data["is_anonymous"] = is_anonymous
        if type:
            data["type"] = type
        if allows_multiple_answers:
            data["allows_multiple_answers"] = allows_multiple_answers
        if correct_option_id is not None:
            data["correct_option_id"] = correct_option_id
        if is_closed:
            data["is_closed"] = is_closed
        if explanation:
            data["explanation"] = explanation
        if explanation_entities:
            data["explanation_entities"] = explanation_entities
        if open_period:
            data["open_period"] = open_period
        if close_date:
            data["close_date"] = close_date

        return await self._send_message(  # type: ignore[return-value]
            "sendPoll",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
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
        """
        Use this method to stop a poll which was sent by the bot.

        .. seealso:: :attr:`telegram.Message.stop_poll`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of the original message with the poll.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): An object for a new
                message inline keyboard.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Poll`: On success, the stopped Poll is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id, "message_id": message_id}

        if reply_markup:
            data["reply_markup"] = reply_markup

        result = await self._post(
            "stopPoll",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return Poll.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def send_dice(
        self,
        chat_id: Union[int, str],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        emoji: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Message:
        """
        Use this method to send an animated emoji that will display a random value.

        .. seealso:: :attr:`telegram.Message.reply_dice`,  :attr:`telegram.Chat.send_dice`,
            :attr:`telegram.User.send_dice`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user
            emoji (:obj:`str`, optional): Emoji on which the dice throw animation is based.
                Currently, must be one of :class:`telegram.constants.DiceEmoji`. Dice can have
                values 1-6 for :tg-const:`telegram.constants.DiceEmoji.DICE`,
                :tg-const:`telegram.constants.DiceEmoji.DARTS` and
                :tg-const:`telegram.constants.DiceEmoji.BOWLING`, values 1-5 for
                :tg-const:`telegram.constants.DiceEmoji.BASKETBALL` and
                :tg-const:`telegram.constants.DiceEmoji.FOOTBALL`, and values 1-64
                for :tg-const:`telegram.constants.DiceEmoji.SLOT_MACHINE`. Defaults to
                :tg-const:`telegram.constants.DiceEmoji.DICE`.

                .. versionchanged:: 13.4
                   Added the :tg-const:`telegram.constants.DiceEmoji.BOWLING` emoji..
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {"chat_id": chat_id}
        if emoji:
            data["emoji"] = emoji

        return await self._send_message(  # type: ignore[return-value]
            "sendDice",
            data,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_my_default_administrator_rights(
        self,
        for_channels: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatAdministratorRights:
        """Use this method to get the current default administrator rights of the bot.

        .. seealso:: :meth:`set_my_default_administrator_rights`

        .. versionadded:: 20.0

        Args:
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to get default administrator
                rights of the bot in channels. Otherwise, default administrator rights of the bot
                for groups and supergroups will be returned.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatAdministratorRights`: On success.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if for_channels is not None:
            data["for_channels"] = for_channels

        result = await self._post(
            "getMyDefaultAdministratorRights",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return ChatAdministratorRights.de_json(result, self)  # type: ignore[return-value,arg-type]

    @_log
    async def set_my_default_administrator_rights(
        self,
        rights: ChatAdministratorRights = None,
        for_channels: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to change the default administrator rights requested by the bot when
        it's added as an administrator to groups or channels. These rights will be suggested to
        users, but they are are free to modify the list before adding the bot.

        .. seealso:: :meth:`get_my_default_administrator_rights`

        .. versionadded:: 20.0

        Args:
            rights (:obj:`telegram.ChatAdministratorRights`, optional): A
                :obj:`telegram.ChatAdministratorRights` object describing new default administrator
                rights. If not specified, the default administrator rights will be cleared.
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to change the default
                administrator rights of the bot in channels. Otherwise, the default administrator
                rights of the bot for groups and supergroups will be changed.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: Returns :obj:`True` on success.

        Raises:
            :obj:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if rights is not None:
            data["rights"] = rights

        if for_channels is not None:
            data["for_channels"] = for_channels

        result = await self._post(
            "setMyDefaultAdministratorRights",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def get_my_commands(
        self,
        scope: BotCommandScope = None,
        language_code: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[BotCommand]:
        """
        Use this method to get the current list of the bot's commands for the given scope and user
        language.

        Args:
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users. Defaults to :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

                .. versionadded:: 13.7

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.BotCommand`]: On success, the commands set for the bot. An empty
            list is returned if commands are not set.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {}

        if scope:
            data["scope"] = scope

        if language_code:
            data["language_code"] = language_code

        result = await self._post(
            "getMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return BotCommand.de_list(result, self)  # type: ignore[return-value,arg-type]

    @_log
    async def set_my_commands(
        self,
        commands: List[Union[BotCommand, Tuple[str, str]]],
        scope: BotCommandScope = None,
        language_code: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to change the list of the bot's commands. See the
        `Telegram docs <https://core.telegram.org/bots#commands>`_ for more details about bot
        commands.

        Args:
            commands (List[:class:`BotCommand` | (:obj:`str`, :obj:`str`)]): A list
                of bot commands to be set as the list of the bot's commands. At most 100 commands
                can be specified.
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.

                .. versionadded:: 13.7

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        cmds = [c if isinstance(c, BotCommand) else BotCommand(c[0], c[1]) for c in commands]
        data: JSONDict = {"commands": cmds}

        if scope:
            data["scope"] = scope

        if language_code:
            data["language_code"] = language_code

        result = await self._post(
            "setMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def delete_my_commands(
        self,
        scope: BotCommandScope = None,
        language_code: str = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete the list of the bot's commands for the given scope and user
        language. After deletion,
        `higher level commands <https://core.telegram.org/bots/api#determining-list-of-commands>`_
        will be shown to affected users.

        .. versionadded:: 13.7

        Args:
            scope (:class:`telegram.BotCommandScope`, optional): An object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if scope:
            data["scope"] = scope

        if language_code:
            data["language_code"] = language_code

        result = await self._post(
            "deleteMyCommands",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @_log
    async def log_out(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to log out from the cloud Bot API server before launching the bot locally.
        You *must* log out the bot before running it locally, otherwise there is no guarantee that
        the bot will receive updates. After a successful call, you can immediately log in on a
        local server, but will not be able to log in back to the cloud Bot API server for 10
        minutes.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

                .. versionadded:: 20.0

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return await self._post(  # type: ignore[return-value]
            "logOut",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def close(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to close the bot instance before moving it from one local server to
        another. You need to delete the webhook before calling this method to ensure that the bot
        isn't launched again after server restart. The method will return error 429 in the first
        10 minutes after the bot is launched.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return await self._post(  # type: ignore[return-value]
            "close",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
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
        """
        Use this method to copy messages of any kind. Service messages and invoice messages can't
        be copied. The method is analogous to the method :meth:`forward_message`, but the copied
        message doesn't have a link to the original message.

        .. seealso:: :attr:`telegram.Message.copy`, :attr:`telegram.Chat.send_copy`,
            :attr:`telegram.Chat.copy_message`, :attr:`telegram.User.send_copy`,
            :attr:`telegram.User.copy_message`

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format ``@channelusername``).
            message_id (:obj:`int`): Message identifier in the chat specified in from_chat_id.
            caption (:obj:`str`, optional): New caption for media,
                0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
                entities parsing. If not specified, the original caption is kept.
            parse_mode (:obj:`str`, optional): Mode for parsing entities in the new caption. See
                the constants in :class:`telegram.constants.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in the new caption, which can be specified instead
                of parse_mode.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`InlineKeyboardMarkup` | :class:`ReplyKeyboardMarkup` | \
                :class:`ReplyKeyboardRemove` | :class:`ForceReply`, optional):
                Additional interface options. An object for an inline keyboard, custom reply
                keyboard, instructions to remove reply keyboard or to force a reply from the user.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.MessageId`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "allow_sending_without_reply": allow_sending_without_reply,
            "protect_content": protect_content,
        }
        if caption is not None:
            data["caption"] = caption
        if caption_entities:
            data["caption_entities"] = caption_entities
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            data["reply_markup"] = reply_markup

        result = await self._post(
            "copyMessage",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return MessageId.de_json(result, self)  # type: ignore[return-value, arg-type]

    @_log
    async def set_chat_menu_button(
        self,
        chat_id: int = None,
        menu_button: MenuButton = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to change the bot's menu button in a private chat, or the default menu
        button.

        .. seealso:: :meth:`get_chat_menu_button`, :meth:`telegram.Chat.set_menu_button`,
            :meth:`telegram.Chat.get_menu_button`, meth:`telegram.User.set_menu_button`,
            :meth:`telegram.User.get_menu_button`

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be changed
            menu_button (:class:`telegram.MenuButton`, optional): An object for the new bot's menu
                button. Defaults to :class:`telegram.MenuButtonDefault`.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        data: JSONDict = {}
        if chat_id is not None:
            data["chat_id"] = chat_id
        if menu_button is not None:
            data["menu_button"] = menu_button

        return await self._post(  # type: ignore[return-value]
            "setChatMenuButton",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    @_log
    async def get_chat_menu_button(
        self,
        chat_id: int = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> MenuButton:
        """Use this method to get the current value of the bot's menu button in a private chat, or
        the default menu button.

        .. seealso:: :meth:`set_chat_menu_button`, :meth:`telegram.Chat.get_menu_button`,
            :meth:`telegram.Chat.set_menu_button`, :meth:`telegram.User.get_menu_button`,
            :meth:`telegram.User.set_menu_button`

        .. versionadded:: 20.0

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be returned.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional):  Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.MenuButton`: On success, the current menu button is returned.

        """
        data = {}
        if chat_id is not None:
            data["chat_id"] = chat_id

        result = await self._post(
            "getChatMenuButton",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return MenuButton.de_json(result, bot=self)  # type: ignore[return-value, arg-type]

    @_log
    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List["LabeledPrice"],
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
        provider_data: Union[str, object] = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        is_flexible: bool = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> str:
        """Use this method to create a link for an invoice.

        .. versionadded:: 20.0

        Args:
            title (:obj:`str`): Product name. :tg-const:`telegram.Invoice.MIN_TITLE_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_TITLE_LENGTH` characters.
            description (:obj:`str`): Product description.
                :tg-const:`telegram.Invoice.MIN_DESCRIPTION_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_DESCRIPTION_LENGTH` characters.
            payload (:obj:`str`): Bot-defined invoice payload.
                :tg-const:`telegram.Invoice.MIN_PAYLOAD_LENGTH`-
                :tg-const:`telegram.Invoice.MAX_PAYLOAD_LENGTH` bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via
                `@BotFather <https://t.me/BotFather>`_.
            currency (:obj:`str`): Three-letter ISO 4217 currency code, see `more on currencies
                <https://core.telegram.org/bots/payments#supported-currencies>`_.
            prices (List[:class:`telegram.LabeledPrice`)]: Price breakdown, a list
                of components (e.g. product price, tax, discount, delivery cost, delivery tax,
                bonus, etc.).
            max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the
                *smallest* units of the currency (integer, **not** float/double). For example, for
                a maximum tip of US$ 1.45 pass ``max_tip_amount = 145``. See the exp parameter in
                `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
                shows the number of digits past the decimal point for each currency (2 for the
                majority of currencies). Defaults to ``0``.
            suggested_tip_amounts (List[:obj:`int`], optional): An array of
                suggested amounts of tips in the *smallest* units of the currency (integer, **not**
                float/double). At most 4 suggested tip amounts can be specified. The suggested tip
                amounts must be positive, passed in a strictly increased order and must not exceed
                :paramref:`max_tip_amount`.
            provider_data (:obj:`str` | :obj:`object`, optional): Data about the
                invoice, which will be shared with the payment provider. A detailed description of
                required fields should be provided by the payment provider. When an object is
                passed, it will be encoded as JSON.
            photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a
                photo of the goods or a marketing image for a service.
            photo_size (:obj:`int`, optional): Photo size in bytes.
            photo_width (:obj:`int`, optional): Photo width.
            photo_height (:obj:`int`, optional): Photo height.
            need_name (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's full
                name to complete the order.
            need_phone_number (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
                phone number to complete the order.
            need_email (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's email
                address to complete the order.
            need_shipping_address (:obj:`bool`, optional): Pass :obj:`True`, if you require the
                user's shipping address to complete the order.
            send_phone_number_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's
                phone number should be sent to provider.
            send_email_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's email
                address should be sent to provider.
            is_flexible (:obj:`bool`, optional): Pass :obj:`True`, if the final price depends on
                the shipping method.

        Keyword Args:
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to
                :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`str`: On success, the created invoice link is returned.

        """
        data: JSONDict = {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": prices,
        }
        if max_tip_amount is not None:
            data["max_tip_amount"] = max_tip_amount
        if suggested_tip_amounts is not None:
            data["suggested_tip_amounts"] = suggested_tip_amounts
        if provider_data is not None:
            data["provider_data"] = provider_data
        if photo_url is not None:
            data["photo_url"] = photo_url
        if photo_size is not None:
            data["photo_size"] = photo_size
        if photo_width is not None:
            data["photo_width"] = photo_width
        if photo_height is not None:
            data["photo_height"] = photo_height
        if need_name is not None:
            data["need_name"] = need_name
        if need_phone_number is not None:
            data["need_phone_number"] = need_phone_number
        if need_email is not None:
            data["need_email"] = need_email
        if need_shipping_address is not None:
            data["need_shipping_address"] = need_shipping_address
        if is_flexible is not None:
            data["is_flexible"] = is_flexible
        if send_phone_number_to_provider is not None:
            data["send_phone_number_to_provider"] = send_phone_number_to_provider
        if send_email_to_provider is not None:
            data["send_email_to_provider"] = send_email_to_provider

        return await self._post(  # type: ignore[return-value]
            "createInvoiceLink",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    def to_dict(self, recursive: bool = True) -> JSONDict:  # skipcq: PYL-W0613
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data: JSONDict = {"id": self.id, "username": self.username, "first_name": self.first_name}

        if self.last_name:
            data["last_name"] = self.last_name

        return data

    def __eq__(self, other: object) -> bool:
        return self.bot == other

    def __hash__(self) -> int:
        return hash(self.bot)

    # camelCase aliases
    getMe = get_me
    """Alias for :meth:`get_me`"""
    sendMessage = send_message
    """Alias for :meth:`send_message`"""
    deleteMessage = delete_message
    """Alias for :meth:`delete_message`"""
    forwardMessage = forward_message
    """Alias for :meth:`forward_message`"""
    sendPhoto = send_photo
    """Alias for :meth:`send_photo`"""
    sendAudio = send_audio
    """Alias for :meth:`send_audio`"""
    sendDocument = send_document
    """Alias for :meth:`send_document`"""
    sendSticker = send_sticker
    """Alias for :meth:`send_sticker`"""
    sendVideo = send_video
    """Alias for :meth:`send_video`"""
    sendAnimation = send_animation
    """Alias for :meth:`send_animation`"""
    sendVoice = send_voice
    """Alias for :meth:`send_voice`"""
    sendVideoNote = send_video_note
    """Alias for :meth:`send_video_note`"""
    sendMediaGroup = send_media_group
    """Alias for :meth:`send_media_group`"""
    sendLocation = send_location
    """Alias for :meth:`send_location`"""
    editMessageLiveLocation = edit_message_live_location
    """Alias for :meth:`edit_message_live_location`"""
    stopMessageLiveLocation = stop_message_live_location
    """Alias for :meth:`stop_message_live_location`"""
    sendVenue = send_venue
    """Alias for :meth:`send_venue`"""
    sendContact = send_contact
    """Alias for :meth:`send_contact`"""
    sendGame = send_game
    """Alias for :meth:`send_game`"""
    sendChatAction = send_chat_action
    """Alias for :meth:`send_chat_action`"""
    answerInlineQuery = answer_inline_query
    """Alias for :meth:`answer_inline_query`"""
    getUserProfilePhotos = get_user_profile_photos
    """Alias for :meth:`get_user_profile_photos`"""
    getFile = get_file
    """Alias for :meth:`get_file`"""
    banChatMember = ban_chat_member
    """Alias for :meth:`ban_chat_member`"""
    banChatSenderChat = ban_chat_sender_chat
    """Alias for :meth:`ban_chat_sender_chat`"""
    unbanChatMember = unban_chat_member
    """Alias for :meth:`unban_chat_member`"""
    unbanChatSenderChat = unban_chat_sender_chat
    """Alias for :meth:`unban_chat_sender_chat`"""
    answerCallbackQuery = answer_callback_query
    """Alias for :meth:`answer_callback_query`"""
    editMessageText = edit_message_text
    """Alias for :meth:`edit_message_text`"""
    editMessageCaption = edit_message_caption
    """Alias for :meth:`edit_message_caption`"""
    editMessageMedia = edit_message_media
    """Alias for :meth:`edit_message_media`"""
    editMessageReplyMarkup = edit_message_reply_markup
    """Alias for :meth:`edit_message_reply_markup`"""
    getUpdates = get_updates
    """Alias for :meth:`get_updates`"""
    setWebhook = set_webhook
    """Alias for :meth:`set_webhook`"""
    deleteWebhook = delete_webhook
    """Alias for :meth:`delete_webhook`"""
    leaveChat = leave_chat
    """Alias for :meth:`leave_chat`"""
    getChat = get_chat
    """Alias for :meth:`get_chat`"""
    getChatAdministrators = get_chat_administrators
    """Alias for :meth:`get_chat_administrators`"""
    getChatMember = get_chat_member
    """Alias for :meth:`get_chat_member`"""
    setChatStickerSet = set_chat_sticker_set
    """Alias for :meth:`set_chat_sticker_set`"""
    deleteChatStickerSet = delete_chat_sticker_set
    """Alias for :meth:`delete_chat_sticker_set`"""
    getChatMemberCount = get_chat_member_count
    """Alias for :meth:`get_chat_member_count`"""
    getWebhookInfo = get_webhook_info
    """Alias for :meth:`get_webhook_info`"""
    setGameScore = set_game_score
    """Alias for :meth:`set_game_score`"""
    getGameHighScores = get_game_high_scores
    """Alias for :meth:`get_game_high_scores`"""
    sendInvoice = send_invoice
    """Alias for :meth:`send_invoice`"""
    answerShippingQuery = answer_shipping_query
    """Alias for :meth:`answer_shipping_query`"""
    answerPreCheckoutQuery = answer_pre_checkout_query
    """Alias for :meth:`answer_pre_checkout_query`"""
    answerWebAppQuery = answer_web_app_query
    """Alias for :meth:`answer_web_app_query`"""
    restrictChatMember = restrict_chat_member
    """Alias for :meth:`restrict_chat_member`"""
    promoteChatMember = promote_chat_member
    """Alias for :meth:`promote_chat_member`"""
    setChatPermissions = set_chat_permissions
    """Alias for :meth:`set_chat_permissions`"""
    setChatAdministratorCustomTitle = set_chat_administrator_custom_title
    """Alias for :meth:`set_chat_administrator_custom_title`"""
    exportChatInviteLink = export_chat_invite_link
    """Alias for :meth:`export_chat_invite_link`"""
    createChatInviteLink = create_chat_invite_link
    """Alias for :meth:`create_chat_invite_link`"""
    editChatInviteLink = edit_chat_invite_link
    """Alias for :meth:`edit_chat_invite_link`"""
    revokeChatInviteLink = revoke_chat_invite_link
    """Alias for :meth:`revoke_chat_invite_link`"""
    approveChatJoinRequest = approve_chat_join_request
    """Alias for :meth:`approve_chat_join_request`"""
    declineChatJoinRequest = decline_chat_join_request
    """Alias for :meth:`decline_chat_join_request`"""
    setChatPhoto = set_chat_photo
    """Alias for :meth:`set_chat_photo`"""
    deleteChatPhoto = delete_chat_photo
    """Alias for :meth:`delete_chat_photo`"""
    setChatTitle = set_chat_title
    """Alias for :meth:`set_chat_title`"""
    setChatDescription = set_chat_description
    """Alias for :meth:`set_chat_description`"""
    pinChatMessage = pin_chat_message
    """Alias for :meth:`pin_chat_message`"""
    unpinChatMessage = unpin_chat_message
    """Alias for :meth:`unpin_chat_message`"""
    unpinAllChatMessages = unpin_all_chat_messages
    """Alias for :meth:`unpin_all_chat_messages`"""
    getCustomEmojiStickers = get_custom_emoji_stickers
    """Alias for :meth:`get_custom_emoji_stickers`"""
    getStickerSet = get_sticker_set
    """Alias for :meth:`get_sticker_set`"""
    uploadStickerFile = upload_sticker_file
    """Alias for :meth:`upload_sticker_file`"""
    createNewStickerSet = create_new_sticker_set
    """Alias for :meth:`create_new_sticker_set`"""
    addStickerToSet = add_sticker_to_set
    """Alias for :meth:`add_sticker_to_set`"""
    setStickerPositionInSet = set_sticker_position_in_set
    """Alias for :meth:`set_sticker_position_in_set`"""
    deleteStickerFromSet = delete_sticker_from_set
    """Alias for :meth:`delete_sticker_from_set`"""
    setStickerSetThumb = set_sticker_set_thumb
    """Alias for :meth:`set_sticker_set_thumb`"""
    setPassportDataErrors = set_passport_data_errors
    """Alias for :meth:`set_passport_data_errors`"""
    sendPoll = send_poll
    """Alias for :meth:`send_poll`"""
    stopPoll = stop_poll
    """Alias for :meth:`stop_poll`"""
    sendDice = send_dice
    """Alias for :meth:`send_dice`"""
    getMyCommands = get_my_commands
    """Alias for :meth:`get_my_commands`"""
    setMyCommands = set_my_commands
    """Alias for :meth:`set_my_commands`"""
    deleteMyCommands = delete_my_commands
    """Alias for :meth:`delete_my_commands`"""
    logOut = log_out
    """Alias for :meth:`log_out`"""
    copyMessage = copy_message
    """Alias for :meth:`copy_message`"""
    getChatMenuButton = get_chat_menu_button
    """Alias for :meth:`get_chat_menu_button`"""
    setChatMenuButton = set_chat_menu_button
    """Alias for :meth:`set_chat_menu_button`"""
    getMyDefaultAdministratorRights = get_my_default_administrator_rights
    """Alias for :meth:`get_my_default_administrator_rights`"""
    setMyDefaultAdministratorRights = set_my_default_administrator_rights
    """Alias for :meth:`set_my_default_administrator_rights`"""
    createInvoiceLink = create_invoice_link
    """Alias for :meth:`create_invoice_link`"""
