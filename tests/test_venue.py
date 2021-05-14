#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import Location, Venue
from telegram.error import BadRequest


@pytest.fixture(scope='class')
def venue():
    return Venue(
        TestVenue.location,
        TestVenue.title,
        TestVenue.address,
        foursquare_id=TestVenue.foursquare_id,
        foursquare_type=TestVenue.foursquare_type,
        google_place_id=TestVenue.google_place_id,
        google_place_type=TestVenue.google_place_type,
    )


class TestVenue:
    location = Location(longitude=-46.788279, latitude=-23.691288)
    title = 'title'
    address = 'address'
    foursquare_id = 'foursquare id'
    foursquare_type = 'foursquare type'
    google_place_id = 'google place id'
    google_place_type = 'google place type'

    def test_slot_behaviour(self, venue, mro_slots, recwarn):
        for attr in venue.__slots__:
            assert getattr(venue, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not venue.__dict__, f"got missing slot(s): {venue.__dict__}"
        assert len(mro_slots(venue)) == len(set(mro_slots(venue))), "duplicate slot"
        venue.custom, venue.title = 'should give warning', self.title
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {
            'location': TestVenue.location.to_dict(),
            'title': TestVenue.title,
            'address': TestVenue.address,
            'foursquare_id': TestVenue.foursquare_id,
            'foursquare_type': TestVenue.foursquare_type,
            'google_place_id': TestVenue.google_place_id,
            'google_place_type': TestVenue.google_place_type,
        }
        venue = Venue.de_json(json_dict, bot)

        assert venue.location == self.location
        assert venue.title == self.title
        assert venue.address == self.address
        assert venue.foursquare_id == self.foursquare_id
        assert venue.foursquare_type == self.foursquare_type
        assert venue.google_place_id == self.google_place_id
        assert venue.google_place_type == self.google_place_type

    def test_send_with_venue(self, monkeypatch, bot, chat_id, venue):
        def test(url, data, **kwargs):
            return (
                data['longitude'] == self.location.longitude
                and data['latitude'] == self.location.latitude
                and data['title'] == self.title
                and data['address'] == self.address
                and data['foursquare_id'] == self.foursquare_id
                and data['foursquare_type'] == self.foursquare_type
                and data['google_place_id'] == self.google_place_id
                and data['google_place_type'] == self.google_place_type
            )

        monkeypatch.setattr(bot.request, 'post', test)
        message = bot.send_venue(chat_id, venue=venue)
        assert message

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    def test_send_venue_default_allow_sending_without_reply(
        self, default_bot, chat_id, venue, custom
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            message = default_bot.send_venue(
                chat_id,
                venue=venue,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = default_bot.send_venue(
                chat_id, venue=venue, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_venue(
                    chat_id, venue=venue, reply_to_message_id=reply_to_message.message_id
                )

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
        assert venue_dict['google_place_id'] == venue.google_place_id
        assert venue_dict['google_place_type'] == venue.google_place_type

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
