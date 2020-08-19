#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from dataclasses import dataclass
from telegram import InputMessageContent
from typing import Any, Optional


@dataclass(eq=False)
class InputVenueMessageContent(InputMessageContent):
    """Represents the content of a venue message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`latitude`, :attr:`longitude` and :attr:`title`
    are equal.

    Attributes:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue, if known.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)

    Args:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue, if known.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    # Required
    latitude: float
    longitude: float
    title: str
    address: str
    # Optionals
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None

    def __post_init__(self, **kwargs: Any) -> None:
        self._id_attrs = (
            self.latitude,
            self.longitude,
            self.title,
        )
