# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
# by the python-telegram-bot contributors <devs@python-telegram-bot.org>
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
"""This module contains several constants that are relevant for working with the Bot API.

Unless noted otherwise, all constants in this module were extracted from the
`Telegram Bots FAQ <https://core.telegram.org/bots/faq>`_ and
`Telegram Bots API <https://core.telegram.org/bots/api>`_.

Attributes:
    BOT_API_VERSION (:obj:`str`): `5.3`. Telegram Bot API version supported by this
        version of `python-telegram-bot`. Also available as ``telegram.bot_api_version``.

        .. versionadded:: 13.4
    SUPPORTED_WEBHOOK_PORTS (List[:obj:`int`]): [443, 80, 88, 8443]
    MAX_INLINE_QUERY_RESULTS (:obj:`int`): 50
    MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH (:obj:`int`): 200

        .. versionadded:: 13.2

The following constant have been found by experimentation:

Attributes:
    ANONYMOUS_ADMIN_ID (:obj:`int`): ``1087968824`` (User id in groups for anonymous admin)
    SERVICE_CHAT_ID (:obj:`int`): ``777000`` (Telegram service chat, that also acts as sender of
        channel posts forwarded to discussion groups)

The following constants are related to specific classes or topics and are grouped into enums. If
they are related to a specific class, then they are also available as attributes of those classes.
"""
from enum import Enum, IntEnum
from typing import List


__all__ = [
    'ANONYMOUS_ADMIN_ID',
    'BOT_API_VERSION',
    'BotCommandScopeType',
    'ChatAction',
    'ChatMemberStatus',
    'ChatType',
    'DiceEmoji',
    'FileSizeLimit',
    'FloodLimit',
    'InlineKeyboardMarkupLimit',
    'MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH',
    'MAX_INLINE_QUERY_RESULTS',
    'MaskPosition',
    'MessageEntityType',
    'MessageLimit',
    'ParseMode',
    'PollLimit',
    'PollType',
    'SERVICE_CHAT_ID',
    'SUPPORTED_WEBHOOK_PORTS',
    'UpdateType',
]


