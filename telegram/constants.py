# python-telegram-bot - a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

Most of the following constants are related to specific classes or topics and are grouped into
enums. If they are related to a specific class, then they are also available as attributes of
those classes.

.. versionchanged:: 20.0

    * Most of the constants in this module are grouped into enums.
"""
# TODO: Remove this when https://github.com/PyCQA/pylint/issues/6887 is resolved.
# pylint: disable=invalid-enum-extension

__all__ = [
    "BOT_API_VERSION",
    "BOT_API_VERSION_INFO",
    "BotCommandLimit",
    "BotCommandScopeType",
    "CallbackQueryLimit",
    "ChatAction",
    "ChatID",
    "ChatInviteLinkLimit",
    "ChatLimit",
    "ChatMemberStatus",
    "ChatPhotoSize",
    "ChatType",
    "ContactLimit",
    "CustomEmojiStickerLimit",
    "DiceEmoji",
    "DiceLimit",
    "FileSizeLimit",
    "FloodLimit",
    "ForumIconColor",
    "ForumTopicLimit",
    "InlineKeyboardButtonLimit",
    "InlineKeyboardMarkupLimit",
    "InlineQueryLimit",
    "InlineQueryResultLimit",
    "InlineQueryResultType",
    "InputMediaType",
    "InvoiceLimit",
    "LocationLimit",
    "MaskPosition",
    "MediaGroupLimit",
    "MenuButtonType",
    "MessageAttachmentType",
    "MessageEntityType",
    "MessageLimit",
    "MessageType",
    "PollingLimit",
    "ParseMode",
    "PollLimit",
    "PollType",
    "ReplyLimit",
    "SUPPORTED_WEBHOOK_PORTS",
    "StickerLimit",
    "StickerType",
    "WebhookLimit",
    "UpdateType",
    "UserProfilePhotosLimit",
]

import sys
from typing import List, NamedTuple

from telegram._utils.enum import IntEnum, StringEnum


class _BotAPIVersion(NamedTuple):
    """Similar behavior to sys.version_info.
    So far TG has only published X.Y releases. We can add X.Y.Z(a(S)) if needed.
    """

    major: int
    minor: int

    def __repr__(self) -> str:
        """Unfortunately calling super().__repr__ doesn't work with typing.NamedTuple, so we
        do this manually.
        """
        return f"BotAPIVersion(major={self.major}, minor={self.minor})"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


#: :class:`typing.NamedTuple`: A tuple containing the two components of the version number:
# ``major`` and ``minor``. Both values are integers.
#: The components can also be accessed by name, so ``BOT_API_VERSION_INFO[0]`` is equivalent
#: to ``BOT_API_VERSION_INFO.major`` and so on. Also available as
#: :data:`telegram.__bot_api_version_info__`.
#:
#: .. versionadded:: 20.0
BOT_API_VERSION_INFO = _BotAPIVersion(major=6, minor=4)
#: :obj:`str`: Telegram Bot API
#: version supported by this version of `python-telegram-bot`. Also available as
#: :data:`telegram.__bot_api_version__`.
#:
#: .. versionadded:: 13.4
BOT_API_VERSION = str(BOT_API_VERSION_INFO)

# constants above this line are tested

#: List[:obj:`int`]: Ports supported by
#:  :paramref:`telegram.Bot.set_webhook.url`.
SUPPORTED_WEBHOOK_PORTS: List[int] = [443, 80, 88, 8443]


class BotCommandLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.BotCommand` and
    :meth:`telegram.Bot.set_my_commands`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_COMMAND = 1
    """:obj:`int`: Minimum value allowed for :paramref:`~telegram.BotCommand.command` parameter of
    :class:`telegram.BotCommand`.
    """
    MAX_COMMAND = 32
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.BotCommand.command` parameter of
    :class:`telegram.BotCommand`.
    """
    MIN_DESCRIPTION = 1
    """:obj:`int`: Minimum value allowed for :paramref:`~telegram.BotCommand.description`
    parameter of :class:`telegram.BotCommand`.
    """
    MAX_DESCRIPTION = 256
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.BotCommand.description`
    parameter of :class:`telegram.BotCommand`.
    """
    MAX_COMMAND_NUMBER = 100
    """:obj:`int`: Maximum number of bot commands passed in a :obj:`list` to the
    :paramref:`~telegram.Bot.set_my_commands.commands`
    parameter of :meth:`telegram.Bot.set_my_commands`.
    """


class BotCommandScopeType(StringEnum):
    """This enum contains the available types of :class:`telegram.BotCommandScope`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    DEFAULT = "default"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeDefault`."""
    ALL_PRIVATE_CHATS = "all_private_chats"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllPrivateChats`."""
    ALL_GROUP_CHATS = "all_group_chats"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllGroupChats`."""
    ALL_CHAT_ADMINISTRATORS = "all_chat_administrators"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeAllChatAdministrators`."""
    CHAT = "chat"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChat`."""
    CHAT_ADMINISTRATORS = "chat_administrators"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChatAdministrators`."""
    CHAT_MEMBER = "chat_member"
    """:obj:`str`: The type of :class:`telegram.BotCommandScopeChatMember`."""


class CallbackQueryLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.CallbackQuery`/
    :meth:`telegram.Bot.answer_callback_query`. The enum members of this enumeration are instances
    of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    ANSWER_CALLBACK_QUERY_TEXT_LENGTH = 200
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.answer_callback_query.text` parameter of
    :meth:`telegram.Bot.answer_callback_query`."""


class ChatAction(StringEnum):
    """This enum contains the available chat actions for :meth:`telegram.Bot.send_chat_action`.
    The enum members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    CHOOSE_STICKER = "choose_sticker"
    """:obj:`str`: Chat action indicating that the bot is selecting a sticker."""
    FIND_LOCATION = "find_location"
    """:obj:`str`: Chat action indicating that the bot is selecting a location."""
    RECORD_VOICE = "record_voice"
    """:obj:`str`: Chat action indicating that the bot is recording a voice message."""
    RECORD_VIDEO = "record_video"
    """:obj:`str`: Chat action indicating that the bot is recording a video."""
    RECORD_VIDEO_NOTE = "record_video_note"
    """:obj:`str`: Chat action indicating that the bot is recording a video note."""
    TYPING = "typing"
    """:obj:`str`: A chat indicating the bot is typing."""
    UPLOAD_VOICE = "upload_voice"
    """:obj:`str`: Chat action indicating that the bot is uploading a voice message."""
    UPLOAD_DOCUMENT = "upload_document"
    """:obj:`str`: Chat action indicating that the bot is uploading a document."""
    UPLOAD_PHOTO = "upload_photo"
    """:obj:`str`: Chat action indicating that the bot is uploading a photo."""
    UPLOAD_VIDEO = "upload_video"
    """:obj:`str`: Chat action indicating that the bot is uploading a video."""
    UPLOAD_VIDEO_NOTE = "upload_video_note"
    """:obj:`str`: Chat action indicating that the bot is uploading a video note."""


class ChatID(IntEnum):
    """This enum contains some special chat IDs. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    ANONYMOUS_ADMIN = 1087968824
    """:obj:`int`: User ID in groups for messages sent by anonymous admins.

    Note:
        :attr:`telegram.Message.from_user` will contain this ID for backwards compatibility only.
        It's recommended to use :attr:`telegram.Message.sender_chat` instead.
    """
    SERVICE_CHAT = 777000
    """:obj:`int`: Telegram service chat, that also acts as sender of channel posts forwarded to
    discussion groups.

    Note:
        :attr:`telegram.Message.from_user` will contain this ID for backwards compatibility only.
        It's recommended to use :attr:`telegram.Message.sender_chat` instead.
    """
    FAKE_CHANNEL = 136817688
    """:obj:`int`: User ID in groups when message is sent on behalf of a channel.

    Note:
        * :attr:`telegram.Message.from_user` will contain this ID for backwards compatibility only.
          It's recommended to use :attr:`telegram.Message.sender_chat` instead.
        * This value is undocumented and might be changed by Telegram.
    """


class ChatInviteLinkLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.ChatInviteLink`/
    :meth:`telegram.Bot.create_chat_invite_link`/:meth:`telegram.Bot.edit_chat_invite_link`. The
    enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_MEMBER_LIMIT = 1
    """:obj:`int`: Minimum value allowed for the
    :paramref:`~telegram.Bot.create_chat_invite_link.member_limit` parameter of
    :meth:`telegram.Bot.create_chat_invite_link` and
    :paramref:`~telegram.Bot.edit_chat_invite_link.member_limit` of
    :meth:`telegram.Bot.edit_chat_invite_link`.
    """
    MAX_MEMBER_LIMIT = 99999
    """:obj:`int`: Maximum value allowed for the
    :paramref:`~telegram.Bot.create_chat_invite_link.member_limit` parameter of
    :meth:`telegram.Bot.create_chat_invite_link` and
    :paramref:`~telegram.Bot.edit_chat_invite_link.member_limit` of
    :meth:`telegram.Bot.edit_chat_invite_link`.
    """
    NAME_LENGTH = 32
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.create_chat_invite_link.name` parameter of
    :meth:`telegram.Bot.create_chat_invite_link` and
    :paramref:`~telegram.Bot.edit_chat_invite_link.name` of
    :meth:`telegram.Bot.edit_chat_invite_link`.
    """


class ChatLimit(IntEnum):
    """This enum contains limitations for
    :meth:`telegram.Bot.set_chat_administrator_custom_title`,
    :meth:`telegram.Bot.set_chat_description`, and :meth:`telegram.Bot.set_chat_title`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    CHAT_ADMINISTRATOR_CUSTOM_TITLE_LENGTH = 16
    """:obj:`int`: Maximum length of a :obj:`str` passed as the
    :paramref:`~telegram.Bot.set_chat_administrator_custom_title.custom_title` parameter of
    :meth:`telegram.Bot.set_chat_administrator_custom_title`.
    """
    CHAT_DESCRIPTION_LENGTH = 255
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.set_chat_description.description` parameter of
    :meth:`telegram.Bot.set_chat_description`.
    """
    MIN_CHAT_TITLE_LENGTH = 1
    """:obj:`int`: Minimum length of a :obj:`str` passed as the
    :paramref:`~telegram.Bot.set_chat_title.title` parameter of
    :meth:`telegram.Bot.set_chat_title`.
    """
    MAX_CHAT_TITLE_LENGTH = 128
    """:obj:`int`: Maximum length of a :obj:`str` passed as the
    :paramref:`~telegram.Bot.set_chat_title.title` parameter of
    :meth:`telegram.Bot.set_chat_title`.
    """


class ChatMemberStatus(StringEnum):
    """This enum contains the available states for :class:`telegram.ChatMember`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    ADMINISTRATOR = "administrator"
    """:obj:`str`: A :class:`telegram.ChatMember` who is administrator of the chat."""
    OWNER = "creator"
    """:obj:`str`: A :class:`telegram.ChatMember` who is the owner of the chat."""
    BANNED = "kicked"
    """:obj:`str`: A :class:`telegram.ChatMember` who was banned in the chat."""
    LEFT = "left"
    """:obj:`str`: A :class:`telegram.ChatMember` who has left the chat."""
    MEMBER = "member"
    """:obj:`str`: A :class:`telegram.ChatMember` who is a member of the chat."""
    RESTRICTED = "restricted"
    """:obj:`str`: A :class:`telegram.ChatMember` who was restricted in this chat."""


