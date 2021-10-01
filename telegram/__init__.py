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
"""A library that provides a Python interface to the Telegram Bot API"""

from ._telegramobject import TelegramObject
from ._botcommand import BotCommand
from ._user import User
from .files._chatphoto import ChatPhoto
from ._chat import Chat
from ._chatlocation import ChatLocation
from ._chatinvitelink import ChatInviteLink
from ._chatmember import (
    ChatMember,
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberRestricted,
    ChatMemberLeft,
    ChatMemberBanned,
)
from ._chatmemberupdated import ChatMemberUpdated
from ._chatpermissions import ChatPermissions
from .files._photosize import PhotoSize
from .files._audio import Audio
from .files._voice import Voice
from .files._document import Document
from .files._animation import Animation
from .files._sticker import Sticker, StickerSet, MaskPosition
from .files._video import Video
from .files._contact import Contact
from .files._location import Location
from .files._venue import Venue
from .files._videonote import VideoNote
from ._chataction import ChatAction
from ._dice import Dice
from ._userprofilephotos import UserProfilePhotos
from ._keyboardbuttonpolltype import KeyboardButtonPollType
from ._keyboardbutton import KeyboardButton
from ._replymarkup import ReplyMarkup
from ._replykeyboardmarkup import ReplyKeyboardMarkup
from ._replykeyboardremove import ReplyKeyboardRemove
from ._forcereply import ForceReply
from .files._inputfile import InputFile
from .files._file import File
from ._parsemode import ParseMode
from ._messageentity import MessageEntity
from ._messageid import MessageId
from .games._game import Game
from ._poll import Poll, PollOption, PollAnswer
from ._voicechat import (
    VoiceChatStarted,
    VoiceChatEnded,
    VoiceChatParticipantsInvited,
    VoiceChatScheduled,
)
from ._loginurl import LoginUrl
from ._proximityalerttriggered import ProximityAlertTriggered
from .games._callbackgame import CallbackGame
from .payment._shippingaddress import ShippingAddress
from .payment._orderinfo import OrderInfo
from .payment._successfulpayment import SuccessfulPayment
from .payment._invoice import Invoice
from .passport._credentials import EncryptedCredentials
from .passport._passportfile import PassportFile
from .passport._data import IdDocumentData, PersonalDetails, ResidentialAddress
from .passport._encryptedpassportelement import EncryptedPassportElement
from .passport._passportdata import PassportData
from .inline._inlinekeyboardbutton import InlineKeyboardButton
from .inline._inlinekeyboardmarkup import InlineKeyboardMarkup
from ._messageautodeletetimerchanged import MessageAutoDeleteTimerChanged
from ._message import Message
from ._callbackquery import CallbackQuery
from ._choseninlineresult import ChosenInlineResult
from .inline._inputmessagecontent import InputMessageContent
from .inline._inlinequery import InlineQuery
from .inline._inlinequeryresult import InlineQueryResult
from .inline._inlinequeryresultarticle import InlineQueryResultArticle
from .inline._inlinequeryresultaudio import InlineQueryResultAudio
from .inline._inlinequeryresultcachedaudio import InlineQueryResultCachedAudio
from .inline._inlinequeryresultcacheddocument import InlineQueryResultCachedDocument
from .inline._inlinequeryresultcachedgif import InlineQueryResultCachedGif
from .inline._inlinequeryresultcachedmpeg4gif import InlineQueryResultCachedMpeg4Gif
from .inline._inlinequeryresultcachedphoto import InlineQueryResultCachedPhoto
from .inline._inlinequeryresultcachedsticker import InlineQueryResultCachedSticker
from .inline._inlinequeryresultcachedvideo import InlineQueryResultCachedVideo
from .inline._inlinequeryresultcachedvoice import InlineQueryResultCachedVoice
from .inline._inlinequeryresultcontact import InlineQueryResultContact
from .inline._inlinequeryresultdocument import InlineQueryResultDocument
from .inline._inlinequeryresultgif import InlineQueryResultGif
from .inline._inlinequeryresultlocation import InlineQueryResultLocation
from .inline._inlinequeryresultmpeg4gif import InlineQueryResultMpeg4Gif
from .inline._inlinequeryresultphoto import InlineQueryResultPhoto
from .inline._inlinequeryresultvenue import InlineQueryResultVenue
from .inline._inlinequeryresultvideo import InlineQueryResultVideo
from .inline._inlinequeryresultvoice import InlineQueryResultVoice
from .inline._inlinequeryresultgame import InlineQueryResultGame
from .inline._inputtextmessagecontent import InputTextMessageContent
from .inline._inputlocationmessagecontent import InputLocationMessageContent
from .inline._inputvenuemessagecontent import InputVenueMessageContent
from .payment._labeledprice import LabeledPrice
from .inline._inputinvoicemessagecontent import InputInvoiceMessageContent
from .inline._inputcontactmessagecontent import InputContactMessageContent
from .payment._shippingoption import ShippingOption
from .payment._precheckoutquery import PreCheckoutQuery
from .payment._shippingquery import ShippingQuery
from ._webhookinfo import WebhookInfo
from .games._gamehighscore import GameHighScore
from ._update import Update
from .files._inputmedia import (
    InputMedia,
    InputMediaVideo,
    InputMediaPhoto,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
)
from .passport._passportelementerrors import (
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
from .passport._credentials import (
    Credentials,
    DataCredentials,
    SecureData,
    SecureValue,
    FileCredentials,
)
from ._botcommandscope import (
    BotCommandScope,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
)
from ._bot import Bot
from .version import __version__, bot_api_version  # noqa: F401

__author__ = 'devs@python-telegram-bot.org'

__all__ = (  # Keep this alphabetically ordered
    'Animation',
    'Audio',
    'Bot',
    'BotCommand',
    'BotCommandScope',
    'BotCommandScopeAllChatAdministrators',
    'BotCommandScopeAllGroupChats',
    'BotCommandScopeAllPrivateChats',
    'BotCommandScopeChat',
    'BotCommandScopeChatAdministrators',
    'BotCommandScopeChatMember',
    'BotCommandScopeDefault',
    'CallbackGame',
    'CallbackQuery',
    'Chat',
    'ChatAction',
    'ChatInviteLink',
    'ChatLocation',
    'ChatMember',
    'ChatMemberOwner',
    'ChatMemberAdministrator',
    'ChatMemberMember',
    'ChatMemberRestricted',
    'ChatMemberLeft',
    'ChatMemberBanned',
    'ChatMemberUpdated',
    'ChatPermissions',
    'ChatPhoto',
    'ChosenInlineResult',
    'Contact',
    'Credentials',
    'DataCredentials',
    'Dice',
    'Document',
    'EncryptedCredentials',
    'EncryptedPassportElement',
    'File',
    'FileCredentials',
    'ForceReply',
    'Game',
    'GameHighScore',
    'IdDocumentData',
    'InlineKeyboardButton',
    'InlineKeyboardMarkup',
    'InlineQuery',
    'InlineQueryResult',
    'InlineQueryResultArticle',
    'InlineQueryResultAudio',
    'InlineQueryResultCachedAudio',
    'InlineQueryResultCachedDocument',
    'InlineQueryResultCachedGif',
    'InlineQueryResultCachedMpeg4Gif',
    'InlineQueryResultCachedPhoto',
    'InlineQueryResultCachedSticker',
    'InlineQueryResultCachedVideo',
    'InlineQueryResultCachedVoice',
    'InlineQueryResultContact',
    'InlineQueryResultDocument',
    'InlineQueryResultGame',
    'InlineQueryResultGif',
    'InlineQueryResultLocation',
    'InlineQueryResultMpeg4Gif',
    'InlineQueryResultPhoto',
    'InlineQueryResultVenue',
    'InlineQueryResultVideo',
    'InlineQueryResultVoice',
    'InputContactMessageContent',
    'InputFile',
    'InputInvoiceMessageContent',
    'InputLocationMessageContent',
    'InputMedia',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputMessageContent',
    'InputTextMessageContent',
    'InputVenueMessageContent',
    'Invoice',
    'KeyboardButton',
    'KeyboardButtonPollType',
    'LabeledPrice',
    'Location',
    'LoginUrl',
    'MaskPosition',
    'Message',
    'MessageAutoDeleteTimerChanged',
    'MessageEntity',
    'MessageId',
    'OrderInfo',
    'ParseMode',
    'PassportData',
    'PassportElementError',
    'PassportElementErrorDataField',
    'PassportElementErrorFile',
    'PassportElementErrorFiles',
    'PassportElementErrorFrontSide',
    'PassportElementErrorReverseSide',
    'PassportElementErrorSelfie',
    'PassportElementErrorTranslationFile',
    'PassportElementErrorTranslationFiles',
    'PassportElementErrorUnspecified',
    'PassportFile',
    'PersonalDetails',
    'PhotoSize',
    'Poll',
    'PollAnswer',
    'PollOption',
    'PreCheckoutQuery',
    'ProximityAlertTriggered',
    'ReplyKeyboardMarkup',
    'ReplyKeyboardRemove',
    'ReplyMarkup',
    'ResidentialAddress',
    'SecureData',
    'SecureValue',
    'ShippingAddress',
    'ShippingOption',
    'ShippingQuery',
    'Sticker',
    'StickerSet',
    'SuccessfulPayment',
    'TelegramObject',
    'Update',
    'User',
    'UserProfilePhotos',
    'Venue',
    'Video',
    'VideoNote',
    'Voice',
    'VoiceChatStarted',
    'VoiceChatEnded',
    'VoiceChatScheduled',
    'VoiceChatParticipantsInvited',
    'WebhookInfo',
)
