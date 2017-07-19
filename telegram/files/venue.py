#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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


class Venue(TelegramObject):
    """
    This object represents a venue.

    Attributes:
        location (:class:`telegram.Location`): Venue location.
        title (str): Name of the venue.
        address (str): Address of the venue.
        foursquare_id (str): Optional. Foursquare identifier of the venue.

    Args:
        location (:class:`telegram.Location`): Venue location.
        title (str): Name of the venue.
        address (str): Address of the venue.
        foursquare_id (Optional[str]): Foursquare identifier of the venue.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, location, title, address, foursquare_id=None, **kwargs):
        # Required
        self.location = location
        self.title = title
        self.address = address
        # Optionals
        self.foursquare_id = foursquare_id

        self._id_attrs = (self.location, self.title)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (:class:`telegram.Bot`):

        Returns:
            :class:`telegram.Venue`
        """

        data = super(Venue, Venue).de_json(data, bot)

        if not data:
            return None

        data['location'] = Location.de_json(data.get('location'), bot)

        return Venue(**data)
