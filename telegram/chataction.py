#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains an object that represents a Telegram ChatAction."""


class ChatAction(object):
    """Helper class to provide constants for different chatactions

    Attributes:
        FIND_LOCATION (str): 'find_location'
        RECORD_AUDIO (str): 'record_audio'
        RECORD_VIDEO (str): 'record_video'
        RECORD_VIDEO_NOTE (str): 'record_video_note'
        TYPING (str): 'typing'
        UPLOAD_AUDIO (str): 'upload_audio'
        UPLOAD_DOCUMENT (str): 'upload_document'
        UPLOAD_PHOTO (str): 'upload_photo'
        UPLOAD_VIDEO (str): 'upload_video'
        UPLOAD_VIDEO_NOTE (str): 'upload_video_note'
    """

    FIND_LOCATION = 'find_location'
    RECORD_AUDIO = 'record_audio'
    RECORD_VIDEO = 'record_video'
    RECORD_VIDEO_NOTE = 'record_video_note'
    TYPING = 'typing'
    UPLOAD_AUDIO = 'upload_audio'
    UPLOAD_DOCUMENT = 'upload_document'
    UPLOAD_PHOTO = 'upload_photo'
    UPLOAD_VIDEO = 'upload_video'
    UPLOAD_VIDEO_NOTE = 'upload_video_note'
