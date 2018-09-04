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

from telegram import Location, Venue


@pytest.fixture(scope='class')
def venue():
    return Venue(TestVenue.location,
                 TestVenue.title,
                 TestVenue.address,
                 foursquare_id=TestVenue.foursquare_id,
                 foursquare_type=TestVenue.foursquare_type)


class TestVenue(object):
    location = Location(longitude=-46.788279, latitude=-23.691288)
    title = 'title'
    address = 'address'
    foursquare_id = 'foursquare id'
    foursquare_type = 'foursquare type'

    def test_de_json(self, bot):
        json_dict = {
            'location': TestVenue.location.to_dict(),
            'title': TestVenue.title,
            'address': TestVenue.address,
            'foursquare_id': TestVenue.foursquare_id,
            'foursquare_type': TestVenue.foursquare_type
        }
        venue = Venue.de_json(json_dict, bot)

        assert venue.location == self.location
        assert venue.title == self.title
        assert venue.address == self.address
        assert venue.foursquare_id == self.foursquare_id
        assert venue.foursquare_type == self.foursquare_type

    def test_send_with_venue(self, monkeypatch, bot, chat_id, venue):
        def test(_, url, data, **kwargs):
            return (data['longitude'] == self.location.longitude
                    and data['latitude'] == self.location.latitude
                    and data['title'] == self.title
                    and data['address'] == self.address
                    and data['foursquare_id'] == self.foursquare_id
                    and data['foursquare_type'] == self.foursquare_type)

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_venue(chat_id, venue=venue)
        assert message

    def test_send_venue_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match='Either venue or latitude, longitude, address and'):
            bot.send_venue(chat_id=chat_id)

    def test_to_dict(self, venue):
        venue_dict = venue.to_dict()

        assert isinstance(venue_dict, dict)
        assert venue_dict['location'] == venue.location.to_dict()
        assert venue_dict['title'] == venue.title
        assert venue_dict['address'] == venue.address
        assert venue_dict['foursquare_id'] == venue.foursquare_id
        assert venue_dict['foursquare_type'] == venue.foursquare_type

    def test_equality(self):
        a = Venue(Location(0, 0), self.title, self.address)
        b = Venue(Location(0, 0), self.title, self.address)
        c = Venue(Location(0, 0), self.title, '')
        d = Venue(Location(0, 1), self.title, self.address)
        d2 = Venue(Location(0, 0), '', self.address)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)
