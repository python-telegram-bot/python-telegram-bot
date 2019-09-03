#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import datetime as dtm
import time

import pytest

from telegram import Sticker
from telegram import Update
from telegram import User
from telegram.message import Message
from telegram.utils import helpers
from telegram.utils.helpers import _UtcOffsetTimezone, _datetime_to_float_timestamp


# TODO: move time test utils to tests.utils.time
# TODO: unify pytest.approx() calls when using now time

# constants
DAY_TOTAL_SECONDS = dtm.timedelta(days=1).total_seconds()

# sample time specification values categorised into absolute / delta / time-of-day
ABSOLUTE_TIME_SPECS = [dtm.datetime.now(tz=_UtcOffsetTimezone(dtm.timedelta(hours=-7))),
                       dtm.datetime.utcnow()]
DELTA_TIME_SPECS = [dtm.timedelta(hours=3, seconds=42, milliseconds=2), 30, 7.5]
TIME_OF_DAY_TIME_SPECS = [dtm.time(12, 42, tzinfo=_UtcOffsetTimezone(dtm.timedelta(hours=-7))),
                          dtm.time(12, 42)]
RELATIVE_TIME_SPECS = DELTA_TIME_SPECS + TIME_OF_DAY_TIME_SPECS
TIME_SPECS = ABSOLUTE_TIME_SPECS + RELATIVE_TIME_SPECS

# (naive UTC datetime, timestamp) input / expected pairs
NAIVE_DATETIME_FLOAT_TIMESTAMP_PAIRS = [
    (dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5), 1573431976.1),
    (dtm.datetime(1970, 1, 1), 0.0),
    (dtm.datetime(1970, 1, 1, microsecond=1), 1e-6)]


def microsecond_precision(x):
    """Utility to make equality assertions up to microsecond precision
    (when floating point arithmetic means we don't have any guarantee beyond that)"""
    return pytest.approx(x, abs=1e-6)


