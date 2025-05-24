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
"""This module contains the classes that represent Telegram InputLocationMessageContent."""

from typing import Final, Optional

from telegram import constants
from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._utils.types import JSONDict


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
            measured in meters; 0-
            :tg-const:`telegram.InputLocationMessageContent.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`, optional): Period in seconds for which the location will be
            updated, should be between
            :tg-const:`telegram.InputLocationMessageContent.MIN_LIVE_PERIOD` and
            :tg-const:`telegram.InputLocationMessageContent.MAX_LIVE_PERIOD` or
            :tg-const:`telegram.constants.LocationLimit.LIVE_PERIOD_FOREVER` for live
            locations that can be edited indefinitely.
        heading (:obj:`int`, optional): For live locations, a direction in which the user is
            moving, in degrees. Must be between
            :tg-const:`telegram.InputLocationMessageContent.MIN_HEADING` and
            :tg-const:`telegram.InputLocationMessageContent.MAX_HEADING` if specified.
        proximity_alert_radius (:obj:`int`, optional): For live locations, a maximum distance
            for proximity alerts about approaching another chat member, in meters. Must be
            between :tg-const:`telegram.InputLocationMessageContent.MIN_PROXIMITY_ALERT_RADIUS`
            and :tg-const:`telegram.InputLocationMessageContent.MAX_PROXIMITY_ALERT_RADIUS`
            if specified.

    Attributes:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        horizontal_accuracy (:obj:`float`): Optional. The radius of uncertainty for the location,
            measured in meters; 0-
            :tg-const:`telegram.InputLocationMessageContent.HORIZONTAL_ACCURACY`.
        live_period (:obj:`int`): Optional. Period in seconds for which the location can be
            updated, should be between
            :tg-const:`telegram.InputLocationMessageContent.MIN_LIVE_PERIOD` and
            :tg-const:`telegram.InputLocationMessageContent.MAX_LIVE_PERIOD`.
        heading (:obj:`int`): Optional. For live locations, a direction in which the user is
            moving, in degrees. Must be between
            :tg-const:`telegram.InputLocationMessageContent.MIN_HEADING` and
            :tg-const:`telegram.InputLocationMessageContent.MAX_HEADING` if specified.
        proximity_alert_radius (:obj:`int`): Optional. For live locations, a maximum distance
            for proximity alerts about approaching another chat member, in meters. Must be
            between :tg-const:`telegram.InputLocationMessageContent.MIN_PROXIMITY_ALERT_RADIUS`
            and :tg-const:`telegram.InputLocationMessageContent.MAX_PROXIMITY_ALERT_RADIUS`
            if specified.

    """

    __slots__ = (
        "heading",
        "horizontal_accuracy",
        "latitude",
        "live_period",
        "longitude",
        "proximity_alert_radius")
    # fmt: on

    def __init__(
        self,
        latitude: float,
        longitude: float,
        live_period: Optional[int] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        with self._unfrozen():
            # Required
            self.latitude: float = latitude
            self.longitude: float = longitude

            # Optionals
            self.live_period: Optional[int] = live_period
            self.horizontal_accuracy: Optional[float] = horizontal_accuracy
            self.heading: Optional[int] = heading
            self.proximity_alert_radius: Optional[int] = (
                int(proximity_alert_radius) if proximity_alert_radius else None
            )

            self._id_attrs = (self.latitude, self.longitude)

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
