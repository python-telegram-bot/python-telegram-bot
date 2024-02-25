#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2024
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains subclasses of classes from the python-telegram-bot library that
modify behavior of the respective parent classes in order to make them easier to use in the
pytest framework. A common change is to allow monkeypatching of the class members by not
enforcing slots in the subclasses."""
from telegram import Bot, Message, User
from telegram.ext import Application, ExtBot
from tests.auxil.ci_bots import BOT_INFO_PROVIDER
from tests.auxil.constants import PRIVATE_KEY
from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.networking import NonchalantHttpxRequest


def _get_bot_user(token: str) -> User:
    """Used to return a mock user in bot.get_me(). This saves API calls on every init."""
    bot_info = BOT_INFO_PROVIDER.get_info()
    # We don't take token from bot_info, because we need to make a bot with a specific ID. So we
    # generate the correct user_id from the token (token from bot_info is random each test run).
    # This is important in e.g. bot equality tests. The other parameters like first_name don't
    # matter as much. In the future we may provide a way to get all the correct info from the token
    user_id = int(token.split(":")[0])
    first_name = bot_info.get(
        "name",
    )
    username = bot_info.get(
        "username",
    ).strip("@")
    return User(
        user_id,
        first_name,
        is_bot=True,
        username=username,
        can_join_groups=True,
        can_read_all_group_messages=False,
        supports_inline_queries=True,
    )


async def _mocked_get_me(bot: Bot):
    if bot._bot_user is None:
        bot._bot_user = _get_bot_user(bot.token)
    return bot._bot_user


class PytestExtBot(ExtBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args, **kwargs):
        return await _mocked_get_me(self)


class PytestBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args, **kwargs):
        return await _mocked_get_me(self)


class PytestApplication(Application):
    pass


class PytestMessage(Message):
    pass


def make_bot(bot_info=None, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    token = kwargs.pop("token", (bot_info or {}).get("token"))
    private_key = kwargs.pop("private_key", PRIVATE_KEY)
    kwargs.pop("token", None)
    return PytestExtBot(
        token=token,
        private_key=private_key if TEST_WITH_OPT_DEPS else None,
        request=NonchalantHttpxRequest(8),
        get_updates_request=NonchalantHttpxRequest(1),
        **kwargs,
    )
