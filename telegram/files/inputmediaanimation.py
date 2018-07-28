#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
from telegram import InputMedia, Animation


class InputMediaAnimation(InputMedia):
    """Represents an animation file (GIF or H.264/MPEG-4 AVC video without sound) to be sent.

    Attributes:
        type (:obj:`str`): ``video``.
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Animation` object to send.
        thumb (:obj:`str`): Optional. Thumbnail of the file sent. The thumbnail should be in JPEG
            format and less than 200 kB in size. A thumbnail‘s width and height should not exceed
            90. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can’t be
            reused and can be only uploaded as a new file, so you can pass
            “attach://<file_attach_name>” if the thumbnail was uploaded using multipart/form-data
            under <file_attach_name>.
        caption (:obj:`str`): Optional. Caption of the video to be sent, 0-200 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`): Optional. Animation width.
        height (:obj:`int`): Optional. Animation height.
        duration (:obj:`int`): Optional. Animation duration.


    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Video` object to send.
        thumb (:obj:`str`, optional): Thumbnail of the file sent. The thumbnail should be in JPEG
            format and less than 200 kB in size. A thumbnail‘s width and height should not exceed
            90. Ignored if the file is not uploaded using multipart/form-data. Thumbnails can’t be
            reused and can be only uploaded as a new file, so you can pass
            “attach://<file_attach_name>” if the thumbnail was uploaded using multipart/form-data
            under <file_attach_name>.
        caption (:obj:`str`, optional): Caption of the video to be sent, 0-200 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`, optional): Animation width.
        height (:obj:`int`, optional): Animation height.
        duration (:obj:`int`, optional): Animation duration.
        supports_streaming (:obj:`bool`, optional): Pass True, if the uploaded video is suitable
            for streaming.

    Note:
        When using a :class:`telegram.Animation` for the :attr:`media` attribute. It will take the
        width, height and duration from that video, unless otherwise specified with the optional
        arguments.
        At the moment using a new file is not yet supported.
    """

    # TODO: Make InputMediaPhoto, InputMediaVideo, InputMediaAnimation, send_media_group work with
    # new files

    def __init__(self, media, caption=None, width=None, height=None, duration=None,
                 supports_streaming=None, parse_mode=None):
        self.type = 'animation'

        if isinstance(media, Animation):
            self.media = media.file_id
            self.width = media.width
            self.height = media.height
            self.duration = media.duration
        elif hasattr(media, 'read'):
            raise ValueError('Sending files is not supported (yet).  Use file_id, url or Animation')
        else:
            self.media = media

        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
        if width:
            self.width = width
        if height:
            self.height = height
        if duration:
            self.duration = duration
        if supports_streaming:
            self.supports_streaming = supports_streaming
