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

__author__ = 'devs@python-telegram-bot.org'
__version__ = '3.3b1'

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
from .chataction import ChatAction
from .userprofilephotos import UserProfilePhotos
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
from .message import Message
from .inlinequery import InlineQuery
from .choseninlineresult import ChosenInlineResult
from .inlinequeryresult import InlineQueryResultArticle, InlineQueryResultGif,\
    InlineQueryResultMpeg4Gif, InlineQueryResultPhoto, InlineQueryResultVideo
from .update import Update
from .bot import Bot
from .dispatcher import Dispatcher
from .jobqueue import JobQueue
from .updater import Updater

__all__ = ['Bot', 'Updater', 'Dispatcher', 'Emoji', 'TelegramError',
           'InputFile', 'ReplyMarkup', 'ForceReply', 'ReplyKeyboardHide',
           'ReplyKeyboardMarkup', 'UserProfilePhotos', 'ChatAction',
           'Location', 'Contact', 'Video', 'Sticker', 'Document', 'File',
           'Audio', 'PhotoSize', 'Chat', 'Update', 'ParseMode', 'Message',
           'User', 'TelegramObject', 'NullHandler', 'Voice', 'JobQueue',
           'InlineQuery', 'ChosenInlineResult', 'InlineQueryResultArticle',
           'InlineQueryResultGif', 'InlineQueryResultPhoto',
           'InlineQueryResultMpeg4Gif', 'InlineQueryResultVideo']
