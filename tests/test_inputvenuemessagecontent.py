#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import InputVenueMessageContent


@pytest.fixture(scope='class')
def input_venue_message_content():
    return InputVenueMessageContent(TestInputVenueMessageContent.latitude,
                                    TestInputVenueMessageContent.longitude,
                                    TestInputVenueMessageContent.title,
                                    TestInputVenueMessageContent.address,
                                    foursquare_id=TestInputVenueMessageContent.foursquare_id,
                                    foursquare_type=TestInputVenueMessageContent.foursquare_type)


class TestInputVenueMessageContent(object):
    latitude = 1.
    longitude = 2.
    title = 'title'
    address = 'address'
    foursquare_id = 'foursquare id'
    foursquare_type = 'foursquare type'

    def test_expected_values(self, input_venue_message_content):
        assert input_venue_message_content.longitude == self.longitude
        assert input_venue_message_content.latitude == self.latitude
        assert input_venue_message_content.title == self.title
        assert input_venue_message_content.address == self.address
        assert input_venue_message_content.foursquare_id == self.foursquare_id
        assert input_venue_message_content.foursquare_type == self.foursquare_type

    def test_to_dict(self, input_venue_message_content):
        input_venue_message_content_dict = input_venue_message_content.to_dict()

        assert isinstance(input_venue_message_content_dict, dict)
        assert (input_venue_message_content_dict['latitude']
                == input_venue_message_content.latitude)
        assert (input_venue_message_content_dict['longitude']
                == input_venue_message_content.longitude)
        assert input_venue_message_content_dict['title'] == input_venue_message_content.title
        assert input_venue_message_content_dict['address'] == input_venue_message_content.address
        assert (input_venue_message_content_dict['foursquare_id']
                == input_venue_message_content.foursquare_id)
        assert (input_venue_message_content_dict['foursquare_type']
                == input_venue_message_content.foursquare_type)
