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
# along with this program. If not, see [http://www.gnu.org/licenses/].

import pytest

from telegram import WebAppInfo
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def web_app_info():
    return WebAppInfo(url=TestWebAppInfoBase.url)


class TestWebAppInfoBase:
    url = "https://www.example.com"


class TestWebAppInfoWithoutRequest(TestWebAppInfoBase):
    def test_slot_behaviour(self, web_app_info):
        for attr in web_app_info.__slots__:
            assert getattr(web_app_info, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(web_app_info)) == len(set(mro_slots(web_app_info))), "duplicate slot"

    def test_to_dict(self, web_app_info):
        web_app_info_dict = web_app_info.to_dict()

        assert isinstance(web_app_info_dict, dict)
        assert web_app_info_dict["url"] == self.url

    def test_de_json(self, bot):
        json_dict = {"url": self.url}
        web_app_info = WebAppInfo.de_json(json_dict, bot)
        assert web_app_info.api_kwargs == {}

        assert web_app_info.url == self.url

    def test_equality(self):
        a = WebAppInfo(self.url)
        b = WebAppInfo(self.url)
        c = WebAppInfo("")
        d = WebAppInfo("not_url")

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
