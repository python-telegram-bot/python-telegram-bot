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
from ._files._chatphoto import ChatPhoto
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
from ._files._photosize import PhotoSize
from ._files._audio import Audio
from ._files._voice import Voice
from ._files._document import Document
from ._files._animation import Animation
from ._files._sticker import Sticker, StickerSet, MaskPosition
from ._files._video import Video
from ._files._contact import Contact
from ._files._location import Location
from ._files._venue import Venue
from ._files._videonote import VideoNote
from ._chataction import ChatAction
from ._dice import Dice
from ._userprofilephotos import UserProfilePhotos
from ._keyboardbuttonpolltype import KeyboardButtonPollType
from ._keyboardbutton import KeyboardButton
from ._replymarkup import ReplyMarkup
from ._replykeyboardmarkup import ReplyKeyboardMarkup
from ._replykeyboardremove import ReplyKeyboardRemove
from ._forcereply import ForceReply
from ._files._inputfile import InputFile
from ._files._file import File
from ._parsemode import ParseMode
from ._messageentity import MessageEntity
from ._messageid import MessageId
from ._games._game import Game
from ._poll import Poll, PollOption, PollAnswer
from ._voicechat import (
    VoiceChatStarted,
    VoiceChatEnded,
    VoiceChatParticipantsInvited,
    VoiceChatScheduled,
)
from ._loginurl import LoginUrl
from ._proximityalerttriggered import ProximityAlertTriggered
from ._games._callbackgame import CallbackGame
from ._payment._shippingaddress import ShippingAddress
from ._payment._orderinfo import OrderInfo
from ._payment._successfulpayment import SuccessfulPayment
from ._payment._invoice import Invoice
from ._passport._credentials import EncryptedCredentials
from ._passport._passportfile import PassportFile
from ._passport._data import IdDocumentData, PersonalDetails, ResidentialAddress
from ._passport._encryptedpassportelement import EncryptedPassportElement
from ._passport._passportdata import PassportData
from ._inline._inlinekeyboardbutton import InlineKeyboardButton
from ._inline._inlinekeyboardmarkup import InlineKeyboardMarkup
from ._messageautodeletetimerchanged import MessageAutoDeleteTimerChanged
from ._message import Message
from ._callbackquery import CallbackQuery
from ._choseninlineresult import ChosenInlineResult
from ._inline._inputmessagecontent import InputMessageContent
from ._inline._inlinequery import InlineQuery
from ._inline._inlinequeryresult import InlineQueryResult
from ._inline._inlinequeryresultarticle import InlineQueryResultArticle
from ._inline._inlinequeryresultaudio import InlineQueryResultAudio
from ._inline._inlinequeryresultcachedaudio import InlineQueryResultCachedAudio
from ._inline._inlinequeryresultcacheddocument import InlineQueryResultCachedDocument
from ._inline._inlinequeryresultcachedgif import InlineQueryResultCachedGif
from ._inline._inlinequeryresultcachedmpeg4gif import InlineQueryResultCachedMpeg4Gif
from ._inline._inlinequeryresultcachedphoto import InlineQueryResultCachedPhoto
from ._inline._inlinequeryresultcachedsticker import InlineQueryResultCachedSticker
from ._inline._inlinequeryresultcachedvideo import InlineQueryResultCachedVideo
from ._inline._inlinequeryresultcachedvoice import InlineQueryResultCachedVoice
from ._inline._inlinequeryresultcontact import InlineQueryResultContact
from ._inline._inlinequeryresultdocument import InlineQueryResultDocument
from ._inline._inlinequeryresultgif import InlineQueryResultGif
from ._inline._inlinequeryresultlocation import InlineQueryResultLocation
from ._inline._inlinequeryresultmpeg4gif import InlineQueryResultMpeg4Gif
from ._inline._inlinequeryresultphoto import InlineQueryResultPhoto
from ._inline._inlinequeryresultvenue import InlineQueryResultVenue
from ._inline._inlinequeryresultvideo import InlineQueryResultVideo
from ._inline._inlinequeryresultvoice import InlineQueryResultVoice
from ._inline._inlinequeryresultgame import InlineQueryResultGame
from ._inline._inputtextmessagecontent import InputTextMessageContent
from ._inline._inputlocationmessagecontent import InputLocationMessageContent
from ._inline._inputvenuemessagecontent import InputVenueMessageContent
from ._payment._labeledprice import LabeledPrice
from ._inline._inputinvoicemessagecontent import InputInvoiceMessageContent
from ._inline._inputcontactmessagecontent import InputContactMessageContent
from ._payment._shippingoption import ShippingOption
from ._payment._precheckoutquery import PreCheckoutQuery
from ._payment._shippingquery import ShippingQuery
from ._webhookinfo import WebhookInfo
from ._games._gamehighscore import GameHighScore
from ._update import Update
from ._files._inputmedia import (
    InputMedia,
    InputMediaVideo,
    InputMediaPhoto,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
)
from ._passport._passportelementerrors import (
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
from ._passport._credentials import (
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
from ._version import __version__, bot_api_version  # noqa: F401

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