class ChatPhotoSize(IntEnum):
    """This enum contains limitations for :class:`telegram.ChatPhoto`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    SMALL = 160
    """:obj:`int`: Width and height of a small chat photo, ID of which is passed in
    :paramref:`~telegram.ChatPhoto.small_file_id` and
    :paramref:`~telegram.ChatPhoto.small_file_unique_id` parameters of
    :class:`telegram.ChatPhoto`.
    """
    BIG = 640
    """:obj:`int`: Width and height of a big chat photo, ID of which is passed in
    :paramref:`~telegram.ChatPhoto.big_file_id` and
    :paramref:`~telegram.ChatPhoto.big_file_unique_id` parameters of
    :class:`telegram.ChatPhoto`.
    """


class ChatType(StringEnum):
    """This enum contains the available types of :class:`telegram.Chat`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    SENDER = "sender"
    """:obj:`str`: A :class:`telegram.Chat` that represents the chat of a :class:`telegram.User`
    sending an :class:`telegram.InlineQuery`. """
    PRIVATE = "private"
    """:obj:`str`: A :class:`telegram.Chat` that is private."""
    GROUP = "group"
    """:obj:`str`: A :class:`telegram.Chat` that is a group."""
    SUPERGROUP = "supergroup"
    """:obj:`str`: A :class:`telegram.Chat` that is a supergroup."""
    CHANNEL = "channel"
    """:obj:`str`: A :class:`telegram.Chat` that is a channel."""


class ContactLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineQueryResultContact`,
    :class:`telegram.InputContactMessageContent`, and :meth:`telegram.Bot.send_contact`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    VCARD = 2048
    """:obj:`int`: Maximum value allowed for:

    * :paramref:`~telegram.Bot.send_contact.vcard` parameter of :meth:`~telegram.Bot.send_contact`
    * :paramref:`~telegram.InlineQueryResultContact.vcard` parameter of
      :class:`~telegram.InlineQueryResultContact`
    * :paramref:`~telegram.InputContactMessageContent.vcard` parameter of
      :class:`~telegram.InputContactMessageContent`
    """


class CustomEmojiStickerLimit(IntEnum):
    """This enum contains limitations for :meth:`telegram.Bot.get_custom_emoji_stickers`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    CUSTOM_EMOJI_IDENTIFIER_LIMIT = 200
    """:obj:`int`: Maximum amount of custom emoji identifiers which can be specified for the
    :paramref:`~telegram.Bot.get_custom_emoji_stickers.custom_emoji_ids` parameter of
    :meth:`telegram.Bot.get_custom_emoji_stickers`.
    """


class DiceEmoji(StringEnum):
    """This enum contains the available emoji for :class:`telegram.Dice`/
    :meth:`telegram.Bot.send_dice`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    DICE = "🎲"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎲``."""
    DARTS = "🎯"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎯``."""
    BASKETBALL = "🏀"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🏀``."""
    FOOTBALL = "⚽"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``⚽``."""
    SLOT_MACHINE = "🎰"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎰``."""
    BOWLING = "🎳"
    """:obj:`str`: A :class:`telegram.Dice` with the emoji ``🎳``."""


class DiceLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.Dice`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_VALUE = 1
    """:obj:`int`: Minimum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` (any emoji).
    """

    MAX_VALUE_BASKETBALL = 5
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.BASKETBALL`.
    """
    MAX_VALUE_BOWLING = 6
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.BOWLING`.
    """
    MAX_VALUE_DARTS = 6
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.DARTS`.
    """
    MAX_VALUE_DICE = 6
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.DICE`.
    """
    MAX_VALUE_FOOTBALL = 5
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.FOOTBALL`.
    """
    MAX_VALUE_SLOT_MACHINE = 64
    """:obj:`int`: Maximum value allowed for :paramref:`~telegram.Dice.value` parameter of
    :class:`telegram.Dice` if :paramref:`~telegram.Dice.emoji` is
    :tg-const:`telegram.constants.DiceEmoji.SLOT_MACHINE`.
    """


class FileSizeLimit(IntEnum):
    """This enum contains limitations regarding the upload and download of files. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    FILESIZE_DOWNLOAD = int(20e6)  # (20MB)
    """:obj:`int`: Bots can download files of up to 20MB in size."""
    FILESIZE_UPLOAD = int(50e6)  # (50MB)
    """:obj:`int`: Bots can upload non-photo files of up to 50MB in size."""
    FILESIZE_UPLOAD_LOCAL_MODE = int(2e9)  # (2000MB)
    """:obj:`int`: Bots can upload non-photo files of up to 2000MB in size when using a local bot
       API server.
    """
    FILESIZE_DOWNLOAD_LOCAL_MODE = sys.maxsize
    """:obj:`int`: Bots can download files without a size limit when using a local bot API server.
    """
    PHOTOSIZE_UPLOAD = int(10e6)  # (10MB)
    """:obj:`int`: Bots can upload photo files of up to 10MB in size."""
    VOICE_NOTE_FILE_SIZE = int(1e6)  # (1MB)
    """:obj:`int`: File size limit for the :meth:`~telegram.Bot.send_voice` method of
    :class:`telegram.Bot`. Bots can send :mimetype:`audio/ogg` files of up to 1MB in size as
    a voice note. Larger voice notes (up to 20MB) will be sent as files."""
    # It seems OK to link 20MB limit to FILESIZE_DOWNLOAD rather than creating a new constant


class FloodLimit(IntEnum):
    """This enum contains limitations regarding flood limits. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MESSAGES_PER_SECOND_PER_CHAT = 1
    """:obj:`int`: The number of messages that can be sent per second in a particular chat.
    Telegram may allow short bursts that go over this limit, but eventually you'll begin
    receiving 429 errors.
    """
    MESSAGES_PER_SECOND = 30
    """:obj:`int`: The number of messages that can roughly be sent in an interval of 30 seconds
    across all chats.
    """
    MESSAGES_PER_MINUTE_PER_GROUP = 20
    """:obj:`int`: The number of messages that can roughly be sent to a particular group within one
    minute.
    """


class ForumIconColor(IntEnum):
    """This enum contains the available colors for use in
    :paramref:`telegram.Bot.create_forum_topic.icon_color`. The enum members of this enumeration
    are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    BLUE = 0x6FB9F0
    """:obj:`int`: An icon with a color which corresponds to blue (``0x6FB9F0``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#6FB9F0;"></div>

    """
    YELLOW = 0xFFD67E
    """:obj:`int`: An icon with a color which corresponds to yellow (``0xFFD67E``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#FFD67E;"></div>

    """
    PURPLE = 0xCB86DB
    """:obj:`int`: An icon with a color which corresponds to purple (``0xCB86DB``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#CB86DB;"></div>

    """
    GREEN = 0x8EEE98
    """:obj:`int`: An icon with a color which corresponds to green (``0x8EEE98``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#8EEE98;"></div>

    """
    PINK = 0xFF93B2
    """:obj:`int`: An icon with a color which corresponds to pink (``0xFF93B2``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#FF93B2;"></div>

    """
    RED = 0xFB6F5F
    """:obj:`int`: An icon with a color which corresponds to red (``0xFB6F5F``).

    .. raw:: html

        <div style="height:15px; width:15px; background-color:#FB6F5F;"></div>

    """


class InlineKeyboardButtonLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineKeyboardButton`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_CALLBACK_DATA = 1
    """:obj:`int`: Minimum value allowed for
    :paramref:`~telegram.InlineKeyboardButton.callback_data` parameter of
    :class:`telegram.InlineKeyboardButton`
    """
    MAX_CALLBACK_DATA = 64
    """:obj:`int`: Maximum value allowed for
    :paramref:`~telegram.InlineKeyboardButton.callback_data` parameter of
    :class:`telegram.InlineKeyboardButton`
    """


class InlineKeyboardMarkupLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineKeyboardMarkup`/
    :meth:`telegram.Bot.send_message` & friends. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
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


