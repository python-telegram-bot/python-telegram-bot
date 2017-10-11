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
from flaky import flaky

from telegram import Location
from telegram.error import BadRequest


@pytest.fixture(scope='class')
def location():
    return Location(latitude=TestLocation.latitude, longitude=TestLocation.longitude)


class TestLocation(object):
    latitude = -23.691288
    longitude = -46.788279

    def test_de_json(self, bot):
        json_dict = {'latitude': TestLocation.latitude,
                     'longitude': TestLocation.longitude}
        location = Location.de_json(json_dict, bot)

        assert location.latitude == self.latitude
        assert location.longitude == self.longitude

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_location(self, bot, chat_id):
        message = bot.send_location(chat_id=chat_id, latitude=-23.691288, longitude=-46.788279)

        assert message.location
        assert message.location.longitude == -46.788279
        assert message.location.latitude == -23.691288

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_live_location(self, bot, chat_id):
        message = bot.send_location(chat_id=chat_id, latitude=52.223880, longitude=5.166146,
                                    live_period=80)
        message2 = bot.edit_message_live_location(message.chat_id, message.message_id,
                                                  latitude=52.223098, longitude=5.164306)

        assert message2.location.latitude == 52.223098
        assert message2.location.longitude == 5.164306

        bot.stop_message_live_location(message.chat_id, message.message_id)
        # should throw error to capture with with pytest.raises. Need to know the error though.¿
        with pytest.raises(BadRequest):
            bot.edit_message_live_location(message.chat_id, message.message_id, latitude=52.223880,
                                           longitude=5.164306)

    @pytest.mark.skip(reason='need reference to an inline message')
    def test_live_inline_message(self):
        pass

    def test_send_with_location(self, monkeypatch, bot, chat_id, location):
        def test(_, url, data, **kwargs):
            lat = data['latitude'] == location.latitude
            lon = data['longitude'] == location.longitude
            return lat and lon

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        assert bot.send_location(location=location, chat_id=chat_id)

    def test_send_location_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match='Either location or latitude and longitude'):
            bot.send_location(chat_id=chat_id)

    def test_to_dict(self, location):
        location_dict = location.to_dict()

        assert location_dict['latitude'] == location.latitude
        assert location_dict['longitude'] == location.longitude

    def test_equality(self):
        a = Location(self.longitude, self.latitude)
        b = Location(self.longitude, self.latitude)
        d = Location(0, self.latitude)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)
