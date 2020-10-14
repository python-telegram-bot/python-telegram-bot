#!/usr/bin/env python
# pylint: disable=R0903
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
from telegram import constants


class ChatAction:
    """Helper class to provide constants for different chat actions."""

    FIND_LOCATION: str = constants.CHATACTION_FIND_LOCATION
    """:const:`telegram.constants.CHATACTION_FIND_LOCATION`"""
    RECORD_AUDIO: str = constants.CHATACTION_RECORD_AUDIO
    """:const:`telegram.constants.CHATACTION_RECORD_AUDIO`"""
    RECORD_VIDEO: str = constants.CHATACTION_RECORD_VIDEO
    """:const:`telegram.constants.CHATACTION_RECORD_VIDEO`"""
    RECORD_VIDEO_NOTE: str = constants.CHATACTION_RECORD_VIDEO_NOTE
    """:const:`telegram.constants.CHATACTION_RECORD_VIDEO_NOTE`"""
    TYPING: str = constants.CHATACTION_TYPING
    """:const:`telegram.constants.CHATACTION_TYPING`"""
    UPLOAD_AUDIO: str = constants.CHATACTION_UPLOAD_AUDIO
    """:const:`telegram.constants.CHATACTION_UPLOAD_AUDIO`"""
    UPLOAD_DOCUMENT: str = constants.CHATACTION_UPLOAD_DOCUMENT
    """:const:`telegram.constants.CHATACTION_UPLOAD_DOCUMENT`"""
    UPLOAD_PHOTO: str = constants.CHATACTION_UPLOAD_PHOTO
    """:const:`telegram.constants.CHATACTION_UPLOAD_PHOTO`"""
    UPLOAD_VIDEO: str = constants.CHATACTION_UPLOAD_VIDEO
    """:const:`telegram.constants.CHATACTION_UPLOAD_VIDEO`"""
    UPLOAD_VIDEO_NOTE: str = constants.CHATACTION_UPLOAD_VIDEO_NOTE
    """:const:`telegram.constants.CHATACTION_UPLOAD_VIDEO_NOTE`"""
