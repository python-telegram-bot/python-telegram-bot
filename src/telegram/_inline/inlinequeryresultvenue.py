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
"""This module contains the classes that represent Telegram InlineQueryResultVenue."""

from typing import TYPE_CHECKING

from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._inline.inlinequeryresult import InlineQueryResult
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram.constants import InlineQueryResultType

if TYPE_CHECKING:
    from telegram import InputMessageContent


@tg_dataclass()
class InlineQueryResultVenue(InlineQueryResult):
    """
    Represents a venue. By default, the venue will be sent by the user. Alternatively, you can
    use :attr:`input_message_content` to send a message with the specified content instead of the
    venue.

    Note:
      Foursquare details and Google Pace details are mutually exclusive. However, this
      behaviour is undocumented and might be changed by Telegram.

    .. versionchanged:: 20.5
        |removed_thumb_wildcard_note|

    Args:
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        latitude (:obj:`float`): Latitude of the venue location in degrees.
        longitude (:obj:`float`): Longitude of the venue location in degrees.
        title (:obj:`str`): Title of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue if known.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        google_place_id (:obj:`str`, optional): Google Places identifier of the venue.
        google_place_type (:obj:`str`, optional): Google Places type of the venue. (See
            `supported types <https://developers.google.com/maps/documentation/places/web-service\
            /place-types>`_.)
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the venue.
        thumbnail_url (:obj:`str`, optional): Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`, optional): Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`, optional): Thumbnail height.

            .. versionadded:: 20.2

    Attributes:
        type (:obj:`str`): :tg-const:`telegram.constants.InlineQueryResultType.VENUE`.
        id (:obj:`str`): Unique identifier for this result,
            :tg-const:`telegram.InlineQueryResult.MIN_ID_LENGTH`-
            :tg-const:`telegram.InlineQueryResult.MAX_ID_LENGTH` Bytes.
        latitude (:obj:`float`): Latitude of the venue location in degrees.
        longitude (:obj:`float`): Longitude of the venue location in degrees.
        title (:obj:`str`): Title of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue if known.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        google_place_id (:obj:`str`): Optional. Google Places identifier of the venue.
        google_place_type (:obj:`str`): Optional. Google Places type of the venue. (See
            `supported types <https://developers.google.com/maps/documentation/places/web-service\
            /place-types>`_.)
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the venue.
        thumbnail_url (:obj:`str`): Optional. Url of the thumbnail for the result.

            .. versionadded:: 20.2
        thumbnail_width (:obj:`int`): Optional. Thumbnail width.

            .. versionadded:: 20.2
        thumbnail_height (:obj:`int`): Optional. Thumbnail height.

            .. versionadded:: 20.2

    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=InlineQueryResultType.VENUE)
    # Required
    latitude: float = tg_field()
    longitude: float = tg_field()
    title: str = tg_field()
    address: str = tg_field()
    # Optional
    foursquare_id: str | None = tg_field(default=None)
    foursquare_type: str | None = tg_field(default=None)
    reply_markup: InlineKeyboardMarkup | None = tg_field(default=None)
    input_message_content: "InputMessageContent | None" = tg_field(default=None)
    google_place_id: str | None = tg_field(default=None)
    google_place_type: str | None = tg_field(default=None)
    thumbnail_url: str | None = tg_field(default=None)
    thumbnail_width: int | None = tg_field(default=None)
    thumbnail_height: int | None = tg_field(default=None)
