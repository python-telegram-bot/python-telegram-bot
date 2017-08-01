#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import InputVenueMessageContent, InputMessageContent

@pytest.fixture(scope='class')
def json_dict():
    return {
            'longitude': TestInputVenueMessageContent.longitude,
            'latitude': TestInputVenueMessageContent.latitude,
            'title': TestInputVenueMessageContent.title,
            'address': TestInputVenueMessageContent._address,
            'foursquare_id': TestInputVenueMessageContent.foursquare_id,
        }

@pytest.fixture(scope='class')
def input_venue_message_content():
   return InputVenueMessageContent(longitude=TestInputVenueMessageContent.longitude, latitude=TestInputVenueMessageContent.latitude, title=TestInputVenueMessageContent.title, address=TestInputVenueMessageContent._address, foursquare_id=TestInputVenueMessageContent.foursquare_id)

class TestInputVenueMessageContent:
    """This object represents Tests for Telegram InputVenueMessageContent."""

    latitude = 1.
    longitude = 2.
    title = 'title'
    _address = 'address'  # nose binds address for testing
    foursquare_id = 'foursquare id'
    
    
    
    def test_de_json(self):
        ivmc = InputVenueMessageContent.de_json(json_dict, bot)

        assert ivmc.longitude == self.longitude
        assert ivmc.latitude == self.latitude
        assert ivmc.title == self.title
        assert ivmc.address == self._address
        assert ivmc.foursquare_id == self.foursquare_id

    def test_ivmc_de_json_factory(self):
        ivmc = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(ivmc, InputVenueMessageContent)

    def test_ivmc_de_json_factory_without_required_args(self):
        json_dict = json_dict

        del (json_dict['longitude'])
        del (json_dict['latitude'])
        del (json_dict['title'])
        del (json_dict['address'])

        ivmc = InputMessageContent.de_json(json_dict, bot)

        assert ivmc is False

    def test_to_json(self):
        ivmc = InputVenueMessageContent.de_json(json_dict, bot)

        json.loads(ivmc.to_json())

    def test_to_dict(self):
        ivmc = InputVenueMessageContent.de_json(json_dict, bot).to_dict()

        assert isinstance(ivmc, dict)
        assert json_dict == ivmc


