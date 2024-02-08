#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains helper functions related to datetime and timestamp conversations.

.. versionchanged:: 20.0
   Previously, the contents of this module were available through the (no longer existing)
   module ``telegram._utils.helpers``.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""
import datetime as dtm
import time
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from telegram import Bot

# pytz is only available if it was installed as dependency of APScheduler, so we make a little
# workaround here
DTM_UTC = dtm.timezone.utc
try:
    import pytz

    UTC = pytz.utc
except ImportError:
    UTC = DTM_UTC  # type: ignore[assignment]


def _localize(datetime: dtm.datetime, tzinfo: dtm.tzinfo) -> dtm.datetime:
    """Localize the datetime, where UTC is handled depending on whether pytz is available or not"""
    if tzinfo is DTM_UTC:
        return datetime.replace(tzinfo=DTM_UTC)
    return tzinfo.localize(datetime)  # type: ignore[attr-defined]


def to_float_timestamp(
    time_object: Union[float, dtm.timedelta, dtm.datetime, dtm.time],
    reference_timestamp: Optional[float] = None,
    tzinfo: Optional[dtm.tzinfo] = None,
) -> float:
    """
    Converts a given time object to a float POSIX timestamp.
    Used to convert different time specifications to a common format. The time object
    can be relative (i.e. indicate a time increment, or a time of day) or absolute.
    Objects from the :class:`datetime` module that are timezone-naive will be assumed
    to be in UTC, if ``bot`` is not passed or ``bot.defaults`` is :obj:`None`.

    Args:
        time_object (:obj:`float` | :obj:`datetime.timedelta` | \
            :obj:`datetime.datetime` | :obj:`datetime.time`):
            Time value to convert. The semantics of this parameter will depend on its type:

            * :obj:`float` will be interpreted as "seconds from :paramref:`reference_t`"
            * :obj:`datetime.timedelta` will be interpreted as
              "time increment from :paramref:`reference_timestamp`"
            * :obj:`datetime.datetime` will be interpreted as an absolute date/time value
            * :obj:`datetime.time` will be interpreted as a specific time of day

        reference_timestamp (:obj:`float`, optional): POSIX timestamp that indicates the absolute
            time from which relative calculations are to be performed (e.g. when
            :paramref:`time_object` is given as an :obj:`int`, indicating "seconds from
            :paramref:`reference_time`"). Defaults to now (the time at which this function is
            called).

            If :paramref:`time_object` is given as an absolute representation of date & time (i.e.
            a :obj:`datetime.datetime` object), :paramref:`reference_timestamp` is not relevant
            and so its value should be :obj:`None`. If this is not the case, a :exc:`ValueError`
            will be raised.
        tzinfo (:class:`datetime.tzinfo`, optional): If :paramref:`time_object` is a naive object
            from the :mod:`datetime` module, it will be interpreted as this timezone. Defaults to
            ``pytz.utc``, if available, and :attr:`datetime.timezone.utc` otherwise.

            Note:
                Only to be used by ``telegram.ext``.

    Returns:
        :obj:`float` | :obj:`None`:
            The return value depends on the type of argument :paramref:`time_object`.
            If :paramref:`time_object` is given as a time increment (i.e. as a :obj:`int`,
            :obj:`float` or :obj:`datetime.timedelta`), then the return value will be
            :paramref:`reference_timestamp` + :paramref:`time_object`.

            Else if it is given as an absolute date/time value (i.e. a :obj:`datetime.datetime`
            object), the equivalent value as a POSIX timestamp will be returned.

            Finally, if it is a time of the day without date (i.e. a :obj:`datetime.time`
            object), the return value is the nearest future occurrence of that time of day.

    Raises:
        TypeError: If :paramref:`time_object` s type is not one of those described above.
        ValueError: If :paramref:`time_object` is a :obj:`datetime.datetime` and
            :paramref:`reference_timestamp` is not :obj:`None`.
    """
    if reference_timestamp is None:
        reference_timestamp = time.time()
    elif isinstance(time_object, dtm.datetime):
        raise ValueError("t is an (absolute) datetime while reference_timestamp is not None")

    if isinstance(time_object, dtm.timedelta):
        return reference_timestamp + time_object.total_seconds()
    if isinstance(time_object, (int, float)):
        return reference_timestamp + time_object

    if tzinfo is None:
        tzinfo = UTC

    if isinstance(time_object, dtm.time):
        reference_dt = dtm.datetime.fromtimestamp(
            reference_timestamp, tz=time_object.tzinfo or tzinfo
        )
        reference_date = reference_dt.date()
        reference_time = reference_dt.timetz()

        aware_datetime = dtm.datetime.combine(reference_date, time_object)
        if aware_datetime.tzinfo is None:
            aware_datetime = _localize(aware_datetime, tzinfo)

        # if the time of day has passed today, use tomorrow
        if reference_time > aware_datetime.timetz():
            aware_datetime += dtm.timedelta(days=1)
        return _datetime_to_float_timestamp(aware_datetime)
    if isinstance(time_object, dtm.datetime):
        if time_object.tzinfo is None:
            time_object = _localize(time_object, tzinfo)
        return _datetime_to_float_timestamp(time_object)

    raise TypeError(f"Unable to convert {type(time_object).__name__} object to timestamp")


def to_timestamp(
    dt_obj: Union[float, dtm.timedelta, dtm.datetime, dtm.time, None],
    reference_timestamp: Optional[float] = None,
    tzinfo: Optional[dtm.tzinfo] = None,
) -> Optional[int]:
    """
    Wrapper over :func:`to_float_timestamp` which returns an integer (the float value truncated
    down to the nearest integer).

    See the documentation for :func:`to_float_timestamp` for more details.
    """
    return (
        int(to_float_timestamp(dt_obj, reference_timestamp, tzinfo))
        if dt_obj is not None
        else None
    )


def from_timestamp(
    unixtime: Optional[int],
    tzinfo: Optional[dtm.tzinfo] = None,
) -> Optional[dtm.datetime]:
    """
    Converts an (integer) unix timestamp to a timezone aware datetime object.
    :obj:`None` s are left alone (i.e. ``from_timestamp(None)`` is :obj:`None`).

    Args:
        unixtime (:obj:`int`): Integer POSIX timestamp.
        tzinfo (:obj:`datetime.tzinfo`, optional): The timezone to which the timestamp is to be
            converted to. Defaults to :obj:`None`, in which case the returned datetime object will
            be timezone aware and in UTC.

    Returns:
        Timezone aware equivalent :obj:`datetime.datetime` value if :paramref:`unixtime` is not
        :obj:`None`; else :obj:`None`.
    """
    if unixtime is None:
        return None

    return dtm.datetime.fromtimestamp(unixtime, tz=UTC if tzinfo is None else tzinfo)


def extract_tzinfo_from_defaults(bot: "Bot") -> Union[dtm.tzinfo, None]:
    """
    Extracts the timezone info from the default values of the bot.
    If the bot has no default values, :obj:`None` is returned.
    """
    # We don't use `ininstance(bot, ExtBot)` here so that this works
    # in `python-telegram-bot-raw` as well
    if hasattr(bot, "defaults") and bot.defaults:
        return bot.defaults.tzinfo
    return None


def _datetime_to_float_timestamp(dt_obj: dtm.datetime) -> float:
    """
    Converts a datetime object to a float timestamp (with sub-second precision).
    If the datetime object is timezone-naive, it is assumed to be in UTC.
    """
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=dtm.timezone.utc)
    return dt_obj.timestamp()
