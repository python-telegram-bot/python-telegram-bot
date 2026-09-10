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
# along with this program. If not, see [http://www.gnu.org/licenses/].
"""This module contains objects that represent paid media in Telegram."""

import datetime as dtm
from typing import TYPE_CHECKING, ClassVar

from telegram import constants
from telegram._files.livephoto import LivePhoto
from telegram._files.video import Video
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import (
    parse_sequence_arg,
    to_timedelta,
)
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import get_timedelta_value

if TYPE_CHECKING:
    from telegram._files.photosize import PhotoSize
    from telegram._user import User


@tg_dataclass()
class PaidMedia(TelegramObject):
    """Describes the paid media added to a message. Currently, it can be one of:

    * :class:`telegram.PaidMediaPreview`
    * :class:`telegram.PaidMediaPhoto`
    * :class:`telegram.PaidMediaVideo`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): Type of the paid media.

    Attributes:
        type (:obj:`str`): Type of the paid media.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "preview": "PaidMediaPreview",
            "photo": "PaidMediaPhoto",
            "video": "PaidMediaVideo",
            "live_photo": "PaidMediaLivePhoto",
        },
    )

    PREVIEW: ClassVar[str] = constants.PaidMediaType.PREVIEW
    """:const:`telegram.constants.PaidMediaType.PREVIEW`"""
    PHOTO: ClassVar[str] = constants.PaidMediaType.PHOTO
    """:const:`telegram.constants.PaidMediaType.PHOTO`"""
    VIDEO: ClassVar[str] = constants.PaidMediaType.VIDEO
    """:const:`telegram.constants.PaidMediaType.VIDEO`"""
    LIVE_PHOTO: ClassVar[str] = constants.PaidMediaType.LIVE_PHOTO
    """:const:`telegram.constants.PaidMediaType.LIVE_PHOTO`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.PaidMediaType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class PaidMediaPreview(PaidMedia):
    """The paid media isn't available before the payment.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`width`, :attr:`height`, and :attr:`duration`
    are equal.

    .. versionadded:: 21.4

    .. versionchanged:: v22.2
       As part of the migration to representing time periods using ``datetime.timedelta``,
       equality comparison now considers integer durations and equivalent timedeltas as equal.

    Args:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.PREVIEW`.
        width (:obj:`int`, optional): Media width as defined by the sender.
        height (:obj:`int`, optional): Media height as defined by the sender.
        duration (:obj:`int` | :class:`datetime.timedelta`, optional): Duration of the media in
            seconds as defined by the sender.

            .. versionchanged:: v22.2
                |time-period-input|

    Attributes:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.PREVIEW`.
        width (:obj:`int`): Optional. Media width as defined by the sender.
        height (:obj:`int`): Optional. Media height as defined by the sender.
        duration (:obj:`int` | :class:`datetime.timedelta`): Optional. Duration of the media in
            seconds as defined by the sender.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=PaidMedia.PREVIEW)

    width: int | None = tg_field(compare=True, default=None)
    height: int | None = tg_field(compare=True, default=None)
    _duration: dtm.timedelta | None = tg_field(
        compare=True, alias="duration", default=None, converter=to_timedelta
    )

    @property
    def duration(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._duration, attribute="duration")


@tg_dataclass()
class PaidMediaPhoto(PaidMedia):
    """
    The paid media is a photo.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`photo` are equal.

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.PHOTO`.
        photo (Sequence[:class:`telegram.PhotoSize`]): The photo.

    Attributes:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.PHOTO`.
        photo (tuple[:class:`telegram.PhotoSize`]): The photo.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=PaidMedia.PHOTO)

    photo: tuple["PhotoSize", ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class PaidMediaVideo(PaidMedia):
    """
    The paid media is a video.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`video` are equal.

    .. versionadded:: 21.4

    Args:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.VIDEO`.
        video (:class:`telegram.Video`): The video.

    Attributes:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.VIDEO`.
        video (:class:`telegram.Video`): The video.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=PaidMedia.VIDEO)

    video: Video = tg_field(compare=True)


@tg_dataclass()
class PaidMediaLivePhoto(PaidMedia):
    """
    The paid media is a live photo.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`live_photo` are equal.

    .. versionadded:: 22.8

    Args:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.LIVE_PHOTO`
        live_photo (:class:`telegram.LivePhoto`): The photo.

    Attributes:
        type (:obj:`str`): Type of the paid media, always :tg-const:`telegram.PaidMedia.LIVE_PHOTO`
        live_photo (:class:`telegram.LivePhoto`): The photo.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=PaidMedia.VIDEO)

    live_photo: LivePhoto = tg_field(compare=True)


@tg_dataclass()
class PaidMediaInfo(TelegramObject):
    """
    Describes the paid media added to a message.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`star_count` and :attr:`paid_media` are equal.

    .. versionadded:: 21.4

    Args:
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to buy access to
            the media.
        paid_media (Sequence[:class:`telegram.PaidMedia`]): Information about the paid media.

    Attributes:
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to buy access to
            the media.
        paid_media (tuple[:class:`telegram.PaidMedia`]): Information about the paid media.
    """

    star_count: int = tg_field(compare=True)
    paid_media: tuple[PaidMedia, ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class PaidMediaPurchased(TelegramObject):
    """This object contains information about a paid media purchase.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`from_user` and :attr:`paid_media_payload` are equal.

    Note:
        In Python :keyword:`from` is a reserved word. Use :paramref:`from_user` instead.

    .. versionadded:: 21.6

    Args:
        from_user (:class:`telegram.User`): User who purchased the media.
        paid_media_payload (:obj:`str`): Bot-specified paid media payload.

    Attributes:
        from_user (:class:`telegram.User`): User who purchased the media.
        paid_media_payload (:obj:`str`): Bot-specified paid media payload.
    """

    from_user: "User" = tg_field(compare=True)
    paid_media_payload: str = tg_field(compare=True)