class InputMediaType(StringEnum):
    """This enum contains the available types of :class:`telegram.InputMedia`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    ANIMATION = "animation"
    """:obj:`str`: Type of :class:`telegram.InputMediaAnimation`."""
    DOCUMENT = "document"
    """:obj:`str`: Type of :class:`telegram.InputMediaDocument`."""
    AUDIO = "audio"
    """:obj:`str`: Type of :class:`telegram.InputMediaAudio`."""
    PHOTO = "photo"
    """:obj:`str`: Type of :class:`telegram.InputMediaPhoto`."""
    VIDEO = "video"
    """:obj:`str`: Type of :class:`telegram.InputMediaVideo`."""


class InlineQueryLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineQuery`/
    :meth:`telegram.Bot.answer_inline_query`. The enum members of this enumeration are instances
    of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    RESULTS = 50
    """:obj:`int`: Maximum number of results that can be passed to
    :meth:`telegram.Bot.answer_inline_query`."""
    MAX_OFFSET_LENGTH = 64
    """:obj:`int`: Maximum number of bytes in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.answer_inline_query.next_offset` parameter of
    :meth:`telegram.Bot.answer_inline_query`."""
    MAX_QUERY_LENGTH = 256
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.InlineQuery.query` parameter of :class:`telegram.InlineQuery`."""
    MIN_SWITCH_PM_TEXT_LENGTH = 1
    """:obj:`int`: Minimum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.answer_inline_query.switch_pm_parameter` parameter of
    :meth:`telegram.Bot.answer_inline_query`."""
    MAX_SWITCH_PM_TEXT_LENGTH = 64
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.answer_inline_query.switch_pm_parameter` parameter of
    :meth:`telegram.Bot.answer_inline_query`."""


class InlineQueryResultLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InlineQueryResult` and its subclasses.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_ID_LENGTH = 1
    """:obj:`int`: Minimum number of bytes in a :obj:`str` passed as the
    :paramref:`~telegram.InlineQueryResult.id` parameter of
    :class:`telegram.InlineQueryResult` and its subclasses
    """
    MAX_ID_LENGTH = 64
    """:obj:`int`: Maximum number of bytes in a :obj:`str` passed as the
    :paramref:`~telegram.InlineQueryResult.id` parameter of
    :class:`telegram.InlineQueryResult` and its subclasses
    """


class InlineQueryResultType(StringEnum):
    """This enum contains the available types of :class:`telegram.InlineQueryResult`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    AUDIO = "audio"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultAudio` and
    :class:`telegram.InlineQueryResultCachedAudio`.
    """
    DOCUMENT = "document"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultDocument` and
    :class:`telegram.InlineQueryResultCachedDocument`.
    """
    GIF = "gif"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultGif` and
    :class:`telegram.InlineQueryResultCachedGif`.
    """
    MPEG4GIF = "mpeg4_gif"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultMpeg4Gif` and
    :class:`telegram.InlineQueryResultCachedMpeg4Gif`.
    """
    PHOTO = "photo"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultPhoto` and
    :class:`telegram.InlineQueryResultCachedPhoto`.
    """
    STICKER = "sticker"
    """:obj:`str`: Type of and :class:`telegram.InlineQueryResultCachedSticker`."""
    VIDEO = "video"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultVideo` and
    :class:`telegram.InlineQueryResultCachedVideo`.
    """
    VOICE = "voice"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultVoice` and
    :class:`telegram.InlineQueryResultCachedVoice`.
    """
    ARTICLE = "article"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultArticle`."""
    CONTACT = "contact"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultContact`."""
    GAME = "game"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultGame`."""
    LOCATION = "location"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultLocation`."""
    VENUE = "venue"
    """:obj:`str`: Type of :class:`telegram.InlineQueryResultVenue`."""


class LocationLimit(IntEnum):
    """This enum contains limitations for
    :class:`telegram.Location`/:class:`telegram.ChatLocation`/
    :meth:`telegram.Bot.edit_message_live_location`/:meth:`telegram.Bot.send_location`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_CHAT_LOCATION_ADDRESS = 1
    """:obj:`int`: Minimum value allowed for :paramref:`~telegram.ChatLocation.address` parameter
    of :class:`telegram.ChatLocation`
    """
    MAX_CHAT_LOCATION_ADDRESS = 64
    """:obj:`int`: Minimum value allowed for :paramref:`~telegram.ChatLocation.address` parameter
    of :class:`telegram.ChatLocation`
    """

    HORIZONTAL_ACCURACY = 1500
    """:obj:`int`: Maximum value allowed for:

    * :paramref:`~telegram.Location.horizontal_accuracy` parameter of :class:`telegram.Location`
    * :paramref:`~telegram.InlineQueryResultLocation.horizontal_accuracy` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.horizontal_accuracy` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.horizontal_accuracy` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.horizontal_accuracy` parameter of
      :meth:`telegram.Bot.send_location`
    """

    MIN_HEADING = 1
    """:obj:`int`: Minimum value allowed for:

    * :paramref:`~telegram.Location.heading` parameter of :class:`telegram.Location`
    * :paramref:`~telegram.InlineQueryResultLocation.heading` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.heading` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.heading` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.heading` parameter of
      :meth:`telegram.Bot.send_location`
    """
    MAX_HEADING = 360
    """:obj:`int`: Maximum value allowed for:

    * :paramref:`~telegram.Location.heading` parameter of :class:`telegram.Location`
    * :paramref:`~telegram.InlineQueryResultLocation.heading` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.heading` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.heading` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.heading` parameter of
      :meth:`telegram.Bot.send_location`
    """

    MIN_LIVE_PERIOD = 60
    """:obj:`int`: Minimum value allowed for:

    * :paramref:`~telegram.InlineQueryResultLocation.live_period` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.live_period` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.live_period` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.live_period` parameter of
      :meth:`telegram.Bot.send_location`
    """
    MAX_LIVE_PERIOD = 86400
    """:obj:`int`: Maximum value allowed for:

    * :paramref:`~telegram.InlineQueryResultLocation.live_period` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.live_period` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.live_period` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.live_period` parameter of
      :meth:`telegram.Bot.send_location`
    """

    MIN_PROXIMITY_ALERT_RADIUS = 1
    """:obj:`int`: Minimum value allowed for:

    * :paramref:`~telegram.InlineQueryResultLocation.proximity_alert_radius` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.proximity_alert_radius` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.proximity_alert_radius` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.proximity_alert_radius` parameter of
      :meth:`telegram.Bot.send_location`
    """
    MAX_PROXIMITY_ALERT_RADIUS = 100000
    """:obj:`int`: Maximum value allowed for:

    * :paramref:`~telegram.InlineQueryResultLocation.proximity_alert_radius` parameter of
      :class:`telegram.InlineQueryResultLocation`
    * :paramref:`~telegram.InputLocationMessageContent.proximity_alert_radius` parameter of
      :class:`telegram.InputLocationMessageContent`
    * :paramref:`~telegram.Bot.edit_message_live_location.proximity_alert_radius` parameter of
      :meth:`telegram.Bot.edit_message_live_location`
    * :paramref:`~telegram.Bot.send_location.proximity_alert_radius` parameter of
      :meth:`telegram.Bot.send_location`
    """


