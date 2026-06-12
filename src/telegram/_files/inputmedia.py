#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""Base classes for Telegram InputMedia, InputPaidMedia, InputPollMedia
and InputPollOptionMedia Objects."""

import datetime as dtm
from collections.abc import Sequence
from typing import TYPE_CHECKING, Final, TypeAlias

from telegram import constants
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.inputfile import InputFile
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import Sticker
from telegram._files.video import Video
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg, to_timedelta
from telegram._utils.datetime import get_timedelta_value
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.files import parse_file_input
from telegram._utils.types import JSONDict, ODVInput, TimePeriod
from telegram._utils.warnings import warn
from telegram.constants import BaseInputMediaType
from telegram.warnings import PTBDeprecationWarning

if TYPE_CHECKING:
    from telegram._utils.types import FileInput


class _BaseInputMedia(TelegramObject):
    """
    Base class for objects representing the various input media types.

    Args:
        media_type (:obj:`str`): Type of media that the instance represents.

    Attributes:
        type (:obj:`str`): Type of media that the instance represents.
    """

    __slots__ = ("type",)

    def __init__(
        self,
        media_type: str,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.BaseInputMediaType, media_type, media_type)


class InputMedia(_BaseInputMedia):
    """
    This object represents the content of a media message to be sent. It should be one of:

    * :class:`telegram.InputMediaAnimation`
    * :class:`telegram.InputMediaAudio`
    * :class:`telegram.InputMediaDocument`
    * :class:`telegram.InputMediaLivePhoto`
    * :class:`telegram.InputMediaPhoto`
    * :class:`telegram.InputMediaVideo`

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

    __slots__ = ("caption", "caption_entities", "media", "parse_mode")

    def __init__(
        self,
        media_type: str,
        media: str | InputFile,
        caption: str | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(media_type=media_type, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.media: str | InputFile = media
            self.caption: str | None = caption
            self.caption_entities: tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
            self.parse_mode: ODVInput[str] = parse_mode

    @staticmethod
    def _parse_thumbnail_input(thumbnail: "FileInput | None") -> str | InputFile | None:
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
    * :class:`telegram.InputPaidMediaLivePhoto`

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
    LIVE_PHOTO: Final[str] = constants.InputPaidMediaType.LIVE_PHOTO
    """:const:`telegram.constants.InputPaidMediaType.LIVE_PHOTO`

    .. versionadded:: 22.8
    """

    __slots__ = ("media", "type")

    def __init__(
        self,
        type: str,  # pylint: disable=redefined-builtin
        media: str | InputFile,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = enum.get_member(constants.InputPaidMediaType, type, type)
        self.media: str | InputFile = media

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
        media: "FileInput | PhotoSize",
        *,
        api_kwargs: JSONDict | None = None,
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
        duration (:obj:`int` | :class:`datetime.timedelta`, optional): Video duration in seconds.

            .. versionchanged:: v22.2
                |time-period-input|
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
        duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Video duration in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        supports_streaming (:obj:`bool`): Optional. :obj:`True`, if the uploaded video is
            suitable for streaming.
    """

    __slots__ = (
        "_duration",
        "cover",
        "height",
        "start_timestamp",
        "supports_streaming",
        "thumbnail",
        "width",
    )

    def __init__(
        self,
        media: "FileInput | Video",
        thumbnail: "FileInput | None" = None,
        width: int | None = None,
        height: int | None = None,
        duration: TimePeriod | None = None,
        supports_streaming: bool | None = None,
        cover: "FileInput | None" = None,
        start_timestamp: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        if isinstance(media, Video):
            width = width if width is not None else media.width
            height = height if height is not None else media.height
            duration = duration if duration is not None else media._duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            media = parse_file_input(media, attach=True, local_mode=True)

        super().__init__(type=InputPaidMedia.VIDEO, media=media, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.thumbnail: str | InputFile | None = InputMedia._parse_thumbnail_input(thumbnail)
            self.width: int | None = width
            self.height: int | None = height
            self._duration: dtm.timedelta | None = to_timedelta(duration)
            self.supports_streaming: bool | None = supports_streaming
            self.cover: InputFile | str | None = (
                parse_file_input(cover, attach=True, local_mode=True) if cover else None
            )
            self.start_timestamp: int | None = start_timestamp

    @property
    def duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._duration, attribute="duration")


class InputPaidMediaLivePhoto(InputPaidMedia):
    """
    The paid media to send is a live photo.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 22.8

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` \
            | :class:`pathlib.Path` | :class:`~telegram.Video`): Video of the live photo to send.
           Pass a ``file_id`` to send a file that exists on the Telegram servers (recommended).
           |uploadinputnopath| Sending live photos by a URL is currently unsupported. Lastly you
           can pass an existing :class:`telegram.Video` object to send.
        photo (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`~telegram.PhotoSize`): Photo of the live photo to send.
            Pass a ``file_id`` to send a file that exists on the Telegram servers (recommended).
            |uploadinputnopath| Sending live photos by a URL is currently unsupported.
            Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

    Attributes:
        type (:obj:`str`): Type of the media, always
            :tg-const:`telegram.constants.InputPaidMediaType.LIVE_PHOTO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Video of the live photo to send.
            |fileinputnopath|
        photo (:obj:`str` | :class:`telegram.InputFile`): Photo of the live photo to send.
            |fileinputnopath|
    """

    __slots__ = ("photo",)

    def __init__(
        self,
        media: "FileInput | Video",
        photo: "FileInput | PhotoSize",
        *,
        api_kwargs: JSONDict | None = None,
    ):
        media = parse_file_input(media, tg_type=Video, attach=True, local_mode=True)
        photo = parse_file_input(photo, tg_type=PhotoSize, attach=True, local_mode=True)
        super().__init__(type=InputPaidMedia.LIVE_PHOTO, media=media, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.photo: str | InputFile = photo


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
        filename_depr (:obj:`str`, optional): Positional placeholder for keyword only parameter
            :paramref:`filename`. For backward compatibility.

            .. versionadded:: 22.8
            .. deprecated:: 22.8
                This parameter is deprecated, use :paramref:`filename` instead.
        caption (:obj:`str`, optional): Caption of the animation to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        width (:obj:`int`, optional): Animation width.
        height (:obj:`int`, optional): Animation height.
        duration (:obj:`int` | :class:`datetime.timedelta`, optional): Animation duration
            in seconds.

            .. versionchanged:: v22.2
                |time-period-input|
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the animation needs to be covered
            with a spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|

            .. versionadded:: 21.3

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
            .. versionchanged:: 22.8
               This parameter is now keyword-only.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.ANIMATION`.
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
        duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Animation duration
            in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the animation is covered with a
            spoiler animation.

            .. versionadded:: 20.0
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|

            .. versionadded:: 21.3
    """

    __slots__ = (
        "_duration",
        "has_spoiler",
        "height",
        "show_caption_above_media",
        "thumbnail",
        "width",
    )

    def __init__(
        self,
        media: "FileInput | Animation",
        caption: str | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        width: int | None = None,
        height: int | None = None,
        duration: TimePeriod | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        # tag: deprecated 22.8
        filename_depr: str | None = None,
        # -
        has_spoiler: bool | None = None,
        thumbnail: "FileInput | None" = None,
        show_caption_above_media: bool | None = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        if filename_depr is not None and filename is not None:
            raise ValueError("`filename_depr` and `filename` are mutually exclusive.")
        if filename_depr is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "Positional passing of `filename` or keyword usage of `filename_depr`"
                    " is deprecated. `filename` will become a keyword-only argument.",
                ),
                stacklevel=2,
            )

        if isinstance(media, Animation):
            width = media.width if width is None else width
            height = media.height if height is None else height
            duration = duration if duration is not None else media._duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            effective_filename = filename_depr or filename
            media = parse_file_input(
                media, filename=effective_filename, attach=True, local_mode=True
            )

        super().__init__(
            BaseInputMediaType.ANIMATION,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: str | InputFile | None = self._parse_thumbnail_input(thumbnail)
            self.width: int | None = width
            self.height: int | None = height
            self._duration: dtm.timedelta | None = to_timedelta(duration)
            self.has_spoiler: bool | None = has_spoiler
            self.show_caption_above_media: bool | None = show_caption_above_media

    @property
    def duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._duration, attribute="duration")


class InputMediaPhoto(InputMedia):
    """Represents a photo to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.PhotoSize`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.PhotoSize` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename_depr (:obj:`str`, optional): Positional placeholder for keyword only parameter
            :paramref:`filename`. For backward compatibility.

            .. versionadded:: 22.8
            .. deprecated:: 22.8
                This parameter is deprecated, use :paramref:`filename` instead.
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

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the photo, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
            .. versionchanged:: 22.8
               This parameter is now keyword-only.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.PHOTO`.
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
        media: "FileInput | PhotoSize",
        caption: str | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence[MessageEntity] | None = None,
        # tag: deprecated 22.8
        filename_depr: str | None = None,
        # -
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        if filename_depr is not None and filename is not None:
            raise ValueError("`filename_depr` and `filename` are mutually exclusive.")
        if filename_depr is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "Positional passing of `filename` or keyword usage of `filename_depr`"
                    " is deprecated. `filename` will become a keyword-only argument.",
                ),
                stacklevel=2,
            )

        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        effective_filename = filename_depr or filename
        media = parse_file_input(
            media, PhotoSize, filename=effective_filename, attach=True, local_mode=True
        )
        super().__init__(
            BaseInputMediaType.PHOTO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )

        with self._unfrozen():
            self.has_spoiler: bool | None = has_spoiler
            self.show_caption_above_media: bool | None = show_caption_above_media


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
        filename_depr (:obj:`str`, optional): Positional placeholder for keyword only parameter
            :paramref:`filename`. For backward compatibility.

            .. versionadded:: 22.8
            .. deprecated:: 22.8
                This parameter is deprecated, use :paramref:`filename` instead.
        caption (:obj:`str`, optional): Caption of the video to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        width (:obj:`int`, optional): Video width.
        height (:obj:`int`, optional): Video height.
        duration (:obj:`int` | :class:`datetime.timedelta`, optional): Video duration in seconds.

            .. versionchanged:: v22.2
                |time-period-input|
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

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the video, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
            .. versionchanged:: 22.8
               This parameter is now keyword-only.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.VIDEO`.
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
        duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Video duration in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
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
        "_duration",
        "cover",
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
        media: "FileInput | Video",
        caption: str | None = None,
        width: int | None = None,
        height: int | None = None,
        duration: TimePeriod | None = None,
        supports_streaming: bool | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence[MessageEntity] | None = None,
        # tag: deprecated 22.8
        filename_depr: str | None = None,
        # -
        has_spoiler: bool | None = None,
        thumbnail: "FileInput | None" = None,
        show_caption_above_media: bool | None = None,
        cover: "FileInput | None" = None,
        start_timestamp: int | None = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        if filename_depr is not None and filename is not None:
            raise ValueError("`filename_depr` and `filename` are mutually exclusive.")
        if filename_depr is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "Positional passing of `filename` or keyword usage of `filename_depr`"
                    " is deprecated. `filename` will become a keyword-only argument.",
                ),
                stacklevel=2,
            )

        if isinstance(media, Video):
            width = width if width is not None else media.width
            height = height if height is not None else media.height
            duration = duration if duration is not None else media._duration
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            effective_filename = filename_depr or filename
            media = parse_file_input(
                media, filename=effective_filename, attach=True, local_mode=True
            )

        super().__init__(
            BaseInputMediaType.VIDEO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.width: int | None = width
            self.height: int | None = height
            self._duration: dtm.timedelta | None = to_timedelta(duration)
            self.thumbnail: str | InputFile | None = self._parse_thumbnail_input(thumbnail)
            self.supports_streaming: bool | None = supports_streaming
            self.has_spoiler: bool | None = has_spoiler
            self.show_caption_above_media: bool | None = show_caption_above_media
            self.cover: InputFile | str | None = (
                parse_file_input(cover, attach=True, local_mode=True) if cover else None
            )
            self.start_timestamp: int | None = start_timestamp

    @property
    def duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._duration, attribute="duration")


class InputMediaLocation(_BaseInputMedia):
    """Represents a location to be sent.

    .. versionadded:: 22.8

    Args:
        latitude (:obj:`float`): Latitude of the location.
        longitude (:obj:`float`): Longitude of the location.
        horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the location,
            measured in meters; 0-:tg-const:`telegram.Location.HORIZONTAL_ACCURACY`.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.LOCATION`.
        latitude (:obj:`float`): Latitude of the location.
        longitude (:obj:`float`): Longitude of the location.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters; 0-:tg-const:`telegram.Location.HORIZONTAL_ACCURACY`.
    """

    __slots__ = ("horizontal_accuracy", "latitude", "longitude")

    def __init__(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(media_type=BaseInputMediaType.LOCATION, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.latitude: float = latitude
            self.longitude: float = longitude
            self.horizontal_accuracy: float | None = horizontal_accuracy


class InputMediaVenue(_BaseInputMedia):
    """Represents a venue to be sent.

    .. versionadded:: 22.8

    Args:
        latitude (:obj:`float`): Latitude of the location.
        longitude (:obj:`float`): Longitude of the location.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known. (For
            example, ``“arts_entertainment/default”``, ``“arts_entertainment/aquarium”``
            or ``“food/icecream”``).
        google_place_id (:obj:`str`, optional): Google Places identifier of the venue.
        google_place_type (:obj:`str`, optional): Google Places type of the venue. (See\
        `supported types <https://developers.google.com/places/web-service/supported_types>`__)

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.VENUE`.
        latitude (:obj:`float`): Latitude of the location.
        longitude (:obj:`float`): Longitude of the location.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue, if known. (For
            example, ``“arts_entertainment/default”``, ``“arts_entertainment/aquarium”``
            or ``“food/icecream”``).
        google_place_id (:obj:`str`): Optional. Google Places identifier of the venue.
        google_place_type (:obj:`str`): Optional. Google Places type of the venue. (See\
        `supported types <https://developers.google.com/places/web-service/supported_types>`__)
    """

    __slots__ = (
        "address",
        "foursquare_id",
        "foursquare_type",
        "google_place_id",
        "google_place_type",
        "latitude",
        "longitude",
        "title",
    )

    def __init__(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str | None = None,
        foursquare_type: str | None = None,
        google_place_id: str | None = None,
        google_place_type: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(media_type=BaseInputMediaType.VENUE, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.latitude: float = latitude
            self.longitude: float = longitude
            self.title: str = title
            self.address: str = address
            self.foursquare_id: str | None = foursquare_id
            self.foursquare_type: str | None = foursquare_type
            self.google_place_id: str | None = google_place_id
            self.google_place_type: str | None = google_place_type


class InputMediaSticker(_BaseInputMedia):
    """Represents a sticker file to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 22.8

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` | \
            :class:`pathlib.Path` | :class:`telegram.Sticker`): File to send. |fileinputnopath|

            Lastly you can pass an existing :class:`telegram.Sticker` object to send.
        emoji (:obj:`str`, optional): Emoji associated with the sticker; only for just uploaded
            stickers.

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the sticker, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.STICKER`.
        media (:obj:`str` | :class:`telegram.InputFile`): Sticker file to send.
        emoji (:obj:`str`): Optional. Emoji associated with the sticker; only for just uploaded
            stickers.
    """

    __slots__ = ("emoji", "media")

    def __init__(
        self,
        media: "FileInput | Sticker",
        emoji: str | None = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        media = parse_file_input(media, Sticker, filename=filename, attach=True, local_mode=True)

        super().__init__(media_type=BaseInputMediaType.STICKER, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.media: str | InputFile = media
            self.emoji: str | None = emoji


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
        filename_depr (:obj:`str`, optional): Positional placeholder for keyword only parameter
            :paramref:`filename`. For backward compatibility.

            .. versionadded:: 22.8
            .. deprecated:: 22.8
                This parameter is deprecated, use :paramref:`filename` instead.
        caption (:obj:`str`, optional): Caption of the audio to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        duration (:obj:`int` | :class:`datetime.timedelta`, optional): Duration of the audio
            in seconds as defined by the sender.

            .. versionchanged:: v22.2
                |time-period-input|
        performer (:obj:`str`, optional): Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`, optional): Title of the audio as defined by the sender or by audio tags.
        thumbnail (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionadded:: 20.2

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the audio, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
            .. versionchanged:: 22.8
               This parameter is now keyword-only.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.AUDIO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Audio file to send.
        caption (:obj:`str`): Optional. Caption of the audio to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Duration of the audio
            in seconds.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        performer (:obj:`str`): Optional. Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`): Optional. Title of the audio as defined by the sender or by audio tags.
        thumbnail (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

            .. versionadded:: 20.2

    """

    __slots__ = ("_duration", "performer", "thumbnail", "title")

    def __init__(
        self,
        media: "FileInput | Audio",
        caption: str | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        duration: TimePeriod | None = None,
        performer: str | None = None,
        title: str | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        # tag: deprecated 22.8
        filename_depr: str | None = None,
        # -
        thumbnail: "FileInput | None" = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        if filename_depr is not None and filename is not None:
            raise ValueError("`filename_depr` and `filename` are mutually exclusive.")
        if filename_depr is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "Positional passing of `filename` or keyword usage of `filename_depr`"
                    " is deprecated. `filename` will become a keyword-only argument.",
                ),
                stacklevel=2,
            )

        if isinstance(media, Audio):
            duration = duration if duration is not None else media._duration
            performer = media.performer if performer is None else performer
            title = media.title if title is None else title
            media = media.file_id
        else:
            # We use local_mode=True because we don't have access to the actual setting and want
            # things to work in local mode.
            effective_filename = filename_depr or filename
            media = parse_file_input(
                media, filename=effective_filename, attach=True, local_mode=True
            )

        super().__init__(
            BaseInputMediaType.AUDIO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: str | InputFile | None = self._parse_thumbnail_input(thumbnail)
            self._duration: dtm.timedelta | None = to_timedelta(duration)
            self.title: str | None = title
            self.performer: str | None = performer

    @property
    def duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._duration, attribute="duration")


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
        filename_depr (:obj:`str`, optional): Positional placeholder for keyword only parameter
            :paramref:`filename`. For backward compatibility.

            .. versionadded:: 22.8
            .. deprecated:: 22.8
                This parameter is deprecated, use :paramref:`filename` instead.
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

    Keyword Args:
        filename (:obj:`str`, optional): Custom file name for the document, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
            .. versionchanged:: 22.8
               This parameter is now keyword-only.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.DOCUMENT`.
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
        media: "FileInput | Document",
        caption: str | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: bool | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        # tag: deprecated 22.8
        filename_depr: str | None = None,
        # -
        thumbnail: "FileInput | None" = None,
        *,
        filename: str | None = None,
        api_kwargs: JSONDict | None = None,
    ):
        if filename_depr is not None and filename is not None:
            raise ValueError("`filename_depr` and `filename` are mutually exclusive.")
        if filename_depr is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "Positional passing of `filename` or keyword usage of `filename_depr`"
                    " is deprecated. `filename` will become a keyword-only argument.",
                ),
                stacklevel=2,
            )

        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        effective_filename = filename_depr or filename
        media = parse_file_input(
            media, Document, filename=effective_filename, attach=True, local_mode=True
        )

        super().__init__(
            BaseInputMediaType.DOCUMENT,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.thumbnail: str | InputFile | None = self._parse_thumbnail_input(thumbnail)
            self.disable_content_type_detection: bool | None = disable_content_type_detection


class InputMediaLivePhoto(InputMedia):
    """Represents a live photo to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    .. versionadded:: 22.8

    Args:
        media (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` \
            | :class:`pathlib.Path` | :class:`~telegram.Video`): Video of the live photo to send.
           Pass a ``file_id`` to send a file that exists on the Telegram servers (recommended).
           |uploadinputnopath| Sending live photos by a URL is currently unsupported. Lastly
           you can pass an existing :class:`telegram.Video` object to send.
        photo (:obj:`str` | :term:`file object` | :class:`~telegram.InputFile` | :obj:`bytes` \
            | :class:`pathlib.Path` | :class:`~telegram.PhotoSize`): The static photo to send.
            Pass a ``file_id`` to send a file that exists on the Telegram servers (recommended).
            |uploadinputnopath| Sending live photos by a URL is currently unsupported. Lastly
            you can pass an existing :class:`telegram.PhotoSize` object to send.
        caption (:obj:`str`, optional): Caption of the live photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters after
            entities parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        caption_entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|
        show_caption_above_media (:obj:`bool`, optional): Pass |show_cap_above_med|
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the video needs to be covered
            with a spoiler animation.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.BaseInputMediaType.LIVE_PHOTO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Video of the live photo to send.
        photo (:obj:`str` | :class:`telegram.InputFile`): The static photo to send.
        caption (:obj:`str`): Optional. Caption of the live photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|
        show_caption_above_media (:obj:`bool`): Optional. |show_cap_above_med|
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the video is covered with a
            spoiler animation.
    """

    __slots__ = ("has_spoiler", "photo", "show_caption_above_media")

    def __init__(
        self,
        media: "FileInput | Video",
        photo: "FileInput | PhotoSize",
        caption: str | None = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence[MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        media = parse_file_input(media, tg_type=Video, attach=True, local_mode=True)
        photo = parse_file_input(photo, tg_type=PhotoSize, attach=True, local_mode=True)

        super().__init__(
            BaseInputMediaType.LIVE_PHOTO,
            media,
            caption,
            caption_entities,
            parse_mode,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            self.photo: str | InputFile = photo
            self.show_caption_above_media: bool | None = show_caption_above_media
            self.has_spoiler: bool | None = has_spoiler


InputPollMedia: TypeAlias = (
    InputMediaAnimation
    | InputMediaAudio
    | InputMediaDocument
    | InputMediaLivePhoto
    | InputMediaLocation
    | InputMediaPhoto
    | InputMediaVenue
    | InputMediaVideo
)
"""Type alias for InputPollMedia objects.

versionadded:: 22.8
"""

InputPollOptionMedia: TypeAlias = (
    InputMediaAnimation
    | InputMediaLivePhoto
    | InputMediaLocation
    | InputMediaPhoto
    | InputMediaSticker
    | InputMediaVenue
    | InputMediaVideo
)
"""Type alias for InputPollOptionMedia objects.

.. versionadded:: 22.8
"""
