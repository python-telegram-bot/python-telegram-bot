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


def Updater(*args, **kwargs):
    """
    Load the updater module on invocation and return an Updater instance.
    """
    import warnings
    warnings.warn("telegram.Updater is being deprecated, please use "
                  "telegram.ext.Updater from now on.")
    from .ext.updater import Updater as Up
    return Up(*args, **kwargs)


def Dispatcher(*args, **kwargs):
    """
    Load the dispatcher module on invocation and return an Dispatcher instance.
    """
    import warnings
    warnings.warn("telegram.Dispatcher is being deprecated, please use "
                  "telegram.ext.Dispatcher from now on.")
    from .ext.dispatcher import Dispatcher as Dis
    return Dis(*args, **kwargs)


def JobQueue(*args, **kwargs):
    """
    Load the jobqueue module on invocation and return a JobQueue instance.
    """
    import warnings
    warnings.warn("telegram.JobQueue is being deprecated, please use "
                  "telegram.ext.JobQueue from now on.")
    from .ext.jobqueue import JobQueue as JobQ
    return JobQ(*args, **kwargs)


__author__ = 'devs@python-telegram-bot.org'
__version__ = '3.3'
__all__ = ('Audio', 'Bot', 'Chat', 'Emoji', 'TelegramError', 'InputFile',
           'Contact', 'ForceReply', 'ReplyKeyboardHide', 'ReplyKeyboardMarkup',
           'UserProfilePhotos', 'ChatAction', 'Location', 'Video', 'Document',
           'Sticker', 'File', 'PhotoSize', 'Update', 'ParseMode', 'Message',
           'User', 'TelegramObject', 'NullHandler', 'Voice', 'InlineQuery',
           'ReplyMarkup', 'ChosenInlineResult', 'InlineQueryResultArticle',
           'InlineQueryResultGif', 'InlineQueryResultPhoto',
           'InlineQueryResultMpeg4Gif', 'InlineQueryResultVideo')
