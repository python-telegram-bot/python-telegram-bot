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

__author__ = 'devs@python-telegram-bot.org'

__all__ = (  # Keep this alphabetically ordered
    'Animation',
    'Audio',
    'Bot',
    'bot_api_version',
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
    'ChatInviteLink',
    'ChatJoinRequest',
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
    'constants',
    'Contact',
    'Credentials',
    'DataCredentials',
    'Dice',
    'Document',
    'EncryptedCredentials',
    'EncryptedPassportElement',
    'error',
    'File',
    'FileCredentials',
    'ForceReply',
    'Game',
    'GameHighScore',
    'helpers',
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
    'request',
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
    'warnings',
    'WebhookInfo',
)


from ._telegramobject import TelegramObject
from ._botcommand import BotCommand
from ._user import User
from ._files.chatphoto import ChatPhoto
from ._chat import Chat
from ._chatlocation import ChatLocation
from ._chatinvitelink import ChatInviteLink
from ._chatjoinrequest import ChatJoinRequest
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
from ._files.photosize import PhotoSize
from ._files.audio import Audio
from ._files.voice import Voice
from ._files.document import Document
from ._files.animation import Animation
from ._files.sticker import Sticker, StickerSet, MaskPosition
from ._files.video import Video
from ._files.contact import Contact
from ._files.location import Location
from ._files.venue import Venue
from ._files.videonote import VideoNote
from ._dice import Dice
from ._userprofilephotos import UserProfilePhotos
from ._keyboardbuttonpolltype import KeyboardButtonPollType
from ._keyboardbutton import KeyboardButton
from ._replymarkup import ReplyMarkup
from ._replykeyboardmarkup import ReplyKeyboardMarkup
from ._replykeyboardremove import ReplyKeyboardRemove
from ._forcereply import ForceReply
from ._files.inputfile import InputFile
from ._files.file import File
from ._messageentity import MessageEntity
from ._messageid import MessageId
from ._games.game import Game
from ._poll import Poll, PollOption, PollAnswer
from ._voicechat import (
    VoiceChatStarted,
    VoiceChatEnded,
    VoiceChatParticipantsInvited,
    VoiceChatScheduled,
)
from ._loginurl import LoginUrl
from ._proximityalerttriggered import ProximityAlertTriggered
from ._games.callbackgame import CallbackGame
from ._payment.shippingaddress import ShippingAddress
from ._payment.orderinfo import OrderInfo
from ._payment.successfulpayment import SuccessfulPayment
from ._payment.invoice import Invoice
from ._passport.credentials import EncryptedCredentials
from ._passport.passportfile import PassportFile
from ._passport.data import IdDocumentData, PersonalDetails, ResidentialAddress
from ._passport.encryptedpassportelement import EncryptedPassportElement
from ._passport.passportdata import PassportData
from ._inline.inlinekeyboardbutton import InlineKeyboardButton
from ._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from ._messageautodeletetimerchanged import MessageAutoDeleteTimerChanged
from ._message import Message
from ._callbackquery import CallbackQuery
from ._choseninlineresult import ChosenInlineResult
from ._inline.inputmessagecontent import InputMessageContent
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
from ._inline.inlinequeryresultgif import InlineQueryResultGif
from ._inline.inlinequeryresultlocation import InlineQueryResultLocation
from ._inline.inlinequeryresultmpeg4gif import InlineQueryResultMpeg4Gif
from ._inline.inlinequeryresultphoto import InlineQueryResultPhoto
from ._inline.inlinequeryresultvenue import InlineQueryResultVenue
from ._inline.inlinequeryresultvideo import InlineQueryResultVideo
from ._inline.inlinequeryresultvoice import InlineQueryResultVoice
from ._inline.inlinequeryresultgame import InlineQueryResultGame
from ._inline.inputtextmessagecontent import InputTextMessageContent
from ._inline.inputlocationmessagecontent import InputLocationMessageContent
from ._inline.inputvenuemessagecontent import InputVenueMessageContent
from ._payment.labeledprice import LabeledPrice
from ._inline.inputinvoicemessagecontent import InputInvoiceMessageContent
from ._inline.inputcontactmessagecontent import InputContactMessageContent
from ._payment.shippingoption import ShippingOption
from ._payment.precheckoutquery import PreCheckoutQuery
from ._payment.shippingquery import ShippingQuery
from ._webhookinfo import WebhookInfo
from ._games.gamehighscore import GameHighScore
from ._update import Update
from ._files.inputmedia import (
    InputMedia,
    InputMediaVideo,
    InputMediaPhoto,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
)
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
from ._passport.credentials import (
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
