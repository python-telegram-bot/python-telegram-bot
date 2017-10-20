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
"""This module contains an object that represents a Telegram Location."""

from telegram import TelegramObject


class Location(TelegramObject):
    """This object represents a point on the map.

    Attributes:
        longitude (:obj:`float`): Longitude as defined by sender.
        latitude (:obj:`float`): Latitude as defined by sender.

    Args:
        longitude (:obj:`float`): Longitude as defined by sender.
        latitude (:obj:`float`): Latitude as defined by sender.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, longitude, latitude, **kwargs):
        # Required
        self.longitude = float(longitude)
        self.latitude = float(latitude)

        self._id_attrs = (self.longitude, self.latitude)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
