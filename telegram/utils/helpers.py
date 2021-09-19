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
"""This module contains helper functions used internally by the library.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""

import datetime as dtm  # dtm = "DateTime Module"
import signal
import time

from collections import defaultdict
from pathlib import Path

from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Dict,
    Optional,
    Tuple,
    Union,
    Type,
    cast,
    IO,
    TypeVar,
    Generic,
    overload,
)

from telegram.utils.types import JSONDict, FileInput

if TYPE_CHECKING:
    from telegram import TelegramObject, InputFile

# in PTB-Raw we don't have pytz, so we make a little workaround here
DTM_UTC = dtm.timezone.utc
try:
    import pytz

    UTC = pytz.utc
except ImportError:
    UTC = DTM_UTC  # type: ignore[assignment]

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]


# From https://stackoverflow.com/questions/2549939/get-signal-names-from-numbers-in-python
_signames = {
    v: k
    for k, v in reversed(sorted(vars(signal).items()))
    if k.startswith('SIG') and not k.startswith('SIG_')
}


def get_signal_name(signum: int) -> str:
    """Returns the signal name of the given signal number."""
    return _signames[signum]


def is_local_file(obj: Optional[Union[str, Path]]) -> bool:
    """
    Checks if a given string is a file on local system.

    Args:
        obj (:obj:`str`): The string to check.
    """
    if obj is None:
        return False

    path = Path(obj)
    try:
        return path.is_file()
    except Exception:
        return False


def parse_file_input(
    file_input: Union[FileInput, 'TelegramObject'],
    tg_type: Type['TelegramObject'] = None,
    attach: bool = None,
    filename: str = None,
) -> Union[str, 'InputFile', Any]:
    """
    Parses input for sending files:

    * For string input, if the input is an absolute path of a local file,
      adds the ``file://`` prefix. If the input is a relative path of a local file, computes the
      absolute path and adds the ``file://`` prefix. Returns the input unchanged, otherwise.
    * :class:`pathlib.Path` objects are treated the same way as strings.
    * For IO and bytes input, returns an :class:`telegram.InputFile`.
    * If :attr:`tg_type` is specified and the input is of that type, returns the ``file_id``
      attribute.

    Args:
        file_input (:obj:`str` | :obj:`bytes` | `filelike object` | Telegram media object): The
            input to parse.
        tg_type (:obj:`type`, optional): The Telegram media type the input can be. E.g.
            :class:`telegram.Animation`.
        attach (:obj:`bool`, optional): Whether this file should be send as one file or is part of
            a collection of files. Only relevant in case an :class:`telegram.InputFile` is
            returned.
        filename (:obj:`str`, optional): The filename. Only relevant in case an
            :class:`telegram.InputFile` is returned.

    Returns:
        :obj:`str` | :class:`telegram.InputFile` | :obj:`object`: The parsed input or the untouched
        :attr:`file_input`, in case it's no valid file input.
    """
    # Importing on file-level yields cyclic Import Errors
    from telegram import InputFile  # pylint: disable=C0415

    if isinstance(file_input, str) and file_input.startswith('file://'):
        return file_input
    if isinstance(file_input, (str, Path)):
        if is_local_file(file_input):
            out = Path(file_input).absolute().as_uri()
        else:
            out = file_input  # type: ignore[assignment]
        return out
    if isinstance(file_input, bytes):
        return InputFile(file_input, attach=attach, filename=filename)
    if InputFile.is_file(file_input):
        file_input = cast(IO, file_input)
        return InputFile(file_input, attach=attach, filename=filename)
    if tg_type and isinstance(file_input, tg_type):
        return file_input.file_id  # type: ignore[attr-defined]
    return file_input


# -------- date/time related helpers --------
def _datetime_to_float_timestamp(dt_obj: dtm.datetime) -> float:
    """
    Converts a datetime object to a float timestamp (with sub-second precision).
    If the datetime object is timezone-naive, it is assumed to be in UTC.
    """
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=dtm.timezone.utc)
    return dt_obj.timestamp()


def _localize(datetime: dtm.datetime, tzinfo: dtm.tzinfo) -> dtm.datetime:
    """Localize the datetime, where UTC is handled depending on whether pytz is available or not"""
    if tzinfo is DTM_UTC:
        return datetime.replace(tzinfo=DTM_UTC)
    return tzinfo.localize(datetime)  # type: ignore[attr-defined]


def to_float_timestamp(
    time_object: Union[int, float, dtm.timedelta, dtm.datetime, dtm.time],
    reference_timestamp: float = None,
    tzinfo: dtm.tzinfo = None,
) -> float:
    """
    Converts a given time object to a float POSIX timestamp.
    Used to convert different time specifications to a common format. The time object
    can be relative (i.e. indicate a time increment, or a time of day) or absolute.
    object objects from the :class:`datetime` module that are timezone-naive will be assumed
    to be in UTC, if ``bot`` is not passed or ``bot.defaults`` is :obj:`None`.

    Args:
        time_object (:obj:`int` | :obj:`float` | :obj:`datetime.timedelta` | \
            :obj:`datetime.datetime` | :obj:`datetime.time`):
            Time value to convert. The semantics of this parameter will depend on its type:

            * :obj:`int` or :obj:`float` will be interpreted as "seconds from ``reference_t``"
            * :obj:`datetime.timedelta` will be interpreted as
              "time increment from ``reference_t``"
            * :obj:`datetime.datetime` will be interpreted as an absolute date/time value
            * :obj:`datetime.time` will be interpreted as a specific time of day

        reference_timestamp (:obj:`float`, optional): POSIX timestamp that indicates the absolute
            time from which relative calculations are to be performed (e.g. when ``t`` is given as
            an :obj:`int`, indicating "seconds from ``reference_t``"). Defaults to now (the time at
            which this function is called).

            If ``t`` is given as an absolute representation of date & time (i.e. a
            :obj:`datetime.datetime` object), ``reference_timestamp`` is not relevant and so its
            value should be :obj:`None`. If this is not the case, a ``ValueError`` will be raised.
        tzinfo (:obj:`pytz.BaseTzInfo`, optional): If ``t`` is a naive object from the
            :class:`datetime` module, it will be interpreted as this timezone. Defaults to
            ``pytz.utc``.

            Note:
                Only to be used by ``telegram.ext``.


    Returns:
        :obj:`float` | :obj:`None`:
            The return value depends on the type of argument ``t``.
            If ``t`` is given as a time increment (i.e. as a :obj:`int`, :obj:`float` or
            :obj:`datetime.timedelta`), then the return value will be ``reference_t`` + ``t``.

            Else if it is given as an absolute date/time value (i.e. a :obj:`datetime.datetime`
            object), the equivalent value as a POSIX timestamp will be returned.

            Finally, if it is a time of the day without date (i.e. a :obj:`datetime.time`
            object), the return value is the nearest future occurrence of that time of day.

    Raises:
        TypeError: If ``t``'s type is not one of those described above.
        ValueError: If ``t`` is a :obj:`datetime.datetime` and :obj:`reference_timestamp` is not
            :obj:`None`.
    """
    if reference_timestamp is None:
        reference_timestamp = time.time()
    elif isinstance(time_object, dtm.datetime):
        raise ValueError('t is an (absolute) datetime while reference_timestamp is not None')

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

    raise TypeError(f'Unable to convert {type(time_object).__name__} object to timestamp')


def to_timestamp(
    dt_obj: Union[int, float, dtm.timedelta, dtm.datetime, dtm.time, None],
    reference_timestamp: float = None,
    tzinfo: dtm.tzinfo = None,
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


def from_timestamp(unixtime: Optional[int], tzinfo: dtm.tzinfo = UTC) -> Optional[dtm.datetime]:
    """
    Converts an (integer) unix timestamp to a timezone aware datetime object.
    :obj:`None` s are left alone (i.e. ``from_timestamp(None)`` is :obj:`None`).

    Args:
        unixtime (:obj:`int`): Integer POSIX timestamp.
        tzinfo (:obj:`datetime.tzinfo`, optional): The timezone to which the timestamp is to be
            converted to. Defaults to UTC.

    Returns:
        Timezone aware equivalent :obj:`datetime.datetime` value if ``unixtime`` is not
        :obj:`None`; else :obj:`None`.
    """
    if unixtime is None:
        return None

    if tzinfo is not None:
        return dtm.datetime.fromtimestamp(unixtime, tz=tzinfo)
    return dtm.datetime.utcfromtimestamp(unixtime)


# -------- end --------


def encode_conversations_to_json(conversations: Dict[str, Dict[Tuple, object]]) -> str:
    """Helper method to encode a conversations dict (that uses tuples as keys) to a
    JSON-serializable way. Use :meth:`decode_conversations_from_json` to decode.

    Args:
        conversations (:obj:`dict`): The conversations dict to transform to JSON.

    Returns:
        :obj:`str`: The JSON-serialized conversations dict
    """
    tmp: Dict[str, JSONDict] = {}
    for handler, states in conversations.items():
        tmp[handler] = {}
        for key, state in states.items():
            tmp[handler][json.dumps(key)] = state
    return json.dumps(tmp)


def decode_conversations_from_json(json_string: str) -> Dict[str, Dict[Tuple, object]]:
    """Helper method to decode a conversations dict (that uses tuples as keys) from a
    JSON-string created with :meth:`encode_conversations_to_json`.

    Args:
        json_string (:obj:`str`): The conversations dict as JSON string.

    Returns:
        :obj:`dict`: The conversations dict after decoding
    """
    tmp = json.loads(json_string)
    conversations: Dict[str, Dict[Tuple, object]] = {}
    for handler, states in tmp.items():
        conversations[handler] = {}
        for key, state in states.items():
            conversations[handler][tuple(json.loads(key))] = state
    return conversations


def decode_user_chat_data_from_json(data: str) -> DefaultDict[int, Dict[object, object]]:
    """Helper method to decode chat or user data (that uses ints as keys) from a
    JSON-string.

    Args:
        data (:obj:`str`): The user/chat_data dict as JSON string.

    Returns:
        :obj:`dict`: The user/chat_data defaultdict after decoding
    """
    tmp: DefaultDict[int, Dict[object, object]] = defaultdict(dict)
    decoded_data = json.loads(data)
    for user, user_data in decoded_data.items():
        user = int(user)
        tmp[user] = {}
        for key, value in user_data.items():
            try:
                key = int(key)
            except ValueError:
                pass
            tmp[user][key] = value
    return tmp


DVType = TypeVar('DVType', bound=object)
OT = TypeVar('OT', bound=object)


class DefaultValue(Generic[DVType]):
    """Wrapper for immutable default arguments that allows to check, if the default value was set
    explicitly. Usage::

        DefaultOne = DefaultValue(1)
        def f(arg=DefaultOne):
            if arg is DefaultOne:
                print('`arg` is the default')
                arg = arg.value
            else:
                print('`arg` was set explicitly')
            print(f'`arg` = {str(arg)}')

    This yields::

        >>> f()
        `arg` is the default
        `arg` = 1
        >>> f(1)
        `arg` was set explicitly
        `arg` = 1
        >>> f(2)
        `arg` was set explicitly
        `arg` = 2

    Also allows to evaluate truthiness::

        default = DefaultValue(value)
        if default:
            ...

    is equivalent to::

        default = DefaultValue(value)
        if value:
            ...

    ``repr(DefaultValue(value))`` returns ``repr(value)`` and ``str(DefaultValue(value))`` returns
    ``f'DefaultValue({value})'``.

    Args:
        value (:obj:`obj`): The value of the default argument

    Attributes:
        value (:obj:`obj`): The value of the default argument

    """

    __slots__ = ('value',)

    def __init__(self, value: DVType = None):
        self.value = value

    def __bool__(self) -> bool:
        return bool(self.value)

    @overload
    @staticmethod
    def get_value(obj: 'DefaultValue[OT]') -> OT:
        ...

    @overload
    @staticmethod
    def get_value(obj: OT) -> OT:
        ...

    @staticmethod
    def get_value(obj: Union[OT, 'DefaultValue[OT]']) -> OT:
        """
        Shortcut for::

            return obj.value if isinstance(obj, DefaultValue) else obj

        Args:
            obj (:obj:`object`): The object to process

        Returns:
            Same type as input, or the value of the input: The value
        """
        return obj.value if isinstance(obj, DefaultValue) else obj  # type: ignore[return-value]

    # This is mostly here for readability during debugging
    def __str__(self) -> str:
        return f'DefaultValue({self.value})'

    # This is here to have the default instances nicely rendered in the docs
    def __repr__(self) -> str:
        return repr(self.value)


DEFAULT_NONE: DefaultValue = DefaultValue(None)
""":class:`DefaultValue`: Default :obj:`None`"""

DEFAULT_FALSE: DefaultValue = DefaultValue(False)
""":class:`DefaultValue`: Default :obj:`False`"""

DEFAULT_20: DefaultValue = DefaultValue(20)
""":class:`DefaultValue`: Default :obj:`20`"""