class MaskPosition(StringEnum):
    """This enum contains the available positions for :class:`telegram.MaskPosition`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    FOREHEAD = "forehead"
    """:obj:`str`: Mask position for a sticker on the forehead."""
    EYES = "eyes"
    """:obj:`str`: Mask position for a sticker on the eyes."""
    MOUTH = "mouth"
    """:obj:`str`: Mask position for a sticker on the mouth."""
    CHIN = "chin"
    """:obj:`str`: Mask position for a sticker on the chin."""


class MediaGroupLimit(IntEnum):
    """This enum contains limitations for :meth:`telegram.Bot.send_media_group`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_MEDIA_LENGTH = 2
    """:obj:`int`: Minimum length of a :obj:`list` passed as the
    :paramref:`~telegram.Bot.send_media_group.media` parameter of
    :meth:`telegram.Bot.send_media_group`.
    """
    MAX_MEDIA_LENGTH = 10
    """:obj:`int`: Maximum length of a :obj:`list` passed as the
    :paramref:`~telegram.Bot.send_media_group.media` parameter of
    :meth:`telegram.Bot.send_media_group`.
    """


class MenuButtonType(StringEnum):
    """This enum contains the available types of :class:`telegram.MenuButton`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    COMMANDS = "commands"
    """:obj:`str`: The type of :class:`telegram.MenuButtonCommands`."""
    WEB_APP = "web_app"
    """:obj:`str`: The type of :class:`telegram.MenuButtonWebApp`."""
    DEFAULT = "default"
    """:obj:`str`: The type of :class:`telegram.MenuButtonDefault`."""


class MessageAttachmentType(StringEnum):
    """This enum contains the available types of :class:`telegram.Message` that can be seen
    as attachment. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    # Make sure that all constants here are also listed in the MessageType Enum!
    # (Enums are not extendable)

    ANIMATION = "animation"
    """:obj:`str`: Messages with :attr:`telegram.Message.animation`."""
    AUDIO = "audio"
    """:obj:`str`: Messages with :attr:`telegram.Message.audio`."""
    CONTACT = "contact"
    """:obj:`str`: Messages with :attr:`telegram.Message.contact`."""
    DICE = "dice"
    """:obj:`str`: Messages with :attr:`telegram.Message.dice`."""
    DOCUMENT = "document"
    """:obj:`str`: Messages with :attr:`telegram.Message.document`."""
    GAME = "game"
    """:obj:`str`: Messages with :attr:`telegram.Message.game`."""
    INVOICE = "invoice"
    """:obj:`str`: Messages with :attr:`telegram.Message.invoice`."""
    LOCATION = "location"
    """:obj:`str`: Messages with :attr:`telegram.Message.location`."""
    PASSPORT_DATA = "passport_data"
    """:obj:`str`: Messages with :attr:`telegram.Message.passport_data`."""
    PHOTO = "photo"
    """:obj:`str`: Messages with :attr:`telegram.Message.photo`."""
    POLL = "poll"
    """:obj:`str`: Messages with :attr:`telegram.Message.poll`."""
    STICKER = "sticker"
    """:obj:`str`: Messages with :attr:`telegram.Message.sticker`."""
    SUCCESSFUL_PAYMENT = "successful_payment"
    """:obj:`str`: Messages with :attr:`telegram.Message.successful_payment`."""
    VIDEO = "video"
    """:obj:`str`: Messages with :attr:`telegram.Message.video`."""
    VIDEO_NOTE = "video_note"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_note`."""
    VOICE = "voice"
    """:obj:`str`: Messages with :attr:`telegram.Message.voice`."""
    VENUE = "venue"
    """:obj:`str`: Messages with :attr:`telegram.Message.venue`."""


class MessageEntityType(StringEnum):
    """This enum contains the available types of :class:`telegram.MessageEntity`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MENTION = "mention"
    """:obj:`str`: Message entities representing a mention."""
    HASHTAG = "hashtag"
    """:obj:`str`: Message entities representing a hashtag."""
    CASHTAG = "cashtag"
    """:obj:`str`: Message entities representing a cashtag."""
    PHONE_NUMBER = "phone_number"
    """:obj:`str`: Message entities representing a phone number."""
    BOT_COMMAND = "bot_command"
    """:obj:`str`: Message entities representing a bot command."""
    URL = "url"
    """:obj:`str`: Message entities representing a url."""
    EMAIL = "email"
    """:obj:`str`: Message entities representing a email."""
    BOLD = "bold"
    """:obj:`str`: Message entities representing bold text."""
    ITALIC = "italic"
    """:obj:`str`: Message entities representing italic text."""
    CODE = "code"
    """:obj:`str`: Message entities representing monowidth string."""
    PRE = "pre"
    """:obj:`str`: Message entities representing monowidth block."""
    TEXT_LINK = "text_link"
    """:obj:`str`: Message entities representing clickable text URLs."""
    TEXT_MENTION = "text_mention"
    """:obj:`str`: Message entities representing text mention for users without usernames."""
    UNDERLINE = "underline"
    """:obj:`str`: Message entities representing underline text."""
    STRIKETHROUGH = "strikethrough"
    """:obj:`str`: Message entities representing strikethrough text."""
    SPOILER = "spoiler"
    """:obj:`str`: Message entities representing spoiler text."""
    CUSTOM_EMOJI = "custom_emoji"
    """:obj:`str`: Message entities representing inline custom emoji stickers.

    .. versionadded:: 20.0
    """


class MessageLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.Message`/
    :class:`telegram.InputTextMessageContent`/
    :meth:`telegram.Bot.send_message` & friends. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    # TODO add links to params?
    MAX_TEXT_LENGTH = 4096
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.Game.text` parameter of :class:`telegram.Game`
    * :paramref:`~telegram.Message.text` parameter of :class:`telegram.Message`
    * :paramref:`~telegram.InputTextMessageContent.message_text` parameter of
      :class:`telegram.InputTextMessageContent`
    * :paramref:`~telegram.Bot.send_message.text` parameter of :meth:`telegram.Bot.send_message`
    * :paramref:`~telegram.Bot.edit_message_text.text` parameter of
      :meth:`telegram.Bot.edit_message_text`
    """
    CAPTION_LENGTH = 1024
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.Message.caption` parameter of :class:`telegram.Message`
    * :paramref:`~telegram.InputMedia.caption` parameter of :class:`telegram.InputMedia`
      and its subclasses
    * ``caption`` parameter of subclasses of :class:`telegram.InlineQueryResult`
    * ``caption`` parameter of :meth:`telegram.Bot.send_photo`, :meth:`telegram.Bot.send_audio`,
      :meth:`telegram.Bot.send_document`, :meth:`telegram.Bot.send_video`,
      :meth:`telegram.Bot.send_animation`, :meth:`telegram.Bot.send_voice`,
      :meth:`telegram.Bot.edit_message_caption`, :meth:`telegram.Bot.copy_message`
    """
    # constants above this line are tested
    MIN_TEXT_LENGTH = 1
    """:obj:`int`: Minimum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.InputTextMessageContent.message_text` parameter of
    :class:`telegram.InputTextMessageContent` and the
    :paramref:`~telegram.Bot.edit_message_text.text` parameter of
    :meth:`telegram.Bot.edit_message_text`.
    """
    # TODO this constant is not used. helpers.py contains 64 as a number
    DEEP_LINK_LENGTH = 64
    """:obj:`int`: Maximum number of characters for a deep link."""
    # TODO this constant is not used anywhere
    MESSAGE_ENTITIES = 100
    """:obj:`int`: Maximum number of entities that can be displayed in a message. Further entities
    will simply be ignored by Telegram.

    Note:
        This value is undocumented and might be changed by Telegram.
    """


class MessageType(StringEnum):
    """This enum contains the available types of :class:`telegram.Message` that can be seen
    as attachment. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    # Make sure that all attachment type constants are also listed in the
    # MessageAttachmentType Enum! (Enums are not extendable)

    # -------------------------------------------------- Attachment types
    ANIMATION = "animation"
    """:obj:`str`: Messages with :attr:`telegram.Message.animation`."""
    AUDIO = "audio"
    """:obj:`str`: Messages with :attr:`telegram.Message.audio`."""
    CONTACT = "contact"
    """:obj:`str`: Messages with :attr:`telegram.Message.contact`."""
    DICE = "dice"
    """:obj:`str`: Messages with :attr:`telegram.Message.dice`."""
    DOCUMENT = "document"
    """:obj:`str`: Messages with :attr:`telegram.Message.document`."""
    GAME = "game"
    """:obj:`str`: Messages with :attr:`telegram.Message.game`."""
    INVOICE = "invoice"
    """:obj:`str`: Messages with :attr:`telegram.Message.invoice`."""
    LOCATION = "location"
    """:obj:`str`: Messages with :attr:`telegram.Message.location`."""
    PASSPORT_DATA = "passport_data"
    """:obj:`str`: Messages with :attr:`telegram.Message.passport_data`."""
    PHOTO = "photo"
    """:obj:`str`: Messages with :attr:`telegram.Message.photo`."""
    POLL = "poll"
    """:obj:`str`: Messages with :attr:`telegram.Message.poll`."""
    STICKER = "sticker"
    """:obj:`str`: Messages with :attr:`telegram.Message.sticker`."""
    SUCCESSFUL_PAYMENT = "successful_payment"
    """:obj:`str`: Messages with :attr:`telegram.Message.successful_payment`."""
    VIDEO = "video"
    """:obj:`str`: Messages with :attr:`telegram.Message.video`."""
    VIDEO_NOTE = "video_note"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_note`."""
    VOICE = "voice"
    """:obj:`str`: Messages with :attr:`telegram.Message.voice`."""
    VENUE = "venue"
    """:obj:`str`: Messages with :attr:`telegram.Message.venue`."""
    # -------------------------------------------------- Other types
    TEXT = "text"
    """:obj:`str`: Messages with :attr:`telegram.Message.text`."""
    NEW_CHAT_MEMBERS = "new_chat_members"
    """:obj:`str`: Messages with :attr:`telegram.Message.new_chat_members`."""
    LEFT_CHAT_MEMBER = "left_chat_member"
    """:obj:`str`: Messages with :attr:`telegram.Message.left_chat_member`."""
    NEW_CHAT_TITLE = "new_chat_title"
    """:obj:`str`: Messages with :attr:`telegram.Message.new_chat_title`."""
    NEW_CHAT_PHOTO = "new_chat_photo"
    """:obj:`str`: Messages with :attr:`telegram.Message.new_chat_photo`."""
    DELETE_CHAT_PHOTO = "delete_chat_photo"
    """:obj:`str`: Messages with :attr:`telegram.Message.delete_chat_photo`."""
    GROUP_CHAT_CREATED = "group_chat_created"
    """:obj:`str`: Messages with :attr:`telegram.Message.group_chat_created`."""
    SUPERGROUP_CHAT_CREATED = "supergroup_chat_created"
    """:obj:`str`: Messages with :attr:`telegram.Message.supergroup_chat_created`."""
    CHANNEL_CHAT_CREATED = "channel_chat_created"
    """:obj:`str`: Messages with :attr:`telegram.Message.channel_chat_created`."""
    MESSAGE_AUTO_DELETE_TIMER_CHANGED = "message_auto_delete_timer_changed"
    """:obj:`str`: Messages with :attr:`telegram.Message.message_auto_delete_timer_changed`."""
    MIGRATE_TO_CHAT_ID = "migrate_to_chat_id"
    """:obj:`str`: Messages with :attr:`telegram.Message.migrate_to_chat_id`."""
    MIGRATE_FROM_CHAT_ID = "migrate_from_chat_id"
    """:obj:`str`: Messages with :attr:`telegram.Message.migrate_from_chat_id`."""
    PINNED_MESSAGE = "pinned_message"
    """:obj:`str`: Messages with :attr:`telegram.Message.pinned_message`."""
    PROXIMITY_ALERT_TRIGGERED = "proximity_alert_triggered"
    """:obj:`str`: Messages with :attr:`telegram.Message.proximity_alert_triggered`."""
    VIDEO_CHAT_SCHEDULED = "video_chat_scheduled"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_chat_scheduled`."""
    VIDEO_CHAT_STARTED = "video_chat_started"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_chat_started`."""
    VIDEO_CHAT_ENDED = "video_chat_ended"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_chat_ended`."""
    VIDEO_CHAT_PARTICIPANTS_INVITED = "video_chat_participants_invited"
    """:obj:`str`: Messages with :attr:`telegram.Message.video_chat_participants_invited`."""


class PollingLimit(IntEnum):
    """This enum contains limitations for :paramref:`telegram.Bot.get_updates.limit`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_LIMIT = 1
    """:obj:`int`: Minimum value allowed for the :paramref:`~telegram.Bot.get_updates.limit`
    parameter of :meth:`telegram.Bot.get_updates`.
    """
    MAX_LIMIT = 100
    """:obj:`int`: Maximum value allowed for the :paramref:`~telegram.Bot.get_updates.limit`
    parameter of :meth:`telegram.Bot.get_updates`.
    """


class ReplyLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.ForceReply`
    and :class:`telegram.ReplyKeyboardMarkup`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_INPUT_FIELD_PLACEHOLDER = 1
    """:obj:`int`: Minimum value allowed for
    :paramref:`~telegram.ForceReply.input_field_placeholder` parameter of
    :class:`telegram.ForceReply` and
    :paramref:`~telegram.ReplyKeyboardMarkup.input_field_placeholder` parameter of
    :class:`telegram.ReplyKeyboardMarkup`
    """
    MAX_INPUT_FIELD_PLACEHOLDER = 64
    """:obj:`int`: Maximum value allowed for
    :paramref:`~telegram.ForceReply.input_field_placeholder` parameter of
    :class:`telegram.ForceReply` and
    :paramref:`~telegram.ReplyKeyboardMarkup.input_field_placeholder` parameter of
    :class:`telegram.ReplyKeyboardMarkup`
    """


class StickerLimit(IntEnum):
    """This enum contains limitations for :meth:`telegram.Bot.create_new_sticker_set`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_NAME_AND_TITLE = 1
    """:obj:`int`: Minimum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.create_new_sticker_set.name` parameter or the
    :paramref:`~telegram.Bot.create_new_sticker_set.title` parameter of
    :meth:`telegram.Bot.create_new_sticker_set`.
    """
    MAX_NAME_AND_TITLE = 64
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.create_new_sticker_set.name` parameter or the
    :paramref:`~telegram.Bot.create_new_sticker_set.title` parameter of
    :meth:`telegram.Bot.create_new_sticker_set`.
    """


