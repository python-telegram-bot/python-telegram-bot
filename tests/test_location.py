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

from telegram import Location
from telegram.error import BadRequest


@pytest.fixture(scope='class')
def location():
    return Location(
        latitude=TestLocation.latitude,
        longitude=TestLocation.longitude,
        horizontal_accuracy=TestLocation.horizontal_accuracy,
        live_period=TestLocation.live_period,
        heading=TestLocation.live_period,
        proximity_alert_radius=TestLocation.proximity_alert_radius,
    )


class TestLocation:
    latitude = -23.691288
    longitude = -46.788279
    horizontal_accuracy = 999
    live_period = 60
    heading = 90
    proximity_alert_radius = 50

    def test_slot_behaviour(self, location, recwarn, mro_slots):
        for attr in location.__slots__:
            assert getattr(location, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not location.__dict__, f"got missing slot(s): {location.__dict__}"
        assert len(mro_slots(location)) == len(set(mro_slots(location))), "duplicate slot"
        location.custom, location.heading = 'should give warning', self.heading
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json(self, bot):
        json_dict = {
            'latitude': TestLocation.latitude,
            'longitude': TestLocation.longitude,
            'horizontal_accuracy': TestLocation.horizontal_accuracy,
            'live_period': TestLocation.live_period,
            'heading': TestLocation.heading,
            'proximity_alert_radius': TestLocation.proximity_alert_radius,
        }
        location = Location.de_json(json_dict, bot)

        assert location.latitude == self.latitude
        assert location.longitude == self.longitude
        assert location.horizontal_accuracy == self.horizontal_accuracy
        assert location.live_period == self.live_period
        assert location.heading == self.heading
        assert location.proximity_alert_radius == self.proximity_alert_radius

    @flaky(3, 1)
    @pytest.mark.xfail
    def test_send_live_location(self, bot, chat_id):
        message = bot.send_location(
            chat_id=chat_id,
            latitude=52.223880,
            longitude=5.166146,
            live_period=80,
            horizontal_accuracy=50,
            heading=90,
            proximity_alert_radius=1000,
        )
        assert message.location
        assert pytest.approx(52.223880, message.location.latitude)
        assert pytest.approx(5.166146, message.location.longitude)
        assert message.location.live_period == 80
        assert message.location.horizontal_accuracy == 50
        assert message.location.heading == 90
        assert message.location.proximity_alert_radius == 1000

        message2 = bot.edit_message_live_location(
            message.chat_id,
            message.message_id,
            latitude=52.223098,
            longitude=5.164306,
            horizontal_accuracy=30,
            heading=10,
            proximity_alert_radius=500,
        )

        assert pytest.approx(52.223098, message2.location.latitude)
        assert pytest.approx(5.164306, message2.location.longitude)
        assert message2.location.horizontal_accuracy == 30
        assert message2.location.heading == 10
        assert message2.location.proximity_alert_radius == 500

        bot.stop_message_live_location(message.chat_id, message.message_id)
        with pytest.raises(BadRequest, match="Message can't be edited"):
            bot.edit_message_live_location(
                message.chat_id, message.message_id, latitude=52.223880, longitude=5.164306
            )

    # TODO: Needs improvement with in inline sent live location.
    def test_edit_live_inline_message(self, monkeypatch, bot, location):
        def make_assertion(url, data, **kwargs):
            lat = data['latitude'] == location.latitude
            lon = data['longitude'] == location.longitude
            id_ = data['inline_message_id'] == 1234
            ha = data['horizontal_accuracy'] == 50
            heading = data['heading'] == 90
            prox_alert = data['proximity_alert_radius'] == 1000
            return lat and lon and id_ and ha and heading and prox_alert

        monkeypatch.setattr(bot.request, 'post', make_assertion)
        assert bot.edit_message_live_location(
            inline_message_id=1234,
            location=location,
            horizontal_accuracy=50,
            heading=90,
            proximity_alert_radius=1000,
        )

    # TODO: Needs improvement with in inline sent live location.
    def test_stop_live_inline_message(self, monkeypatch, bot):
        def test(url, data, **kwargs):
            id_ = data['inline_message_id'] == 1234
            return id_

        monkeypatch.setattr(bot.request, 'post', test)
        assert bot.stop_message_live_location(inline_message_id=1234)

    def test_send_with_location(self, monkeypatch, bot, chat_id, location):
        def test(url, data, **kwargs):
            lat = data['latitude'] == location.latitude
            lon = data['longitude'] == location.longitude
            return lat and lon

        monkeypatch.setattr(bot.request, 'post', test)
        assert bot.send_location(location=location, chat_id=chat_id)

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
    def test_send_location_default_allow_sending_without_reply(
        self, default_bot, chat_id, location, custom
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            message = default_bot.send_location(
                chat_id,
                location=location,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = default_bot.send_location(
                chat_id, location=location, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_location(
                    chat_id, location=location, reply_to_message_id=reply_to_message.message_id
                )

    def test_edit_live_location_with_location(self, monkeypatch, bot, location):
        def test(url, data, **kwargs):
            lat = data['latitude'] == location.latitude
            lon = data['longitude'] == location.longitude
            return lat and lon

        monkeypatch.setattr(bot.request, 'post', test)
        assert bot.edit_message_live_location(None, None, location=location)

    def test_send_location_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match='Either location or latitude and longitude'):
            bot.send_location(chat_id=chat_id)

    def test_edit_location_without_required(self, bot):
        with pytest.raises(ValueError, match='Either location or latitude and longitude'):
            bot.edit_message_live_location(chat_id=2, message_id=3)

    def test_send_location_with_all_args(self, bot, location):
        with pytest.raises(ValueError, match='Not both'):
            bot.send_location(chat_id=1, latitude=2.5, longitude=4.6, location=location)

    def test_edit_location_with_all_args(self, bot, location):
        with pytest.raises(ValueError, match='Not both'):
            bot.edit_message_live_location(
                chat_id=1, message_id=7, latitude=2.5, longitude=4.6, location=location
            )

    def test_to_dict(self, location):
        location_dict = location.to_dict()

        assert location_dict['latitude'] == location.latitude
        assert location_dict['longitude'] == location.longitude
        assert location_dict['horizontal_accuracy'] == location.horizontal_accuracy
        assert location_dict['live_period'] == location.live_period
        assert location['heading'] == location.heading
        assert location['proximity_alert_radius'] == location.proximity_alert_radius

    def test_equality(self):
        a = Location(self.longitude, self.latitude)
        b = Location(self.longitude, self.latitude)
        d = Location(0, self.latitude)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)
