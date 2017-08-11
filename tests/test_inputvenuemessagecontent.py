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

import pytest

from telegram import InputVenueMessageContent, InputMessageContent


@pytest.fixture(scope='function')
def json_dict():
    return {
        'longitude': TestInputVenueMessageContent.longitude,
        'latitude': TestInputVenueMessageContent.latitude,
        'title': TestInputVenueMessageContent.title,
        'address': TestInputVenueMessageContent.address,
        'foursquare_id': TestInputVenueMessageContent.foursquare_id,
    }


@pytest.fixture(scope='class')
def input_venue_message_content():
    return InputVenueMessageContent(TestInputVenueMessageContent.latitude,
                                    TestInputVenueMessageContent.longitude,
                                    TestInputVenueMessageContent.title,
                                    TestInputVenueMessageContent.address,
                                    foursquare_id=TestInputVenueMessageContent.foursquare_id)


class TestInputVenueMessageContent(object):
    latitude = 1.
    longitude = 2.
    title = 'title'
    address = 'address'
    foursquare_id = 'foursquare id'

    def test_de_json(self, json_dict, bot):
        input_venue_message_content_json = InputVenueMessageContent.de_json(json_dict, bot)

        assert input_venue_message_content_json.longitude == self.longitude
        assert input_venue_message_content_json.latitude == self.latitude
        assert input_venue_message_content_json.title == self.title
        assert input_venue_message_content_json.address == self.address
        assert input_venue_message_content_json.foursquare_id == self.foursquare_id

    def test_de_json_factory(self, json_dict, bot):
        input_venue_message_content_json = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(input_venue_message_content_json, InputVenueMessageContent)

    def test_de_json_factory_without_required_args(self, json_dict, bot):
        json_dict = json_dict

        del (json_dict['longitude'])
        del (json_dict['latitude'])
        del (json_dict['title'])
        del (json_dict['address'])

        input_venue_message_content_json = InputMessageContent.de_json(json_dict, bot)

        assert input_venue_message_content_json is None

    def test_to_dict(self, input_venue_message_content):
        input_venue_message_content_dict = input_venue_message_content.to_dict()

        assert isinstance(input_venue_message_content_dict, dict)
        assert input_venue_message_content_dict['latitude'] == \
               input_venue_message_content.latitude
        assert input_venue_message_content_dict['longitude'] == \
               input_venue_message_content.longitude
        assert input_venue_message_content_dict['title'] == input_venue_message_content.title
        assert input_venue_message_content_dict['address'] == input_venue_message_content.address
        assert input_venue_message_content_dict['foursquare_id'] == \
               input_venue_message_content.foursquare_id