class _StringEnum(str, Enum):
    """Helper class for string enums where the value is not important to be displayed on
    stringification.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}.{self.name}>'


BOT_API_VERSION = '5.3'
ANONYMOUS_ADMIN_ID = 1087968824
SERVICE_CHAT_ID = 777000

# constants above this line are tested

SUPPORTED_WEBHOOK_PORTS: List[int] = [443, 80, 88, 8443]
MAX_INLINE_QUERY_RESULTS = 50
MAX_ANSWER_CALLBACK_QUERY_TEXT_LENGTH = 200


class BotCommandScopeType(_StringEnum):
    """This enum contains the available types of :class:`telegram.BotCommandScope`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    DEFAULT = 'default'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeDefault`."""
    ALL_PRIVATE_CHATS = 'all_private_chats'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllPrivateChats`."""
    ALL_GROUP_CHATS = 'all_group_chats'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllGroupChats`."""
    ALL_CHAT_ADMINISTRATORS = 'all_chat_administrators'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllChatAdministrators`."""
    CHAT = 'chat'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChat`."""
    CHAT_ADMINISTRATORS = 'chat_administrators'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChatAdministrators`."""
    CHAT_MEMBER = 'chat_member'
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChatMember`."""


class ChatAction(_StringEnum):
    """This enum contains the available chat actions for :method:`telegram.Bot.send_chat_action`.
    The enum members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    FIND_LOCATION = 'find_location'
    """:obj:`str`: A chat indicating the bot is selecting a location."""
    RECORD_VOICE = 'record_voice'
    """:obj:`str`: A chat indicating the bot is recording a voice message."""
    RECORD_VIDEO = 'record_video'
    """:obj:`str`: A chat indicating the bot is recording a video."""
    RECORD_VIDEO_NOTE = 'record_video_note'
    """:obj:`str`: A chat indicating the bot is recording a video note."""
    TYPING = 'typing'
    """:obj:`str`: A chat indicating the bot is typing."""
    UPLOAD_VOICE = 'upload_voice'
    """:obj:`str`: A chat indicating the bot is uploading a voice message."""
    UPLOAD_DOCUMENT = 'upload_document'
    """:obj:`str`: A chat indicating the bot is uploading a document."""
    UPLOAD_PHOTO = 'upload_photo'
    """:obj:`str`: A chat indicating the bot is uploading a photo."""
    UPLOAD_VIDEO = 'upload_video'
    """:obj:`str`: A chat indicating the bot is uploading a video."""
    UPLOAD_VIDEO_NOTE = 'upload_video_note'
    """:obj:`str`: A chat indicating the bot is uploading a video note."""


class ChatMemberStatus(_StringEnum):
    """This enum contains the available states for :class:`telegram.ChatMember`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    ADMINISTRATOR = 'administrator'
    """:obj:`str`: A :class:`telegram.ChatMember` who is administrator of the chat."""
    CREATOR = 'creator'
    """:obj:`str`: A :class:`telegram.ChatMember` who is the creator of the chat."""
    KICKED = 'kicked'
    """:obj:`str`: A :class:`telegram.ChatMember` who was kicked from the chat."""
    LEFT = 'left'
    """:obj:`str`: A :class:`telegram.ChatMember` who has left the chat."""
    MEMBER = 'member'
    """:obj:`str`: A :class:`telegram.ChatMember` who is a member of the chat."""
    RESTRICTED = 'restricted'
    """:obj:`str`: A :class:`telegram.ChatMember` who was restricted in this chat."""


class ChatType(_StringEnum):
    """This enum contains the available types of :class:`telegram.Chat`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    SENDER = 'sender'
    """:obj:`str`: A :class:`telegram.Chat` that represents the chat of a :class:`telegram.User`
    sending an :class:`telegram.InlineQuery`. """
    PRIVATE = 'private'
    """:obj:`str`: A :class:`telegram.Chat` that is private."""
    GROUP = 'group'
    """:obj:`str`: A :class:`telegram.Chat` that is a group."""
    SUPERGROUP = 'supergroup'
    """:obj:`str`: A :class:`telegram.Chat` that is a supergroup."""
    CHANNEL = 'channel'
    """:obj:`str`: A :class:`telegram.Chat` that is a channel."""


class DiceEmoji(_StringEnum):
    """This enum contains the available emoji for :class:`telegram.Dice`/
    :meth:`telegram.Bot.send_dice`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    DICE = '🎲'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎲``."""
    DARTS = '🎯'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎯``."""
    BASKETBALL = '🏀'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🏀``."""
    FOOTBALL = '⚽'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``⚽``."""
    SLOT_MACHINE = '🎰'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎰``."""
    BOWLING = '🎳'
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎳``."""


class FileSizeLimit(IntEnum):
    """This enum contains limitations regarding the upload and download of files. The enum
    members of this enumerations are instances of :class:`int` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    FILESIZE_DOWNLOAD = int(20e6)  # (20MB)
    """:obj:`int`: Bots can download files of up to 20MB in size."""
    FILESIZE_UPLOAD = int(50e6)  # (50MB)
    """:obj:`int`: Bots can upload non-photo files of up to 50MB in size."""
    PHOTOSIZE_UPLOAD = int(10e6)  # (10MB)
    """:obj:`int`: Bots can upload photo files of up to 10MB in size."""


class FloodLimit(IntEnum):
    """This enum contains limitations regarding flood limits. The enum
    members of this enumerations are instances of :class:`int` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    MESSAGES_PER_SECOND_PER_CHAT = 1
    """:obj:`int`: The number of messages that can be send per second in a particular chat.
    Telegram may allow short bursts that go over this limit, but eventually you'll begin
    receiving 429 errors.
    """
    MESSAGES_PER_SECOND = 30
    """:obj:`int`: The number of messages that can roughly be send in an interval of 30 seconds
    across all chats.
    """
    MESSAGES_PER_MINUTE_PER_GROUP = 20
    """:obj:`int`: The number of messages that can roughly be send to a particluar group within one
    minute.
    """


class InlineKeyboardMarkupLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineKeyboardMarkup`/
    :meth:`telegram.Bot.send_message` & friends. The enum
    members of this enumerations are instances of :class:`int` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    TOTAL_BUTTON_NUMBER = 100
    """:obj:`int`: Maximum number of buttons that can be attached to a message.

    Note:
        This value is undocumented and might be changed by Telegram.
    """
    BUTTONS_PER_ROW = 8
    """:obj:`int`: Maximum number of buttons that can be attached to a message per row.

    Note:
        This value is undocumented and might be changed by Telegram.
    """


class MaskPosition(_StringEnum):
    """This enum contains the available positions for :class:`telegram.MasPosition`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    FOREHEAD = 'forehead'
    """:obj:`str`: Mask position for a sticker on the forehead."""
    EYES = 'eyes'
    """:obj:`str`: Mask position for a sticker on the eyes."""
    MOUTH = 'mouth'
    """:obj:`str`: Mask position for a sticker on the mouth."""
    CHIN = 'chin'
    """:obj:`str`: Mask position for a sticker on the chin."""


class MessageEntityType(_StringEnum):
    """This enum contains the available types of :class:`telegram.MessageEntity`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    MENTION = 'mention'
    """:obj:`str`: Message entities representing a mention."""
    HASHTAG = 'hashtag'
    """:obj:`str`: Message entities representing a hashtag."""
    CASHTAG = 'cashtag'
    """:obj:`str`: Message entities representing a cashtag."""
    PHONE_NUMBER = 'phone_number'
    """:obj:`str`: Message entities representing a phone number."""
    BOT_COMMAND = 'bot_command'
    """:obj:`str`: Message entities representing a bot command."""
    URL = 'url'
    """:obj:`str`: Message entities representing a url."""
    EMAIL = 'email'
    """:obj:`str`: Message entities representing a email."""
    BOLD = 'bold'
    """:obj:`str`: Message entities representing bold text."""
    ITALIC = 'italic'
    """:obj:`str`: Message entities representing italic text."""
    CODE = 'code'
    """:obj:`str`: Message entities representing monowidth string."""
    PRE = 'pre'
    """:obj:`str`: Message entities representing monowidth block."""
    TEXT_LINK = 'text_link'
    """:obj:`str`: Message entities representing clickable text URLs."""
    TEXT_MENTION = 'text_mention'
    """:obj:`str`: Message entities representing text mention for users without usernames."""
    UNDERLINE = 'underline'
    """:obj:`str`: Message entities representing underline text."""
    STRIKETHROUGH = 'strikethrough'
    """:obj:`str`: Message entities representing strikethrough text."""


class MessageLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.Message`/
    :meth:`telegram.Bot.send_message` & friends. The enum
    members of this enumerations are instances of :class:`int` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    TEXT_LENGTH = 4096
    """:obj:`int`: Maximum number of characters for a text message."""
    CAPTION_LENGTH = 1024
    """:obj:`int`: Maximum number of characters for a message caption."""
    # constants above this line are tested
    MESSAGE_ENTITIES = 100
    """:obj:`int`: Maximum number of entities that can be displayed in a message. Further entities
    will simply be ignored by Telegram.

    Note:
        This value is undocumented and might be changed by Telegram.
    """


class ParseMode(_StringEnum):
    """This enum contains the available parse modes. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    MARKDOWN = 'Markdown'
    """:obj:`str`: Markdown parse mode.

    Note:
        :attr:`MARKDOWN` is a legacy mode, retained by Telegram for backward compatibility.
        You should use :attr:`MARKDOWN_V2` instead.
    """
    MARKDOWN_V2 = 'MarkdownV2'
    """:obj:`str`: Markdown parse mode version 2."""
    HTML = 'HTML'
    """:obj:`str`: HTML parse mode."""


class PollLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.Poll`/
    :meth:`telegram.Bot.send_poll`. The enum
    members of this enumerations are instances of :class:`int` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    QUESTION_LENGTH = 300
    """:obj:`str`: Maximum number of characters of the polls question."""
    OPTION_LENGTH = 100
    """:obj:`str`: Maximum number of available options for the poll."""


class PollType(_StringEnum):
    """This enum contains the available types for :class:`telegram.Poll`/
    :meth:`telegram.Bot.send_poll`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    REGULAR = 'regular'
    """:obj:`str`: regular polls."""
    QUIZ = 'quiz'
    """:obj:`str`: quiz polls."""


class UpdateType(_StringEnum):
    """This enum contains the available types of :class:`telegram.Update`. The enum
    members of this enumerations are instances of :class:`str` and can be treated as such.

    .. versionadded:: 14.0
    """

    __slots__ = ()

    MESSAGE = 'message'
    """:obj:`str`: Updates with :attr:`telegram.Update.message`."""
    EDITED_MESSAGE = 'edited_message'
    """:obj:`str`: Updates with :attr:`telegram.Update.edited_message`."""
    CHANNEL_POST = 'channel_post'
    """:obj:`str`: Updates with :attr:`telegram.Update.channel_post`."""
    EDITED_CHANNEL_POST = 'edited_channel_post'
    """:obj:`str`: Updates with :attr:`telegram.Update.edited_channel_post`."""
    INLINE_QUERY = 'inline_query'
    """:obj:`str`: Updates with :attr:`telegram.Update.inline_query`."""
    CHOSEN_INLINE_RESULT = 'chosen_inline_result'
    """:obj:`str`: Updates with :attr:`telegram.Update.chosen_inline_result`."""
    CALLBACK_QUERY = 'callback_query'
    """:obj:`str`: Updates with :attr:`telegram.Update.callback_query`."""
    SHIPPING_QUERY = 'shipping_query'
    """:obj:`str`: Updates with :attr:`telegram.Update.shipping_query`."""
    PRE_CHECKOUT_QUERY = 'pre_checkout_query'
    """:obj:`str`: Updates with :attr:`telegram.Update.pre_checkout_query`."""
    POLL = 'poll'
    """:obj:`str`: Updates with :attr:`telegram.Update.poll`."""
    POLL_ANSWER = 'poll_answer'
    """:obj:`str`: Updates with :attr:`telegram.Update.poll_answer`."""
    MY_CHAT_MEMBER = 'my_chat_member'
    """:obj:`str`: Updates with :attr:`telegram.Update.my_chat_member`."""
    CHAT_MEMBER = 'chat_member'
    """:obj:`str`: Updates with :attr:`telegram.Update.chat_member`."""
