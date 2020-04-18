#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import time
import datetime as dtm

import pytest

from telegram import Sticker
from telegram import Update
from telegram import User
from telegram import MessageEntity
from telegram.message import Message
from telegram.utils import helpers
from telegram.utils.helpers import _UtcOffsetTimezone, _datetime_to_float_timestamp


# sample time specification values categorised into absolute / delta / time-of-day
ABSOLUTE_TIME_SPECS = [dtm.datetime.now(tz=_UtcOffsetTimezone(dtm.timedelta(hours=-7))),
                       dtm.datetime.utcnow()]
DELTA_TIME_SPECS = [dtm.timedelta(hours=3, seconds=42, milliseconds=2), 30, 7.5]
TIME_OF_DAY_TIME_SPECS = [dtm.time(12, 42, tzinfo=_UtcOffsetTimezone(dtm.timedelta(hours=-7))),
                          dtm.time(12, 42)]
RELATIVE_TIME_SPECS = DELTA_TIME_SPECS + TIME_OF_DAY_TIME_SPECS
TIME_SPECS = ABSOLUTE_TIME_SPECS + RELATIVE_TIME_SPECS


class TestHelpers(object):
    def test_escape_markdown(self):
        test_str = '*bold*, _italic_, `code`, [text_link](http://github.com/)'
        expected_str = '\*bold\*, \_italic\_, \`code\`, \[text\_link](http://github.com/)'

        assert expected_str == helpers.escape_markdown(test_str)

    def test_escape_markdown_v2(self):
        test_str = 'a_b*c[d]e (fg) h~I`>JK#L+MN -O=|p{qr}s.t! u'
        expected_str = 'a\_b\*c\[d\]e \(fg\) h\~I\`\>JK\#L\+MN \-O\=\|p\{qr\}s\.t\! u'

        assert expected_str == helpers.escape_markdown(test_str, version=2)

    def test_escape_markdown_v2_monospaced(self):

        test_str = 'mono/pre: `abc` \int (`\some \`stuff)'
        expected_str = 'mono/pre: \`abc\` \\\\int (\`\\\\some \\\\\`stuff)'

        assert expected_str == helpers.escape_markdown(test_str, version=2,
                                                       entity_type=MessageEntity.PRE)
        assert expected_str == helpers.escape_markdown(test_str, version=2,
                                                       entity_type=MessageEntity.CODE)

    def test_escape_markdown_v2_text_link(self):

        test_str = 'https://url.containing/funny)cha)\\ra\)cter\s'
        expected_str = 'https://url.containing/funny\)cha\)\\\\ra\\\\\)cter\\\\s'

        assert expected_str == helpers.escape_markdown(test_str, version=2,
                                                       entity_type=MessageEntity.TEXT_LINK)

    def test_markdown_invalid_version(self):
        with pytest.raises(ValueError):
            helpers.escape_markdown('abc', version=-1)

    def test_to_float_timestamp_absolute_naive(self):
        """Conversion from timezone-naive datetime to timestamp.
        Naive datetimes should be assumed to be in UTC.
        """
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5)
        assert helpers.to_float_timestamp(datetime) == 1573431976.1

    def test_to_float_timestamp_absolute_aware(self, timezone):
        """Conversion from timezone-aware datetime to timestamp"""
        # we're parametrizing this with two different UTC offsets to exclude the possibility
        # of an xpass when the test is run in a timezone with the same UTC offset
        datetime = dtm.datetime(2019, 11, 11, 0, 26, 16, 10**5, tzinfo=timezone)
        assert (helpers.to_float_timestamp(datetime)
                == 1573431976.1 - timezone.utcoffset(None).total_seconds())

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
        utc_offset = timezone.utcoffset(None)
        ref_datetime = dtm.datetime(1970, 1, 1, 12)
        ref_t, time_of_day = _datetime_to_float_timestamp(ref_datetime), ref_datetime.time()

        # first test that naive time is assumed to be utc:
        assert helpers.to_float_timestamp(time_of_day, ref_t) == pytest.approx(ref_t)
        # test that by setting the timezone the timestamp changes accordingly:
        assert (helpers.to_float_timestamp(time_of_day.replace(tzinfo=timezone), ref_t)
                == pytest.approx(ref_t + (-utc_offset.total_seconds() % (24 * 60 * 60))))

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

        test_message = build_test_message(sticker=Sticker('sticker_id', 'unique_id',
                                          50, 50, False))
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
