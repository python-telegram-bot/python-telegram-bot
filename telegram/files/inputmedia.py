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
"""Base class for Telegram InputMedia Objects."""

from telegram import TelegramObject, InputFile, PhotoSize, Animation, Video, Audio, Document


class InputMedia(TelegramObject):
    """Base class for Telegram InputMedia Objects.

    See :class:`telegram.InputMediaAnimation`, :class:`telegram.InputMediaAudio`,
    :class:`telegram.InputMediaDocument`, :class:`telegram.InputMediaPhoto` and
    :class:`telegram.InputMediaVideo` for detailed use.

    """
    pass


class InputMediaAnimation(InputMedia):
    """Represents an animation file (GIF or H.264/MPEG-4 AVC video without sound) to be sent.

    Attributes:
        type (:obj:`str`): ``animation``.
        media (:obj:`str` | `filelike object` | :class:`telegram.Animation`): Animation to
            send. Pass a file_id as String to send an animation that exists on the Telegram
            servers (recommended), pass an HTTP URL as a String for Telegram to get an
            animation from the Internet, or upload a new animation using multipart/form-data.
            Lastly you can pass an existing :class:`telegram.Animation` object to send.
        thumb (`filelike object`): Optional. Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.
        caption (:obj:`str`): Optional. Caption of the animation to be sent, 0-1024 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`): Optional. Animation width.
        height (:obj:`int`): Optional. Animation height.
        duration (:obj:`int`): Optional. Animation duration.


    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Animation` object to send.
        thumb (`filelike object`, optional): Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.
        caption (:obj:`str`, optional): Caption of the animation to be sent, 0-1024 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`, optional): Animation width.
        height (:obj:`int`, optional): Animation height.
        duration (:obj:`int`, optional): Animation duration.

    Note:
        When using a :class:`telegram.Animation` for the :attr:`media` attribute. It will take the
        width, height and duration from that video, unless otherwise specified with the optional
        arguments.
    """

    def __init__(self, media, thumb=None, caption=None, parse_mode=None, width=None, height=None,
                 duration=None):
        self.type = 'animation'

        if isinstance(media, Animation):
            self.media = media.file_id
            self.width = media.width
            self.height = media.height
            self.duration = media.duration
        elif InputFile.is_file(media):
            self.media = InputFile(media, attach=True)
        else:
            self.media = media

        if thumb:
            self.thumb = thumb
            if InputFile.is_file(self.thumb):
                self.thumb = InputFile(self.thumb, attach=True)

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


class InputMediaPhoto(InputMedia):
    """Represents a photo to be sent.

    Attributes:
        type (:obj:`str`): ``photo``.
        media (:obj:`str` | `filelike object` | :class:`telegram.PhotoSize`): Photo to send.
            Pass a file_id as String to send a photo that exists on the Telegram servers
            (recommended), pass an HTTP URL as a String for Telegram to get a photo from the
            Internet, or upload a new photo using multipart/form-data. Lastly you can pass
            an existing :class:`telegram.PhotoSize` object to send.
        caption (:obj:`str`): Optional. Caption of the photo to be sent, 0-1024 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the
            Telegram servers (recommended), pass an HTTP URL for Telegram to get a file from the
            Internet. Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.
        caption (:obj:`str`, optional ): Caption of the photo to be sent, 0-1024 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
    """

    def __init__(self, media, caption=None, parse_mode=None):
        self.type = 'photo'

        if isinstance(media, PhotoSize):
            self.media = media.file_id
        elif InputFile.is_file(media):
            self.media = InputFile(media, attach=True)
        else:
            self.media = media

        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode


class InputMediaVideo(InputMedia):
    """Represents a video to be sent.

    Attributes:
        type (:obj:`str`): ``video``.
        media (:obj:`str` | `filelike object` | :class:`telegram.Video`): Video file to send.
            Pass a file_id as String to send an video file that exists on the Telegram servers
            (recommended), pass an HTTP URL as a String for Telegram to get an video file from
            the Internet, or upload a new one using multipart/form-data. Lastly you can pass
            an existing :class:`telegram.Video` object to send.
        caption (:obj:`str`): Optional. Caption of the video to be sent, 0-1024 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`): Optional. Video width.
        height (:obj:`int`): Optional. Video height.
        duration (:obj:`int`): Optional. Video duration.
        supports_streaming (:obj:`bool`): Optional. Pass True, if the uploaded video is suitable
            for streaming.
        thumb (`filelike object`): Optional. Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Video` object to send.
        caption (:obj:`str`, optional): Caption of the video to be sent, 0-1024 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        width (:obj:`int`, optional): Video width.
        height (:obj:`int`, optional): Video height.
        duration (:obj:`int`, optional): Video duration.
        supports_streaming (:obj:`bool`, optional): Pass True, if the uploaded video is suitable
            for streaming.
        thumb (`filelike object`, optional): Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.

    Note:
        When using a :class:`telegram.Video` for the :attr:`media` attribute. It will take the
        width, height and duration from that video, unless otherwise specified with the optional
        arguments.
    """

    def __init__(self, media, caption=None, width=None, height=None, duration=None,
                 supports_streaming=None, parse_mode=None, thumb=None):
        self.type = 'video'

        if isinstance(media, Video):
            self.media = media.file_id
            self.width = media.width
            self.height = media.height
            self.duration = media.duration
        elif InputFile.is_file(media):
            self.media = InputFile(media, attach=True)
        else:
            self.media = media

        if thumb:
            self.thumb = thumb
            if InputFile.is_file(self.thumb):
                self.thumb = InputFile(self.thumb, attach=True)

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


