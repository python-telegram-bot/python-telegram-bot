#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
from future.utils import PY2

from telegram import TelegramObject


# TODO: when TelegramObject is no longer ABC this class needs overhaul
class TestTelegramObject:
    # TODO: Why is this??
    @pytest.mark.skipif(not PY2, reason='TelegramObject is only ABC on py2 for some reason')
    def test_abc(self):
        with pytest.raises(TypeError):
            TelegramObject()

    def test_to_json(self, monkeypatch):
        # to_json simply takes whatever comes from to_dict, therefore we only need to test it once
        if PY2:  # TelegramObject is only ABC on py2 :/
            monkeypatch.setattr('telegram.TelegramObject.__abstractmethods__', set())
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
