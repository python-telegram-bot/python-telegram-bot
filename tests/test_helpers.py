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
from pathlib import Path
from unittest import mock

import pytest

from telegram import Sticker, InputFile, Animation
from telegram import Update
from telegram import User
from telegram import MessageEntity
from telegram.ext import Defaults
from telegram.message import Message
from telegram.utils import helpers
from telegram.utils.helpers import _datetime_to_float_timestamp


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
        reload(helpers)


class TestHelpers:
    def test_helpers_utc(self):
        # Here we just test, that we got the correct UTC variant
        if TEST_NO_PYTZ:
            assert helpers.UTC is helpers.DTM_UTC
        else:
            assert helpers.UTC is not helpers.DTM_UTC

    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = r'\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    def test_escape_markdown_v2(self):
        test_str = 'a_b*c[d]e (fg) h~I`>JK#L+MN -O=|p{qr}s.t! u'
        expected_str = r'a\_b\*c\[d\]e \(fg\) h\~I\`\>JK\#L\+MN \-O\=\|p\{qr\}s\.t\! u'

        assert expected_str == helpers.escape_markdown(test_str, version=2)

    def test_escape_markdown_v2_monospaced(self):

        test_str = r'mono/pre: `abc` \int (`\some \`stuff)'
        expected_str = 'mono/pre: \\`abc\\` \\\\int (\\`\\\\some \\\\\\`stuff)'

        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.PRE
        )
        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.CODE
        )

    def test_escape_markdown_v2_text_link(self):

        test_str = 'https://url.containing/funny)cha)\\ra\\)cter\\s'
        expected_str = 'https://url.containing/funny\\)cha\\)\\\\ra\\\\\\)cter\\\\s'

        assert expected_str == helpers.escape_markdown(
            test_str, version=2, entity_type=MessageEntity.TEXT_LINK
        )

    def test_markdown_invalid_version(self):
        with pytest.raises(ValueError):
            helpers.escape_markdown('abc', version=-1)

    def test_to_float_timestamp_absolute_naive(self):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        assert helpers.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_naive_no_pytz(self, monkeypatch):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        monkeypatch.setattr(helpers, 'UTC', helpers.DTM_UTC)
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        assert helpers.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_aware(self, timezone):
        """Conversion from timezone-aware datetime to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        datetime = timezone.localize(test_datetime)
        assert (
            helpers.to_float_timestamp(datetime)
            == 1573431976.1 - timezone.utcoffset(test_datetime).total_seconds()
        )

    def test_to_float_timestamp_absolute_no_reference(self):
        """A reference timestamp is only relevant for relative time specifications"""
        with pytest.raises(ValueError):
            helpers.to_float_timestamp(dtm.datetime(2019, 11, 11), reference_timestamp=123)

    @pytest.mark.parametrize('time_spec', DELTA_TIME_SPECS, ids=str)
    def test_to_float_timestamp_delta(self, time_spec):
        """Conversion from a 'delta' time specification to timestamp"""
        reference_t = 0
        delta = time_spec.total_seconds() if hasattr(time_spec, 'total_seconds') else time_spec
        assert helpers.to_float_timestamp(time_spec, reference_t) == reference_t + delta

    def test_to_float_timestamp_time_of_day(self):
        """Conversion from time-of-day specification to timestamp"""
        hour, hour_delta = 12, 1
        ref_t = _datetime_to_float_timestamp(dtm.datetime(1970, 1, 1, hour=hour))

        # test for a time of day that is still to come, and one in the past
        time_future, time_past = dtm.time(hour + hour_delta), dtm.time(hour - hour_delta)
        assert helpers.to_float_timestamp(time_future, ref_t) == ref_t + 60 * 60 * hour_delta
        assert helpers.to_float_timestamp(time_past, ref_t) == ref_t + 60 * 60 * (24 - hour_delta)

    def test_to_float_timestamp_time_of_day_timezone(self, timezone):
        """Conversion from timezone-aware time-of-day specification to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        ref_datetime = dtm.datetime(1970, 1, 1, 12)
        utc_offset = timezone.utcoffset(ref_datetime)
        ref_t, time_of_day = _datetime_to_float_timestamp(ref_datetime), ref_datetime.time()
        aware_time_of_day = timezone.localize(ref_datetime).timetz()

        # first test that naive time is assumed to be utc:
        assert helpers.to_float_timestamp(time_of_day, ref_t) == pytest.approx(ref_t)
        # test that by setting the timezone the timestamp changes accordingly:
        assert helpers.to_float_timestamp(aware_time_of_day, ref_t) == pytest.approx(
            ref_t + (-utc_offset.total_seconds() % (24 * 60 * 60))
        )

    @pytest.mark.parametrize('time_spec', RELATIVE_TIME_SPECS, ids=str)
    def test_to_float_timestamp_default_reference(self, time_spec):
        """The reference timestamp for relative time specifications should default to now"""
        now = time.time()
        assert helpers.to_float_timestamp(time_spec) == pytest.approx(
            helpers.to_float_timestamp(time_spec, reference_timestamp=now)
        )

    def test_to_float_timestamp_error(self):
        with pytest.raises(TypeError, match='Defaults'):
            helpers.to_float_timestamp(Defaults())

    @pytest.mark.parametrize('time_spec', TIME_SPECS, ids=str)
    def test_to_timestamp(self, time_spec):
        # delegate tests to `to_float_timestamp`
        assert helpers.to_timestamp(time_spec) == int(helpers.to_float_timestamp(time_spec))

    def test_to_timestamp_none(self):
        # this 'convenience' behaviour has been left left for backwards compatibility
        assert helpers.to_timestamp(None) is None

    def test_from_timestamp_none(self):
        assert helpers.from_timestamp(None) is None

    def test_from_timestamp_naive(self):
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, tzinfo=None)
        assert helpers.from_timestamp(1573431976, tzinfo=None) == datetime

    def test_from_timestamp_aware(self, timezone):
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        test_datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5)
        datetime = timezone.localize(test_datetime)
        assert (
            helpers.from_timestamp(
                1573431976.1 - timezone.utcoffset(test_datetime).total_seconds()
            )
            == datetime
        )

    def test_create_deep_linked_url(self):
        username = 'JamesTheMock'

        payload = "hello"
        expected = f"https://t.me/{username}?start={payload}"
        actual = helpers.create_deep_linked_url(username, payload)
        assert expected == actual

        expected = f"https://t.me/{username}?startgroup={payload}"
        actual = helpers.create_deep_linked_url(username, payload, group=True)
        assert expected == actual

        payload = ""
        expected = f"https://t.me/{username}"
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

        test_message = build_test_message(
            sticker=Sticker('sticker_id', 'unique_id', 50, 50, False)
        )
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

    def test_mention_markdown_2(self):
        expected = r'[the\_name](tg://user?id=1)'

        assert expected == helpers.mention_markdown(1, 'the_name')

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('tests/data/game.gif', True),
            ('tests/data', False),
            (str(Path.cwd() / 'tests' / 'data' / 'game.gif'), True),
            (str(Path.cwd() / 'tests' / 'data'), False),
            (Path.cwd() / 'tests' / 'data' / 'game.gif', True),
            (Path.cwd() / 'tests' / 'data', False),
            ('https:/api.org/file/botTOKEN/document/file_3', False),
            (None, False),
        ],
    )
    def test_is_local_file(self, string, expected):
        assert helpers.is_local_file(string) == expected

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('tests/data/game.gif', (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri()),
            ('tests/data', 'tests/data'),
            ('file://foobar', 'file://foobar'),
            (
                str(Path.cwd() / 'tests' / 'data' / 'game.gif'),
                (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri(),
            ),
            (str(Path.cwd() / 'tests' / 'data'), str(Path.cwd() / 'tests' / 'data')),
            (
                Path.cwd() / 'tests' / 'data' / 'game.gif',
                (Path.cwd() / 'tests' / 'data' / 'game.gif').as_uri(),
            ),
            (Path.cwd() / 'tests' / 'data', Path.cwd() / 'tests' / 'data'),
            (
                'https:/api.org/file/botTOKEN/document/file_3',
                'https:/api.org/file/botTOKEN/document/file_3',
            ),
        ],
    )
    def test_parse_file_input_string(self, string, expected):
        assert helpers.parse_file_input(string) == expected

    def test_parse_file_input_file_like(self):
        with open('tests/data/game.gif', 'rb') as file:
            parsed = helpers.parse_file_input(file)

        assert isinstance(parsed, InputFile)
        assert not parsed.attach
        assert parsed.filename == 'game.gif'

        with open('tests/data/game.gif', 'rb') as file:
            parsed = helpers.parse_file_input(file, attach=True, filename='test_file')

        assert isinstance(parsed, InputFile)
        assert parsed.attach
        assert parsed.filename == 'test_file'

    def test_parse_file_input_bytes(self):
        with open('tests/data/text_file.txt', 'rb') as file:
            parsed = helpers.parse_file_input(file.read())

        assert isinstance(parsed, InputFile)
        assert not parsed.attach
        assert parsed.filename == 'application.octet-stream'

        with open('tests/data/text_file.txt', 'rb') as file:
            parsed = helpers.parse_file_input(file.read(), attach=True, filename='test_file')

        assert isinstance(parsed, InputFile)
        assert parsed.attach
        assert parsed.filename == 'test_file'

    def test_parse_file_input_tg_object(self):
        animation = Animation('file_id', 'unique_id', 1, 1, 1)
        assert helpers.parse_file_input(animation, Animation) == 'file_id'
        assert helpers.parse_file_input(animation, MessageEntity) is animation

    @pytest.mark.parametrize('obj', [{1: 2}, [1, 2], (1, 2)])
    def test_parse_file_input_other(self, obj):
        assert helpers.parse_file_input(obj) is obj
