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
import time

from telegram import WebhookInfo, LoginUrl


@pytest.fixture(scope='class')
def webhook_info():
    return WebhookInfo(
        url=TestWebhookInfo.url,
        has_custom_certificate=TestWebhookInfo.has_custom_certificate,
        pending_update_count=TestWebhookInfo.pending_update_count,
        ip_address=TestWebhookInfo.ip_address,
        last_error_date=TestWebhookInfo.last_error_date,
        max_connections=TestWebhookInfo.max_connections,
        allowed_updates=TestWebhookInfo.allowed_updates,
    )


class TestWebhookInfo:
    url = "http://www.google.com"
    has_custom_certificate = False
    pending_update_count = 5
    ip_address = '127.0.0.1'
    last_error_date = time.time()
    max_connections = 42
    allowed_updates = ['type1', 'type2']

    def test_slot_behaviour(self, webhook_info, mro_slots, recwarn):
        for attr in webhook_info.__slots__:
            assert getattr(webhook_info, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not webhook_info.__dict__, f"got missing slot(s): {webhook_info.__dict__}"
        assert len(mro_slots(webhook_info)) == len(set(mro_slots(webhook_info))), "duplicate slot"
        webhook_info.custom, webhook_info.url = 'should give warning', self.url
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_to_dict(self, webhook_info):
        webhook_info_dict = webhook_info.to_dict()

        assert isinstance(webhook_info_dict, dict)
        assert webhook_info_dict['url'] == self.url
        assert webhook_info_dict['pending_update_count'] == self.pending_update_count
        assert webhook_info_dict['last_error_date'] == self.last_error_date
        assert webhook_info_dict['max_connections'] == self.max_connections
        assert webhook_info_dict['allowed_updates'] == self.allowed_updates
        assert webhook_info_dict['ip_address'] == self.ip_address

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
        d = LoginUrl("text.com")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
