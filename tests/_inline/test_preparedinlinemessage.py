#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

import pytest

from telegram import Location, PreparedInlineMessage
from telegram._utils.datetime import UTC, to_timestamp
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def prepared_inline_message():
    return PreparedInlineMessage(
        PreparedInlineMessageTestBase.id,
        PreparedInlineMessageTestBase.expiration_date,
    )


class PreparedInlineMessageTestBase:
    id = "some_uid"
    expiration_date = dtm.datetime.now(tz=UTC).replace(microsecond=0)


class TestPreparedInlineMessageWithoutRequest(
    PreparedInlineMessageTestBase, DeserializationTestBase
):
    de_json_class = PreparedInlineMessage

    @pytest.fixture
    def de_json_dict(self):
        return {
            "id": self.id,
            "expiration_date": to_timestamp(self.expiration_date),
        }

    def test_slot_behaviour(self, prepared_inline_message):
        inst = prepared_inline_message
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_expected_values(self, prepared_inline_message):
        assert prepared_inline_message.id == self.id
        assert prepared_inline_message.expiration_date == self.expiration_date

    def test_de_json(self, offline_bot, de_json_dict, prepared_inline_message):
        new_prepared_inline_message = PreparedInlineMessage.de_json(de_json_dict, offline_bot)
        assert new_prepared_inline_message.api_kwargs == {}

        assert isinstance(new_prepared_inline_message, PreparedInlineMessage)
        assert new_prepared_inline_message.id == prepared_inline_message.id
        assert (
            new_prepared_inline_message.expiration_date == prepared_inline_message.expiration_date
        )

    def test_to_dict(self, prepared_inline_message):
        prepared_inline_message_dict = prepared_inline_message.to_dict()

        assert isinstance(prepared_inline_message_dict, dict)
        assert prepared_inline_message_dict["id"] == prepared_inline_message.id
        assert prepared_inline_message_dict["expiration_date"] == to_timestamp(
            self.expiration_date
        )

    def test_equality(self, prepared_inline_message):
        a = prepared_inline_message
        b = PreparedInlineMessage(self.id, self.expiration_date)
        c = PreparedInlineMessage(self.id, self.expiration_date + dtm.timedelta(seconds=1))
        d = PreparedInlineMessage("other_uid", self.expiration_date)
        e = Location(123, 456)

        assert a == b
        assert hash(a) == hash(b)

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
