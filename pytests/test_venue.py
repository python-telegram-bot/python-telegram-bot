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

from telegram import Location, Venue

@pytest.fixture(scope='class')
def json_dict():
    return {
            'location': TestVenue.location.to_dict(),
            'title': TestVenue.title,
            'address': TestVenue._address,
            'foursquare_id': TestVenue.foursquare_id
        }

@pytest.fixture(scope='class')
def venue():
   return Venue(location=TestVenue.location, title=TestVenue.title, address=TestVenue._address, foursquare_id=TestVenue.foursquare_id)

class TestVenue:
    """This object represents Tests for Telegram Venue."""

    location = Location(longitude=-46.788279, latitude=-23.691288)
    title = 'title'
    _address = '_address'
    foursquare_id = 'foursquare id'
    
    
    
    def test_de_json(self):
        sticker = Venue.de_json(json_dict, bot)

        assert isinstance(sticker.location, Location)
        assert sticker.title == self.title
        assert sticker.address == self._address
        assert sticker.foursquare_id == self.foursquare_id

    def test_send_venue_with_venue(self):
        ven = Venue.de_json(json_dict, bot)
        message = bot.send_venue(chat_id=chat_id, venue=ven)
        venue = message.venue

        assert venue == ven

    def test_to_json(self):
        sticker = Venue.de_json(json_dict, bot)

        json.loads(sticker.to_json())

    def test_to_dict(self):
        sticker = Venue.de_json(json_dict, bot).to_dict()

        assert isinstance(sticker, dict)
        assert json_dict == sticker

    @flaky(3, 1)
    def test_reply_venue(self):
        """Test for Message.reply_venue"""
        message = bot.sendMessage(chat_id, '.')
        message = message.reply_venue(self.location.latitude, self.location.longitude, self.title,
                                      self._address)

        self.assertAlmostEqual(message.venue.location.latitude, self.location.latitude, 2)
        self.assertAlmostEqual(message.venue.location.longitude, self.location.longitude, 2)

    def test_equality(self):
        a = Venue(Location(0, 0), "Title", "Address")
        b = Venue(Location(0, 0), "Title", "Address")
        c = Venue(Location(0, 0), "Title", "Not Address")
        d = Venue(Location(0, 1), "Title", "Address")
        d2 = Venue(Location(0, 0), "Not Title", "Address")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != d2
        assert hash(a) != hash(d2)


