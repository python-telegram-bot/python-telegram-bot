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

from telegram import InputLocationMessageContent


@pytest.fixture(scope='class')
def input_location_message_content():
    return InputLocationMessageContent(TestInputLocationMessageContent.latitude,
                                       TestInputLocationMessageContent.longitude)


class TestInputLocationMessageContent(object):
    latitude = -23.691288
    longitude = -46.788279

    def test_expected_values(self, input_location_message_content):
        assert input_location_message_content.longitude == self.longitude
        assert input_location_message_content.latitude == self.latitude

    def test_to_dict(self, input_location_message_content):
        input_location_message_content_dict = input_location_message_content.to_dict()

        assert isinstance(input_location_message_content_dict, dict)
        assert input_location_message_content_dict['latitude'] == \
               input_location_message_content.latitude
        assert input_location_message_content_dict['longitude'] == \
               input_location_message_content.longitude
