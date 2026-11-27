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
import time

import pytest

from telegram import LoginUrl, WebhookInfo
from telegram._utils.datetime import from_timestamp
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def webhook_info():
    return WebhookInfo(
        url=WebhookInfoTestBase.url,
        has_custom_certificate=WebhookInfoTestBase.has_custom_certificate,
        pending_update_count=WebhookInfoTestBase.pending_update_count,
        ip_address=WebhookInfoTestBase.ip_address,
        last_error_date=WebhookInfoTestBase.last_error_date,
        last_error_message=WebhookInfoTestBase.last_error_message,
        max_connections=WebhookInfoTestBase.max_connections,
        allowed_updates=WebhookInfoTestBase.allowed_updates,
        last_synchronization_error_date=WebhookInfoTestBase.last_synchronization_error_date,
    )


class WebhookInfoTestBase:
    url = "http://www.google.com"
    has_custom_certificate = False
    pending_update_count = 5
    ip_address = "127.0.0.1"
    last_error_date = int(time.time())
    last_error_message = "Connection timed out"
    max_connections = 42
    allowed_updates = ["message", "callback_query"]
    last_synchronization_error_date = int(time.time())


class TestWebhookInfoWithoutRequest(WebhookInfoTestBase, DeserializationTestBase):
    de_json_class = WebhookInfo

    @pytest.fixture
    def de_json_dict(self):
        return {
            "url": self.url,
            "has_custom_certificate": self.has_custom_certificate,
            "pending_update_count": self.pending_update_count,
            "last_error_date": self.last_error_date,
            "last_error_message": self.last_error_message,
            "max_connections": self.max_connections,
            "allowed_updates": self.allowed_updates,
            "ip_address": self.ip_address,
            "last_synchronization_error_date": self.last_synchronization_error_date,
        }

    def test_slot_behaviour(self, webhook_info):
        for attr in webhook_info.__slots__:
            assert getattr(webhook_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(webhook_info)) == len(set(mro_slots(webhook_info))), "duplicate slot"

    def test_to_dict(self, webhook_info):
        webhook_info_dict = webhook_info.to_dict()

        assert isinstance(webhook_info_dict, dict)
        assert webhook_info_dict["url"] == self.url
        assert webhook_info_dict["pending_update_count"] == self.pending_update_count
        assert webhook_info_dict["last_error_date"] == self.last_error_date
        assert webhook_info_dict["last_error_message"] == self.last_error_message
        assert webhook_info_dict["max_connections"] == self.max_connections
        assert webhook_info_dict["allowed_updates"] == self.allowed_updates
        assert webhook_info_dict["ip_address"] == self.ip_address
        assert (
            webhook_info_dict["last_synchronization_error_date"]
            == self.last_synchronization_error_date
        )

    def test_de_json(self, offline_bot, de_json_dict):
        webhook_info = WebhookInfo.de_json(de_json_dict, offline_bot)
        assert webhook_info.api_kwargs == {}

        assert webhook_info.url == self.url
        assert webhook_info.has_custom_certificate == self.has_custom_certificate
        assert webhook_info.pending_update_count == self.pending_update_count
        assert isinstance(webhook_info.last_error_date, dtm.datetime)
        assert webhook_info.last_error_date == from_timestamp(self.last_error_date)
        assert webhook_info.last_error_message == self.last_error_message
        assert webhook_info.max_connections == self.max_connections
        assert webhook_info.allowed_updates == tuple(self.allowed_updates)
        assert webhook_info.ip_address == self.ip_address
        assert isinstance(webhook_info.last_synchronization_error_date, dtm.datetime)
        assert webhook_info.last_synchronization_error_date == from_timestamp(
            self.last_synchronization_error_date
        )

    def test_always_tuple_allowed_updates(self):
        webhook_info = WebhookInfo(
            self.url, self.has_custom_certificate, self.pending_update_count
        )
        assert webhook_info.allowed_updates == ()

    def test_equality(self):
        a = WebhookInfo(
            url=self.url,
            has_custom_certificate=self.has_custom_certificate,
            pending_update_count=self.pending_update_count,
            last_error_date=self.last_error_date,
            max_connections=self.max_connections,
        )
        b = WebhookInfo(
            url=self.url,
            has_custom_certificate=self.has_custom_certificate,
            pending_update_count=self.pending_update_count,
            last_error_date=self.last_error_date,
            max_connections=self.max_connections,
        )
        c = WebhookInfo(
            url="http://github.com",
            has_custom_certificate=True,
            pending_update_count=78,
            last_error_date=0,
            max_connections=1,
        )
        d = WebhookInfo(
            url="http://github.com",
            has_custom_certificate=True,
            pending_update_count=78,
            last_error_date=0,
            max_connections=1,
            last_synchronization_error_date=123,
        )
        e = LoginUrl("text.com")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
