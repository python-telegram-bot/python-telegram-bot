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
"""This module contains the classes that represent Telegram InputLocationMessageContent."""

from telegram import InputMessageContent
from typing import Any


class InputLocationMessageContent(InputMessageContent):
    """
    Represents the content of a location message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`latitude` and :attr:`longitude` are equal.

    Attributes:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        live_period	(:obj:`int`): Optional. Period in seconds for which the location can be
            updated.

    Args:
        latitude (:obj:`float`): Latitude of the location in degrees.
        longitude (:obj:`float`): Longitude of the location in degrees.
        live_period	(:obj:`int`, optional): Period in seconds for which the location can be
            updated, should be between 60 and 86400.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, latitude: float, longitude: float, live_period: int = None, **kwargs: Any):
        # Required
        self.latitude = latitude
        self.longitude = longitude
        self.live_period = live_period

        self._id_attrs = (self.latitude, self.longitude)
