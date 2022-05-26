#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

from typing import TYPE_CHECKING, Any

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


class InlineQueryResultLocation(InlineQueryResult):
    """
    Represents a location on a map. By default, the location will be sent by the user.
    Alternatively, you can use :attr:`input_message_content` to send a message with the specified
    content instead of the location.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        title (:obj:`str`): Location title.
        horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the location,
            measured in meters; 0-:tg-const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`, optional): Period in seconds for which the location can be
            updated, should be between 60 and 86400.
        heading (:obj:`int`, optional): For live locations, a direction in which the user is
            moving, in degrees. Must be between 1 and
            :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
        proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance for
            proximity alerts about approaching another chat member, in meters. Must be between 1
            and :tg-const:`telegram.constants.LocationLimit.HEADING` if specified.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the location.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.LOCATION`.
        id (:obj:`str`): Unique identifier for this result, 1-64 bytes.
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        title (:obj:`str`): Location title.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters.
        live_period (:obj:`int`): Optional. Period in seconds for which the location can be
            updated, should be between 60 and 86400.
        heading (:obj:`int`): Optional. For live locations, a direction in which the user is
            moving, in degrees.
        proximity_alert_radius (:obj:`int`): Optional. For live locations, a maximum distance for
            proximity alerts about approaching another chat member, in meters.
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the location.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    """

    __slots__ = (
        "longitude",
        "reply_markup",
        "thumb_width",
        "thumb_height",
        "heading",
        "title",
        "live_period",
        "proximity_alert_radius",
        "input_message_content",
        "latitude",
        "horizontal_accuracy",
        "thumb_url",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        latitude: float,
        longitude: float,
        title: str,
        live_period: int = None,
        reply_markup: InlineKeyboardMarkup = None,
        input_message_content: "InputMessageContent" = None,
        thumb_url: str = None,
        thumb_width: int = None,
        thumb_height: int = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        **_kwargs: Any,
    ):
        # Required
        super().__init__(InlineQueryResultType.LOCATION, id)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title

        # Optionals
        self.live_period = live_period
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        self.horizontal_accuracy = horizontal_accuracy
        self.heading = heading
        self.proximity_alert_radius = (
            int(proximity_alert_radius) if proximity_alert_radius else None
        )
