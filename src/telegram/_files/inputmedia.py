#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
from collections.abc import Sequence
from typing import Final, Optional, Union

from telegram import constants
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.inputfile import InputFile
from telegram._files.photosize import PhotoSize
from telegram._files.video import Video
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.files import parse_file_input
from telegram._utils.types import FileInput, JSONDict, ODVInput
from telegram.constants import InputMediaType

MediaType = Union[Animation, Audio, Document, PhotoSize, Video]


class InputMedia(TelegramObject):
    """
    Base class for Telegram InputMedia Objects.

    .. versionchanged:: 20.0
        Added arguments and attributes :attr:`type`, :attr:`media`, :attr:`caption`,
            :attr:`caption_entities`, :paramref:`parse_mode`.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media_type (:obj:`str`): Type of media that the instance represents.
        media (:obj:`str` | :class:`~telegram.InputFile`): File to send.
            |fileinputnopath|
        caption (:obj:`str`, optional): Caption of the media to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after entities
            parsing.
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        parse_mode (:obj:`str`, optional): |parse_mode|

    Attributes:
        type (:obj:`str`): Type of the input media.
        media (:obj:`str` | :class:`telegram.InputFile`): Media to send.
        caption (:obj:`str`): Optional. Caption of the media to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|

    """

    __slots__ = ("caption", "caption_entities", "media", "parse_mode", "type")

    def __init__(
        self,
        media_type: str,
        media: Union[str, InputFile],
        caption: Optional[str] = None,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.InputMediaType, media_type, media_type)
        self.media: Union[str, InputFile] = media
        self.caption: Optional[str] = caption
        self.caption_entities: tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
        self.parse_mode: ODVInput[str] = parse_mode

        self._freeze()

    @staticmethod
    def _parse_thumbnail_input(thumbnail: Optional[FileInput]) -> Optional[Union[str, InputFile]]:
        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        return (
            parse_file_input(thumbnail, attach=True, local_mode=True)
            if thumbnail is not None
            else thumbnail
        )


class InputPaidMedia(TelegramObject):
    """
    Base class for Telegram InputPaidMedia Objects. Currently, it can be one of:

    * :class:`telegram.InputPaidMediaPhoto`
    * :class:`telegram.InputPaidMediaVideo`

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): Type of media that the instance represents.
        media (:obj:`str` | :class:`~telegram.InputFile`): File
            to send. |fileinputnopath|

    Attributes:
        type (:obj:`str`): Type of the input media.
        media (:obj:`str` | :class:`telegram.InputFile`): Media to send.
    """

    PHOTO: Final[str] = constants.InputPaidMediaType.PHOTO
    """:const:`telegram.constants.InputPaidMediaType.PHOTO`"""
    VIDEO: Final[str] = constants.InputPaidMediaType.VIDEO
    """:const:`telegram.constants.InputPaidMediaType.VIDEO`"""

    __slots__ = ("media", "type")

    def __init__(
        self,
        type: str,  # pylint: disable=redefined-builtin
        media: Union[str, InputFile],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.InputPaidMediaType, type, type)
        self.media: Union[str, InputFile] = media

        self._freeze()


