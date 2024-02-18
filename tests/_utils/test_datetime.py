#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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

from telegram._utils import datetime as tg_dtm
from telegram.ext import Defaults

# sample time specification values categorised into absolute / delta / time-of-day
from tests.auxil.envvars import TEST_WITH_OPT_DEPS

# We do not parametrize tests with these variables, since there's a tiny chance that there is an
# error while collecting the tests (happens when time goes from HH:59:00 -> HH+1:00:00) when we
# run the test suite with multiple workers
DELTA_TIME_SPECS = [dtm.timedelta(hours=3, seconds=42, milliseconds=2), 30, 7.5]
TIME_OF_DAY_TIME_SPECS = [
    dtm.time(12, 42, tzinfo=dtm.timezone(dtm.timedelta(hours=-7))),
    dtm.time(12, 42),
]
RELATIVE_TIME_SPECS = DELTA_TIME_SPECS + TIME_OF_DAY_TIME_SPECS

ABSOLUTE_TIME_SPECS = [
    dtm.datetime.now(tz=dtm.timezone(dtm.timedelta(hours=-7))),
    dtm.datetime.utcnow(),
]
TIME_SPECS = ABSOLUTE_TIME_SPECS + RELATIVE_TIME_SPECS

"""
This part is here because pytz is just installed as dependency of the optional dependency
APScheduler, so we don't always have pytz (unless the user installs it).
Because imports in pytest are intricate, we just run

    pytest -k test_datetime.py

with the TEST_WITH_OPT_DEPS=False environment variable in addition to the regular test suite.
"""


class TestDatetime:
    @staticmethod
    def localize(dt, tzinfo):
        if TEST_WITH_OPT_DEPS:
            return tzinfo.localize(dt)
        return dt.replace(tzinfo=tzinfo)

    def test_helpers_utc(self):
        # Here we just test, that we got the correct UTC variant
        if not TEST_WITH_OPT_DEPS:
            assert tg_dtm.UTC is tg_dtm.DTM_UTC
        else:
            assert tg_dtm.UTC is not tg_dtm.DTM_UTC

    def test_to_float_timestamp_absolute_naive(self):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5)
        assert tg_dtm.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_naive_no_pytz(self, monkeypatch):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        monkeypatch.setattr(tg_dtm, "UTC", tg_dtm.DTM_UTC)
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5)
        assert tg_dtm.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_aware(self, timezone):
        """Conversion from timezone-aware datetime to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5)
        datetime = self.localize(test_datetime, timezone)
        assert (
            tg_dtm.to_float_timestamp(datetime)
            == 1573431976.1 - timezone.utcoffset(test_datetime).total_seconds()
        )

    def test_to_float_timestamp_absolute_no_reference(self):
        """A reference timestamp is only relevant for relative time specifications"""
        with pytest.raises(ValueError, match="while reference_timestamp is not None"):
            tg_dtm.to_float_timestamp(dtm.datetime(2019, 11, 11), reference_timestamp=123)

    # see note on parametrization at the top of this file
    def test_to_float_timestamp_delta(self):
        """Conversion from a 'delta' time specification to timestamp"""
        reference_t = 0
        for i in DELTA_TIME_SPECS:
            delta = i.total_seconds() if hasattr(i, "total_seconds") else i
            assert (
                tg_dtm.to_float_timestamp(i, reference_t) == reference_t + delta
            ), f"failed for {i}"

    def test_to_float_timestamp_time_of_day(self):
        """Conversion from time-of-day specification to timestamp"""
        hour, hour_delta = 12, 1
        ref_t = tg_dtm._datetime_to_float_timestamp(dtm.datetime(1970, 1, 1, hour=hour))

        # test for a time of day that is still to come, and one in the past
        time_future, time_past = dtm.time(hour + hour_delta), dtm.time(hour - hour_delta)
        assert tg_dtm.to_float_timestamp(time_future, ref_t) == ref_t + 60 * 60 * hour_delta
        assert tg_dtm.to_float_timestamp(time_past, ref_t) == ref_t + 60 * 60 * (24 - hour_delta)

    def test_to_float_timestamp_time_of_day_timezone(self, timezone):
        """Conversion from timezone-aware time-of-day specification to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        ref_datetime = dtm.datetime(1970, 1, 1, 12)
        utc_offset = timezone.utcoffset(ref_datetime)
        ref_t, time_of_day = tg_dtm._datetime_to_float_timestamp(ref_datetime), ref_datetime.time()
        aware_time_of_day = self.localize(ref_datetime, timezone).timetz()

        # first test that naive time is assumed to be utc:
        assert tg_dtm.to_float_timestamp(time_of_day, ref_t) == pytest.approx(ref_t)
        # test that by setting the timezone the timestamp changes accordingly:
        assert tg_dtm.to_float_timestamp(aware_time_of_day, ref_t) == pytest.approx(
            ref_t + (-utc_offset.total_seconds() % (24 * 60 * 60))
        )

    # see note on parametrization at the top of this file
    def test_to_float_timestamp_default_reference(self):
        """The reference timestamp for relative time specifications should default to now"""
        for i in RELATIVE_TIME_SPECS:
            now = time.time()
            assert tg_dtm.to_float_timestamp(i) == pytest.approx(
                tg_dtm.to_float_timestamp(i, reference_timestamp=now)
            ), f"Failed for {i}"

    def test_to_float_timestamp_error(self):
        with pytest.raises(TypeError, match="Defaults"):
            tg_dtm.to_float_timestamp(Defaults())

    # see note on parametrization at the top of this file
    def test_to_timestamp(self):
        # delegate tests to `to_float_timestamp`
        for i in TIME_SPECS:
            assert tg_dtm.to_timestamp(i) == int(tg_dtm.to_float_timestamp(i)), f"Failed for {i}"

    def test_to_timestamp_none(self):
        # this 'convenience' behaviour has been left left for backwards compatibility
        assert tg_dtm.to_timestamp(None) is None

    def test_from_timestamp_none(self):
        assert tg_dtm.from_timestamp(None) is None

    def test_from_timestamp_naive(self):
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, tzinfo=dtm.timezone.utc)
        assert tg_dtm.from_timestamp(1573431976, tzinfo=None) == datetime

    def test_from_timestamp_aware(self, timezone):
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5)
        datetime = self.localize(test_datetime, timezone)
        assert (
            tg_dtm.from_timestamp(1573431976.1 - timezone.utcoffset(test_datetime).total_seconds())
            == datetime
        )

    def test_extract_tzinfo_from_defaults(self, tz_bot, bot, raw_bot):
        assert tg_dtm.extract_tzinfo_from_defaults(tz_bot) == tz_bot.defaults.tzinfo
        assert tg_dtm.extract_tzinfo_from_defaults(bot) is None
        assert tg_dtm.extract_tzinfo_from_defaults(raw_bot) is None