class InputMediaAudio(InputMedia):
    """Represents an audio file to be treated as music to be sent.

    Attributes:
        type (:obj:`str`): ``audio``.
        media (:obj:`str` | `filelike object` | :class:`telegram.Audio`): Audio file to send.
            Pass a file_id as String to send an audio file that exists on the Telegram servers
            (recommended), pass an HTTP URL as a String for Telegram to get an audio file from
            the Internet, or upload a new one using multipart/form-data. Lastly you can pass
            an existing :class:`telegram.Audio` object to send.
        caption (:obj:`str`): Optional. Caption of the audio to be sent, 0-1024 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        duration (:obj:`int`): Duration of the audio in seconds.
        performer (:obj:`str`): Optional. Performer of the audio as defined by sender or by audio
            tags.
        title (:obj:`str`): Optional. Title of the audio as defined by sender or by audio tags.
        thumb (`filelike object`): Optional. Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Document` object to send.
        caption (:obj:`str`, optional): Caption of the audio to be sent, 0-1024 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        duration (:obj:`int`): Duration of the audio in seconds as defined by sender.
        performer (:obj:`str`, optional): Performer of the audio as defined by sender or by audio
            tags.
        title (:obj:`str`, optional): Title of the audio as defined by sender or by audio tags.
        thumb (`filelike object`, optional): Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.

    Note:
        When using a :class:`telegram.Audio` for the :attr:`media` attribute. It will take the
        duration, performer and title from that video, unless otherwise specified with the
        optional arguments.
    """

    def __init__(self, media, thumb=None, caption=None, parse_mode=None,
                 duration=None, performer=None, title=None):
        self.type = 'audio'

        if isinstance(media, Audio):
            self.media = media.file_id
            self.duration = media.duration
            self.performer = media.performer
            self.title = media.title
        elif InputFile.is_file(media):
            self.media = InputFile(media, attach=True)
        else:
            self.media = media

        if thumb:
            self.thumb = thumb
            if InputFile.is_file(self.thumb):
                self.thumb = InputFile(self.thumb, attach=True)

        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
        if duration:
            self.duration = duration
        if performer:
            self.performer = performer
        if title:
            self.title = title


class InputMediaDocument(InputMedia):
    """Represents a general file to be sent.

    Attributes:
        type (:obj:`str`): ``document``.
        media (:obj:`str` | `filelike object` | :class:`telegram.Document`): File to send.
            Pass a file_id as String to send a file that exists on the Telegram servers
            (recommended), pass an HTTP URL as a String for Telegram to get a file from the
            Internet, or upload a new one using multipart/form-data. Lastly you can pass
            an existing :class:`telegram.Document` object to send.
        caption (:obj:`str`): Optional. Caption of the document to be sent, 0-1024 characters.
        parse_mode (:obj:`str`): Optional. Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        thumb (`filelike object`): Optional. Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.

    Args:
        media (:obj:`str`): File to send. Pass a file_id to send a file that exists on the Telegram
            servers (recommended), pass an HTTP URL for Telegram to get a file from the Internet.
            Lastly you can pass an existing :class:`telegram.Document` object to send.
        caption (:obj:`str`, optional): Caption of the document to be sent, 0-1024 characters.
        parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to show
            bold, italic, fixed-width text or inline URLs in the media caption. See the constants
            in :class:`telegram.ParseMode` for the available modes.
        thumb (`filelike object`, optional): Thumbnail of the
            file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
            A thumbnail's width and height should not exceed 90. Ignored if the file is not
            is passed as a string or file_id.
    """

    def __init__(self, media, thumb=None, caption=None, parse_mode=None):
        self.type = 'document'

        if isinstance(media, Document):
            self.media = media.file_id
        elif InputFile.is_file(media):
            self.media = InputFile(media, attach=True)
        else:
            self.media = media

        if thumb:
            self.thumb = thumb
            if InputFile.is_file(self.thumb):
                self.thumb = InputFile(self.thumb, attach=True)

        if caption:
            self.caption = caption
        if parse_mode:
            self.parse_mode = parse_mode