class StickerType(StringEnum):
    """This enum contains the available types of :class:`telegram.Sticker`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    REGULAR = "regular"
    """:obj:`str`: Regular sticker."""
    MASK = "mask"
    """:obj:`str`: Mask sticker."""
    CUSTOM_EMOJI = "custom_emoji"
    """:obj:`str`: Custom emoji sticker."""


class ParseMode(StringEnum):
    """This enum contains the available parse modes. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MARKDOWN = "Markdown"
    """:obj:`str`: Markdown parse mode.

    Note:
        :attr:`MARKDOWN` is a legacy mode, retained by Telegram for backward compatibility.
        You should use :attr:`MARKDOWN_V2` instead.
    """
    MARKDOWN_V2 = "MarkdownV2"
    """:obj:`str`: Markdown parse mode version 2."""
    HTML = "HTML"
    """:obj:`str`: HTML parse mode."""


class PollLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.Poll`/:class:`telegram.PollOption`/
    :meth:`telegram.Bot.send_poll`. The enum
    members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_QUESTION_LENGTH = 1
    """:obj:`int`: Minimum value allowed for the :paramref:`~telegram.Poll.question`
    parameter of :class:`telegram.Poll` and the :paramref:`~telegram.Bot.send_poll.question`
    parameter of :meth:`telegram.Bot.send_poll`.
    """
    MAX_QUESTION_LENGTH = 300
    """:obj:`int`: Maximum value allowed for the :paramref:`~telegram.Poll.question`
    parameter of :class:`telegram.Poll` and the :paramref:`~telegram.Bot.send_poll.question`
    parameter of :meth:`telegram.Bot.send_poll`.
    """
    MIN_OPTION_LENGTH = 1
    """:obj:`int`: Minimum length of each :obj:`str` passed in a :obj:`list`
    to the :paramref:`~telegram.Bot.send_poll.options` parameter of
    :meth:`telegram.Bot.send_poll`.
    """
    MAX_OPTION_LENGTH = 100
    """:obj:`int`: Maximum length of each :obj:`str` passed in a :obj:`list`
    to the :paramref:`~telegram.Bot.send_poll.options` parameter of
    :meth:`telegram.Bot.send_poll`.
    """
    MIN_OPTION_NUMBER = 2
    """:obj:`int`: Minimum number of strings passed in a :obj:`list`
    to the :paramref:`~telegram.Bot.send_poll.options` parameter of
    :meth:`telegram.Bot.send_poll`.
    """
    MAX_OPTION_NUMBER = 10
    """:obj:`int`: Maximum number of strings passed in a :obj:`list`
    to the :paramref:`~telegram.Bot.send_poll.options` parameter of
    :meth:`telegram.Bot.send_poll`.
    """
    MAX_EXPLANATION_LENGTH = 200
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as the
    :paramref:`~telegram.Poll.explanation` parameter of :class:`telegram.Poll` and the
    :paramref:`~telegram.Bot.send_poll.explanation` parameter of :meth:`telegram.Bot.send_poll`.
    """
    MAX_EXPLANATION_LINE_FEEDS = 2
    """:obj:`int`: Maximum number of line feeds in a :obj:`str` passed as the
    :paramref:`~telegram.Bot.send_poll.explanation` parameter of :meth:`telegram.Bot.send_poll`
    after entities parsing.
    """
    MIN_OPEN_PERIOD = 5
    """:obj:`int`: Minimum value allowed for the
    :paramref:`~telegram.Bot.send_poll.open_period` parameter of :meth:`telegram.Bot.send_poll`.
    Also used in the :paramref:`~telegram.Bot.send_poll.close_date` parameter of
    :meth:`telegram.Bot.send_poll`.
    """
    MAX_OPEN_PERIOD = 600
    """:obj:`int`: Maximum value allowed for the
    :paramref:`~telegram.Bot.send_poll.open_period` parameter of :meth:`telegram.Bot.send_poll`.
    Also used in the :paramref:`~telegram.Bot.send_poll.close_date` parameter of
    :meth:`telegram.Bot.send_poll`.
    """


class PollType(StringEnum):
    """This enum contains the available types for :class:`telegram.Poll`/
    :meth:`telegram.Bot.send_poll`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    REGULAR = "regular"
    """:obj:`str`: regular polls."""
    QUIZ = "quiz"
    """:obj:`str`: quiz polls."""


class UpdateType(StringEnum):
    """This enum contains the available types of :class:`telegram.Update`. The enum
    members of this enumeration are instances of :class:`str` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MESSAGE = "message"
    """:obj:`str`: Updates with :attr:`telegram.Update.message`."""
    EDITED_MESSAGE = "edited_message"
    """:obj:`str`: Updates with :attr:`telegram.Update.edited_message`."""
    CHANNEL_POST = "channel_post"
    """:obj:`str`: Updates with :attr:`telegram.Update.channel_post`."""
    EDITED_CHANNEL_POST = "edited_channel_post"
    """:obj:`str`: Updates with :attr:`telegram.Update.edited_channel_post`."""
    INLINE_QUERY = "inline_query"
    """:obj:`str`: Updates with :attr:`telegram.Update.inline_query`."""
    CHOSEN_INLINE_RESULT = "chosen_inline_result"
    """:obj:`str`: Updates with :attr:`telegram.Update.chosen_inline_result`."""
    CALLBACK_QUERY = "callback_query"
    """:obj:`str`: Updates with :attr:`telegram.Update.callback_query`."""
    SHIPPING_QUERY = "shipping_query"
    """:obj:`str`: Updates with :attr:`telegram.Update.shipping_query`."""
    PRE_CHECKOUT_QUERY = "pre_checkout_query"
    """:obj:`str`: Updates with :attr:`telegram.Update.pre_checkout_query`."""
    POLL = "poll"
    """:obj:`str`: Updates with :attr:`telegram.Update.poll`."""
    POLL_ANSWER = "poll_answer"
    """:obj:`str`: Updates with :attr:`telegram.Update.poll_answer`."""
    MY_CHAT_MEMBER = "my_chat_member"
    """:obj:`str`: Updates with :attr:`telegram.Update.my_chat_member`."""
    CHAT_MEMBER = "chat_member"
    """:obj:`str`: Updates with :attr:`telegram.Update.chat_member`."""
    CHAT_JOIN_REQUEST = "chat_join_request"
    """:obj:`str`: Updates with :attr:`telegram.Update.chat_join_request`."""


class InvoiceLimit(IntEnum):
    """This enum contains limitations for :class:`telegram.InputInvoiceMessageContent`,
    :meth:`telegram.Bot.send_invoice`, and :meth:`telegram.Bot.create_invoice_link`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_TITLE_LENGTH = 1
    """:obj:`int`: Minimum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.title` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.title` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.title` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MAX_TITLE_LENGTH = 32
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.title` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.title` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.title` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MIN_DESCRIPTION_LENGTH = 1
    """:obj:`int`: Minimum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.description` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.description` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.description` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MAX_DESCRIPTION_LENGTH = 255
    """:obj:`int`: Maximum number of characters in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.description` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.description` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.description` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MIN_PAYLOAD_LENGTH = 1
    """:obj:`int`: Minimum amount of bytes in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.payload` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.payload` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.payload` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MAX_PAYLOAD_LENGTH = 128
    """:obj:`int`: Maximum amount of bytes in a :obj:`str` passed as:

    * :paramref:`~telegram.InputInvoiceMessageContent.payload` parameter of
      :class:`telegram.InputInvoiceMessageContent`
    * :paramref:`~telegram.Bot.send_invoice.payload` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.payload` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """
    MAX_TIP_AMOUNTS = 4
    """:obj:`int`: Maximum length of a :obj:`Sequence` passed as:

    * :paramref:`~telegram.Bot.send_invoice.suggested_tip_amounts` parameter of
      :meth:`telegram.Bot.send_invoice`.
    * :paramref:`~telegram.Bot.create_invoice_link.suggested_tip_amounts` parameter of
      :meth:`telegram.Bot.create_invoice_link`.
    """


class UserProfilePhotosLimit(IntEnum):
    """This enum contains limitations for :paramref:`telegram.Bot.get_user_profile_photos.limit`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_LIMIT = 1
    """:obj:`int`: Minimum value allowed for
    :paramref:`~telegram.Bot.get_user_profile_photos.limit` parameter of
    :meth:`telegram.Bot.get_user_profile_photos`.
    """
    MAX_LIMIT = 100
    """:obj:`int`: Maximum value allowed for
    :paramref:`~telegram.Bot.get_user_profile_photos.limit` parameter of
    :meth:`telegram.Bot.get_user_profile_photos`.
    """


