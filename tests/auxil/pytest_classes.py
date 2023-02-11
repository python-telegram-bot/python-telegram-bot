#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
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
from telegram import Bot, User
from telegram.ext import Application, ExtBot
from tests.conftest import BOT_INFO


def _get_bot_user(token: str) -> User:
    """Used to return a mock user in bot.get_me(). This saves API calls on every init."""
    bot_info = BOT_INFO.get_info()
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
