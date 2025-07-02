#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,E1101,R0913,R0904
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

import functools
import logging
import warnings
from datetime import datetime

from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    no_type_check,
    Dict,
    cast,
    Sequence,
)

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]  # noqa: F723

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    CRYPTO_INSTALLED = True
except ImportError:
    default_backend = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    CRYPTO_INSTALLED = False

from telegram import (
    Animation,
    Audio,
    BotCommand,
    BotCommandScope,
    Chat,
    ChatMember,
    ChatPermissions,
    ChatPhoto,
    Contact,
    Document,
    File,
    GameHighScore,
    Location,
    MaskPosition,
    Message,
    MessageId,
    PassportElementError,
    PhotoSize,
    Poll,
    ReplyMarkup,
    ShippingOption,
    Sticker,
    StickerSet,
    TelegramObject,
    Update,
    User,
    UserProfilePhotos,
    Venue,
    Video,
    VideoNote,
    Voice,
    WebhookInfo,
    InlineKeyboardMarkup,
    ChatInviteLink,
    SentWebAppMessage,
    ChatAdministratorRights,
    MenuButton,
)
from telegram.constants import MAX_INLINE_QUERY_RESULTS
from telegram.error import InvalidToken, TelegramError
from telegram.forumtopic import ForumTopic
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.helpers import (
    DEFAULT_NONE,
    DefaultValue,
    to_timestamp,
    is_local_file,
    parse_file_input,
    DEFAULT_20,
)
from telegram.utils.request import Request
from telegram.utils.types import FileInput, JSONDict, ODVInput, DVInput

if TYPE_CHECKING:
    from telegram.ext import Defaults
    from telegram import (
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        InputMedia,
        InlineQueryResult,
        LabeledPrice,
        MessageEntity,
    )

RT = TypeVar('RT')


def log(  # skipcq: PY-D0003
    func: Callable[..., RT], *args: object, **kwargs: object  # pylint: disable=W0613
) -> Callable[..., RT]:
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def decorator(*args: object, **kwargs: object) -> RT:  # pylint: disable=W0613
        logger.debug('Entering: %s', func.__name__)
        result = func(*args, **kwargs)
        logger.debug(result)
        logger.debug('Exiting: %s', func.__name__)
        return result

    return decorator