class WebhookLimit(IntEnum):
    """This enum contains limitations for :paramref:`telegram.Bot.set_webhook.max_connections` and
    :paramref:`telegram.Bot.set_webhook.secret_token`. The enum members of this enumeration are
    instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_CONNECTIONS_LIMIT = 1
    """:obj:`int`: Minimum value allowed for the
    :paramref:`~telegram.Bot.set_webhook.max_connections` parameter of
    :meth:`telegram.Bot.set_webhook`.
    """
    MAX_CONNECTIONS_LIMIT = 100
    """:obj:`int`: Maximum value allowed for the
    :paramref:`~telegram.Bot.set_webhook.max_connections` parameter of
    :meth:`telegram.Bot.set_webhook`.
    """
    MIN_SECRET_TOKEN_LENGTH = 1
    """:obj:`int`: Minimum length of the secret token for the
    :paramref:`~telegram.Bot.set_webhook.secret_token` parameter of
    :meth:`telegram.Bot.set_webhook`.
    """
    MAX_SECRET_TOKEN_LENGTH = 256
    """:obj:`int`: Maximum length of the secret token for the
    :paramref:`~telegram.Bot.set_webhook.secret_token` parameter of
    :meth:`telegram.Bot.set_webhook`.
    """


class ForumTopicLimit(IntEnum):
    """This enum contains limitations for :paramref:`telegram.Bot.create_forum_topic.name` and
    :paramref:`telegram.Bot.edit_forum_topic.name`.
    The enum members of this enumeration are instances of :class:`int` and can be treated as such.

    .. versionadded:: 20.0
    """

    __slots__ = ()

    MIN_NAME_LENGTH = 1
    """:obj:`int`: Minimum length of a :obj:`str` passed as:

    * :paramref:`~telegram.Bot.create_forum_topic.name` parameter of
      :meth:`telegram.Bot.create_forum_topic`
    * :paramref:`~telegram.Bot.edit_forum_topic.name` parameter of
      :meth:`telegram.Bot.edit_forum_topic`
    * :paramref:`~telegram.Bot.edit_general_forum_topic.name` parameter of
      :meth:`telegram.Bot.edit_general_forum_topic`
    """
    MAX_NAME_LENGTH = 128
    """:obj:`int`: Maximum length of a :obj:`str` passed as:

    * :paramref:`~telegram.Bot.create_forum_topic.name` parameter of
      :meth:`telegram.Bot.create_forum_topic`
    * :paramref:`~telegram.Bot.edit_forum_topic.name` parameter of
      :meth:`telegram.Bot.edit_forum_topic`
    * :paramref:`~telegram.Bot.edit_general_forum_topic.name` parameter of
      :meth:`telegram.Bot.edit_general_forum_topic`
    """
