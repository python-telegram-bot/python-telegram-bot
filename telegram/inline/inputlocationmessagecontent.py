#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains the classes that represent Telegram InputLocationMessageContent."""

from typing import Any

from telegram import InputMessageContent


class InputLocationMessageContent(InputMessageContent):
    # fmt: off
    """
    Represents the content of a location message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`latitude` and :attr:`longitude` are equal.

    Args:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the location,
            measured in meters; 0-1500.
        live_period	(:obj:`int`, optional): Period in seconds for which the location can be
            updated, should be between 60 and 86400.
        heading (:obj:`int`, optional): For live locations, a direction in which the user is
            moving, in degrees. Must be between 1 and 360 if specified.
        proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance for
            proximity alerts about approaching another chat member, in meters. Must be between 1
            and 100000 if specified.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters.
        live_period	(:obj:`int`): Optional. Period in seconds for which the location can be
            updated.
        heading (:obj:`int`): Optional. For live locations, a direction in which the user is
            moving, in degrees.
        proximity_alert_radius (:obj:`int`): Optional. For live locations, a maximum distance for
            proximity alerts about approaching another chat member, in meters.

    """

    __slots__ = ('longitude', 'horizontal_accuracy', 'proximity_alert_radius', 'live_period',
                 'latitude', 'heading', '_id_attrs')
    # fmt: on

    def __init__(
        self,
        latitude: float,
        longitude: float,
        live_period: int = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        **_kwargs: Any,
    ):
        # Required
        self.latitude = latitude
        self.longitude = longitude

        # Optionals
        self.live_period = int(live_period) if live_period else None
        self.horizontal_accuracy = float(horizontal_accuracy) if horizontal_accuracy else None
        self.heading = int(heading) if heading else None
        self.proximity_alert_radius = (
            int(proximity_alert_radius) if proximity_alert_radius else None
        )

        self._id_attrs = (self.latitude, self.longitude)
