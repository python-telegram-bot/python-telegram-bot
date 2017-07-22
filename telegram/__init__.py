#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

from .base import TelegramObject
from .user import User
from .files.chatphoto import ChatPhoto
from .chat import Chat
from .chatmember import ChatMember
from .files.photosize import PhotoSize
from .files.audio import Audio
from .files.voice import Voice
from .files.document import Document
from .files.sticker import Sticker
from .files.video import Video
from .files.contact import Contact
from .files.location import Location
from .files.venue import Venue
from .files.videonote import VideoNote
from .files.animation import Animation
from .chataction import ChatAction
from .userprofilephotos import UserProfilePhotos
from .replymarkup import ReplyMarkup
from .replykeyboard import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from .forcereply import ForceReply
from .files.inputfile import InputFile
from .files.file import File
from .emoji import Emoji
from .parsemode import ParseMode
from .messageentity import MessageEntity
from .game import Game
from .payments.shippingaddress import ShippingAddress
from .payments.orderinfo import OrderInfo
from .payments.successfulpayment import SuccessfulPayment
from .payments.invoice import Invoice
from .message import Message
from .callbackquery import CallbackQuery
from .choseninlineresult import ChosenInlineResult
from .inlinekeyboard import InlineKeyboardMarkup, InlineKeyboardButton
from .inputmessagecontents import (InputContactMessageContent, InputLocationMessageContent,
                                   InputMessageContent, InputTextMessageContent,
                                   InputVenueMessageContent)
from .inlinequeryresults import (InlineQueryResultArticle, InlineQueryResultAudio,
                                 InlineQueryResultCachedAudio, InlineQueryResultCachedDocument,
                                 InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif,
                                 InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker,
                                 InlineQueryResultCachedVideo, InlineQueryResultCachedVoice,
                                 InlineQueryResultContact, InlineQueryResultDocument,
                                 InlineQueryResultGame, InlineQueryResultGif,
                                 InlineQueryResultLocation, InlineQueryResultMpeg4Gif,
                                 InlineQueryResultPhoto, InlineQueryResultVenue,
                                 InlineQueryResultVideo, InlineQueryResultVoice,
                                 InlineQueryResult)
from .inlinequery import InlineQuery
from .payments.labeledprice import LabeledPrice
from .payments.shippingoption import ShippingOption
from .payments.precheckoutquery import PreCheckoutQuery
from .payments.shippingquery import ShippingQuery
from .webhookinfo import WebhookInfo
from .gamehighscore import GameHighScore
from .update import Update
from .bot import Bot
from .utils.error import TelegramError
from .constants import (MAX_MESSAGE_LENGTH, MAX_CAPTION_LENGTH, SUPPORTED_WEBHOOK_PORTS,
                        MAX_FILESIZE_DOWNLOAD, MAX_FILESIZE_UPLOAD,
                        MAX_MESSAGES_PER_SECOND_PER_CHAT, MAX_MESSAGES_PER_SECOND,
                        MAX_MESSAGES_PER_MINUTE_PER_GROUP)
from .version import __version__  # flake8: noqa

__author__ = 'devs@python-telegram-bot.org'

__all__ = [
    'Audio', 'Bot', 'Chat', 'ChatMember', 'ChatAction', 'ChosenInlineResult', 'CallbackQuery',
    'Contact', 'Document', 'Emoji', 'File', 'ForceReply', 'InlineKeyboardButton',
    'InlineKeyboardMarkup', 'InlineQuery', 'InlineQueryResult', 'InlineQueryResult',
    'InlineQueryResultArticle', 'InlineQueryResultAudio', 'InlineQueryResultCachedAudio',
    'InlineQueryResultCachedDocument', 'InlineQueryResultCachedGif',
    'InlineQueryResultCachedMpeg4Gif', 'InlineQueryResultCachedPhoto',
    'InlineQueryResultCachedSticker', 'InlineQueryResultCachedVideo',
    'InlineQueryResultCachedVoice', 'InlineQueryResultContact', 'InlineQueryResultDocument',
    'InlineQueryResultGif', 'InlineQueryResultLocation', 'InlineQueryResultMpeg4Gif',
    'InlineQueryResultPhoto', 'InlineQueryResultVenue', 'InlineQueryResultVideo',
    'InlineQueryResultVoice', 'InlineQueryResultGame', 'InputContactMessageContent', 'InputFile',
    'InputLocationMessageContent', 'InputMessageContent', 'InputTextMessageContent',
    'InputVenueMessageContent', 'KeyboardButton', 'Location', 'Message', 'MessageEntity',
    'ParseMode', 'PhotoSize', 'ReplyKeyboardRemove', 'ReplyKeyboardMarkup', 'ReplyMarkup',
    'Sticker', 'TelegramError', 'TelegramObject', 'Update', 'User', 'UserProfilePhotos', 'Venue',
    'Video', 'Voice', 'MAX_MESSAGE_LENGTH', 'MAX_CAPTION_LENGTH', 'SUPPORTED_WEBHOOK_PORTS',
    'MAX_FILESIZE_DOWNLOAD', 'MAX_FILESIZE_UPLOAD', 'MAX_MESSAGES_PER_SECOND_PER_CHAT',
    'MAX_MESSAGES_PER_SECOND', 'MAX_MESSAGES_PER_MINUTE_PER_GROUP', 'WebhookInfo', 'Animation',
    'Game', 'GameHighScore', 'VideoNote', 'LabeledPrice', 'SuccessfulPayment', 'ShippingOption',
    'ShippingAddress', 'PreCheckoutQuery', 'OrderInfo', 'Invoice', 'ShippingQuery', 'ChatPhoto'
]
