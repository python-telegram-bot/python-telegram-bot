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
"""This module contains the classes that represent Telegram InlineQueryResultLocation."""

from typing import TYPE_CHECKING, Final, Optional

from telegram import constants
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultLocation(InlineQueryResult):
    """
    Represents a location on a map. By default, the location will be sent by the user.
    Alternatively, you can use :attr:`input_message_content` to send a message with the specified
    content instead of the location.

    .. versionchanged:: 20.5
        |removed_thumb_wildcard_note|

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        title (:obj:`str`): Location title.
        horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the location,
            measured in meters; 0-
            :tg-const:`telegram.InlineQueryResultLocation.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`, optional): Period in seconds for which the location will be
            updated, should be between
            :tg-const:`telegram.InlineQueryResultLocation.MIN_LIVE_PERIOD` and
            :tg-const:`telegram.InlineQueryResultLocation.MAX_LIVE_PERIOD`.
        heading (:obj:`int`, optional): For live locations, a direction in which the user is
            moving, in degrees. Must be between
            :tg-const:`telegram.InlineQueryResultLocation.MIN_HEADING` and
            :tg-const:`telegram.InlineQueryResultLocation.MAX_HEADING` if specified.
        proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance
            for proximity alerts about approaching another chat member, in meters. Must be
            between :tg-const:`telegram.InlineQueryResultLocation.MIN_PROXIMITY_ALERT_RADIUS`
            and :tg-const:`telegram.InlineQueryResultLocation.MAX_PROXIMITY_ALERT_RADIUS`
            if specified.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the location.
        thumbnail_url (:obj:`str`, optional): Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`, optional): Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`, optional): Thumbnail height.

            .. versionadded:: 20.2

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.LOCATION`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        title (:obj:`str`): Location title.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters; 0-
            :tg-const:`telegram.InlineQueryResultLocation.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`): Optional. Period in seconds for which the location will be
            updated, should be between
            :tg-const:`telegram.InlineQueryResultLocation.MIN_LIVE_PERIOD` and
            :tg-const:`telegram.InlineQueryResultLocation.MAX_LIVE_PERIOD` or
            :tg-const:`telegram.constants.LocationLimit.LIVE_PERIOD_FOREVER` for live
            locations that can be edited indefinitely.
        heading (:obj:`int`): Optional. For live locations, a direction in which the user is
            moving, in degrees. Must be between
            :tg-const:`telegram.InlineQueryResultLocation.MIN_HEADING` and
            :tg-const:`telegram.InlineQueryResultLocation.MAX_HEADING` if specified.
        proximity_alert_radius (:obj:`int`): Optional. For live locations, a maximum distance
            for proximity alerts about approaching another chat member, in meters. Must be
            between :tg-const:`telegram.InlineQueryResultLocation.MIN_PROXIMITY_ALERT_RADIUS`
            and :tg-const:`telegram.InlineQueryResultLocation.MAX_PROXIMITY_ALERT_RADIUS`
            if specified.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the location.
        thumbnail_url (:obj:`str`): Optional. Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`): Optional. Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`): Optional. Thumbnail height.

            .. versionadded:: 20.2

    """

    __slots__ = (
        "heading",
        "horizontal_accuracy",
        "input_message_content",
        "latitude",
        "live_period",
        "longitude",
        "proximity_alert_radius",
        "reply_markup",
        "thumbnail_height",
        "thumbnail_url",
        "thumbnail_width",
        "title",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        latitude: float,
        longitude: float,
        title: str,
        live_period: Optional[int] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        input_message_content: Optional["InputMessageContent"] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        thumbnail_url: Optional[str] = None,
        thumbnail_width: Optional[int] = None,
        thumbnail_height: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        # Required
        super().__init__(constants.InlineQueryResultType.LOCATION, id, api_kwargs=api_kwargs)
        with self._unfrozen():
            self.latitude: float = latitude
            self.longitude: float = longitude
            self.title: str = title

            # Optionals
            self.live_period: Optional[int] = live_period
            self.reply_markup: Optional[InlineKeyboardMarkup] = reply_markup
            self.input_message_content: Optional[InputMessageContent] = input_message_content
            self.thumbnail_url: Optional[str] = thumbnail_url
            self.thumbnail_width: Optional[int] = thumbnail_width
            self.thumbnail_height: Optional[int] = thumbnail_height
            self.horizontal_accuracy: Optional[float] = horizontal_accuracy
            self.heading: Optional[int] = heading
            self.proximity_alert_radius: Optional[int] = (
                int(proximity_alert_radius) if proximity_alert_radius else None
            )

    HORIZONTAL_ACCURACY: Final[int] = constants.LocationLimit.HORIZONTAL_ACCURACY
    """:const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`

    .. versionadded:: 20.0
    """
    MIN_HEADING: Final[int] = constants.LocationLimit.MIN_HEADING
    """:const:`telegram.constants.LocationLimit.MIN_HEADING`

    .. versionadded:: 20.0
    """
    MAX_HEADING: Final[int] = constants.LocationLimit.MAX_HEADING
    """:const:`telegram.constants.LocationLimit.MAX_HEADING`

    .. versionadded:: 20.0
    """
    MIN_LIVE_PERIOD: Final[int] = constants.LocationLimit.MIN_LIVE_PERIOD
    """:const:`telegram.constants.LocationLimit.MIN_LIVE_PERIOD`

    .. versionadded:: 20.0
    """
    MAX_LIVE_PERIOD: Final[int] = constants.LocationLimit.MAX_LIVE_PERIOD
    """:const:`telegram.constants.LocationLimit.MAX_LIVE_PERIOD`

    .. versionadded:: 20.0
    """
    MIN_PROXIMITY_ALERT_RADIUS: Final[int] = constants.LocationLimit.MIN_PROXIMITY_ALERT_RADIUS
    """:const:`telegram.constants.LocationLimit.MIN_PROXIMITY_ALERT_RADIUS`

    .. versionadded:: 20.0
    """
    MAX_PROXIMITY_ALERT_RADIUS: Final[int] = constants.LocationLimit.MAX_PROXIMITY_ALERT_RADIUS
    """:const:`telegram.constants.LocationLimit.MAX_PROXIMITY_ALERT_RADIUS`

    .. versionadded:: 20.0
    """
