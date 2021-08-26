#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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

"""
We mainly test on UpdaterBuilder because it has all methods that DispatcherBuilder already has
"""

import pytest

from telegram.ext import UpdaterBuilder
from telegram.ext.builders import _BOT_CHECKS, _DISPATCHER_CHECKS


@pytest.fixture(scope='function')
def builder():
    return UpdaterBuilder()


UPDATER_METHODS = [slot.lstrip('_') for slot in UpdaterBuilder.__slots__ if 'was_set' not in slot]


class TestBuilder:
    @pytest.mark.parametrize('method', UPDATER_METHODS)
    def test_call_method_twice_for_updater_builder(self, builder, method):
        getattr(builder, method)(None)
        with pytest.raises(RuntimeError, match=f'`{method}` was already set.'):
            getattr(builder, method)(None)

    @pytest.mark.parametrize(
        'method, description', _BOT_CHECKS, ids=[entry[0] for entry in _BOT_CHECKS]
    )
    def test_mutually_exclusive_for_bot(self, builder, method, description):
        # First that e.g. `bot` can't be set if `request` was already set
        getattr(builder, method)(1)
        with pytest.raises(RuntimeError, match=f'`bot` can only be set, if the no {description}'):
            builder.bot(None)

        # Now test that `request` can't be set if `bot` was already set
        builder = UpdaterBuilder()
        builder.bot(None)
        with pytest.raises(
            RuntimeError, match=f'`{method}` can only be set, if the no bot instance'
        ):
            getattr(builder, method)(None)

    @pytest.mark.parametrize(
        'method, description', _DISPATCHER_CHECKS, ids=[entry[0] for entry in _DISPATCHER_CHECKS]
    )
    def test_mutually_exclusive_for_dispatcher(self, builder, method, description):
        # First that e.g. `dispatcher` can't be set if `bot` was already set
        getattr(builder, method)(None)
        with pytest.raises(
            RuntimeError, match=f'`dispatcher` can only be set, if the no {description}'
        ):
            builder.dispatcher(None)

        # Now test that `bot` can't be set if `dispatcher` was already set
        builder = UpdaterBuilder()
        builder.dispatcher(1)
        with pytest.raises(
            RuntimeError, match=f'`{method}` can only be set, if the no Dispatcher instance'
        ):
            getattr(builder, method)(None)

        # Finally test that `bot` *can* be set if `dispatcher` was set to None
        builder = UpdaterBuilder()
        builder.dispatcher(None)
        getattr(builder, method)(None)

    def test_mutually_exclusive_for_request(self, builder):
        builder.request(None)
        with pytest.raises(
            RuntimeError, match='`request_kwargs` can only be set, if the no Request instance'
        ):
            builder.request_kwargs(None)

        builder = UpdaterBuilder()
        builder.request_kwargs(None)
        with pytest.raises(
            RuntimeError, match='`request` can only be set, if the no request_kwargs'
        ):
            builder.request(None)

    def test_build_without_token(self, builder):
        with pytest.raises(RuntimeError, match='No bot token was set.'):
            builder.build()

    def test_build_custom_bot(self, builder, bot):
        builder.bot(bot)
        updater = builder.build()
        assert updater.bot is bot
        assert updater.dispatcher.bot is bot

    def test_build_custom_dispatcher(self, builder, cdp):
        builder.dispatcher(cdp)
        assert builder.build().dispatcher is cdp

    def test_build_no_dispatcher(self, builder, bot):
        builder.dispatcher(None).token(bot.token)
        updater = builder.build()
        assert updater.dispatcher is None
        assert updater.bot.token == bot.token
