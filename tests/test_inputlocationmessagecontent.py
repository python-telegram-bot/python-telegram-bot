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

from telegram import InputMessageContent, InputLocationMessageContent


@pytest.fixture(scope='function')
def json_dict():
    return {
        'longitude': TestInputLocationMessageContent.longitude,
        'latitude': TestInputLocationMessageContent.latitude,
    }


@pytest.fixture(scope='class')
def input_location_message_content():
    return InputLocationMessageContent(TestInputLocationMessageContent.longitude,
                                       TestInputLocationMessageContent.latitude)


class TestInputLocationMessageContent(object):
    latitude = 1.
    longitude = 2.

    def test_de_json(self, json_dict, bot):
        input_location_message_content_json = InputLocationMessageContent.de_json(json_dict, bot)

        assert input_location_message_content_json.longitude == self.longitude
        assert input_location_message_content_json.latitude == self.latitude

    def test_input_location_message_content_json_de_json_factory(self, json_dict, bot):
        input_location_message_content_json = InputMessageContent.de_json(json_dict, bot)

        assert isinstance(input_location_message_content_json, InputLocationMessageContent)

    def test_de_json_factory_without_required_args(self, json_dict, bot):
        del (json_dict['longitude'])
        # If no args are passed it will fall in a different condition
        # del (json_dict['latitude'])

        input_location_message_content_json = InputMessageContent.de_json(json_dict, bot)

        assert input_location_message_content_json is None

    def test_to_dict(self, input_location_message_content):
        input_location_message_content_dict = input_location_message_content.to_dict()

        assert isinstance(input_location_message_content_dict, dict)
        assert input_location_message_content_dict['latitude'] == \
               input_location_message_content.latitude
        assert input_location_message_content_dict['longitude'] == \
               input_location_message_content.longitude
