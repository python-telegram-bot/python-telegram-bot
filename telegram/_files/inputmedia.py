#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
from typing import Optional, Sequence, Tuple, Union

from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.inputfile import InputFile
from telegram._files.photosize import PhotoSize
from telegram._files.video import Video
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
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
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.Animation` |  :class:`telegram.Audio` | \
            :class:`telegram.Document` | :class:`telegram.PhotoSize` | \
            :class:`telegram.Video`): File to send.
            |fileinputnopath|
            Lastly you can pass an existing telegram media object of the corresponding type
            to send.
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
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|

    """

    __slots__ = ("caption", "caption_entities", "media", "parse_mode", "type")

    def __init__(
        self,
        media_type: str,
        media: Union[str, InputFile, MediaType],
        caption: str = None,
        caption_entities: Sequence[MessageEntity] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = media_type
        self.media: Union[str, InputFile, Animation, Audio, Document, PhotoSize, Video] = media
        self.caption: Optional[str] = caption
        self.caption_entities: Tuple[MessageEntity, ...] = parse_sequence_arg(caption_entities)
        self.parse_mode: ODVInput[str] = parse_mode

        self._freeze()

    @staticmethod
    def _parse_thumb_input(thumb: Optional[FileInput]) -> Optional[Union[str, InputFile]]:
        # We use local_mode=True because we don't have access to the actual setting and want
        # things to work in local mode.
        return (
            parse_file_input(thumb, attach=True, local_mode=True) if thumb is not None else thumb
        )


class InputMediaAnimation(InputMedia):
    """Represents an animation file (GIF or H.264/MPEG-4 AVC video without sound) to be sent.

    Note:
        When using a :class:`telegram.Animation` for the :attr:`media` attribute, it will take the
        width, height and duration from that video, unless otherwise specified with the optional
        arguments.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.Animation`): File to send. |fileinputnopath|
            Lastly you can pass an existing :class:`telegram.Animation` object to send.

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        filename (:obj:`str`, optional): Custom file name for the animation, when uploading a
            new file. Convenience parameter, useful e.g. when sending files generated by the
            :obj:`tempfile` module.

            .. versionadded:: 13.1
        thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
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

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.ANIMATION`.
        media (:obj:`str` | :class:`telegram.InputFile`): Animation to send.
        thumb (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|
        caption (:obj:`str`): Optional. Caption of the animation to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. The parse mode to use for text formatting.
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        width (:obj:`int`): Optional. Animation width.
        height (:obj:`int`): Optional. Animation height.
        duration (:obj:`int`): Optional. Animation duration in seconds.
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the animation is covered with a
            spoiler animation.

            .. versionadded:: 20.0
    """

    __slots__ = ("duration", "height", "thumb", "width", "has_spoiler")

    def __init__(
        self,
        media: Union[FileInput, Animation],
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        width: int = None,
        height: int = None,
        duration: int = None,
        caption_entities: Sequence[MessageEntity] = None,
        filename: str = None,
        has_spoiler: bool = None,
        *,
        api_kwargs: JSONDict = None,
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
            self.thumb: Optional[Union[str, InputFile]] = self._parse_thumb_input(thumb)
            self.width: Optional[int] = width
            self.height: Optional[int] = height
            self.duration: Optional[int] = duration
            self.has_spoiler: Optional[bool] = has_spoiler


class InputMediaPhoto(InputMedia):
    """Represents a photo to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.PhotoSize`): File to send. |fileinputnopath|
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

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.PHOTO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Photo to send.
        caption (:obj:`str`): Optional. Caption of the photo to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the photo is covered with a
            spoiler animation.

            .. versionadded:: 20.0
    """

    __slots__ = ("has_spoiler",)

    def __init__(
        self,
        media: Union[FileInput, PhotoSize],
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Sequence[MessageEntity] = None,
        filename: str = None,
        has_spoiler: bool = None,
        *,
        api_kwargs: JSONDict = None,
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


class InputMediaVideo(InputMedia):
    """Represents a video to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Note:
        *  When using a :class:`telegram.Video` for the :attr:`media` attribute, it will take the
           width, height and duration from that video, unless otherwise specified with the optional
           arguments.
        *  :paramref:`thumb` will be ignored for small video files, for which Telegram can easily
           generate thumbnails. However, this behaviour is undocumented and might be changed
           by Telegram.

    Args:
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.Video`): File to send. |fileinputnopath|
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
        thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        has_spoiler (:obj:`bool`, optional): Pass :obj:`True`, if the video needs to be covered
            with a spoiler animation.

            .. versionadded:: 20.0

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.VIDEO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Video file to send.
        caption (:obj:`str`): Optional. Caption of the video to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        width (:obj:`int`): Optional. Video width.
        height (:obj:`int`): Optional. Video height.
        duration (:obj:`int`): Optional. Video duration in seconds.
        supports_streaming (:obj:`bool`): Optional. :obj:`True`, if the uploaded video is
            suitable for streaming.
        thumb (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|
        has_spoiler (:obj:`bool`): Optional. :obj:`True`, if the video is covered with a
            spoiler animation.

            .. versionadded:: 20.0
    """

    __slots__ = ("duration", "height", "thumb", "supports_streaming", "width", "has_spoiler")

    def __init__(
        self,
        media: Union[FileInput, Video],
        caption: str = None,
        width: int = None,
        height: int = None,
        duration: int = None,
        supports_streaming: bool = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        caption_entities: Sequence[MessageEntity] = None,
        filename: str = None,
        has_spoiler: bool = None,
        *,
        api_kwargs: JSONDict = None,
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
            self.thumb: Optional[Union[str, InputFile]] = self._parse_thumb_input(thumb)
            self.supports_streaming: Optional[bool] = supports_streaming
            self.has_spoiler: Optional[bool] = has_spoiler


class InputMediaAudio(InputMedia):
    """Represents an audio file to be treated as music to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Note:
        When using a :class:`telegram.Audio` for the :attr:`media` attribute, it will take the
        duration, performer and title from that video, unless otherwise specified with the
        optional arguments.

    Args:
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.Audio`): File to send. |fileinputnopath|
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

        duration (:obj:`int`, optional): Duration of the audio in seconds as defined by sender.
        performer (:obj:`str`, optional): Performer of the audio as defined by sender or by audio
            tags.
        title (:obj:`str`, optional): Title of the audio as defined by sender or by audio tags.
        thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.AUDIO`.
        media (:obj:`str` | :class:`telegram.InputFile`): Audio file to send.
        caption (:obj:`str`): Optional. Caption of the audio to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        duration (:obj:`int`): Optional. Duration of the audio in seconds.
        performer (:obj:`str`): Optional. Performer of the audio as defined by sender or by audio
            tags.
        title (:obj:`str`): Optional. Title of the audio as defined by sender or by audio tags.
        thumb (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|

    """

    __slots__ = ("duration", "performer", "thumb", "title")

    def __init__(
        self,
        media: Union[FileInput, Audio],
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption_entities: Sequence[MessageEntity] = None,
        filename: str = None,
        *,
        api_kwargs: JSONDict = None,
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
            self.thumb: Optional[Union[str, InputFile]] = self._parse_thumb_input(thumb)
            self.duration: Optional[int] = duration
            self.title: Optional[str] = title
            self.performer: Optional[str] = performer


class InputMediaDocument(InputMedia):
    """Represents a general file to be sent.

    .. seealso:: :wiki:`Working with Files and Media <Working-with-Files-and-Media>`

    Args:
        media (:obj:`str` | :term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | \
            :class:`telegram.Document`): File to send. |fileinputnopath|
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

        thumb (:term:`file object` | :obj:`bytes` | :class:`pathlib.Path` | :obj:`str`, \
                optional): |thumbdocstringnopath|

            .. versionchanged:: 13.2
               Accept :obj:`bytes` as input.
        disable_content_type_detection (:obj:`bool`, optional): Disables automatic server-side
            content type detection for files uploaded using multipart/form-data. Always
            :obj:`True`, if the document is sent as part of an album.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InputMediaType.DOCUMENT`.
        media (:obj:`str` | :class:`telegram.InputFile`): File to send.
        caption (:obj:`str`): Optional. Caption of the document to be sent,
            0-:tg-const:`telegram.constants.MessageLimit.CAPTION_LENGTH` characters
            after entities parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        caption_entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        thumb (:class:`telegram.InputFile`): Optional. |thumbdocstringbase|
        disable_content_type_detection (:obj:`bool`): Optional. Disables automatic server-side
            content type detection for files uploaded using multipart/form-data. Always
            :obj:`True`, if the document is sent as part of an album.

    """

    __slots__ = ("disable_content_type_detection", "thumb")

    def __init__(
        self,
        media: Union[FileInput, Document],
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: bool = None,
        caption_entities: Sequence[MessageEntity] = None,
        filename: str = None,
        *,
        api_kwargs: JSONDict = None,
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
            self.thumb: Optional[Union[str, InputFile]] = self._parse_thumb_input(thumb)
            self.disable_content_type_detection: Optional[bool] = disable_content_type_detection
