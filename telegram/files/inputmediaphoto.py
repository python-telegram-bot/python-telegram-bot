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
from telegram import InputMedia, PhotoSize


class InputMediaPhoto(InputMedia):
    """Represents a photo to be sent.

    Attributes:
        type (:obj:`str`): ``photo``.
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the
            Telegram servers (recommended), pass an HTTP URL for Telegram to get a file from the
            Internet. Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.
        caption (:obj:`str`): Optional. Caption of the photo to be sent, 0-200 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the
            Telegram servers (recommended), pass an HTTP URL for Telegram to get a file from the
            Internet. Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.
        caption (:obj:`str`, optional ): Caption of the photo to be sent, 0-200 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption.. See the constants
            in :class:`telegram.ParseMode` for the available modes.

    Note:
        At the moment using a new file is not yet supported.
    """

    # TODO: Make InputMediaPhoto, InputMediaVideo and send_media_group work with new files

    def __init__(self, media, caption=None, parse_mode=None):
        self.type = 'photo'

        if isinstance(media, PhotoSize):
            self.media = media.file_id
        elif hasattr(media, 'read'):
            raise ValueError(
                'Sending files is not supported (yet).  Use file_id, url or PhotoSize')
        else:
            self.media = media

        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
