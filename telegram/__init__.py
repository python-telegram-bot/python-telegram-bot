#!/usr/bin/env python
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
"""A library that provides a Python interface to the Telegram Bot API"""

__author__ = "devs@python-telegram-bot.org"

__all__ = (  # Keep this alphabetically ordered
    "__bot_api_version__",
    "__bot_api_version_info__",
    "__version__",
    "__version_info__",
    "Animation",
    "Audio",
    "Bot",
    "BotCommand",
    "BotCommandScope",
    "BotCommandScopeAllChatAdministrators",
    "BotCommandScopeAllGroupChats",
    "BotCommandScopeAllPrivateChats",
    "BotCommandScopeChat",
    "BotCommandScopeChatAdministrators",
    "BotCommandScopeChatMember",
    "BotCommandScopeDefault",
    "CallbackGame",
    "CallbackQuery",
    "Chat",
    "ChatAdministratorRights",
    "ChatInviteLink",
    "ChatJoinRequest",
    "ChatLocation",
    "ChatMember",
    "ChatMemberOwner",
    "ChatMemberAdministrator",
    "ChatMemberMember",
    "ChatMemberRestricted",
    "ChatMemberLeft",
    "ChatMemberBanned",
    "ChatMemberUpdated",
    "ChatPermissions",
    "ChatPhoto",
    "ChosenInlineResult",
    "constants",
    "Contact",
    "Credentials",
    "DataCredentials",
    "Dice",
    "Document",
    "EncryptedCredentials",
    "EncryptedPassportElement",
    "error",
    "File",
    "FileCredentials",
    "ForceReply",
    "ForumTopic",
    "ForumTopicClosed",
    "ForumTopicCreated",
    "ForumTopicEdited",
    "ForumTopicReopened",
    "Game",
    "GameHighScore",
    "GeneralForumTopicHidden",
    "GeneralForumTopicUnhidden",
    "helpers",
    "IdDocumentData",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "InlineQuery",
    "InlineQueryResult",
    "InlineQueryResultArticle",
    "InlineQueryResultAudio",
    "InlineQueryResultCachedAudio",
    "InlineQueryResultCachedDocument",
    "InlineQueryResultCachedGif",
    "InlineQueryResultCachedMpeg4Gif",
    "InlineQueryResultCachedPhoto",
    "InlineQueryResultCachedSticker",
    "InlineQueryResultCachedVideo",
    "InlineQueryResultCachedVoice",
    "InlineQueryResultContact",
    "InlineQueryResultDocument",
    "InlineQueryResultGame",
    "InlineQueryResultGif",
    "InlineQueryResultLocation",
    "InlineQueryResultMpeg4Gif",
    "InlineQueryResultPhoto",
    "InlineQueryResultVenue",
    "InlineQueryResultVideo",
    "InlineQueryResultVoice",
    "InputContactMessageContent",
    "InputFile",
    "InputInvoiceMessageContent",
    "InputLocationMessageContent",
    "InputMedia",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMessageContent",
    "InputTextMessageContent",
    "InputVenueMessageContent",
    "Invoice",
    "KeyboardButton",
    "KeyboardButtonPollType",
    "LabeledPrice",
    "Location",
    "LoginUrl",
    "MaskPosition",
    "MenuButton",
    "MenuButtonCommands",
    "MenuButtonDefault",
    "MenuButtonWebApp",
    "Message",
    "MessageAutoDeleteTimerChanged",
    "MessageEntity",
    "MessageId",
    "OrderInfo",
    "PassportData",
    "PassportElementError",
    "PassportElementErrorDataField",
    "PassportElementErrorFile",
    "PassportElementErrorFiles",
    "PassportElementErrorFrontSide",
    "PassportElementErrorReverseSide",
    "PassportElementErrorSelfie",
    "PassportElementErrorTranslationFile",
    "PassportElementErrorTranslationFiles",
    "PassportElementErrorUnspecified",
    "PassportFile",
    "PersonalDetails",
    "PhotoSize",
    "Poll",
    "PollAnswer",
    "PollOption",
    "PreCheckoutQuery",
    "ProximityAlertTriggered",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "request",
    "ResidentialAddress",
    "SecureData",
    "SecureValue",
    "SentWebAppMessage",
    "ShippingAddress",
    "ShippingOption",
    "ShippingQuery",
    "Sticker",
    "StickerSet",
    "SuccessfulPayment",
    "TelegramObject",
    "Update",
    "User",
    "UserProfilePhotos",
    "Venue",
    "Video",
    "VideoChatEnded",
    "VideoChatParticipantsInvited",
    "VideoChatScheduled",
    "VideoChatStarted",
    "VideoNote",
    "Voice",
    "warnings",
    "WebAppData",
    "WebAppInfo",
    "WebhookInfo",
    "WriteAccessAllowed",
)


