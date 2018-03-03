#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import json as json_lib

import pytest

try:
    import ujson
except ImportError:
    ujson = None

from telegram import TelegramObject


class TestTelegramObject(object):
    def test_to_json_native(self, monkeypatch):
        if ujson:
            monkeypatch.setattr('ujson.dumps', json_lib.dumps)
        # to_json simply takes whatever comes from to_dict, therefore we only need to test it once
        telegram_object = TelegramObject()

        # Test that it works with a dict with str keys as well as dicts as lists as values
        d = {'str': 'str', 'str2': ['str', 'str'], 'str3': {'str': 'str'}}
        monkeypatch.setattr('telegram.TelegramObject.to_dict', lambda _: d)
        json = telegram_object.to_json()
        # Order isn't guarantied
        assert '"str": "str"' in json
        assert '"str2": ["str", "str"]' in json
        assert '"str3": {"str": "str"}' in json

        # Now make sure that it doesn't work with not json stuff and that it fails loudly
        # Tuples aren't allowed as keys in json
        d = {('str', 'str'): 'str'}

        monkeypatch.setattr('telegram.TelegramObject.to_dict', lambda _: d)
        with pytest.raises(TypeError):
            telegram_object.to_json()

    @pytest.mark.skipif(not ujson, reason='ujson not installed')
    def test_to_json_ujson(self, monkeypatch):
        # to_json simply takes whatever comes from to_dict, therefore we only need to test it once
        telegram_object = TelegramObject()

        # Test that it works with a dict with str keys as well as dicts as lists as values
        d = {'str': 'str', 'str2': ['str', 'str'], 'str3': {'str': 'str'}}
        monkeypatch.setattr('telegram.TelegramObject.to_dict', lambda _: d)
        json = telegram_object.to_json()
        # Order isn't guarantied and ujon discards whitespace
        assert '"str":"str"' in json
        assert '"str2":["str","str"]' in json
        assert '"str3":{"str":"str"}' in json

        # Test that ujson allows tuples
        # NOTE: This could be seen as a bug (since it's differnt from the normal "json",
        # but we test it anyways
        d = {('str', 'str'): 'str'}

        monkeypatch.setattr('telegram.TelegramObject.to_dict', lambda _: d)
        telegram_object.to_json()
