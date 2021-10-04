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
import os
import time
import datetime as dtm
from importlib import reload
from unittest import mock

import pytest

from telegram._utils import datetime as tg_dtm
from telegram.ext import Defaults


# sample time specification values categorised into absolute / delta / time-of-day
from tests.conftest import env_var_2_bool

ABSOLUTE_TIME_SPECS = [
    dtm.datetime.now(tz=dtm.timezone(dtm.timedelta(hours=-7))),
    dtm.datetime.utcnow(),
]
DELTA_TIME_SPECS = [dtm.timedelta(hours=3, seconds=42, milliseconds=2), 30, 7.5]
TIME_OF_DAY_TIME_SPECS = [
    dtm.time(12, 42, tzinfo=dtm.timezone(dtm.timedelta(hours=-7))),
    dtm.time(12, 42),
]
RELATIVE_TIME_SPECS = DELTA_TIME_SPECS + TIME_OF_DAY_TIME_SPECS
TIME_SPECS = ABSOLUTE_TIME_SPECS + RELATIVE_TIME_SPECS

"""
This part is here for ptb-raw, where we don't have pytz (unless the user installs it)
Because imports in pytest are intricate, we just run

    pytest -k test_helpers.py

with the TEST_NO_PYTZ environment variable set in addition to the regular test suite.
Because actually uninstalling pytz would lead to errors in the test suite we just mock the
import to raise the expected exception.

Note that a fixture that just does this for every test that needs it is a nice idea, but for some
reason makes test_updater.py hang indefinitely on GitHub Actions (at least when Hinrich tried that)
"""
TEST_NO_PYTZ = env_var_2_bool(os.getenv('TEST_NO_PYTZ', False))

if TEST_NO_PYTZ:
    orig_import = __import__

    def import_mock(module_name, *args, **kwargs):
        if module_name == 'pytz':
            raise ModuleNotFoundError('We are testing without pytz here')
        return orig_import(module_name, *args, **kwargs)

    with mock.patch('builtins.__import__', side_effect=import_mock):
        reload(tg_dtm)


class TestDatetime:
    def test_helpers_utc(self):
        # Here we just test, that we got the correct UTC variant
        if TEST_NO_PYTZ:
            assert tg_dtm.UTC is tg_dtm.DTM_UTC
        else:
            assert tg_dtm.UTC is not tg_dtm.DTM_UTC

    def test_to_float_timestamp_absolute_naive(self):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        assert tg_dtm.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_naive_no_pytz(self, monkeypatch):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        monkeypatch.setattr(tg_dtm, 'UTC', tg_dtm.DTM_UTC)
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        assert tg_dtm.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_aware(self, timezone):
        """Conversion from timezone-aware datetime to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        datetime = timezone.localize(test_datetime)
        assert (
            tg_dtm.to_float_timestamp(datetime)
            == 1573431976.1 - timezone.utcoffset(test_datetime).total_seconds()
        )

    def test_to_float_timestamp_absolute_no_reference(self):
        """A reference timestamp is only relevant for relative time specifications"""
        with pytest.raises(ValueError):
            tg_dtm.to_float_timestamp(dtm.datetime(2019, 11, 11), reference_timestamp=123)

    @pytest.mark.parametrize('time_spec', DELTA_TIME_SPECS, ids=str)
    def test_to_float_timestamp_delta(self, time_spec):
        """Conversion from a 'delta' time specification to timestamp"""
        reference_t = 0
        delta = time_spec.total_seconds() if hasattr(time_spec, 'total_seconds') else time_spec
        assert tg_dtm.to_float_timestamp(time_spec, reference_t) == reference_t + delta

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
        aware_time_of_day = timezone.localize(ref_datetime).timetz()

        # first test that naive time is assumed to be utc:
        assert tg_dtm.to_float_timestamp(time_of_day, ref_t) == pytest.approx(ref_t)
        # test that by setting the timezone the timestamp changes accordingly:
        assert tg_dtm.to_float_timestamp(aware_time_of_day, ref_t) == pytest.approx(
            ref_t + (-utc_offset.total_seconds() % (24 * 60 * 60))
        )

    @pytest.mark.parametrize('time_spec', RELATIVE_TIME_SPECS, ids=str)
    def test_to_float_timestamp_default_reference(self, time_spec):
        """The reference timestamp for relative time specifications should default to now"""
        now = time.time()
        assert tg_dtm.to_float_timestamp(time_spec) == pytest.approx(
            tg_dtm.to_float_timestamp(time_spec, reference_timestamp=now)
        )

    def test_to_float_timestamp_error(self):
        with pytest.raises(TypeError, match='Defaults'):
            tg_dtm.to_float_timestamp(Defaults())

    @pytest.mark.parametrize('time_spec', TIME_SPECS, ids=str)
    def test_to_timestamp(self, time_spec):
        # delegate tests to `to_float_timestamp`
        assert tg_dtm.to_timestamp(time_spec) == int(tg_dtm.to_float_timestamp(time_spec))

    def test_to_timestamp_none(self):
        # this 'convenience' behaviour has been left left for backwards compatibility
        assert tg_dtm.to_timestamp(None) is None

    def test_from_timestamp_none(self):
        assert tg_dtm.from_timestamp(None) is None

    def test_from_timestamp_naive(self):
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, tzinfo=None)
        assert tg_dtm.from_timestamp(1573431976, tzinfo=None) == datetime

    def test_from_timestamp_aware(self, timezone):
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        datetime = timezone.localize(test_datetime)
        assert (
            tg_dtm.from_timestamp(1573431976.1 - timezone.utcoffset(test_datetime).total_seconds())
            == datetime
        )