from . import _version, constants, error, helpers, request, warnings
from ._bot import Bot
from ._botcommand import BotCommand
from ._botcommandscope import (
    BotCommandScope,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
    BotCommandScopeDefault,
)
from ._callbackquery import CallbackQuery
from ._chat import Chat
from ._chatadministratorrights import ChatAdministratorRights
from ._chatinvitelink import ChatInviteLink
from ._chatjoinrequest import ChatJoinRequest
from ._chatlocation import ChatLocation
from ._chatmember import (
    ChatMember,
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
)
from ._chatmemberupdated import ChatMemberUpdated
from ._chatpermissions import ChatPermissions
from ._choseninlineresult import ChosenInlineResult
from ._dice import Dice
from ._files.animation import Animation
from ._files.audio import Audio
from ._files.chatphoto import ChatPhoto
from ._files.contact import Contact
from ._files.document import Document
from ._files.file import File
from ._files.inputfile import InputFile
from ._files.inputmedia import (
    InputMedia,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from ._files.location import Location
from ._files.photosize import PhotoSize
from ._files.sticker import MaskPosition, Sticker, StickerSet
from ._files.venue import Venue
from ._files.video import Video
from ._files.videonote import VideoNote
from ._files.voice import Voice
from ._forcereply import ForceReply
from ._forumtopic import (
    ForumTopic,
    ForumTopicClosed,
    ForumTopicCreated,
    ForumTopicEdited,
    ForumTopicReopened,
    GeneralForumTopicHidden,
    GeneralForumTopicUnhidden,
)
from ._games.callbackgame import CallbackGame
from ._games.game import Game
from ._games.gamehighscore import GameHighScore
from ._inline.inlinekeyboardbutton import InlineKeyboardButton
from ._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from ._inline.inlinequery import InlineQuery
from ._inline.inlinequeryresult import InlineQueryResult
from ._inline.inlinequeryresultarticle import InlineQueryResultArticle
from ._inline.inlinequeryresultaudio import InlineQueryResultAudio
from ._inline.inlinequeryresultcachedaudio import InlineQueryResultCachedAudio
from ._inline.inlinequeryresultcacheddocument import InlineQueryResultCachedDocument
from ._inline.inlinequeryresultcachedgif import InlineQueryResultCachedGif
from ._inline.inlinequeryresultcachedmpeg4gif import InlineQueryResultCachedMpeg4Gif
from ._inline.inlinequeryresultcachedphoto import InlineQueryResultCachedPhoto
from ._inline.inlinequeryresultcachedsticker import InlineQueryResultCachedSticker
from ._inline.inlinequeryresultcachedvideo import InlineQueryResultCachedVideo
from ._inline.inlinequeryresultcachedvoice import InlineQueryResultCachedVoice
from ._inline.inlinequeryresultcontact import InlineQueryResultContact
from ._inline.inlinequeryresultdocument import InlineQueryResultDocument
from ._inline.inlinequeryresultgame import InlineQueryResultGame
from ._inline.inlinequeryresultgif import InlineQueryResultGif
from ._inline.inlinequeryresultlocation import InlineQueryResultLocation
from ._inline.inlinequeryresultmpeg4gif import InlineQueryResultMpeg4Gif
from ._inline.inlinequeryresultphoto import InlineQueryResultPhoto
from ._inline.inlinequeryresultvenue import InlineQueryResultVenue
from ._inline.inlinequeryresultvideo import InlineQueryResultVideo
from ._inline.inlinequeryresultvoice import InlineQueryResultVoice
from ._inline.inputcontactmessagecontent import InputContactMessageContent
from ._inline.inputinvoicemessagecontent import InputInvoiceMessageContent
from ._inline.inputlocationmessagecontent import InputLocationMessageContent
from ._inline.inputmessagecontent import InputMessageContent
from ._inline.inputtextmessagecontent import InputTextMessageContent
from ._inline.inputvenuemessagecontent import InputVenueMessageContent
from ._keyboardbutton import KeyboardButton
from ._keyboardbuttonpolltype import KeyboardButtonPollType
from ._loginurl import LoginUrl
from ._menubutton import MenuButton, MenuButtonCommands, MenuButtonDefault, MenuButtonWebApp
from ._message import Message
from ._messageautodeletetimerchanged import MessageAutoDeleteTimerChanged
from ._messageentity import MessageEntity
from ._messageid import MessageId
from ._passport.credentials import (
    Credentials,
    DataCredentials,
    EncryptedCredentials,
    FileCredentials,
    SecureData,
    SecureValue,
)
from ._passport.data import IdDocumentData, PersonalDetails, ResidentialAddress
from ._passport.encryptedpassportelement import EncryptedPassportElement
from ._passport.passportdata import PassportData
from ._passport.passportelementerrors import (
    PassportElementError,
    PassportElementErrorDataField,
    PassportElementErrorFile,
    PassportElementErrorFiles,
    PassportElementErrorFrontSide,
    PassportElementErrorReverseSide,
    PassportElementErrorSelfie,
    PassportElementErrorTranslationFile,
    PassportElementErrorTranslationFiles,
    PassportElementErrorUnspecified,
)
from ._passport.passportfile import PassportFile
from ._payment.invoice import Invoice
from ._payment.labeledprice import LabeledPrice
from ._payment.orderinfo import OrderInfo
from ._payment.precheckoutquery import PreCheckoutQuery
from ._payment.shippingaddress import ShippingAddress
from ._payment.shippingoption import ShippingOption
from ._payment.shippingquery import ShippingQuery
from ._payment.successfulpayment import SuccessfulPayment
from ._poll import Poll, PollAnswer, PollOption
from ._proximityalerttriggered import ProximityAlertTriggered
from ._replykeyboardmarkup import ReplyKeyboardMarkup
from ._replykeyboardremove import ReplyKeyboardRemove
from ._sentwebappmessage import SentWebAppMessage
from ._telegramobject import TelegramObject
from ._update import Update
from ._user import User
from ._userprofilephotos import UserProfilePhotos
from ._videochat import (
    VideoChatEnded,
    VideoChatParticipantsInvited,
    VideoChatScheduled,
    VideoChatStarted,
)
from ._webappdata import WebAppData
from ._webappinfo import WebAppInfo
from ._webhookinfo import WebhookInfo
from ._writeaccessallowed import WriteAccessAllowed

#: :obj:`str`: The version of the `python-telegram-bot` library as string.
#: To get detailed information about the version number, please use :data:`__version_info__`
#: instead.
__version__ = _version.__version__
#:  :class:`typing.NamedTuple`: A tuple containing the five components of the version number:
#:  `major`, `minor`, `micro`, `releaselevel`, and `serial`.
#:  All values except `releaselevel` are integers.
#:  The release level is ``'alpha'``, ``'beta'``, ``'candidate'``, or ``'final'``.
#:  The components can also be accessed by name, so ``__version_info__[0]`` is equivalent to
#:  ``__version_info__.major`` and so on.
#:
#:  .. versionadded:: 20.0
__version_info__ = _version.__version_info__
#: :obj:`str`: Shortcut for :const:`telegram.constants.BOT_API_VERSION`.
#:
#: .. versionchanged:: 20.0
#:    This constant was previously named ``bot_api_version``.
__bot_api_version__ = _version.__bot_api_version__
#: :class:`typing.NamedTuple`: Shortcut for :const:`telegram.constants.BOT_API_VERSION_INFO`.
#:
#: .. versionadded:: 20.0
__bot_api_version_info__ = _version.__bot_api_version_info__
