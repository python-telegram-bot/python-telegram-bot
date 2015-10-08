#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

__author__ = 'leandrotoledodesouza@gmail.com'
__version__ = '2.8.7'

from .base import TelegramObject
from .user import User
from .groupchat import GroupChat
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
from .update import Update
from .bot import Bot

__all__ = ['Bot', 'Emoji', 'TelegramError', 'InputFile', 'ReplyMarkup',
           'ForceReply', 'ReplyKeyboardHide', 'ReplyKeyboardMarkup',
           'UserProfilePhotos', 'ChatAction', 'Location', 'Contact',
           'Video', 'Sticker', 'Document', 'File', 'Audio', 'PhotoSize',
           'GroupChat', 'Update', 'ParseMode', 'Message', 'User',
           'TelegramObject', 'NullHandler', 'Voice']
