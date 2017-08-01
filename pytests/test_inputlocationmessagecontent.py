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

from telegram import InputMessageContent, InputLocationMessageContent

@pytest.fixture(scope='class')
def json_dict():
    return {
            'longitude': TestInputLocationMessageContent.longitude,
            'latitude': TestInputLocationMessageContent.latitude,
        }

@pytest.fixture(scope='class')
def input_location_message_content():
   return InputLocationMessageContent(longitude=TestInputLocationMessageContent.longitude, latitude=TestInputLocationMessageContent.latitude)

class TestInputLocationMessageContent:
    """This object represents Tests for Telegram InputLocationMessageContent."""

    latitude = 1.
    longitude = 2.
    
    
    
    def test_de_json(self):
        ilmc = InputLocationMessageContent.de_json(json_dict, bot)

        assert ilmc.longitude == self.longitude
        assert ilmc.latitude == self.latitude

    def test_ilmc_de_json_factory(self):
        ilmc = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(ilmc, InputLocationMessageContent)

    def test_ilmc_de_json_factory_without_required_args(self):
        json_dict = json_dict

        del (json_dict['longitude'])
        # If none args are sent it will fall in a different condition
        # del (json_dict['latitude'])

        ilmc = InputMessageContent.de_json(json_dict, bot)

        assert ilmc is False

    def test_to_json(self):
        ilmc = InputLocationMessageContent.de_json(json_dict, bot)

        json.loads(ilmc.to_json())

    def test_to_dict(self):
        ilmc = InputLocationMessageContent.de_json(json_dict, bot).to_dict()

        assert isinstance(ilmc, dict)
        assert json_dict == ilmc