class TestHelpers(object):
    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = '\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    @pytest.mark.parametrize(['datetime', 'expected_float_timestamp'],
                             NAIVE_DATETIME_FLOAT_TIMESTAMP_PAIRS, ids=str)
    def test_to_float_timestamp_absolute_naive(self, datetime, expected_float_timestamp):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        assert helpers.to_float_timestamp(datetime) == expected_float_timestamp

    @pytest.mark.parametrize('datetime_float_timestamp_pair',
                             NAIVE_DATETIME_FLOAT_TIMESTAMP_PAIRS, ids=str)
    def test_to_float_timestamp_absolute_aware(self, datetime_float_timestamp_pair, timezone):
        """Conversion from timezone-aware datetime to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        datetime, float_timestamp = datetime_float_timestamp_pair
        aware_datetime = datetime.replace(tzinfo=timezone)
        expected = float_timestamp - timezone.utcoffset(None).total_seconds()
        assert helpers.to_float_timestamp(aware_datetime) == microsecond_precision(expected)

    def test_to_float_timestamp_absolute_no_reference(self):
        """A reference timestamp is only relevant for relative time specifications"""
        with pytest.raises(ValueError):
            helpers.to_float_timestamp(dtm.datetime(2019, 11, 11), reference_timestamp=123)

    @pytest.mark.parametrize('time_spec', DELTA_TIME_SPECS, ids=str)
    def test_to_float_timestamp_delta(self, time_spec):
        """Conversion from a 'delta' time specification to timestamp"""
        reference_t = 0
        delta = time_spec.total_seconds() if hasattr(time_spec, 'total_seconds') else time_spec
        assert (helpers.to_float_timestamp(time_spec, reference_t)
                == microsecond_precision(reference_t + delta))

    @pytest.mark.parametrize('delta', [dtm.timedelta(hours=1),
                                       dtm.timedelta(microseconds=1)],
                             ids=lambda d: 'delta={}'.format(d))
    def test_to_float_timestamp_time_of_day(self, delta):
        """Conversion from time-of-day specification to timestamp"""
        hour = 12
        ref_datetime = dtm.datetime(1970, 1, 1, hour=hour)
        ref_t = _datetime_to_float_timestamp(ref_datetime)
        # make sure that ref_datetime ± delta falls within the same day
        delta = min(delta, dtm.timedelta(hours=24 - hour), dtm.timedelta(hours=hour))
        delta_seconds = delta.total_seconds()

        # test for a time of day that is still to come, and one in the past (same day)
        time_future, time_past = (ref_datetime + delta).time(), (ref_datetime - delta).time()
        # pytest.approx(..., abs=1e-6): check up to microseconds (allow floating point arithmetic)
        assert (helpers.to_float_timestamp(time_future, ref_t)
                == microsecond_precision(ref_t + delta_seconds))
        assert (helpers.to_float_timestamp(time_past, ref_t)
                == microsecond_precision(ref_t - delta_seconds + DAY_TOTAL_SECONDS))

    def test_to_float_timestamp_time_of_day_timezone(self, timezone):
        """Conversion from timezone-aware time-of-day specification to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        utc_offset = timezone.utcoffset(None)
        ref_datetime = dtm.datetime(1970, 1, 1, 12)
        ref_t, time_of_day = _datetime_to_float_timestamp(ref_datetime), ref_datetime.time()

        # first test that naive time is assumed to be utc:
        assert helpers.to_float_timestamp(time_of_day, ref_t) == pytest.approx(ref_t)
        # test that by setting the timezone the timestamp changes accordingly:
        assert (helpers.to_float_timestamp(time_of_day.replace(tzinfo=timezone), ref_t)
                == pytest.approx(ref_t + (-utc_offset.total_seconds() % DAY_TOTAL_SECONDS)))

    @pytest.mark.parametrize('time_spec', RELATIVE_TIME_SPECS, ids=str)
    def test_to_float_timestamp_default_reference(self, time_spec):
        """The reference timestamp for relative time specifications should default to now"""
        now = time.time()
        assert (helpers.to_float_timestamp(time_spec)
                == pytest.approx(helpers.to_float_timestamp(time_spec, reference_timestamp=now)))

    @pytest.mark.parametrize('time_spec', TIME_SPECS, ids=str)
    def test_to_timestamp(self, time_spec):
        # delegate tests to `to_float_timestamp`
        assert helpers.to_timestamp(time_spec) == int(helpers.to_float_timestamp(time_spec))

    def test_to_timestamp_none(self):
        # this 'convenience' behaviour has been left left for backwards compatibility
        assert helpers.to_timestamp(None) is None

    def test_from_timestamp(self):
        assert helpers.from_timestamp(1573431976) == dtm.datetime(2019, 11, 11, 0, 26, 16)

    def test_create_deep_linked_url(self):
        username = 'JamesTheMock'

        payload = "hello"
        expected = "https://t.me/{}?start={}".format(username, payload)
        actual = helpers.create_deep_linked_url(username, payload)
        assert expected == actual

        expected = "https://t.me/{}?startgroup={}".format(username, payload)
        actual = helpers.create_deep_linked_url(username, payload, group=True)
        assert expected == actual

        payload = ""
        expected = "https://t.me/{}".format(username)
        assert expected == helpers.create_deep_linked_url(username)
        assert expected == helpers.create_deep_linked_url(username, payload)
        payload = None
        assert expected == helpers.create_deep_linked_url(username, payload)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, 'text with spaces')

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(username, '0' * 65)

        with pytest.raises(ValueError):
            helpers.create_deep_linked_url(None, None)
        with pytest.raises(ValueError):  # too short username (4 is minimum)
            helpers.create_deep_linked_url("abc", None)

    def test_effective_message_type(self):
        def build_test_message(**kwargs):
            config = dict(
                message_id=1,
                from_user=None,
                date=None,
                chat=None,
            )
            config.update(**kwargs)
            return Message(**config)

        test_message = build_test_message(text='Test')
        assert helpers.effective_message_type(test_message) == 'text'
        test_message.text = None

        test_message = build_test_message(sticker=Sticker('sticker_id', 50, 50, False))
        assert helpers.effective_message_type(test_message) == 'sticker'
        test_message.sticker = None

        test_message = build_test_message(new_chat_members=[User(55, 'new_user', False)])
        assert helpers.effective_message_type(test_message) == 'new_chat_members'

        test_message = build_test_message(left_chat_member=[User(55, 'new_user', False)])
        assert helpers.effective_message_type(test_message) == 'left_chat_member'

        test_update = Update(1)
        test_message = build_test_message(text='Test')
        test_update.message = test_message
        assert helpers.effective_message_type(test_update) == 'text'

        empty_update = Update(2)
        assert helpers.effective_message_type(empty_update) is None

    def test_mention_html(self):
        expected = '<a href="tg://user?id=1">the name</a>'

        assert expected == helpers.mention_html(1, 'the name')

    def test_mention_markdown(self):
        expected = '[the name](tg://user?id=1)'

        assert expected == helpers.mention_markdown(1, 'the name')
