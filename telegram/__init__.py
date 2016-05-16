#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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

from sys import version_info

from .base import TelegramObject
from .user import User
from .chat import Chat
from .photosize import PhotoSize
from .audio import Audio
from .voice import Voice
from .document import Document
from .sticker import Sticker
from .video import Video
from .contact import Contact
from .location import Location
from .venue import Venue
from .chataction import ChatAction
from .userprofilephotos import UserProfilePhotos
from .keyboardbutton import KeyboardButton
from .replymarkup import ReplyMarkup
from .replykeyboardmarkup import ReplyKeyboardMarkup
from .replykeyboardhide import ReplyKeyboardHide
from .forcereply import ForceReply
from .error import TelegramError
from .inputfile import InputFile
from .file import File
from .nullhandler import NullHandler
from .emoji import Emoji
from .parsemode import ParseMode
from .messageentity import MessageEntity
from .message import Message
from .inputmessagecontent import InputMessageContent
from .callbackquery import CallbackQuery
from .choseninlineresult import ChosenInlineResult
from .inlinekeyboardbutton import InlineKeyboardButton
from .inlinekeyboardmarkup import InlineKeyboardMarkup
from .inlinequery import InlineQuery
from .inlinequeryresult import InlineQueryResult
from .inlinequeryresultarticle import InlineQueryResultArticle
from .inlinequeryresultaudio import InlineQueryResultAudio
from .inlinequeryresultcachedaudio import InlineQueryResultCachedAudio
from .inlinequeryresultcacheddocument import InlineQueryResultCachedDocument
from .inlinequeryresultcachedgif import InlineQueryResultCachedGif
from .inlinequeryresultcachedmpeg4gif import InlineQueryResultCachedMpeg4Gif
from .inlinequeryresultcachedphoto import InlineQueryResultCachedPhoto
from .inlinequeryresultcachedsticker import InlineQueryResultCachedSticker
from .inlinequeryresultcachedvideo import InlineQueryResultCachedVideo
from .inlinequeryresultcachedvoice import InlineQueryResultCachedVoice
from .inlinequeryresultcontact import InlineQueryResultContact
from .inlinequeryresultdocument import InlineQueryResultDocument
from .inlinequeryresultgif import InlineQueryResultGif
from .inlinequeryresultlocation import InlineQueryResultLocation
from .inlinequeryresultmpeg4gif import InlineQueryResultMpeg4Gif
from .inlinequeryresultphoto import InlineQueryResultPhoto
from .inlinequeryresultvenue import InlineQueryResultVenue
from .inlinequeryresultvideo import InlineQueryResultVideo
from .inlinequeryresultvoice import InlineQueryResultVoice
from .inputtextmessagecontent import InputTextMessageContent
from .inputlocationmessagecontent import InputLocationMessageContent
from .inputvenuemessagecontent import InputVenueMessageContent
from .inputcontactmessagecontent import InputContactMessageContent
from .update import Update
from .bot import Bot

__author__ = 'devs@python-telegram-bot.org'
__version__ = '4.1.1'
__all__ = ['Audio', 'Bot', 'Chat', 'ChatAction', 'ChosenInlineResult', 'CallbackQuery', 'Contact',
           'Document', 'Emoji', 'File', 'ForceReply', 'InlineKeyboardButton',
           'InlineKeyboardMarkup', 'InlineQuery', 'InlineQueryResult', 'InlineQueryResult',
           'InlineQueryResultArticle', 'InlineQueryResultAudio', 'InlineQueryResultCachedAudio',
           'InlineQueryResultCachedDocument', 'InlineQueryResultCachedGif',
           'InlineQueryResultCachedMpeg4Gif', 'InlineQueryResultCachedPhoto',
           'InlineQueryResultCachedSticker', 'InlineQueryResultCachedVideo',
           'InlineQueryResultCachedVoice', 'InlineQueryResultContact', 'InlineQueryResultDocument',
           'InlineQueryResultGif', 'InlineQueryResultLocation', 'InlineQueryResultMpeg4Gif',
           'InlineQueryResultPhoto', 'InlineQueryResultVenue', 'InlineQueryResultVideo',
           'InlineQueryResultVoice', 'InputContactMessageContent', 'InputFile',
           'InputLocationMessageContent', 'InputMessageContent', 'InputTextMessageContent',
           'InputVenueMessageContent', 'KeyboardButton', 'Location', 'Message', 'MessageEntity',
           'NullHandler', 'ParseMode', 'PhotoSize', 'ReplyKeyboardHide', 'ReplyKeyboardMarkup',
           'ReplyMarkup', 'Sticker', 'TelegramError', 'TelegramObject', 'Update', 'User',
           'UserProfilePhotos', 'Venue', 'Video', 'Voice']

if version_info < (2, 7):
    from warnings import warn
    warn("python-telegram-bot will stop supporting Python 2.6 in a future release. "
         "Please upgrade your Python!")