class InputPaidMediaPhoto(InputPaidMedia):
    """The paid media to send is a photo.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 21.4

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.PhotoSize`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

    Attributes:
        type (:obj:`str`): Type of the media, always
            :tg-const:`telegram.constants.InputPaidMediaType.PHOTO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Photo to send.
    """

    __slots__ = ()

    def __init__(
        self,
        media: Union[FileInput, PhotoSize],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        media = parse_file_input(media, PhotoSize, attach=True, local_mode=True)
        super().__init__(type=InputPaidMedia.PHOTO, media=media, api_kwargs=api_kwargs)
        self._freeze()


class InputPaidMediaVideo(InputPaidMedia):
    """
    The paid media to send is a video.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 21.4

    Note:
        *  When using a :class:`telegram.Video` for the :attr:`media` attribute, it will take the
           width, height and duration from that video, unless otherwise specified with the optional
           arguments.
        *  :paramref:`thumbnail` will be ignored for small video files, for which Telegram can
           easily generate thumbnails. However, this behaviour is undocumented and might be
           changed by Telegram.

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.Video`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Video` object to send.
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|
        cover (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): Cover for the video in the message. |fileinputnopath|

            .. versionchanged:: 21.11
        start_timestamp (:obj:`int`, optional): Start timestamp for the video in the message

            .. versionchanged:: 21.11
        width (:obj:`int`, optional): Video width.
        height (:obj:`int`, optional): Video height.
        duration (:obj:`int`, optional): Video duration in seconds.
        supports_streaming (:obj:`bool`, optional): Pass :obj:`True`, if the uploaded video is
            suitable for streaming.

    Attributes:
        type (:obj:`str`): Type of the media, always
            :tg-const:`telegram.constants.InputPaidMediaType.VIDEO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Video to send.
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|
        cover (:class:`telegram.InputFile`): Optional. Cover for the video in the message.
            |fileinputnopath|

            .. versionchanged:: 21.11
        start_timestamp (:obj:`int`): Optional. Start timestamp for the video in the message

            .. versionchanged:: 21.11
        width (:obj:`int`): Optional. Video width.
        height (:obj:`int`): Optional. Video height.
        duration (:obj:`int`): Optional. Video duration in seconds.
        supports_streaming (:obj:`bool`): Optional. :obj:`True`, if the uploaded video is
            suitable for streaming.
    """

    __slots__ = (
        "cover",
        "duration",
        "height",
        "start_timestamp",
        "supports_streaming",
        "thumbnail",
        "width",
    )

    def __init__(
        self,
        media: Union[FileInput, Video],
        thumbnail: Optional[FileInput] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        supports_streaming: Optional[bool] = None,
        cover: Optional[FileInput] = None,
        start_timestamp: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        if isinstance(media, Video):
            width = width if width is not None else media.width
            height = height if height is not None else media.height
            duration = duration if duration is not None else media.duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            media = parse_file_input(media, attach=True, local_mode=True)

        super().__init__(type=InputPaidMedia.VIDEO, media=media, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.thumbnail: Optional[Union[str, InputFile]] = InputMedia._parse_thumbnail_input(
                thumbnail
            )
            self.width: Optional[int] = width
            self.height: Optional[int] = height
            self.duration: Optional[int] = duration
            self.supports_streaming: Optional[bool] = supports_streaming
            self.cover: Optional[Union[InputFile, str]] = (
                parse_file_input(cover, attach=True, local_mode=True) if cover else None
            )
            self.start_timestamp: Optional[int] = start_timestamp


class InputMediaAnimation(InputMedia):
    """Represents an animation file (GIF or H.264/MPEG-4 AVC video without sound) to be sent.

    Note:
        When using a :class:`telegram.Animation` for the :attr:`media` attribute, it will take the
        width, height and duration from that animation, unless otherwise specified with the
        optional arguments.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionchanged:: 20.5
      |removed_thumb_note|

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.Animation`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Animation` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        caption (:obj:`str`, optional): Caption of the animation to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        width (:obj:`int`, optional): Animation width.
        height (:obj:`int`, optional): Animation height.
        duration (:obj:`int`, optional): Animation duration in seconds.
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the animation needs to be covered
            with a spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.ANIMATION`.
        media (:obj:`str` | :class:`telegram.InputFile`): Animation to send.
        caption (:obj:`str`): Optional. Caption of the animation to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. The parse mode to use for text formatting.
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        width (:obj:`int`): Optional. Animation width.
        height (:obj:`int`): Optional. Animation height.
        duration (:obj:`int`): Optional. Animation duration in seconds.
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the animation is covered with a
            spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3
    """

    __slots__ = (
        "duration",
        "has_spoiler",
        "height",
        "show_caption_above_media",
        "thumbnail",
        "width",
    )

    def __init__(
        self,
        media: Union[FileInput, Animation],
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        filename: Optional[str] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        if isinstance(media, Animation):
            width = media.width if width is None else width
            height = media.height if height is None else height
            duration = media.duration if duration is None else duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            media = parse_file_input(media, filename=filename, attach=True, local_mode=True)

        super().__init__(
            InputMediaType.ANIMATION,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: Optional[Union[str, InputFile]] = self._parse_thumbnail_input(
                thumbnail
            )
            self.width: Optional[int] = width
            self.height: Optional[int] = height
            self.duration: Optional[int] = duration
            self.has_spoiler: Optional[bool] = has_spoiler
            self.show_caption_above_media: Optional[bool] = show_caption_above_media


class InputMediaPhoto(InputMedia):
    """Represents a photo to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.PhotoSize`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the photo, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        caption (:obj:`str`, optional ): Caption of the photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the photo needs to be covered
            with a spoiler animation.

            .. versionadded:: 20.0
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.PHOTO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Photo to send.
        caption (:obj:`str`): Optional. Caption of the photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the photo is covered with a
            spoiler animation.

            .. versionadded:: 20.0
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3
    """

    __slots__ = (
        "has_spoiler",
        "show_caption_above_media",
    )

    def __init__(
        self,
        media: Union[FileInput, PhotoSize],
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        filename: Optional[str] = None,
        has_spoiler: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        media = parse_file_input(media, PhotoSize, filename=filename, attach=True, local_mode=True)
        super().__init__(
            InputMediaType.PHOTO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )

        with self._unfrozen():
            self.has_spoiler: Optional[bool] = has_spoiler
            self.show_caption_above_media: Optional[bool] = show_caption_above_media


class InputMediaVideo(InputMedia):
    """Represents a video to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Note:
        *  When using a :class:`telegram.Video` for the :attr:`media` attribute, it will take the
           width, height and duration from that video, unless otherwise specified with the optional
           arguments.
        *  :paramref:`thumbnail` will be ignored for small video files, for which Telegram can
            easily generate thumbnails. However, this behaviour is undocumented and might be
            changed by Telegram.

    .. versionchanged:: 20.5
      |removed_thumb_note|

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.Video`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Video` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the video, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        caption (:obj:`str`, optional): Caption of the video to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        width (:obj:`int`, optional): Video width.
        height (:obj:`int`, optional): Video height.
        duration (:obj:`int`, optional): Video duration in seconds.
        supports_streaming (:obj:`bool`, optional): Pass :obj:`True`, if the uploaded video is
            suitable for streaming.
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the video needs to be covered
            with a spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2
        cover (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): Cover for the video in the message. |fileinputnopath|

            .. versionchanged:: 21.11
        start_timestamp (:obj:`int`, optional): Start timestamp for the video in the message

            .. versionchanged:: 21.11
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.VIDEO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Video file to send.
        caption (:obj:`str`): Optional. Caption of the video to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        width (:obj:`int`): Optional. Video width.
        height (:obj:`int`): Optional. Video height.
        duration (:obj:`int`): Optional. Video duration in seconds.
        supports_streaming (:obj:`bool`): Optional. :obj:`True`, if the uploaded video is
            suitable for streaming.
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the video is covered with a
            spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3
        cover (:class:`telegram.InputFile`): Optional. Cover for the video in the message.
            |fileinputnopath|

            .. versionchanged:: 21.11
        start_timestamp (:obj:`int`): Optional. Start timestamp for the video in the message

            .. versionchanged:: 21.11
    """

    __slots__ = (
        "cover",
        "duration",
        "has_spoiler",
        "height",
        "show_caption_above_media",
        "start_timestamp",
        "supports_streaming",
        "thumbnail",
        "width",
    )

    def __init__(
        self,
        media: Union[FileInput, Video],
        caption: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        supports_streaming: Optional[bool] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        filename: Optional[str] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        show_caption_above_media: Optional[bool] = None,
        cover: Optional[FileInput] = None,
        start_timestamp: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        if isinstance(media, Video):
            width = width if width is not None else media.width
            height = height if height is not None else media.height
            duration = duration if duration is not None else media.duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            media = parse_file_input(media, filename=filename, attach=True, local_mode=True)

        super().__init__(
            InputMediaType.VIDEO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.width: Optional[int] = width
            self.height: Optional[int] = height
            self.duration: Optional[int] = duration
            self.thumbnail: Optional[Union[str, InputFile]] = self._parse_thumbnail_input(
                thumbnail
            )
            self.supports_streaming: Optional[bool] = supports_streaming
            self.has_spoiler: Optional[bool] = has_spoiler
            self.show_caption_above_media: Optional[bool] = show_caption_above_media
            self.cover: Optional[Union[InputFile, str]] = (
                parse_file_input(cover, attach=True, local_mode=True) if cover else None
            )
            self.start_timestamp: Optional[int] = start_timestamp


class InputMediaAudio(InputMedia):
    """Represents an audio file to be treated as music to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Note:
        When using a :class:`telegram.Audio` for the :attr:`media` attribute, it will take the
        duration, performer and title from that video, unless otherwise specified with the
        optional arguments.

    .. versionchanged:: 20.5
      |removed_thumb_note|

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.Audio`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Audio` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the audio, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        caption (:obj:`str`, optional): Caption of the audio to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        duration (:obj:`int`, optional): Duration of the audio in seconds as defined by the sender.
        performer (:obj:`str`, optional): Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`, optional): Title of the audio as defined by the sender or by audio tags.
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.AUDIO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Audio file to send.
        caption (:obj:`str`): Optional. Caption of the audio to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        duration (:obj:`int`): Optional. Duration of the audio in seconds.
        performer (:obj:`str`): Optional. Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`): Optional. Title of the audio as defined by the sender or by audio tags.
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2

    """

    __slots__ = ("duration", "performer", "thumbnail", "title")

    def __init__(
        self,
        media: Union[FileInput, Audio],
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        filename: Optional[str] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        if isinstance(media, Audio):
            duration = media.duration if duration is None else duration
            performer = media.performer if performer is None else performer
            title = media.title if title is None else title
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            media = parse_file_input(media, filename=filename, attach=True, local_mode=True)

        super().__init__(
            InputMediaType.AUDIO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: Optional[Union[str, InputFile]] = self._parse_thumbnail_input(
                thumbnail
            )
            self.duration: Optional[int] = duration
            self.title: Optional[str] = title
            self.performer: Optional[str] = performer


class InputMediaDocument(InputMedia):
    """Represents a general file to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionchanged:: 20.5
      |removed_thumb_note|

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` \
            | :class:`pathlib.Path` | :class:`telegram.Document`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Document` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the document, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        caption (:obj:`str`, optional): Caption of the document to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        disable_content_type_detection (:obj:`bool`, optional): Disables automatic server-side
            content type detection for files uploaded using multipart/form-data. Always
            :obj:`True`, if the document is sent as part of an album.
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.DOCUMENT`.
        media (:obj:`str` | :class:`telegram.InputFile`): File to send.
        caption (:obj:`str`): Optional. Caption of the document to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        disable_content_type_detection (:obj:`bool`): Optional. Disables automatic server-side
            content type detection for files uploaded using multipart/form-data. Always
            :obj:`True`, if the document is sent as part of an album.
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2
    """

    __slots__ = ("disable_content_type_detection", "thumbnail")

    def __init__(
        self,
        media: Union[FileInput, Document],
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: Optional[bool] = None,
        caption_entities: Optional[Sequence[MessageEntity]] = None,
        filename: Optional[str] = None,
        thumbnail: Optional[FileInput] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        media = parse_file_input(media, Document, filename=filename, attach=True, local_mode=True)

        super().__init__(
            InputMediaType.DOCUMENT,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: Optional[Union[str, InputFile]] = self._parse_thumbnail_input(
                thumbnail
            )
            self.disable_content_type_detection: Optional[bool] = disable_content_type_detection
