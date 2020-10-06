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
"""This module contains an object that represents a Telegram Venue."""

from telegram import TelegramObject, Location
from telegram.utils.types import JSONDict
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot


class Venue(TelegramObject):
    """This object represents a venue.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`location` and :attr:`title` are equal.

    Attributes:
        location (:class:`telegram.Location`): Venue location.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue. (For example,
            "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)

    Args:
        location (:class:`telegram.Location`): Venue location.
        title (:obj:`str`): Name of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue. (For example,
            "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 location: Location,
                 title: str,
                 address: str,
                 foursquare_id: str = None,
                 foursquare_type: str = None,
                 **kwargs: Any):
        # Required
        self.location = location
        self.title = title
        self.address = address
        # Optionals
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type

        self._id_attrs = (self.location, self.title)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['Venue']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['location'] = Location.de_json(data.get('location'), bot)

        return cls(**data)
