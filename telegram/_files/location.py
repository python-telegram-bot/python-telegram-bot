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
"""This module contains an object that represents a Telegram Location."""

from typing import ClassVar, Optional

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class Location(TelegramObject):
    """This object represents a point on the map.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`longitude` and :attr:`latitude` are equal.

    Args:
        longitude (:obj:`float`): Longitude as defined by sender.
        latitude (:obj:`float`): Latitude as defined by sender.
        horizontal_accuracy (:obj:`float`, optional): The radius of uncertainty for the location,
            measured in meters; 0-:tg-const:`telegram.Location.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`, optional): Time relative to the message sending date, during which
            the location can be updated, in seconds. For active live locations only.
        heading (:obj:`int`, optional): The direction in which user is moving, in degrees;
            :tg-const:`telegram.Location.MIN_HEADING`-:tg-const:`telegram.Location.MAX_HEADING`.
            For active live locations only.
        proximity_alert_radius (:obj:`int`, optional): Maximum distance for proximity alerts about
            approaching another chat member, in meters. For sent live locations only.

    Attributes:
        longitude (:obj:`float`): Longitude as defined by sender.
        latitude (:obj:`float`): Latitude as defined by sender.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters; 0-:tg-const:`telegram.Location.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`): Optional. Time relative to the message sending date, during which
            the location can be updated, in seconds. For active live locations only.
        heading (:obj:`int`): Optional. The direction in which user is moving, in degrees;
            :tg-const:`telegram.Location.MIN_HEADING`-:tg-const:`telegram.Location.MAX_HEADING`.
            For active live locations only.
        proximity_alert_radius (:obj:`int`): Optional. Maximum distance for proximity alerts about
            approaching another chat member, in meters. For sent live locations only.

    """

    __slots__ = (
        "longitude",
        "horizontal_accuracy",
        "proximity_alert_radius",
        "live_period",
        "latitude",
        "heading",
    )

    def __init__(
        self,
        longitude: float,
        latitude: float,
        horizontal_accuracy: float = None,
        live_period: int = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.longitude: float = longitude
        self.latitude: float = latitude

        # Optionals
        self.horizontal_accuracy: Optional[float] = horizontal_accuracy
        self.live_period: Optional[int] = live_period
        self.heading: Optional[int] = heading
        self.proximity_alert_radius: Optional[int] = (
            int(proximity_alert_radius) if proximity_alert_radius else None
        )

        self._id_attrs = (self.longitude, self.latitude)

        self._freeze()

    HORIZONTAL_ACCURACY: ClassVar[int] = constants.LocationLimit.HORIZONTAL_ACCURACY
    """:const:`telegram.constants.LocationLimit.HORIZONTAL_ACCURACY`

    .. versionadded:: 20.0
    """
    MIN_HEADING: ClassVar[int] = constants.LocationLimit.MIN_HEADING
    """:const:`telegram.constants.LocationLimit.MIN_HEADING`

    .. versionadded:: 20.0
    """
    MAX_HEADING: ClassVar[int] = constants.LocationLimit.MAX_HEADING
    """:const:`telegram.constants.LocationLimit.MAX_HEADING`

    .. versionadded:: 20.0
    """
