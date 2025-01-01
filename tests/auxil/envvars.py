#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2025
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
import os


def env_var_2_bool(env_var: object) -> bool:
    if isinstance(env_var, bool):
        return env_var
    if not isinstance(env_var, str):
        return False
    return env_var.lower().strip() == "true"


GITHUB_ACTIONS: bool = env_var_2_bool(os.getenv("GITHUB_ACTIONS", "false"))
TEST_WITH_OPT_DEPS: bool = env_var_2_bool(os.getenv("TEST_WITH_OPT_DEPS", "false")) or (
    # on local setups, we usually want to test with optional dependencies
    not GITHUB_ACTIONS
)
RUN_TEST_OFFICIAL: bool = env_var_2_bool(os.getenv("TEST_OFFICIAL"))