class Bot(TelegramObject):
    """This object represents a Telegram Bot.

    .. versionadded:: 13.2
        Objects of this class are comparable in terms of equality. Two objects of this class are
        considered equal, if their :attr:`bot` is equal.

    Note:
        Most bot methods have the argument ``api_kwargs`` which allows to pass arbitrary keywords
        to the Telegram API. This can be used to access new features of the API before they were
        incorporated into PTB. However, this is not guaranteed to work, i.e. it will fail for
        passing files.

    Args:
        token (:obj:`str`): Bot's unique authentication.
        base_url (:obj:`str`, optional): Telegram Bot API service URL.
        base_file_url (:obj:`str`, optional): Telegram Bot API file URL.
        request (:obj:`telegram.utils.request.Request`, optional): Pre initialized
            :obj:`telegram.utils.request.Request`.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.
        defaults (:class:`telegram.ext.Defaults`, optional): An object containing default values to
            be used if not set explicitly in the bot methods.

            .. deprecated:: 13.6
               Passing :class:`telegram.ext.Defaults` to :class:`telegram.Bot` is deprecated. If
               you want to use :class:`telegram.ext.Defaults`, please use
               :class:`telegram.ext.ExtBot` instead.

    """

    __slots__ = (
        'token',
        'base_url',
        'base_file_url',
        'private_key',
        'defaults',
        '_bot',
        '_commands',
        '_request',
        'logger',
    )

    def __init__(
        self,
        token: str,
        base_url: str = None,
        base_file_url: str = None,
        request: 'Request' = None,
        private_key: bytes = None,
        private_key_password: bytes = None,
        defaults: 'Defaults' = None,
    ):
        self.token = self._validate_token(token)

        # Gather default
        self.defaults = defaults

        if self.defaults:
            warnings.warn(
                'Passing Defaults to telegram.Bot is deprecated. Use telegram.ext.ExtBot instead.',
                TelegramDeprecationWarning,
                stacklevel=3,
            )

        if base_url is None:
            base_url = 'https://api.telegram.org/bot'

        if base_file_url is None:
            base_file_url = 'https://api.telegram.org/file/bot'

        self.base_url = str(base_url) + str(self.token)
        self.base_file_url = str(base_file_url) + str(self.token)
        self._bot: Optional[User] = None
        self._commands: Optional[List[BotCommand]] = None
        self._request = request or Request()
        self.private_key = None
        self.logger = logging.getLogger(__name__)

        if private_key:
            if not CRYPTO_INSTALLED:
                raise RuntimeError(
                    'To use Telegram Passports, PTB must be installed via `pip install '
                    'python-telegram-bot[passport]`.'
                )
            self.private_key = serialization.load_pem_private_key(
                private_key, password=private_key_password, backend=default_backend()
            )

    # The ext_bot argument is a little hack to get warnings handled correctly.
    # It's not very clean, but the warnings will be dropped at some point anyway.
    def __setattr__(self, key: str, value: object, ext_bot: bool = False) -> None:
        if issubclass(self.__class__, Bot) and self.__class__ is not Bot and not ext_bot:
            object.__setattr__(self, key, value)
            return
        super().__setattr__(key, value)

    def _insert_defaults(
        self, data: Dict[str, object], timeout: ODVInput[float]
    ) -> Optional[float]:
        """
        Inserts the defaults values for optional kwargs for which tg.ext.Defaults provides
        convenience functionality, i.e. the kwargs with a tg.utils.helpers.DefaultValue default

        data is edited in-place. As timeout is not passed via the kwargs, it needs to be passed
        separately and gets returned.

        This can only work, if all kwargs that may have defaults are passed in data!
        """
        effective_timeout = DefaultValue.get_value(timeout)

        # If we have no Defaults, we just need to replace DefaultValue instances
        # with the actual value
        if not self.defaults:
            data.update((key, DefaultValue.get_value(value)) for key, value in data.items())
            return effective_timeout

        # if we have Defaults, we replace all DefaultValue instances with the relevant
        # Defaults value. If there is none, we fall back to the default value of the bot method
        for key, val in data.items():
            if isinstance(val, DefaultValue):
                data[key] = self.defaults.api_defaults.get(key, val.value)

        if isinstance(timeout, DefaultValue):
            # If we get here, we use Defaults.timeout, unless that's not set, which is the
            # case if isinstance(self.defaults.timeout, DefaultValue)
            return (
                self.defaults.timeout
                if not isinstance(self.defaults.timeout, DefaultValue)
                else effective_timeout
            )
        return effective_timeout

    def _post(
        self,
        endpoint: str,
        data: JSONDict = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[bool, JSONDict, None]:
        if data is None:
            data = {}

        if api_kwargs:
            if data:
                data.update(api_kwargs)
            else:
                data = api_kwargs

        # Insert is in-place, so no return value for data
        if endpoint != 'getUpdates':
            effective_timeout = self._insert_defaults(data, timeout)
        else:
            effective_timeout = cast(float, timeout)
        # Drop any None values because Telegram doesn't handle them well
        data = {key: value for key, value in data.items() if value is not None}

        return self.request.post(
            f'{self.base_url}/{endpoint}', data=data, timeout=effective_timeout
        )

    def _message(
        self,
        endpoint: str,
        data: JSONDict,
        reply_to_message_id: int = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Union[bool, Message]:
        if reply_to_message_id is not None:
            data['reply_to_message_id'] = reply_to_message_id

        if protect_content:
            data['protect_content'] = protect_content

        if message_thread_id is not None:
            data["message_thread_id"] = message_thread_id

        # We don't check if (DEFAULT_)None here, so that _put is able to insert the defaults
        # correctly, if necessary
        data['disable_notification'] = disable_notification
        data['allow_sending_without_reply'] = allow_sending_without_reply

        if reply_markup is not None:
            if isinstance(reply_markup, ReplyMarkup):
                # We need to_json() instead of to_dict() here, because reply_markups may be
                # attached to media messages, which aren't json dumped by utils.request
                data['reply_markup'] = reply_markup.to_json()
            else:
                data['reply_markup'] = reply_markup

        if data.get('media') and (data['media'].parse_mode == DEFAULT_NONE):
            if self.defaults:
                data['media'].parse_mode = DefaultValue.get_value(self.defaults.parse_mode)
            else:
                data['media'].parse_mode = None

        result = self._post(endpoint, data, timeout=timeout, api_kwargs=api_kwargs)

        if result is True:
            return result

        return Message.de_json(result, self)  # type: ignore[return-value, arg-type]

    @property
    def request(self) -> Request:  # skip-cq: PY-D0003
        return self._request

    @staticmethod
    def _validate_token(token: str) -> str:
        """A very basic validation on token."""
        if any(x.isspace() for x in token):
            raise InvalidToken()

        left, sep, _right = token.partition(':')
        if (not sep) or (not left.isdigit()) or (len(left) < 3):
            raise InvalidToken()

        return token

    @property
    def bot(self) -> User:
        """:class:`telegram.User`: User instance for the bot as returned by :meth:`get_me`."""
        if self._bot is None:
            self._bot = self.get_me()
        return self._bot

    @property
    def id(self) -> int:  # pylint: disable=C0103
        """:obj:`int`: Unique identifier for this bot."""
        return self.bot.id

    @property
    def first_name(self) -> str:
        """:obj:`str`: Bot's first name."""
        return self.bot.first_name

    @property
    def last_name(self) -> str:
        """:obj:`str`: Optional. Bot's last name."""
        return self.bot.last_name  # type: ignore

    @property
    def username(self) -> str:
        """:obj:`str`: Bot's username."""
        return self.bot.username  # type: ignore

    @property
    def link(self) -> str:
        """:obj:`str`: Convenience property. Returns the t.me link of the bot."""
        return f"https://t.me/{self.username}"

    @property
    def can_join_groups(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_join_groups` attribute."""
        return self.bot.can_join_groups  # type: ignore

    @property
    def can_read_all_group_messages(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.can_read_all_group_messages` attribute."""
        return self.bot.can_read_all_group_messages  # type: ignore

    @property
    def supports_inline_queries(self) -> bool:
        """:obj:`bool`: Bot's :attr:`telegram.User.supports_inline_queries` attribute."""
        return self.bot.supports_inline_queries  # type: ignore

    @property
    def commands(self) -> List[BotCommand]:
        """
        List[:class:`BotCommand`]: Bot's commands as available in the default scope.

        .. deprecated:: 13.7
            This property has been deprecated since there can be different commands available for
            different scopes.
        """
        warnings.warn(
            "Bot.commands has been deprecated since there can be different command "
            "lists for different scopes.",
            TelegramDeprecationWarning,
            stacklevel=2,
        )

        if self._commands is None:
            self._commands = self.get_my_commands()
        return self._commands

    @property
    def name(self) -> str:
        """:obj:`str`: Bot's @username."""
        return f'@{self.username}'

    @log
    def get_me(self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None) -> User:
        """A simple method for testing your bot's auth token. Requires no parameters.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance representing that bot if the
            credentials are valid, :obj:`None` otherwise.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        result = self._post('getMe', timeout=timeout, api_kwargs=api_kwargs)

        self._bot = User.de_json(result, self)  # type: ignore[return-value, arg-type]

        return self._bot  # type: ignore[return-value]

    @log
    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send text messages.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            text (:obj:`str`): Text of the message to be sent. Max 4096 characters after entities
                parsing. Also found as :attr:`telegram.constants.MAX_MESSAGE_LENGTH`.
            parse_mode (:obj:`str`): Send Markdown or HTML, if you want Telegram apps to show bold,
                italic, fixed-width text or inline URLs in your bot's message. See the constants in
                :class:`telegram.ParseMode` for the available modes.
            entities (List[:class:`telegram.MessageEntity`], optional): List of special entities
                that appear in message text, which can be specified instead of :attr:`parse_mode`.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of sent messages from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options.
                A JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
        }

        if entities:
            data['entities'] = [me.to_dict() for me in entities]

        return self._message(  # type: ignore[return-value]
            'sendMessage',
            data,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            timeout=timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def delete_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete a message, including service messages, with the following
        limitations:

            - A message can only be deleted if it was sent less than 48 hours ago.
            - Service messages about a supergroup, channel, or forum topic creation can't be
              deleted.
            - A dice message in a private chat can only be deleted if it was sent more than 24
              hours ago.
            - Bots can delete outgoing messages in private chats, groups, and supergroups.
            - Bots can delete incoming messages in private chats.
            - Bots granted :attr:`telegram.ChatMember.can_post_messages` permissions can delete
              outgoing messages in channels.
            - If the bot is an administrator of a group, it can delete any message there.
            - If the bot has :attr:`telegram.ChatMember.can_delete_messages` permission in a
              supergroup or a channel, it can delete any message there.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of the message to delete.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'message_id': message_id}

        result = self._post('deleteMessage', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to forward messages of any kind. Service messages can't be forwarded.

        Note:
            Since the release of Bot API 5.5 it can be impossible to forward messages from
            some chats. Use the attributes :attr:`telegram.Message.has_protected_content` and
            :attr:`telegram.Chat.has_protected_content` to check this.

            As a workaround, it is still possible to use :meth:`copy_message`. However, this
            behaviour is undocumented and might be changed by Telegram.

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
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {}

        if chat_id:
            data['chat_id'] = chat_id
        if from_chat_id:
            data['from_chat_id'] = from_chat_id
        if message_id:
            data['message_id'] = message_id
        return self._message(  # type: ignore[return-value]
            'forwardMessage',
            data,
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[FileInput, 'PhotoSize'],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send photos.

        Note:
            The photo argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            photo (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.PhotoSize`): Photo to send.
                Pass a file_id as String to send a photo that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a photo from the
                Internet, or upload a new photo using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.PhotoSize` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the photo, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            caption (:obj:`str`, optional): Photo caption (may also be used when resending photos
                by file_id), 0-1024 characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'photo': parse_file_input(photo, PhotoSize, filename=filename),
            'parse_mode': parse_mode,
        }

        if caption:
            data['caption'] = caption

        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]

        return self._message(  # type: ignore[return-value]
            'sendPhoto',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_audio(
        self,
        chat_id: Union[int, str],
        audio: Union[FileInput, 'Audio'],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display them in the
        music player. Your audio must be in the .mp3 or .m4a format.

        Bots can currently send audio files of up to 50 MB in size, this limit may be changed in
        the future.

        For sending voice messages, use the :meth:`send_voice` method instead.

        Note:
            The audio argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            audio (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Audio`): Audio file to send.
                Pass a file_id as String to send an audio file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an audio file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Audio` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the audio, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            caption (:obj:`str`, optional): Audio caption, 0-1024 characters after entities
                parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            duration (:obj:`int`, optional): Duration of sent audio in seconds.
            performer (:obj:`str`, optional): Performer.
            title (:obj:`str`, optional): Track name.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`, optional): Thumbnail
                of the file sent; can be ignored if
                thumbnail generation for the file is supported server-side. The thumbnail should be
                in JPEG format and less than 200 kB in size. A thumbnail's width and height should
                not exceed 320. Ignored if the file is not uploaded using multipart/form-data.
                Thumbnails can't be reused and can be only uploaded as a new file.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'audio': parse_file_input(audio, Audio, filename=filename),
            'parse_mode': parse_mode,
        }

        if duration:
            data['duration'] = duration
        if performer:
            data['performer'] = performer
        if title:
            data['title'] = title
        if caption:
            data['caption'] = caption

        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]
        if thumb:
            data['thumb'] = parse_file_input(thumb, attach=True)

        return self._message(  # type: ignore[return-value]
            'sendAudio',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[FileInput, 'Document'],
        filename: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send general files.

        Bots can currently send files of any type of up to 50 MB in size, this limit may be
        changed in the future.

        Note:
            The document argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            document (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Document`): File to send.
                Pass a file_id as String to send a file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a file from the
                Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Document` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the document, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.
            caption (:obj:`str`, optional): Document caption (may also be used when resending
                documents by file_id), 0-1024 characters after entities parsing.
            disable_content_type_detection (:obj:`bool`, optional): Disables automatic server-side
                content type detection for files uploaded using multipart/form-data.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`, optional): Thumbnail
                of the file sent; can be ignored if
                thumbnail generation for the file is supported server-side. The thumbnail should be
                in JPEG format and less than 200 kB in size. A thumbnail's width and height should
                not exceed 320. Ignored if the file is not uploaded using multipart/form-data.
                Thumbnails can't be reused and can be only uploaded as a new file.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'document': parse_file_input(document, Document, filename=filename),
            'parse_mode': parse_mode,
        }

        if caption:
            data['caption'] = caption

        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]
        if disable_content_type_detection is not None:
            data['disable_content_type_detection'] = disable_content_type_detection
        if thumb:
            data['thumb'] = parse_file_input(thumb, attach=True)

        return self._message(  # type: ignore[return-value]
            'sendDocument',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_sticker(
        self,
        chat_id: Union[int, str],
        sticker: Union[FileInput, 'Sticker'],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send static ``.WEBP``, animated ``.TGS``, or video ``.WEBM`` stickers.

        Note:
            The sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Sticker`): Sticker to send.
                Pass a file_id as String to send a file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a .webp file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Sticker` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'sticker': parse_file_input(sticker, Sticker)}

        return self._message(  # type: ignore[return-value]
            'sendSticker',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[FileInput, 'Video'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send video files, Telegram clients support mp4 videos
        (other formats may be sent as Document).

        Bots can currently send video files of up to 50 MB in size, this limit may be changed in
        the future.

        Note:
            * The video argument can be either a file_id, an URL or a file from disk
              ``open(filename, 'rb')``
            * ``thumb`` will be ignored for small video files, for which Telegram can easily
              generate thumb nails. However, this behaviour is undocumented and might be changed
              by Telegram.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            video (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Video`): Video file to send.
                Pass a file_id as String to send an video file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an video file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Video` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the video, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            width (:obj:`int`, optional): Video width.
            height (:obj:`int`, optional): Video height.
            caption (:obj:`str`, optional): Video caption (may also be used when resending videos
                by file_id), 0-1024 characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            supports_streaming (:obj:`bool`, optional): Pass :obj:`True`, if the uploaded video is
                suitable for streaming.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`, optional): Thumbnail
                of the file sent; can be ignored if
                thumbnail generation for the file is supported server-side. The thumbnail should be
                in JPEG format and less than 200 kB in size. A thumbnail's width and height should
                not exceed 320. Ignored if the file is not uploaded using multipart/form-data.
                Thumbnails can't be reused and can be only uploaded as a new file.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'video': parse_file_input(video, Video, filename=filename),
            'parse_mode': parse_mode,
        }

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption
        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]
        if supports_streaming:
            data['supports_streaming'] = supports_streaming
        if width:
            data['width'] = width
        if height:
            data['height'] = height
        if thumb:
            data['thumb'] = parse_file_input(thumb, attach=True)

        return self._message(  # type: ignore[return-value]
            'sendVideo',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_video_note(
        self,
        chat_id: Union[int, str],
        video_note: Union[FileInput, 'VideoNote'],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        As of v.4.0, Telegram clients support rounded square mp4 videos of up to 1 minute long.
        Use this method to send video messages.

        Note:
            * The video_note argument can be either a file_id or a file from disk
              ``open(filename, 'rb')``
            * ``thumb`` will be ignored for small video files, for which Telegram can easily
              generate thumb nails. However, this behaviour is undocumented and might be changed
              by Telegram.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            video_note (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.VideoNote`): Video note
                to send. Pass a file_id as String to send a video note that exists on the Telegram
                servers (recommended) or upload a new video using multipart/form-data. Or you can
                pass an existing :class:`telegram.VideoNote` object to send. Sending video notes by
                a URL is currently unsupported.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the video note, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            length (:obj:`int`, optional): Video width and height, i.e. diameter of the video
                message.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`, optional): Thumbnail
                of the file sent; can be ignored if
                thumbnail generation for the file is supported server-side. The thumbnail should be
                in JPEG format and less than 200 kB in size. A thumbnail's width and height should
                not exceed 320. Ignored if the file is not uploaded using multipart/form-data.
                Thumbnails can't be reused and can be only uploaded as a new file.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'video_note': parse_file_input(video_note, VideoNote, filename=filename),
        }

        if duration is not None:
            data['duration'] = duration
        if length is not None:
            data['length'] = length
        if thumb:
            data['thumb'] = parse_file_input(thumb, attach=True)

        return self._message(  # type: ignore[return-value]
            'sendVideoNote',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_animation(
        self,
        chat_id: Union[int, str],
        animation: Union[FileInput, 'Animation'],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound).
        Bots can currently send animation files of up to 50 MB in size, this limit may be changed
        in the future.

        Note:
            ``thumb`` will be ignored for small files, for which Telegram can easily
            generate thumbnails. However, this behaviour is undocumented and might be changed
            by Telegram.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            animation (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Animation`): Animation to
                send. Pass a file_id as String to send an animation that exists on the Telegram
                servers (recommended), pass an HTTP URL as a String for Telegram to get an
                animation from the Internet, or upload a new animation using multipart/form-data.
                Lastly you can pass an existing :class:`telegram.Animation` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            duration (:obj:`int`, optional): Duration of sent animation in seconds.
            width (:obj:`int`, optional): Animation width.
            height (:obj:`int`, optional): Animation height.
            thumb (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`, optional): Thumbnail
                of the file sent; can be ignored if
                thumbnail generation for the file is supported server-side. The thumbnail should be
                in JPEG format and less than 200 kB in size. A thumbnail's width and height should
                not exceed 320. Ignored if the file is not uploaded using multipart/form-data.
                Thumbnails can't be reused and can be only uploaded as a new file.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            caption (:obj:`str`, optional): Animation caption (may also be used when resending
                animations by file_id), 0-1024 characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'animation': parse_file_input(animation, Animation, filename=filename),
            'parse_mode': parse_mode,
        }

        if duration:
            data['duration'] = duration
        if width:
            data['width'] = width
        if height:
            data['height'] = height
        if thumb:
            data['thumb'] = parse_file_input(thumb, attach=True)
        if caption:
            data['caption'] = caption
        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]

        return self._message(  # type: ignore[return-value]
            'sendAnimation',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_voice(
        self,
        chat_id: Union[int, str],
        voice: Union[FileInput, 'Voice'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send audio files, if you want Telegram clients to display the file
        as a playable voice message. For this to work, your audio must be in an .ogg file
        encoded with OPUS (other formats may be sent as Audio or Document). Bots can currently
        send voice messages of up to 50 MB in size, this limit may be changed in the future.

        Note:
            The voice argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            voice (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path` | \
                :class:`telegram.Voice`): Voice file to send.
                Pass a file_id as String to send an voice file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an voice file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Voice` object to send.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            filename (:obj:`str`, optional): Custom file name for the voice, when uploading a
                new file. Convenience parameter, useful e.g. when sending files generated by the
                :obj:`tempfile` module.

                .. versionadded:: 13.1
            caption (:obj:`str`, optional): Voice message caption, 0-1024 characters after entities
                parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            duration (:obj:`int`, optional): Duration of the voice message in seconds.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'voice': parse_file_input(voice, Voice, filename=filename),
            'parse_mode': parse_mode,
        }

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption

        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]

        return self._message(  # type: ignore[return-value]
            'sendVoice',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_media_group(
        self,
        chat_id: Union[int, str],
        media: List[
            Union['InputMediaAudio', 'InputMediaDocument', 'InputMediaPhoto', 'InputMediaVideo']
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> List[Message]:
        """Use this method to send a group of photos or videos as an album.

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
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            'chat_id': chat_id,
            'media': media,
            'disable_notification': disable_notification,
            'allow_sending_without_reply': allow_sending_without_reply,
        }

        for med in data['media']:
            if med.parse_mode == DEFAULT_NONE:
                if self.defaults:
                    med.parse_mode = DefaultValue.get_value(self.defaults.parse_mode)
                else:
                    med.parse_mode = None

        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id

        if protect_content:
            data['protect_content'] = protect_content

        if message_thread_id:
            data["message_thread_id"] = message_thread_id

        result = self._post('sendMediaGroup', data, timeout=timeout, api_kwargs=api_kwargs)

        return Message.de_list(result, self)  # type: ignore

    @log
    def send_location(
        self,
        chat_id: Union[int, str],
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        location: Location = None,
        live_period: int = None,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send point on the map.

        Note:
            You can either supply a :obj:`latitude` and :obj:`longitude` or a :obj:`location`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            location (:class:`telegram.Location`, optional): The location to send.
            horizontal_accuracy (:obj:`int`, optional): The radius of uncertainty for the location,
                measured in meters; 0-1500.
            live_period (:obj:`int`, optional): Period in seconds for which the location will be
                updated, should be between 60 and 86400.
            heading (:obj:`int`, optional): For live locations, a direction in which the user is
                moving, in degrees. Must be between 1 and 360 if specified.
            proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance
                for proximity alerts about approaching another chat member, in meters. Must be
                between 1 and 100000 if specified.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
           message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                    original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
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

        data: JSONDict = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude}

        if live_period:
            data['live_period'] = live_period
        if horizontal_accuracy:
            data['horizontal_accuracy'] = horizontal_accuracy
        if heading:
            data['heading'] = heading
        if proximity_alert_radius:
            data['proximity_alert_radius'] = proximity_alert_radius

        return self._message(  # type: ignore[return-value]
            'sendLocation',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def edit_message_live_location(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        latitude: float = None,
        longitude: float = None,
        location: Location = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
    ) -> Union[Message, bool]:
        """Use this method to edit live location messages sent by the bot or via the bot
        (for inline bots). A location can be edited until its :attr:`telegram.Location.live_period`
        expires or editing is explicitly disabled by a call to :meth:`stop_message_live_location`.

        Note:
            You can either supply a :obj:`latitude` and :obj:`longitude` or a :obj:`location`.

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
            location (:class:`telegram.Location`, optional): The location to send.
            horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the
                location, measured in meters; 0-1500.
            heading (:obj:`int`, optional): Direction in which the user is moving, in degrees. Must
                be between 1 and 360 if specified.
            proximity_alert_radius (:obj:`int`, optional): Maximum distance for proximity alerts
                about approaching another chat member, in meters. Must be between 1 and 100000 if
                specified.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for a new inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.
        """
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

        data: JSONDict = {'latitude': latitude, 'longitude': longitude}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if horizontal_accuracy:
            data['horizontal_accuracy'] = horizontal_accuracy
        if heading:
            data['heading'] = heading
        if proximity_alert_radius:
            data['proximity_alert_radius'] = proximity_alert_radius

        return self._message(
            'editMessageLiveLocation',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def stop_message_live_location(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """Use this method to stop updating a live location message sent by the bot or via the bot
        (for inline bots) before live_period expires.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Required if inline_message_id is not specified.
                Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message with live location to stop.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for a new inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            sent Message is returned, otherwise :obj:`True` is returned.
        """
        data: JSONDict = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return self._message(
            'stopMessageLiveLocation',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def send_venue(
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
        timeout: ODVInput[float] = DEFAULT_NONE,
        venue: Venue = None,
        foursquare_type: str = None,
        api_kwargs: JSONDict = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send information about a venue.

        Note:
            * You can either supply :obj:`venue`, or :obj:`latitude`, :obj:`longitude`,
              :obj:`title` and :obj:`address` and optionally :obj:`foursquare_id` and
              :obj:`foursquare_type` or optionally :obj:`google_place_id` and
              :obj:`google_place_type`.
            * Foursquare details and Google Pace details are mutually exclusive. However, this
              behaviour is undocumented and might be changed by Telegram.

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
                <https://developers.google.com/places/web-service/supported_types>`_.)
            venue (:class:`telegram.Venue`, optional): The venue to send.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if not (venue or all([latitude, longitude, address, title])):
            raise ValueError(
                "Either venue or latitude, longitude, address and title must be"
                "passed as arguments."
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
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'title': title,
        }

        if foursquare_id:
            data['foursquare_id'] = foursquare_id
        if foursquare_type:
            data['foursquare_type'] = foursquare_type
        if google_place_id:
            data['google_place_id'] = google_place_id
        if google_place_type:
            data['google_place_type'] = google_place_type

        return self._message(  # type: ignore[return-value]
            'sendVenue',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_contact(
        self,
        chat_id: Union[int, str],
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        contact: Contact = None,
        vcard: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send phone contacts.

        Note:
            You can either supply :obj:`contact` or :obj:`phone_number` and :obj:`first_name`
            with optionally :obj:`last_name` and optionally :obj:`vcard`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            phone_number (:obj:`str`, optional): Contact's phone number.
            first_name (:obj:`str`, optional): Contact's first name.
            last_name (:obj:`str`, optional): Contact's last name.
            vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
                0-2048 bytes.
            contact (:class:`telegram.Contact`, optional): The contact to send.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if (not contact) and (not all([phone_number, first_name])):
            raise ValueError(
                "Either contact or phone_number and first_name must be passed as arguments."
            )

        if isinstance(contact, Contact):
            phone_number = contact.phone_number
            first_name = contact.first_name
            last_name = contact.last_name
            vcard = contact.vcard

        data: JSONDict = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name,
        }

        if last_name:
            data['last_name'] = last_name
        if vcard:
            data['vcard'] = vcard

        return self._message(  # type: ignore[return-value]
            'sendContact',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_game(
        self,
        chat_id: Union[int, str],
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send a game.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat.
            game_short_name (:obj:`str`): Short name of the game, serves as the unique identifier
                for the game. Set up your games via `@BotFather <https://t.me/BotFather>`_.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for a new inline keyboard. If empty, one ‘Play game_title’ button will be
                shown. If not empty, the first button must launch the game.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'game_short_name': game_short_name}

        return self._message(  # type: ignore[return-value]
            'sendGame',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def send_chat_action(
        self,
        chat_id: Union[str, int],
        action: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status). Telegram only recommends using this method when
        a response from the bot will take a noticeable amount of time to arrive.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            action(:class:`telegram.ChatAction` | :obj:`str`): Type of action to broadcast. Choose
                one, depending on what the user is about to receive. For convenience look at the
                constants in :class:`telegram.ChatAction`
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`:  On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'action': action}

        result = self._post('sendChatAction', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    def _effective_inline_results(  # pylint: disable=R0201
        self,
        results: Union[
            Sequence['InlineQueryResult'], Callable[[int], Optional[Sequence['InlineQueryResult']]]
        ],
        next_offset: str = None,
        current_offset: str = None,
    ) -> Tuple[Sequence['InlineQueryResult'], Optional[str]]:
        """
        Builds the effective results from the results input.
        We make this a stand-alone method so tg.ext.ExtBot can wrap it.

        Returns:
            Tuple of 1. the effective results and 2. correct the next_offset

        """
        if current_offset is not None and next_offset is not None:
            raise ValueError('`current_offset` and `next_offset` are mutually exclusive!')

        if current_offset is not None:
            # Convert the string input to integer
            if current_offset == '':
                current_offset_int = 0
            else:
                current_offset_int = int(current_offset)

            # for now set to empty string, stating that there are no more results
            # might change later
            next_offset = ''

            if callable(results):
                callable_output = results(current_offset_int)
                if not callable_output:
                    effective_results: Sequence['InlineQueryResult'] = []
                else:
                    effective_results = callable_output
                    # the callback *might* return more results on the next call, so we increment
                    # the page count
                    next_offset = str(current_offset_int + 1)
            else:
                if len(results) > (current_offset_int + 1) * MAX_INLINE_QUERY_RESULTS:
                    # we expect more results for the next page
                    next_offset_int = current_offset_int + 1
                    next_offset = str(next_offset_int)
                    effective_results = results[
                        current_offset_int
                        * MAX_INLINE_QUERY_RESULTS : next_offset_int
                        * MAX_INLINE_QUERY_RESULTS
                    ]
                else:
                    effective_results = results[current_offset_int * MAX_INLINE_QUERY_RESULTS :]
        else:
            effective_results = results  # type: ignore[assignment]

        return effective_results, next_offset

    @no_type_check
    def _set_ilq_result_defaults(self, res):
        # pylint: disable=W0212
        if hasattr(res, 'parse_mode') and res.parse_mode == DEFAULT_NONE:
            if self.defaults:
                res.parse_mode = self.defaults.parse_mode
            else:
                res.parse_mode = None
        if hasattr(res, 'input_message_content') and res.input_message_content:
            if (
                hasattr(res.input_message_content, 'parse_mode')
                and res.input_message_content.parse_mode == DEFAULT_NONE
            ):
                if self.defaults:
                    res.input_message_content.parse_mode = DefaultValue.get_value(
                        self.defaults.parse_mode
                    )
                else:
                    res.input_message_content.parse_mode = None
            if (
                hasattr(res.input_message_content, 'disable_web_page_preview')
                and res.input_message_content.disable_web_page_preview == DEFAULT_NONE
            ):
                if self.defaults:
                    res.input_message_content.disable_web_page_preview = DefaultValue.get_value(
                        self.defaults.disable_web_page_preview
                    )
                else:
                    res.input_message_content.disable_web_page_preview = None

    @log
    def answer_inline_query(
        self,
        inline_query_id: str,
        results: Union[
            Sequence['InlineQueryResult'], Callable[[int], Optional[Sequence['InlineQueryResult']]]
        ],
        cache_time: int = 300,
        is_personal: bool = None,
        next_offset: str = None,
        switch_pm_text: str = None,
        switch_pm_parameter: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        current_offset: str = None,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to send answers to an inline query. No more than 50 results per query
        are allowed.

        Warning:
            In most use cases :attr:`current_offset` should not be passed manually. Instead of
            calling this method directly, use the shortcut :meth:`telegram.InlineQuery.answer` with
            ``auto_pagination=True``, which will take care of passing the correct value.

        Args:
            inline_query_id (:obj:`str`): Unique identifier for the answered query.
            results (List[:class:`telegram.InlineQueryResult`] | Callable): A list of results for
                the inline query. In case :attr:`current_offset` is passed, ``results`` may also be
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
                bot a start message with the parameter ``switch_pm_parameter``.
            switch_pm_parameter (:obj:`str`, optional): Deep-linking parameter for the /start
                message sent to the bot when user presses the switch button. 1-64 characters,
                only A-Z, a-z, 0-9, _ and - are allowed.
            current_offset (:obj:`str`, optional): The :attr:`telegram.InlineQuery.offset` of
                the inline query to answer. If passed, PTB will automatically take care of
                the pagination for you, i.e. pass the correct ``next_offset`` and truncate the
                results list/get the results from the callable you passed.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
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
            self._set_ilq_result_defaults(result)

        results_dicts = [res.to_dict() for res in effective_results]

        data: JSONDict = {'inline_query_id': inline_query_id, 'results': results_dicts}

        if cache_time or cache_time == 0:
            data['cache_time'] = cache_time
        if is_personal:
            data['is_personal'] = is_personal
        if next_offset is not None:
            data['next_offset'] = next_offset
        if switch_pm_text:
            data['switch_pm_text'] = switch_pm_text
        if switch_pm_parameter:
            data['switch_pm_parameter'] = switch_pm_parameter

        return self._post(  # type: ignore[return-value]
            'answerInlineQuery',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def get_user_profile_photos(
        self,
        user_id: Union[str, int],
        offset: int = None,
        limit: int = 100,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Optional[UserProfilePhotos]:
        """Use this method to get a list of profile pictures for a user.

        Args:
            user_id (:obj:`int`): Unique identifier of the target user.
            offset (:obj:`int`, optional): Sequential number of the first photo to be returned.
                By default, all photos are returned.
            limit (:obj:`int`, optional): Limits the number of photos to be retrieved. Values
                between 1-100 are accepted. Defaults to ``100``.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.UserProfilePhotos`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id}

        if offset is not None:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        result = self._post('getUserProfilePhotos', data, timeout=timeout, api_kwargs=api_kwargs)

        return UserProfilePhotos.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def get_file(
        self,
        file_id: Union[
            str, Animation, Audio, ChatPhoto, Document, PhotoSize, Sticker, Video, VideoNote, Voice
        ],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> File:
        """
        Use this method to get basic info about a file and prepare it for downloading. For the
        moment, bots can download files of up to 20MB in size. The file can then be downloaded
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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
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

        data: JSONDict = {'file_id': file_id}

        result = self._post('getFile', data, timeout=timeout, api_kwargs=api_kwargs)

        if result.get('file_path') and not is_local_file(  # type: ignore[union-attr]
            result['file_path']  # type: ignore[index]
        ):
            result['file_path'] = (  # type: ignore[index]
                f"{self.base_file_url}/" f"{result['file_path']}"  # type: ignore[index]
            )

        return File.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def kick_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        until_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        revoke_messages: bool = None,
    ) -> bool:
        """
        Deprecated, use :func:`~telegram.Bot.ban_chat_member` instead.

        .. deprecated:: 13.7

        """
        warnings.warn(
            '`bot.kick_chat_member` is deprecated. Use `bot.ban_chat_member` instead.',
            TelegramDeprecationWarning,
            stacklevel=2,
        )
        return self.ban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            timeout=timeout,
            until_date=until_date,
            api_kwargs=api_kwargs,
            revoke_messages=revoke_messages,
        )

    @log
    def ban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        until_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        revoke_messages: bool = None,
    ) -> bool:
        """
        Use this method to ban a user from a group, supergroup or a channel. In the case of
        supergroups and channels, the user will not be able to return to the group on their own
        using invite links, etc., unless unbanned first. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

         .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the user will
                be unbanned, unix time. If user is banned for more than 366 days or less than 30
                seconds from the current time they are considered to be banned forever. Applied
                for supergroups and channels only.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.
            revoke_messages (:obj:`bool`, optional): Pass :obj:`True` to delete all messages from
                the chat for the user that is being removed. If :obj:`False`, the user will be able
                to see messages in the group that were sent before the user was removed.
                Always :obj:`True` for supergroups and channels.

                .. versionadded:: 13.4
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        if until_date is not None:
            if isinstance(until_date, datetime):
                until_date = to_timestamp(
                    until_date, tzinfo=self.defaults.tzinfo if self.defaults else None
                )
            data['until_date'] = until_date

        if revoke_messages is not None:
            data['revoke_messages'] = revoke_messages

        result = self._post('banChatMember', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def ban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to ban a channel chat in a supergroup or a channel. Until the chat is
        unbanned, the owner of the banned chat won't be able to send messages on behalf of **any of
        their channels**. The bot must be an administrator in the supergroup or channel for this
        to work and must have the appropriate administrator rights.

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target group or username
                of the target supergroup or channel (in the format ``@channelusername``).
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'sender_chat_id': sender_chat_id}

        result = self._post('banChatSenderChat', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def unban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        only_if_banned: bool = None,
    ) -> bool:
        """Use this method to unban a previously kicked user in a supergroup or channel.

        The user will *not* return to the group or channel automatically, but will be able to join
        via link, etc. The bot must be an administrator for this to work. By default, this method
        guarantees that after the call the user is not a member of the chat, but will be able to
        join it. So if the user is a member of the chat they will also be *removed* from the chat.
        If you don't want this, use the parameter :attr:`only_if_banned`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            only_if_banned (:obj:`bool`, optional): Do nothing if the user is not banned.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        if only_if_banned is not None:
            data['only_if_banned'] = only_if_banned

        result = self._post('unbanChatMember', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def unban_chat_sender_chat(
        self,
        chat_id: Union[str, int],
        sender_chat_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to unban a previously banned channel in a supergroup or channel.
        The bot must be an administrator for this to work and must have the
        appropriate administrator rights.

        .. versionadded:: 13.9

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            sender_chat_id (:obj:`int`): Unique identifier of the target sender chat.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'sender_chat_id': sender_chat_id}

        result = self._post('unbanChatSenderChat', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def answer_callback_query(
        self,
        callback_query_id: str,
        text: str = None,
        show_alert: bool = False,
        url: str = None,
        cache_time: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
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

        Args:
            callback_query_id (:obj:`str`): Unique identifier for the query to be answered.
            text (:obj:`str`, optional): Text of the notification. If not specified, nothing will
                be shown to the user, 0-200 characters.
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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'callback_query_id': callback_query_id}

        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert
        if url:
            data['url'] = url
        if cache_time is not None:
            data['cache_time'] = cache_time

        result = self._post('answerCallbackQuery', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def edit_message_text(
        self,
        text: str,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit text and game messages.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``)
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            text (:obj:`str`): New text of the message, 1-4096 characters after entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in your bot's message. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            entities (List[:class:`telegram.MessageEntity`], optional): List of special entities
                that appear in message text, which can be specified instead of :attr:`parse_mode`.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for an inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
        }

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if entities:
            data['entities'] = [me.to_dict() for me in entities]

        return self._message(
            'editMessageText',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def edit_message_caption(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        caption: str = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit captions of messages.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``)
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            caption (:obj:`str`, optional): New caption of the message, 0-1024 characters after
                entities parsing.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for an inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_caption: Both chat_id and message_id are required when '
                'inline_message_id is not specified'
            )

        data: JSONDict = {'parse_mode': parse_mode}

        if caption:
            data['caption'] = caption
        if caption_entities:
            data['caption_entities'] = [me.to_dict() for me in caption_entities]
        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return self._message(
            'editMessageCaption',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def edit_message_media(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        media: 'InputMedia' = None,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit animation, audio, document, photo, or video messages. If a message
        is part of a message album, then it can be edited only to an audio for audio albums, only
        to a document for document albums and to a photo or a video otherwise. When an inline
        message is edited, a new file can't be uploaded. Use a previously uploaded file via its
        ``file_id`` or specify a URL.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            media (:class:`telegram.InputMedia`): An object for a new media content
                of the message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for an inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_media: Both chat_id and message_id are required when '
                'inline_message_id is not specified'
            )

        data: JSONDict = {'media': media}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return self._message(
            'editMessageMedia',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def edit_message_reply_markup(
        self,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        reply_markup: Optional['InlineKeyboardMarkup'] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot
        (for inline bots).

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of the target channel
                (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the message to edit.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for an inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, if edited message is not an inline message, the
            edited message is returned, otherwise :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_reply_markup: Both chat_id and message_id are required when '
                'inline_message_id is not specified'
            )

        data: JSONDict = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return self._message(
            'editMessageReplyMarkup',
            data,
            timeout=timeout,
            reply_markup=reply_markup,
            api_kwargs=api_kwargs,
        )

    @log
    def get_updates(
        self,
        offset: int = None,
        limit: int = 100,
        timeout: float = 0,
        read_latency: float = 2.0,
        allowed_updates: List[str] = None,
        api_kwargs: JSONDict = None,
    ) -> List[Update]:
        """Use this method to receive incoming updates using long polling.

        Args:
            offset (:obj:`int`, optional): Identifier of the first update to be returned. Must be
                greater by one than the highest among the identifiers of previously received
                updates. By default, updates starting with the earliest unconfirmed update are
                returned. An update is considered confirmed as soon as getUpdates is called with an
                offset higher than its :attr:`telegram.Update.update_id`. The negative offset can
                be specified to retrieve updates starting from -offset update from the end of the
                updates queue. All previous updates will forgotten.
            limit (:obj:`int`, optional): Limits the number of updates to be retrieved. Values
                between 1-100 are accepted. Defaults to ``100``.
            timeout (:obj:`int`, optional): Timeout in seconds for long polling. Defaults to ``0``,
                i.e. usual short polling. Should be positive, short polling should be used for
                testing purposes only.
            read_latency (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the ``timeout`` value and used as the read
                timeout from server. Defaults to  ``2``.
            allowed_updates (List[:obj:`str`]), optional): A JSON-serialized list the types of
                updates you want your bot to receive. For example, specify ["message",
                "edited_channel_post", "callback_query"] to only receive updates of these types.
                See :class:`telegram.Update` for a complete list of available update types.
                Specify an empty list to receive all updates except
                :attr:`telegram.Update.chat_member` (default). If not specified, the previous
                setting will be used. Please note that this parameter doesn't affect updates
                created before the call to the get_updates, so unwanted updates may be received for
                a short period of time.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Note:
            1. This method will not work if an outgoing webhook is set up.
            2. In order to avoid getting duplicate updates, recalculate offset after each
               server response.
            3. To take full advantage of this library take a look at :class:`telegram.ext.Updater`

        Returns:
            List[:class:`telegram.Update`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'timeout': timeout}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates

        # Ideally we'd use an aggressive read timeout for the polling. However,
        # * Short polling should return within 2 seconds.
        # * Long polling poses a different problem: the connection might have been dropped while
        #   waiting for the server to return and there's no way of knowing the connection had been
        #   dropped in real time.
        result = cast(
            List[JSONDict],
            self._post(
                'getUpdates',
                data,
                timeout=float(read_latency) + float(timeout),
                api_kwargs=api_kwargs,
            ),
        )

        if result:
            self.logger.debug('Getting updates: %s', [u['update_id'] for u in result])
        else:
            self.logger.debug('No new updates found.')

        return Update.de_list(result, self)  # type: ignore[return-value]

    @log
    def set_webhook(
        self,
        url: str = None,
        certificate: FileInput = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        max_connections: int = 40,
        allowed_updates: List[str] = None,
        api_kwargs: JSONDict = None,
        ip_address: str = None,
        drop_pending_updates: bool = None,
        secret_token: str = None,
    ) -> bool:
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, Telegram will send an HTTPS POST request to the
        specified url, containing a JSON-serialized Update. In case of an unsuccessful request,
        Telegram will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook was set by you, you can specify secret data in
        the parameter ``secret_token``. If specified, the request will contain a header
        ``X-Telegram-Bot-Api-Secret-Token`` with the secret token as content.

        Note:
            The certificate argument should be a file from disk ``open(filename, 'rb')``.

        Args:
            url (:obj:`str`): HTTPS url to send updates to. Use an empty string to remove webhook
                integration.
            certificate (:obj:`filelike`): Upload your public key certificate so that the root
                certificate in use can be checked. See our self-signed guide for details.
                (https://goo.gl/rw7w6Y)
            ip_address (:obj:`str`, optional): The fixed IP address which will be used to send
                webhook requests instead of the IP address resolved through DNS.
            max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
                connections to the webhook for update delivery, 1-100. Defaults to ``40``. Use
                lower values to limit the load on your bot's server, and higher values to increase
                your bot's throughput.
            allowed_updates (List[:obj:`str`], optional): A JSON-serialized list the types of
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
                ``X-Telegram-Bot-Api-Secret-Token`` in every webhook request, 1-256 characters.
                Only characters ``A-Z``, ``a-z``, ``0-9``, ``_`` and ``-`` are allowed.
                The header is useful to ensure that the request comes from a webhook set by you.

                .. versionadded:: 13.13
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Note:
            1. You will not be able to receive updates using :meth:`get_updates` for long as an
               outgoing webhook is set up.
            2. To use a self-signed certificate, you need to upload your public key certificate
               using certificate parameter. Please upload as InputFile, sending a String will not
               work.
            3. Ports currently supported for Webhooks: ``443``, ``80``, ``88``, ``8443``.

            If you're having any trouble setting up webhooks, please check out this `guide to
            Webhooks`_.

        Returns:
            :obj:`bool` On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        .. _`guide to Webhooks`: https://core.telegram.org/bots/webhooks

        """
        data: JSONDict = {}

        if url is not None:
            data['url'] = url
        if certificate:
            data['certificate'] = parse_file_input(certificate)
        if max_connections is not None:
            data['max_connections'] = max_connections
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates
        if ip_address:
            data['ip_address'] = ip_address
        if drop_pending_updates:
            data['drop_pending_updates'] = drop_pending_updates
        if secret_token is not None:
            data["secret_token"] = secret_token

        result = self._post('setWebhook', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def delete_webhook(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        drop_pending_updates: bool = None,
    ) -> bool:
        """
        Use this method to remove webhook integration if you decide to switch back to
        :meth:`get_updates()`.

        Args:
            drop_pending_updates (:obj:`bool`, optional): Pass :obj:`True` to drop all pending
                updates.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data = {}

        if drop_pending_updates:
            data['drop_pending_updates'] = drop_pending_updates

        result = self._post('deleteWebhook', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def leave_chat(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method for your bot to leave a group, supergroup or channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('leaveChat', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def get_chat(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Chat:
        """
        Use this method to get up to date information about the chat (current name of the user for
        one-on-one conversations, current username of a user, group or channel, etc.).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Chat`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('getChat', data, timeout=timeout, api_kwargs=api_kwargs)

        return Chat.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def get_chat_administrators(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[ChatMember]:
        """
        Use this method to get a list of administrators in a chat.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
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
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('getChatAdministrators', data, timeout=timeout, api_kwargs=api_kwargs)

        return ChatMember.de_list(result, self)  # type: ignore

    @log
    def get_chat_members_count(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> int:
        """
        Deprecated, use :func:`~telegram.Bot.get_chat_member_count` instead.

        .. deprecated:: 13.7
        """
        warnings.warn(
            '`bot.get_chat_members_count` is deprecated. '
            'Use `bot.get_chat_member_count` instead.',
            TelegramDeprecationWarning,
            stacklevel=2,
        )
        return self.get_chat_member_count(chat_id=chat_id, timeout=timeout, api_kwargs=api_kwargs)

    @log
    def get_chat_member_count(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> int:
        """Use this method to get the number of members in a chat.

         .. versionadded:: 13.7

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`int`: Number of members in the chat.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('getChatMemberCount', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def get_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatMember:
        """Use this method to get information about a member of a chat.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup or channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatMember`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        result = self._post('getChatMember', data, timeout=timeout, api_kwargs=api_kwargs)

        return ChatMember.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def set_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        sticker_set_name: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {'chat_id': chat_id, 'sticker_set_name': sticker_set_name}

        result = self._post('setChatStickerSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def delete_chat_sticker_set(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to delete a group sticker set from a supergroup. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned in
        :meth:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
             :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('deleteChatStickerSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    def get_webhook_info(
        self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None
    ) -> WebhookInfo:
        """Use this method to get current webhook status. Requires no parameters.

        If the bot is using :meth:`get_updates`, will return an object with the
        :attr:`telegram.WebhookInfo.url` field empty.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.WebhookInfo`

        """
        result = self._post('getWebhookInfo', None, timeout=timeout, api_kwargs=api_kwargs)

        return WebhookInfo.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def set_game_score(
        self,
        user_id: Union[int, str],
        score: int,
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        force: bool = None,
        disable_edit_message: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Union[Message, bool]:
        """
        Use this method to set the score of the specified user in a game.

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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: The edited message, or if the message wasn't sent by the bot
            , :obj:`True`.

        Raises:
            :class:`telegram.error.TelegramError`: If the new score is not greater than the user's
                current score in the chat and force is :obj:`False`.

        """
        data: JSONDict = {'user_id': user_id, 'score': score}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if force is not None:
            data['force'] = force
        if disable_edit_message is not None:
            data['disable_edit_message'] = disable_edit_message

        return self._message(
            'setGameScore',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def get_game_high_scores(
        self,
        user_id: Union[int, str],
        chat_id: Union[str, int] = None,
        message_id: int = None,
        inline_message_id: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[GameHighScore]:
        """
        Use this method to get data for high score tables. Will return the score of the specified
        user and several of their neighbors in a game.

        Note:
            This method will currently return scores for the target user, plus two of their
            closest neighbors on each side. Will also return the top three users if the user and
            his neighbors are not among them. Please note that this behavior is subject to change.

        Args:
            user_id (:obj:`int`): Target user id.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.GameHighScore`]

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        result = self._post('getGameHighScores', data, timeout=timeout, api_kwargs=api_kwargs)

        return GameHighScore.de_list(result, self)  # type: ignore

    @log
    def send_invoice(
        self,
        chat_id: Union[int, str],
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List['LabeledPrice'],
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
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """Use this method to send invoices.

        Warning:
            As of API 5.2 :attr:`start_parameter` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :attr:`start_parameter` is optional.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            title (:obj:`str`): Product name, 1-32 characters.
            description (:obj:`str`): Product description, 1-255 characters.
            payload (:obj:`str`): Bot-defined invoice payload, 1-128 bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via
                `@BotFather <https://t.me/BotFather>`_.
            currency (:obj:`str`): Three-letter ISO 4217 currency code.
            prices (List[:class:`telegram.LabeledPrice`)]: Price breakdown, a JSON-serialized list
                of components (e.g. product price, tax, discount, delivery cost, delivery tax,
                bonus, etc.).
            max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the
                smallest units of the currency (integer, not float/double). For example, for a
                maximum tip of US$ 1.45 pass ``max_tip_amount = 145``. See the exp parameter in
                `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
                shows the number of digits past the decimal point for each currency (2 for the
                majority of currencies). Defaults to ``0``.

                .. versionadded:: 13.5
            suggested_tip_amounts (List[:obj:`int`], optional): A JSON-serialized array of
                suggested amounts of tips in the smallest units of the currency (integer, not
                float/double). At most 4 suggested tip amounts can be specified. The suggested tip
                amounts must be positive, passed in a strictly increased order and must not exceed
                ``max_tip_amount``.

                .. versionadded:: 13.5
            start_parameter (:obj:`str`, optional): Unique deep-linking parameter. If left empty,
                *forwarded copies* of the sent message will have a *Pay* button, allowing
                multiple users to pay directly from the forwarded message, using the same invoice.
                If non-empty, forwarded copies of the sent message will have a *URL* button with a
                deep link to the bot (instead of a *Pay* button), with the value used as the
                start parameter.

                .. versionchanged:: 13.5
                    As of Bot API 5.2, this parameter is optional.
            provider_data (:obj:`str` | :obj:`object`, optional): JSON-serialized data about the
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
           message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for an inline keyboard. If empty, one 'Pay total price' button will be
                shown. If not empty, the first button must be a Pay button.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'currency': currency,
            'prices': [p.to_dict() for p in prices],
        }
        if max_tip_amount is not None:
            data['max_tip_amount'] = max_tip_amount
        if suggested_tip_amounts is not None:
            data['suggested_tip_amounts'] = suggested_tip_amounts
        if start_parameter is not None:
            data['start_parameter'] = start_parameter
        if provider_data is not None:
            if isinstance(provider_data, str):
                data['provider_data'] = provider_data
            else:
                data['provider_data'] = json.dumps(provider_data)
        if photo_url is not None:
            data['photo_url'] = photo_url
        if photo_size is not None:
            data['photo_size'] = photo_size
        if photo_width is not None:
            data['photo_width'] = photo_width
        if photo_height is not None:
            data['photo_height'] = photo_height
        if need_name is not None:
            data['need_name'] = need_name
        if need_phone_number is not None:
            data['need_phone_number'] = need_phone_number
        if need_email is not None:
            data['need_email'] = need_email
        if need_shipping_address is not None:
            data['need_shipping_address'] = need_shipping_address
        if is_flexible is not None:
            data['is_flexible'] = is_flexible
        if send_phone_number_to_provider is not None:
            data['send_phone_number_to_provider'] = send_phone_number_to_provider
        if send_email_to_provider is not None:
            data['send_email_to_provider'] = send_email_to_provider

        return self._message(  # type: ignore[return-value]
            'sendInvoice',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def answer_shipping_query(  # pylint: disable=C0103
        self,
        shipping_query_id: str,
        ok: bool,
        shipping_options: List[ShippingOption] = None,
        error_message: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        If you sent an invoice requesting a shipping address and the parameter ``is_flexible`` was
        specified, the Bot API will send an :class:`telegram.Update` with a
        :attr:`Update.shipping_query` field to the bot. Use this method to reply to shipping
        queries.

        Args:
            shipping_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify :obj:`True` if delivery to the specified address is possible
                and :obj:`False` if there are any problems (for example, if delivery to the
                specified address is not possible).
            shipping_options (List[:class:`telegram.ShippingOption`]), optional]: Required if ok is
                :obj:`True`. A JSON-serialized array of available shipping options.
            error_message (:obj:`str`, optional): Required if ok is :obj:`False`. Error message in
                human readable form that explains why it is impossible to complete the order (e.g.
                "Sorry, delivery to your desired address is unavailable"). Telegram will display
                this message to the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        ok = bool(ok)

        if ok and (shipping_options is None or error_message is not None):
            raise TelegramError(
                'answerShippingQuery: If ok is True, shipping_options '
                'should not be empty and there should not be error_message'
            )

        if not ok and (shipping_options is not None or error_message is None):
            raise TelegramError(
                'answerShippingQuery: If ok is False, error_message '
                'should not be empty and there should not be shipping_options'
            )

        data: JSONDict = {'shipping_query_id': shipping_query_id, 'ok': ok}

        if ok:
            if not shipping_options:
                # not using an assert statement directly here since they are removed in
                # the optimized bytecode
                raise AssertionError
            data['shipping_options'] = [option.to_dict() for option in shipping_options]
        if error_message is not None:
            data['error_message'] = error_message

        result = self._post('answerShippingQuery', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def answer_pre_checkout_query(  # pylint: disable=C0103
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Once the user has confirmed their payment and shipping details, the Bot API sends the final
        confirmation in the form of an :class:`telegram.Update` with the field
        :attr:`Update.pre_checkout_query`. Use this method to respond to such pre-checkout queries.

        Note:
            The Bot API must receive an answer within 10 seconds after the pre-checkout
            query was sent.

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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        ok = bool(ok)

        if not (ok ^ (error_message is not None)):  # pylint: disable=C0325
            raise TelegramError(
                'answerPreCheckoutQuery: If ok is True, there should '
                'not be error_message; if ok is False, error_message '
                'should not be empty'
            )

        data: JSONDict = {'pre_checkout_query_id': pre_checkout_query_id, 'ok': ok}

        if error_message is not None:
            data['error_message'] = error_message

        result = self._post('answerPreCheckoutQuery', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def answer_web_app_query(
        self,
        web_app_query_id: str,
        result: 'InlineQueryResult',
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> SentWebAppMessage:
        """Use this method to set the result of an interaction with a Web App and send a
        corresponding message on behalf of the user to the chat from which the query originated.

        .. versionadded:: 13.12

        Args:
            web_app_query_id (:obj:`str`): Unique identifier for the query to be answered.
            result (:class:`telegram.InlineQueryResult`): An object describing the message to be
                sent.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.SentWebAppMessage`: On success, a sent
            :class:`telegram.SentWebAppMessage` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        self._set_ilq_result_defaults(result)
        data: JSONDict = {'web_app_query_id': web_app_query_id, 'result': result.to_dict()}

        api_result = self._post(
            'answerWebAppQuery',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

        return SentWebAppMessage.de_json(api_result, self)  # type: ignore[return-value, arg-type]

    @log
    def restrict_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        permissions: ChatPermissions,
        until_date: Union[int, datetime] = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to restrict a user in a supergroup. The bot must be an administrator in
        the supergroup for this to work and must have the appropriate admin rights. Pass
        :obj:`True` for all boolean parameters to lift restrictions from a user.

        Note:
            Since Bot API 4.4, :meth:`restrict_chat_member` takes the new user permissions in a
            single argument of type :class:`telegram.ChatPermissions`. The old way of passing
            parameters will not keep working forever.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when restrictions
                will be lifted for the user, unix time. If user is restricted for more than 366
                days or less than 30 seconds from the current time, they are considered to be
                restricted forever.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.
            permissions (:class:`telegram.ChatPermissions`): A JSON-serialized object for new user
                permissions.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            'chat_id': chat_id,
            'user_id': user_id,
            'permissions': permissions.to_dict(),
        }

        if until_date is not None:
            if isinstance(until_date, datetime):
                until_date = to_timestamp(
                    until_date, tzinfo=self.defaults.tzinfo if self.defaults else None
                )
            data['until_date'] = until_date

        result = self._post('restrictChatMember', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def promote_chat_member(
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
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        is_anonymous: bool = None,
        can_manage_chat: bool = None,
        can_manage_voice_chats: bool = None,
        can_manage_video_chats: bool = None,
        can_manage_topics: bool = None,
    ) -> bool:
        """
        Use this method to promote or demote a user in a supergroup or a channel. The bot must be
        an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass :obj:`False` for all boolean parameters to demote a user.

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

            can_manage_voice_chats (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can manage voice chats.

                .. versionadded:: 13.4

                .. deprecated:: 13.12
                    Since Bot API 6.0, voice chat was renamed to video chat.

            can_manage_video_chats (:obj:`bool`, optional): Pass :obj:`True`, if the administrator
                can manage video chats.

                .. versionadded:: 13.12

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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
            can_manage_topics (:obj:`bool`, optional): Pass :obj:`True`, if the user is
                allowed to create, rename, close, and reopen forum topics; supergroups only.

                .. versionadded:: 13.15

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if can_manage_voice_chats is not None and can_manage_video_chats is not None:
            raise ValueError(
                "Only supply one of `can_manage_video_chats`/`can_manage_voice_chats`, not both."
            )

        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        if is_anonymous is not None:
            data['is_anonymous'] = is_anonymous
        if can_change_info is not None:
            data['can_change_info'] = can_change_info
        if can_post_messages is not None:
            data['can_post_messages'] = can_post_messages
        if can_edit_messages is not None:
            data['can_edit_messages'] = can_edit_messages
        if can_delete_messages is not None:
            data['can_delete_messages'] = can_delete_messages
        if can_invite_users is not None:
            data['can_invite_users'] = can_invite_users
        if can_restrict_members is not None:
            data['can_restrict_members'] = can_restrict_members
        if can_pin_messages is not None:
            data['can_pin_messages'] = can_pin_messages
        if can_promote_members is not None:
            data['can_promote_members'] = can_promote_members
        if can_manage_chat is not None:
            data['can_manage_chat'] = can_manage_chat
        if can_manage_voice_chats is not None:
            data['can_manage_video_chats'] = can_manage_voice_chats
        if can_manage_video_chats is not None:
            data['can_manage_video_chats'] = can_manage_video_chats
        if can_manage_topics is not None:
            data["can_manage_topics"] = can_manage_topics

        result = self._post('promoteChatMember', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_chat_permissions(
        self,
        chat_id: Union[str, int],
        permissions: ChatPermissions,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to set default chat permissions for all members. The bot must be an
        administrator in the group or a supergroup for this to work and must have the
        :attr:`telegram.ChatMember.can_restrict_members` admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username of
                the target supergroup (in the format `@supergroupusername`).
            permissions (:class:`telegram.ChatPermissions`): New default chat permissions.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'permissions': permissions.to_dict()}

        result = self._post('setChatPermissions', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_chat_administrator_custom_title(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        custom_title: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to set a custom title for administrators promoted by the bot in a
        supergroup. The bot must be an administrator for this to work.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username of
                the target supergroup (in the format `@supergroupusername`).
            user_id (:obj:`int`): Unique identifier of the target administrator.
            custom_title (:obj:`str`): New custom title for the administrator; 0-16 characters,
                emoji are not allowed.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id, 'custom_title': custom_title}

        result = self._post(
            'setChatAdministratorCustomTitle', data, timeout=timeout, api_kwargs=api_kwargs
        )

        return result  # type: ignore[return-value]

    @log
    def export_chat_invite_link(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> str:
        """
        Use this method to generate a new primary invite link for a chat; any previously generated
        link is revoked. The bot must be an administrator in the chat for this to work and must
        have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Note:
            Each administrator in a chat generates their own invite links. Bots can't use invite
            links generated by other administrators. If you want your bot to work with invite
            links, it will need to generate its own link using :meth:`export_chat_invite_link` or
            by calling the :meth:`get_chat` method. If your bot needs to generate a new primary
            invite link replacing its previous one, use :attr:`export_chat_invite_link` again.

        Returns:
            :obj:`str`: New invite link on success.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('exportChatInviteLink', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def create_chat_invite_link(
        self,
        chat_id: Union[str, int],
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        name: str = None,
        creates_join_request: bool = None,
    ) -> ChatInviteLink:
        """
        Use this method to create an additional invite link for a chat. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        The link can be revoked using the method :meth:`revoke_chat_invite_link`.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire. Integer input will be interpreted as Unix timestamp.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link; 1-99999.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
            name (:obj:`str`, optional): Invite link name; 0-32 characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, ``member_limit`` can't be specified.

                .. versionadded:: 13.8

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if creates_join_request and member_limit:
            raise ValueError(
                "If `creates_join_request` is `True`, `member_limit` can't be specified."
            )

        data: JSONDict = {
            'chat_id': chat_id,
        }

        if expire_date is not None:
            if isinstance(expire_date, datetime):
                expire_date = to_timestamp(
                    expire_date, tzinfo=self.defaults.tzinfo if self.defaults else None
                )
            data['expire_date'] = expire_date

        if member_limit is not None:
            data['member_limit'] = member_limit

        if name is not None:
            data['name'] = name

        if creates_join_request is not None:
            data['creates_join_request'] = creates_join_request

        result = self._post('createChatInviteLink', data, timeout=timeout, api_kwargs=api_kwargs)

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def edit_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: str,
        expire_date: Union[int, datetime] = None,
        member_limit: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        name: str = None,
        creates_join_request: bool = None,
    ) -> ChatInviteLink:
        """
        Use this method to edit a non-primary invite link created by the bot. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.

        Note:
            Though not stated explicitly in the official docs, Telegram changes not only the
            optional parameters that are explicitly passed, but also replaces all other optional
            parameters to the default values. However, since not documented, this behaviour may
            change unbeknown to PTB.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            invite_link (:obj:`str`): The invite link to edit.
            expire_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the link will
                expire.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.
            member_limit (:obj:`int`, optional): Maximum number of users that can be members of
                the chat simultaneously after joining the chat via this invite link; 1-99999.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
            name (:obj:`str`, optional): Invite link name; 0-32 characters.

                .. versionadded:: 13.8
            creates_join_request (:obj:`bool`, optional): :obj:`True`, if users joining the chat
                via the link need to be approved by chat administrators.
                If :obj:`True`, ``member_limit`` can't be specified.

                .. versionadded:: 13.8

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        if creates_join_request and member_limit:
            raise ValueError(
                "If `creates_join_request` is `True`, `member_limit` can't be specified."
            )

        data: JSONDict = {'chat_id': chat_id, 'invite_link': invite_link}

        if expire_date is not None:
            if isinstance(expire_date, datetime):
                expire_date = to_timestamp(
                    expire_date, tzinfo=self.defaults.tzinfo if self.defaults else None
                )
            data['expire_date'] = expire_date

        if member_limit is not None:
            data['member_limit'] = member_limit

        if name is not None:
            data['name'] = name

        if creates_join_request is not None:
            data['creates_join_request'] = creates_join_request

        result = self._post('editChatInviteLink', data, timeout=timeout, api_kwargs=api_kwargs)

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def revoke_chat_invite_link(
        self,
        chat_id: Union[str, int],
        invite_link: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatInviteLink:
        """
        Use this method to revoke an invite link created by the bot. If the primary link is
        revoked, a new link is automatically generated. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        .. versionadded:: 13.4

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            invite_link (:obj:`str`): The invite link to edit.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatInviteLink`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'invite_link': invite_link}

        result = self._post('revokeChatInviteLink', data, timeout=timeout, api_kwargs=api_kwargs)

        return ChatInviteLink.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def approve_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to approve a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        result = self._post('approveChatJoinRequest', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def decline_chat_join_request(
        self,
        chat_id: Union[str, int],
        user_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to decline a chat join request.

        The bot must be an administrator in the chat for this to work and must have the
        :attr:`telegram.ChatPermissions.can_invite_users` administrator right.

        .. versionadded:: 13.8

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {'chat_id': chat_id, 'user_id': user_id}

        result = self._post('declineChatJoinRequest', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_chat_photo(
        self,
        chat_id: Union[str, int],
        photo: FileInput,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to set a new profile photo for the chat.

        Photos can't be changed for private chats. The bot must be an administrator in the chat
        for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            photo (`filelike object` | :obj:`bytes` | :class:`pathlib.Path`): New chat photo.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'photo': parse_file_input(photo)}

        result = self._post('setChatPhoto', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def delete_chat_photo(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete a chat photo. Photos can't be changed for private chats. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        result = self._post('deleteChatPhoto', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_chat_title(
        self,
        chat_id: Union[str, int],
        title: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to change the title of a chat. Titles can't be changed for private chats.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            title (:obj:`str`): New chat title, 1-255 characters.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'title': title}

        result = self._post('setChatTitle', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_chat_description(
        self,
        chat_id: Union[str, int],
        description: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to change the description of a group, a supergroup or a channel. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            description (:obj:`str`): New chat description, 0-255 characters.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'description': description}

        result = self._post('setChatDescription', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def pin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to add a message to the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :attr:`telegram.ChatMember.can_pin_messages` admin right in a supergroup
        or :attr:`telegram.ChatMember.can_edit_messages` admin right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of a message to pin.
            disable_notification (:obj:`bool`, optional): Pass :obj:`True`, if it is not necessary
                to send a notification to all chat members about the new pinned message.
                Notifications are always disabled in channels and private chats.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification,
        }

        return self._post(  # type: ignore[return-value]
            'pinChatMessage', data, timeout=timeout, api_kwargs=api_kwargs
        )

    @log
    def unpin_chat_message(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        message_id: int = None,
    ) -> bool:
        """
        Use this method to remove a message from the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this to work
        and must have the :attr:`telegram.ChatMember.can_pin_messages` admin right in a
        supergroup or :attr:`telegram.ChatMember.can_edit_messages` admin right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`, optional): Identifier of a message to unpin. If not specified,
                the most recent pinned message (by sending date) will be unpinned.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        if message_id is not None:
            data['message_id'] = message_id

        return self._post(  # type: ignore[return-value]
            'unpinChatMessage', data, timeout=timeout, api_kwargs=api_kwargs
        )

    @log
    def unpin_all_chat_messages(
        self,
        chat_id: Union[str, int],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a chat. If the
        chat is not a private chat, the bot must be an administrator in the chat for this
        to work and must have the :attr:`telegram.ChatMember.can_pin_messages` admin right in a
        supergroup or :attr:`telegram.ChatMember.can_edit_messages` admin right in a channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        return self._post(  # type: ignore[return-value]
            'unpinAllChatMessages', data, timeout=timeout, api_kwargs=api_kwargs
        )

    @log
    def get_sticker_set(
        self,
        name: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> StickerSet:
        """Use this method to get a sticker set.

        Args:
            name (:obj:`str`): Name of the sticker set.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.StickerSet`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'name': name}

        result = self._post('getStickerSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return StickerSet.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def get_custom_emoji_stickers(
        self,
        custom_emoji_ids: List[str],
        *,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[Sticker]:
        """
        Use this method to get information about emoji stickers by their identifiers.

        .. versionadded:: 13.14

        Args:
            custom_emoji_ids (List[:obj:`str`]): List of custom emoji identifiers.
                At most 200 custom emoji identifiers can be specified.
        Keyword Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
        Returns:
            List[:class:`telegram.Sticker`]
        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {"custom_emoji_ids": custom_emoji_ids}
        result = self._post("getCustomEmojiStickers", data, timeout=timeout, api_kwargs=api_kwargs)
        return Sticker.de_list(result, self)  # type: ignore[return-value, arg-type]

    @log
    def upload_sticker_file(
        self,
        user_id: Union[str, int],
        png_sticker: FileInput,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
    ) -> File:
        """
        Use this method to upload a ``.PNG`` file with a sticker for later use in
        :meth:`create_new_sticker_set` and :meth:`add_sticker_to_set` methods (can be used multiple
        times).

        Note:
            The png_sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            user_id (:obj:`int`): User identifier of sticker file owner.
            png_sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`):
                **PNG** image with the sticker, must be up to 512 kilobytes in size,
                dimensions must not exceed 512px, and either width or height must be exactly 512px.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.File`: On success, the uploaded File is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id, 'png_sticker': parse_file_input(png_sticker)}

        result = self._post('uploadStickerFile', data, timeout=timeout, api_kwargs=api_kwargs)

        return File.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def create_new_sticker_set(
        self,
        user_id: Union[str, int],
        name: str,
        title: str,
        emojis: str,
        png_sticker: FileInput = None,
        contains_masks: bool = None,
        mask_position: MaskPosition = None,
        timeout: DVInput[float] = DEFAULT_20,
        tgs_sticker: FileInput = None,
        api_kwargs: JSONDict = None,
        webm_sticker: FileInput = None,
        sticker_type: str = None,
    ) -> bool:
        """
        Use this method to create new sticker set owned by a user.
        The bot will be able to edit the created sticker set.
        You must use exactly one of the fields ``png_sticker``, ``tgs_sticker``, or
        ``webm_sticker``.

        Warning:
            As of API 4.7 ``png_sticker`` is an optional argument and therefore the order of the
            arguments had to be changed. Use keyword arguments to make sure that the arguments are
            passed correctly.

        Note:
            The png_sticker and tgs_sticker argument can be either a file_id, an URL or a file from
            disk ``open(filename, 'rb')``

        .. versionchanged:: 13.14
            The parameter ``contains_masks`` has been depreciated as of Bot API 6.2.
            Use ``sticker_type`` instead.

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Short name of sticker set, to be used in t.me/addstickers/ URLs
                (e.g., animals). Can contain only english letters, digits and underscores.
                Must begin with a letter, can't contain consecutive underscores and
                must end in "_by_<bot username>". <bot_username> is case insensitive.
                1-64 characters.
            title (:obj:`str`): Sticker set title, 1-64 characters.
            png_sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **PNG** image with the sticker,
                must be up to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px. Pass a file_id as a String to
                send a file that already exists on the Telegram servers, pass an HTTP URL as a
                String for Telegram to get a file from the Internet, or upload a new one
                using multipart/form-data.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            tgs_sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **TGS** animation with the sticker, uploaded using multipart/form-data.
                See https://core.telegram.org/stickers#animated-sticker-requirements for technical
                requirements.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            webm_sticker (:obj:`str` | filelike object | :obj:`bytes` | :class:`pathlib.Path`,\
                optional): **WEBM** video with the sticker, uploaded using multipart/form-data.
                See https://core.telegram.org/stickers#video-sticker-requirements for
                technical requirements.

                .. versionadded:: 13.11

            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            contains_masks (:obj:`bool`, optional): Pass :obj:`True`, if a set of mask stickers
                should be created.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should be placed on faces.
            sticker_type (:obj:`str`, optional): Type of stickers in the set, pass
                :attr:`telegram.Sticker.REGULAR` or :attr:`telegram.Sticker.MASK`. Custom emoji
                sticker sets can't be created via the Bot API at the moment. By default, a
                regular sticker set is created.

                .. versionadded:: 13.14
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id, 'name': name, 'title': title, 'emojis': emojis}

        if png_sticker is not None:
            data['png_sticker'] = parse_file_input(png_sticker)
        if tgs_sticker is not None:
            data['tgs_sticker'] = parse_file_input(tgs_sticker)
        if webm_sticker is not None:
            data['webm_sticker'] = parse_file_input(webm_sticker)
        if contains_masks is not None:
            data['contains_masks'] = contains_masks
        if mask_position is not None:
            # We need to_json() instead of to_dict() here, because we're sending a media
            # message here, which isn't json dumped by utils.request
            data['mask_position'] = mask_position.to_json()
        if sticker_type is not None:
            data['sticker_type'] = sticker_type
        result = self._post('createNewStickerSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def add_sticker_to_set(
        self,
        user_id: Union[str, int],
        name: str,
        emojis: str,
        png_sticker: FileInput = None,
        mask_position: MaskPosition = None,
        timeout: DVInput[float] = DEFAULT_20,
        tgs_sticker: FileInput = None,
        api_kwargs: JSONDict = None,
        webm_sticker: FileInput = None,
    ) -> bool:
        """
        Use this method to add a new sticker to a set created by the bot.
        You **must** use exactly one of the fields ``png_sticker``, ``tgs_sticker`` or
        ``webm_sticker``. Animated stickers can be added to animated sticker sets and only to them.
        Animated sticker sets can have up to 50 stickers. Static sticker sets can have up to 120
        stickers.

        Warning:
            As of API 4.7 ``png_sticker`` is an optional argument and therefore the order of the
            arguments had to be changed. Use keyword arguments to make sure that the arguments are
            passed correctly.

        Note:
            The png_sticker and tgs_sticker argument can be either a file_id, an URL or a file from
            disk ``open(filename, 'rb')``

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.

            name (:obj:`str`): Sticker set name.
            png_sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **PNG** image with the sticker,
                must be up to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px. Pass a file_id as a String to
                send a file that already exists on the Telegram servers, pass an HTTP URL as a
                String for Telegram to get a file from the Internet, or upload a new one
                using multipart/form-data.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            tgs_sticker (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): **TGS** animation with the sticker, uploaded using multipart/form-data.
                See https://core.telegram.org/stickers#animated-sticker-requirements for technical
                requirements.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            webm_sticker (:obj:`str` | filelike object | :obj:`bytes` | :class:`pathlib.Path`,\
                optional): **WEBM** video with the sticker, uploaded using multipart/form-data.
                See https://core.telegram.org/stickers#video-sticker-requirements for
                technical requirements.

                .. versionadded:: 13.11
            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should be placed on faces.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id, 'name': name, 'emojis': emojis}

        if png_sticker is not None:
            data['png_sticker'] = parse_file_input(png_sticker)
        if tgs_sticker is not None:
            data['tgs_sticker'] = parse_file_input(tgs_sticker)
        if webm_sticker is not None:
            data['webm_sticker'] = parse_file_input(webm_sticker)
        if mask_position is not None:
            # We need to_json() instead of to_dict() here, because we're sending a media
            # message here, which isn't json dumped by utils.request
            data['mask_position'] = mask_position.to_json()

        result = self._post('addStickerToSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_sticker_position_in_set(
        self,
        sticker: str,
        position: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to move a sticker in a set created by the bot to a specific position.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            position (:obj:`int`): New sticker position in the set, zero-based.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'sticker': sticker, 'position': position}

        result = self._post(
            'setStickerPositionInSet', data, timeout=timeout, api_kwargs=api_kwargs
        )

        return result  # type: ignore[return-value]

    @log
    def delete_sticker_from_set(
        self,
        sticker: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to delete a sticker from a set created by the bot.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'sticker': sticker}

        result = self._post('deleteStickerFromSet', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_sticker_set_thumb(
        self,
        name: str,
        user_id: Union[str, int],
        thumb: FileInput = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to set the thumbnail of a sticker set. Animated thumbnails can be set
        for animated sticker sets only. Video thumbnails can be set only for video sticker sets
        only.

        Note:
            The thumb can be either a file_id, an URL or a file from disk ``open(filename, 'rb')``

        Args:
            name (:obj:`str`): Sticker set name
            user_id (:obj:`int`): User identifier of created sticker set owner.
            thumb (:obj:`str` | `filelike object` | :obj:`bytes` | :class:`pathlib.Path`, \
                optional): A **PNG** image with the thumbnail, must
                be up to 128 kilobytes in size and have width and height exactly 100px, or a
                **TGS** animation with the thumbnail up to 32 kilobytes in size; see
                https://core.telegram.org/stickers#animated-sticker-requirements for animated
                sticker technical requirements, or a **WEBM** video with the thumbnail up to 32
                kilobytes in size; see
                https://core.telegram.org/stickers#video-sticker-requirements for video sticker
                technical requirements. Pass a file_id as a String to send a file that
                already exists on the Telegram servers, pass an HTTP URL as a String for Telegram
                to get a file from the Internet, or upload a new one using multipart/form-data.
                Animated sticker set thumbnails can't be uploaded via HTTP URL.

                .. versionchanged:: 13.2
                   Accept :obj:`bytes` as input.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'name': name, 'user_id': user_id}

        if thumb is not None:
            data['thumb'] = parse_file_input(thumb)

        result = self._post('setStickerSetThumb', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def set_passport_data_errors(
        self,
        user_id: Union[str, int],
        errors: List[PassportElementError],
        timeout: ODVInput[float] = DEFAULT_NONE,
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
            errors (List[:class:`PassportElementError`]): A JSON-serialized array describing the
                errors.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'user_id': user_id, 'errors': [error.to_dict() for error in errors]}

        result = self._post('setPassportDataErrors', data, timeout=timeout, api_kwargs=api_kwargs)

        return result  # type: ignore[return-value]

    @log
    def send_poll(
        self,
        chat_id: Union[int, str],
        question: str,
        options: List[str],
        is_anonymous: bool = True,
        type: str = Poll.REGULAR,  # pylint: disable=W0622
        allows_multiple_answers: bool = False,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send a native poll.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            question (:obj:`str`): Poll question, 1-300 characters.
            options (List[:obj:`str`]): List of answer options, 2-10 strings 1-100 characters each.
            is_anonymous (:obj:`bool`, optional): :obj:`True`, if the poll needs to be anonymous,
                defaults to :obj:`True`.
            type (:obj:`str`, optional): Poll type, :attr:`telegram.Poll.QUIZ` or
                :attr:`telegram.Poll.REGULAR`, defaults to :attr:`telegram.Poll.REGULAR`.
            allows_multiple_answers (:obj:`bool`, optional): :obj:`True`, if the poll allows
                multiple answers, ignored for polls in quiz mode, defaults to :obj:`False`.
            correct_option_id (:obj:`int`, optional): 0-based identifier of the correct answer
                option, required for polls in quiz mode.
            explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
                answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most
                2 line feeds after entities parsing.
            explanation_parse_mode (:obj:`str`, optional): Mode for parsing entities in the
                explanation. See the constants in :class:`telegram.ParseMode` for the available
                modes.
            explanation_entities (List[:class:`telegram.MessageEntity`], optional): List of special
                entities that appear in message text, which can be specified instead of
                :attr:`parse_mode`.
            open_period (:obj:`int`, optional): Amount of time in seconds the poll will be active
                after creation, 5-600. Can't be used together with :attr:`close_date`.
            close_date (:obj:`int` | :obj:`datetime.datetime`, optional): Point in time (Unix
                timestamp) when the poll will be automatically closed. Must be at least 5 and no
                more than 600 seconds in the future. Can't be used together with
                :attr:`open_period`.
                For timezone naive :obj:`datetime.datetime` objects, the default timezone of the
                bot will be used.
            is_closed (:obj:`bool`, optional): Pass :obj:`True`, if the poll needs to be
                immediately closed. This can be useful for poll preview.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {
            'chat_id': chat_id,
            'question': question,
            'options': options,
            'explanation_parse_mode': explanation_parse_mode,
        }

        if not is_anonymous:
            data['is_anonymous'] = is_anonymous
        if type:
            data['type'] = type
        if allows_multiple_answers:
            data['allows_multiple_answers'] = allows_multiple_answers
        if correct_option_id is not None:
            data['correct_option_id'] = correct_option_id
        if is_closed:
            data['is_closed'] = is_closed
        if explanation:
            data['explanation'] = explanation
        if explanation_entities:
            data['explanation_entities'] = [me.to_dict() for me in explanation_entities]
        if open_period:
            data['open_period'] = open_period
        if close_date:
            if isinstance(close_date, datetime):
                close_date = to_timestamp(
                    close_date, tzinfo=self.defaults.tzinfo if self.defaults else None
                )
            data['close_date'] = close_date

        return self._message(  # type: ignore[return-value]
            'sendPoll',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def stop_poll(
        self,
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: InlineKeyboardMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Poll:
        """
        Use this method to stop a poll which was sent by the bot.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            message_id (:obj:`int`): Identifier of the original message with the poll.
            reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): A JSON-serialized
                object for a new message inline keyboard.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Poll`: On success, the stopped Poll with the final results is
            returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id, 'message_id': message_id}

        if reply_markup:
            if isinstance(reply_markup, ReplyMarkup):
                # We need to_json() instead of to_dict() here, because reply_markups may be
                # attached to media messages, which aren't json dumped by utils.request
                data['reply_markup'] = reply_markup.to_json()
            else:
                data['reply_markup'] = reply_markup

        result = self._post('stopPoll', data, timeout=timeout, api_kwargs=api_kwargs)

        return Poll.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def send_dice(
        self,
        chat_id: Union[int, str],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        emoji: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> Message:
        """
        Use this method to send an animated emoji that will display a random value.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            emoji (:obj:`str`, optional): Emoji on which the dice throw animation is based.
                Currently, must be one of “🎲”, “🎯”, “🏀”, “⚽”, "🎳", or “🎰”. Dice can have
                values 1-6 for “🎲”, “🎯” and "🎳", values 1-5 for “🏀” and “⚽”, and values 1-64
                for “🎰”. Defaults to “🎲”.

                .. versionchanged:: 13.4
                   Added the "🎳" emoji.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
           message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {'chat_id': chat_id}

        if emoji:
            data['emoji'] = emoji

        return self._message(  # type: ignore[return-value]
            'sendDice',
            data,
            timeout=timeout,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    @log
    def get_my_default_administrator_rights(
        self,
        for_channels: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ChatAdministratorRights:
        """Use this method to get the current default administrator rights of the bot.

        .. seealso:: :meth:`set_my_default_administrator_rights`

        .. versionadded:: 13.12

        Args:
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to get default administrator
                rights of the bot in channels. Otherwise, default administrator rights of the bot
                for groups and supergroups will be returned.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ChatAdministratorRights`: On success.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if for_channels is not None:
            data['for_channels'] = for_channels

        result = self._post(
            'getMyDefaultAdministratorRights',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

        return ChatAdministratorRights.de_json(result, self)  # type: ignore[return-value,arg-type]

    @log
    def set_my_default_administrator_rights(
        self,
        rights: ChatAdministratorRights = None,
        for_channels: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to change the default administrator rights requested by the bot when
        it's added as an administrator to groups or channels. These rights will be suggested to
        users, but they are are free to modify the list before adding the bot.

        .. seealso:: :meth:`get_my_default_administrator_rights`

        .. versionadded:: 13.12

        Args:
            rights (:obj:`telegram.ChatAdministratorRights`, optional): A
                :obj:`telegram.ChatAdministratorRights` object describing new default administrator
                rights. If not specified, the default administrator rights will be cleared.
            for_channels (:obj:`bool`, optional): Pass :obj:`True` to change the default
                administrator rights of the bot in channels. Otherwise, the default administrator
                rights of the bot for groups and supergroups will be changed.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: Returns :obj:`True` on success.

        Raises:
            :obj:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if rights is not None:
            data['rights'] = rights.to_dict()

        if for_channels is not None:
            data['for_channels'] = for_channels

        result = self._post(
            'setMyDefaultAdministratorRights',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

        return result  # type: ignore[return-value]

    @log
    def get_my_commands(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        scope: BotCommandScope = None,
        language_code: str = None,
    ) -> List[BotCommand]:
        """
        Use this method to get the current list of the bot's commands for the given scope and user
        language.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
            scope (:class:`telegram.BotCommandScope`, optional): A JSON-serialized object,
                describing scope of users. Defaults to :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code or an empty
                string.

                .. versionadded:: 13.7

        Returns:
            List[:class:`telegram.BotCommand`]: On success, the commands set for the bot. An empty
            list is returned if commands are not set.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        data: JSONDict = {}

        if scope:
            data['scope'] = scope.to_dict()

        if language_code:
            data['language_code'] = language_code

        result = self._post('getMyCommands', data, timeout=timeout, api_kwargs=api_kwargs)

        if (scope is None or scope.type == scope.DEFAULT) and language_code is None:
            self._commands = BotCommand.de_list(result, self)  # type: ignore[assignment,arg-type]
            return self._commands  # type: ignore[return-value]

        return BotCommand.de_list(result, self)  # type: ignore[return-value,arg-type]

    @log
    def set_my_commands(
        self,
        commands: List[Union[BotCommand, Tuple[str, str]]],
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        scope: BotCommandScope = None,
        language_code: str = None,
    ) -> bool:
        """
        Use this method to change the list of the bot's commands. See the
        `Telegram docs <https://core.telegram.org/bots#commands>`_ for more details about bot
        commands.

        Args:
            commands (List[:class:`BotCommand` | (:obj:`str`, :obj:`str`)]): A JSON-serialized list
                of bot commands to be set as the list of the bot's commands. At most 100 commands
                can be specified.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.
            scope (:class:`telegram.BotCommandScope`, optional): A JSON-serialized object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.

                .. versionadded:: 13.7

            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.

                .. versionadded:: 13.7

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`

        """
        cmds = [c if isinstance(c, BotCommand) else BotCommand(c[0], c[1]) for c in commands]

        data: JSONDict = {'commands': [c.to_dict() for c in cmds]}

        if scope:
            data['scope'] = scope.to_dict()

        if language_code:
            data['language_code'] = language_code

        result = self._post('setMyCommands', data, timeout=timeout, api_kwargs=api_kwargs)

        # Set commands only for default scope. No need to check for outcome.
        # If request failed, we won't come this far
        if (scope is None or scope.type == scope.DEFAULT) and language_code is None:
            self._commands = cmds

        return result  # type: ignore[return-value]

    @log
    def delete_my_commands(
        self,
        scope: BotCommandScope = None,
        language_code: str = None,
        api_kwargs: JSONDict = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> bool:
        """
        Use this method to delete the list of the bot's commands for the given scope and user
        language. After deletion,
        `higher level commands <https://core.telegram.org/bots/api#determining-list-of-commands>`_
        will be shown to affected users.

        .. versionadded:: 13.7

        Args:
            scope (:class:`telegram.BotCommandScope`, optional): A JSON-serialized object,
                describing scope of users for which the commands are relevant. Defaults to
                :class:`telegram.BotCommandScopeDefault`.
            language_code (:obj:`str`, optional): A two-letter ISO 639-1 language code. If empty,
                commands will be applied to all users from the given scope, for whose language
                there are no dedicated commands.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {}

        if scope:
            data['scope'] = scope.to_dict()

        if language_code:
            data['language_code'] = language_code

        result = self._post('deleteMyCommands', data, timeout=timeout, api_kwargs=api_kwargs)

        if (scope is None or scope.type == scope.DEFAULT) and language_code is None:
            self._commands = []

        return result  # type: ignore[return-value]

    @log
    def log_out(self, timeout: ODVInput[float] = DEFAULT_NONE) -> bool:
        """
        Use this method to log out from the cloud Bot API server before launching the bot locally.
        You *must* log out the bot before running it locally, otherwise there is no guarantee that
        the bot will receive updates. After a successful call, you can immediately log in on a
        local server, but will not be able to log in back to the cloud Bot API server for 10
        minutes.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return self._post('logOut', timeout=timeout)  # type: ignore[return-value]

    @log
    def close(self, timeout: ODVInput[float] = DEFAULT_NONE) -> bool:
        """
        Use this method to close the bot instance before moving it from one local server to
        another. You need to delete the webhook before calling this method to ensure that the bot
        isn't launched again after server restart. The method will return error 429 in the first
        10 minutes after the bot is launched.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
            :obj:`True`: On success

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return self._post('close', timeout=timeout)  # type: ignore[return-value]

    @log
    def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: ReplyMarkup = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        protect_content: bool = None,
        message_thread_id: int = None,
    ) -> MessageId:
        """
        Use this method to copy messages of any kind. Service messages and invoice messages can't
        be copied. The method is analogous to the method :meth:`forward_message`, but the copied
        message doesn't have a link to the original message.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format ``@channelusername``).
            message_id (:obj:`int`): Message identifier in the chat specified in from_chat_id.
            caption (:obj:`str`, optional): New caption for media, 0-1024 characters after
                entities parsing. If not specified, the original caption is kept.
            parse_mode (:obj:`str`, optional): Mode for parsing entities in the new caption. See
                the constants in :class:`telegram.ParseMode` for the available modes.
            caption_entities (:class:`telegram.utils.types.SLT[MessageEntity]`): List of special
                entities that appear in the new caption, which can be specified instead of
                parse_mode
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            protect_content (:obj:`bool`, optional): Protects the contents of the sent message from
                forwarding and saving.

                .. versionadded:: 13.10
            message_thread_id (:obj:`int`, optional): |message_thread_id_arg|

                .. versionadded:: 13.15

            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            allow_sending_without_reply (:obj:`bool`, optional): Pass :obj:`True`, if the message
                should be sent even if the specified replied-to message is not found.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options.
                A JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.MessageId`: On success

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification,
            'allow_sending_without_reply': allow_sending_without_reply,
        }
        if caption is not None:
            data['caption'] = caption
        if caption_entities:
            data['caption_entities'] = caption_entities
        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id
        if protect_content:
            data['protect_content'] = protect_content
        if reply_markup:
            if isinstance(reply_markup, ReplyMarkup):
                # We need to_json() instead of to_dict() here, because reply_markups may be
                # attached to media messages, which aren't json dumped by utils.request
                data['reply_markup'] = reply_markup.to_json()
            else:
                data['reply_markup'] = reply_markup
        if message_thread_id:
            data["message_thread_id"] = message_thread_id

        result = self._post('copyMessage', data, timeout=timeout, api_kwargs=api_kwargs)
        return MessageId.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def set_chat_menu_button(
        self,
        chat_id: int = None,
        menu_button: MenuButton = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Use this method to change the bot's menu button in a private chat, or the default menu
        button.

        .. seealso:: :meth:`get_chat_menu_button`, :meth:`telegram.Chat.set_menu_button`,
            :meth:`telegram.User.set_menu_button`

        .. versionadded:: 13.12

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be changed
            menu_button (:class:`telegram.MenuButton`, optional): An object for the new bot's menu
                button. Defaults to :class:`telegram.MenuButtonDefault`.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        data: JSONDict = {}
        if chat_id is not None:
            data['chat_id'] = chat_id
        if menu_button is not None:
            data['menu_button'] = menu_button.to_dict()

        return self._post(  # type: ignore[return-value]
            'setChatMenuButton',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def get_chat_menu_button(
        self,
        chat_id: int = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> MenuButton:
        """Use this method to get the current value of the bot's menu button in a private chat, or
        the default menu button.

        .. seealso:: :meth:`set_chat_menu_button`, :meth:`telegram.Chat.get_menu_button`,
            :meth:`telegram.User.get_menu_button`

        .. versionadded:: 13.12

        Args:
            chat_id (:obj:`int`, optional): Unique identifier for the target private chat. If not
                specified, default bot's menu button will be returned.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.MenuButton`: On success, the current menu button is returned.
        """
        data = {}
        if chat_id is not None:
            data['chat_id'] = chat_id

        result = self._post(
            'getChatMenuButton',
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
        return MenuButton.de_json(result, bot=self)  # type: ignore[return-value, arg-type]

    @log
    def create_invoice_link(
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
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> str:
        """Use this method to create a link for an invoice.

        .. versionadded:: 13.13

        Args:
            title (:obj:`str`): Product name. 1-32 characters.
            description (:obj:`str`): Product description. 1-255 characters.
            payload (:obj:`str`): Bot-defined invoice payload. 1-128 bytes. This will not be
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
                ``max_tip_amount``.
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
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
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
            "prices": [p.to_dict() for p in prices],
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

        return self._post(  # type: ignore[return-value]
            "createInvoiceLink",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def get_forum_topic_icon_stickers(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> List[Sticker]:
        """Use this method to get custom emoji stickers, which can be used as a forum topic
         icon by any user. Requires no parameters.

        .. versionadded:: 13.15

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            List[:class:`telegram.Sticker`]

        Raises:
            :class:`telegram.error.TelegramError`
        """
        result = self._post(
            "getForumTopicIconStickers",
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
        return Sticker.de_list(result, self)  # type: ignore[return-value, arg-type]

    @log
    def create_forum_topic(
        self,
        chat_id: Union[str, int],
        name: str,
        icon_color: int = None,
        icon_custom_emoji_id: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> ForumTopic:
        """
        Use this method to create a topic in a forum supergroup chat. The bot must be
        an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights.

        .. seealso:: :meth:`telegram.Chat.create_forum_topic`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            name (:obj:`str`): New topic name, 1-128 characters.
            icon_color (:obj:`int`, optional): Color of the topic icon in RGB format. Currently,
                must be one of 7322096 (0x6FB9F0), 16766590 (0xFFD67E), 13338331 (0xCB86DB),
                9367192 (0x8EEE98), 16749490 (0xFF93B2), or 16478047 (0xFB6F5F)
            icon_custom_emoji_id (:obj:`str`, optional): New unique identifier of the custom emoji
                shown as the topic icon. Use :meth:`~telegram.Bot.get_forum_topic_icon_stickers`
                to get all allowed custom emoji identifiers.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :class:`telegram.ForumTopic`

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "name": name,
        }

        if icon_color is not None:
            data["icon_color"] = icon_color

        if icon_custom_emoji_id is not None:
            data["icon_custom_emoji_id"] = icon_custom_emoji_id

        result = self._post(
            "createForumTopic",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
        return ForumTopic.de_json(result, self)  # type: ignore[return-value, arg-type]

    @log
    def edit_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        name: str,
        icon_custom_emoji_id: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to edit name and icon of a topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. seealso:: :meth:`telegram.Message.edit_forum_topic`,
            :meth:`telegram.Chat.edit_forum_topic`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

                .. versionadded:: 13.15
            name (:obj:`str`): New topic name, 1-128 characters.
            icon_custom_emoji_id (:obj:`str`): New unique identifier of the custom emoji shown as
                the topic icon. Use :meth:`~telegram.Bot.get_forum_topic_icon_stickers` to get all
                allowed custom emoji identifiers.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
            "name": name,
            "icon_custom_emoji_id": icon_custom_emoji_id,
        }
        return self._post(  # type: ignore[return-value]
            "editForumTopic",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def close_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to close an open topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :attr:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. seealso:: :meth:`telegram.Message.close_forum_topic`,
            :meth:`telegram.Chat.close_forum_topic`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

                .. versionadded:: 13.15
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return self._post(  # type: ignore[return-value]
            "closeForumTopic",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def reopen_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to reopen a closed topic in a forum supergroup chat. The bot must
        be an administrator in the chat for this to work and must have
        :meth:`~telegram.ChatAdministratorRights.can_manage_topics` administrator rights,
        unless it is the creator of the topic.

        .. seealso:: :meth:`telegram.Message.reopen_forum_topic`,
            :meth:`telegram.Chat.reopen_forum_topic`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

                .. versionadded:: 13.15
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return self._post(  # type: ignore[return-value]
            "reopenForumTopic",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def delete_forum_topic(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to delete a forum topic along with all its messages in a forum supergroup
        chat. The bot must be an administrator in the chat for this to work and must have
        :meth:`~telegram.ChatAdministratorRights.can_delete_messages` administrator rights.

        .. seealso:: :meth:`telegram.Message.delete_forum_topic`,
            :meth:`telegram.Chat.delete_forum_topic`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

                .. versionadded:: 13.15
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return self._post(  # type: ignore[return-value]
            "deleteForumTopic",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    @log
    def unpin_all_forum_topic_messages(
        self,
        chat_id: Union[str, int],
        message_thread_id: int,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """
        Use this method to clear the list of pinned messages in a forum topic. The bot must
        be an administrator in the chat for this to work and must have
        :meth:`~telegram.ChatAdministratorRights.can_pin_messages` administrator rights
        in the supergroup.

        .. seealso:: :meth:`telegram.Message.unpin_all_forum_topic_messages`,
            :meth:`telegram.Chat.unpin_all_forum_topic_messages`,

        .. versionadded:: 13.15

        Args:
            chat_id (:obj:`int` | :obj:`str`): |chat_id_group|
            message_thread_id (:obj:`int`): |message_thread_id|

                .. versionadded:: 13.15
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Telegram API.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        Raises:
            :class:`telegram.error.TelegramError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id,
        }
        return self._post(  # type: ignore[return-value]
            "unpinAllForumTopicMessages",
            data,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data: JSONDict = {'id': self.id, 'username': self.username, 'first_name': self.first_name}

        if self.last_name:
            data['last_name'] = self.last_name

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
    kickChatMember = kick_chat_member
    """Alias for :meth:`kick_chat_member`"""
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
    getChatMembersCount = get_chat_members_count
    """Alias for :meth:`get_chat_members_count`"""
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
    getStickerSet = get_sticker_set
    """Alias for :meth:`get_sticker_set`"""
    getCustomEmojiStickers = get_custom_emoji_stickers
    """Alias for :meth:`get_custom_emoji_stickers`"""
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
    getForumTopicIconStickers = get_forum_topic_icon_stickers
    """Alias for :meth:`get_forum_topic_icon_stickers`"""
    createForumTopic = create_forum_topic
    """Alias for :meth:`create_forum_topic`"""
    editForumTopic = edit_forum_topic
    """Alias for :meth:`edit_forum_topic`"""
    closeForumTopic = close_forum_topic
    """Alias for :meth:`close_forum_topic`"""
    reopenForumTopic = reopen_forum_topic
    """Alias for :meth:`reopen_forum_topic`"""
    deleteForumTopic = delete_forum_topic
    """Alias for :meth:`delete_forum_topic`"""
    unpinAllForumTopicMessages = unpin_all_forum_topic_messages
    """Alias for :meth:`unpin_all_forum_topic_messages`"""
