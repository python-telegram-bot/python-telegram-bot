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
"""This module contains an object that represents a Telegram InputMediaPhoto."""
from telegram import InputMedia, Video


class InputMediaVideo(InputMedia):
    """Represents a video to be sent.

    Attributes:
        type (:obj:`str`): ``video``.
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Video` object to send.
        caption (:obj:`str`): Optional. Caption of the video to be sent, 0-200 characters.
        width (:obj:`int`): Optional. Video width.
        height (:obj:`int`): Optional. Video height.
        duration (:obj:`int`): Optional. Video duration.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Video` object to send.
        caption (:obj:`str`, optional): Caption of the video to be sent, 0-200 characters.
        width (:obj:`int`, optional): Video width.
        height (:obj:`int`, optional): Video height.
        duration (:obj:`int`, optional): Video duration.

    Note:
        When using a :class:`telegram.Video` for the :attr:`media` attribute. It will take the
        width, height and duration from that video, unless otherwise specified with the optional
        arguments.
        At the moment using a new file is not yet supported.
    """

    # TODO: Make InputMediaPhoto, InputMediaVideo and send_media_group work with new files

    def __init__(self, media, caption=None, width=None, height=None, duration=None):
        self.type = 'video'

        if isinstance(media, Video):
            self.media = media.file_id
            self.width = media.width
            self.height = media.height
            self.duration = media.duration
        elif hasattr(media, 'read'):
            raise ValueError('Sending files is not supported (yet).  Use file_id, url or Video')
        else:
            self.media = media

        if caption:
            self.caption = caption
        if width:
            self.width = width
        if height:
            self.height = height
        if duration:
            self.duration = duration
