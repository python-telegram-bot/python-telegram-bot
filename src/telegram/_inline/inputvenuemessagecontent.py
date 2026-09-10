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
"""This module contains the classes that represent Telegram InputVenueMessageContent."""

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class InputVenueMessageContent(InputMessageContent):
    """Represents the content of a venue message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`latitude`, :attr:`longitude` and :attr:`title`
    are equal.

    Note:
      Foursquare details and Google Pace details are mutually exclusive. However, this
      behaviour is undocumented and might be changed by Telegram.

    Args:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue, if known.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        google_place_id (:obj:`str`, optional): Google Places identifier of the venue.
        google_place_type (:obj:`str`, optional): Google Places type of the venue. (See
            `supported types <https://developers.google.com/maps/documentation/places/web-service\
            /place-types>`_.)

    Attributes:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue, if known.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        google_place_id (:obj:`str`): Optional. Google Places identifier of the venue.
        google_place_type (:obj:`str`): Optional. Google Places type of the venue. (See
            `supported types <https://developers.google.com/maps/documentation/places/web-service\
            /place-types>`_.)

    """

    # Required
    latitude: float = tg_field(compare=True)
    longitude: float = tg_field(compare=True)
    title: str = tg_field(compare=True)
    address: str = tg_field()
    # Optional
    foursquare_id: str | None = tg_field(default=None)
    foursquare_type: str | None = tg_field(default=None)
    google_place_id: str | None = tg_field(default=None)
    google_place_type: str | None = tg_field(default=None)
