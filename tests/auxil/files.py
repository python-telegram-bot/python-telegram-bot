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
import logging
from pathlib import Path
from typing import Protocol, Union

from telegram import Bot, File

PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
TEST_DATA_PATH = PROJECT_ROOT_PATH / "tests" / "data"


def data_file(filename: str) -> Path:
    return TEST_DATA_PATH / filename


class _HasGetFile(Protocol):
    async def get_file(self) -> File: ...


async def stable_get_file(bot: Bot, obj: Union[_HasGetFile, str]) -> File:
    """Temporary workaround for Telegram API returning file_path as None on first call to
    get_file. This function will attempt to get the file 3 times before raising an error.
    Remove this once https://github.com/tdlib/telegram-bot-api/issues/658 as closed."""
    for i in range(3):
        file = await bot.get_file(obj) if isinstance(obj, str) else await obj.get_file()
        if file.file_path:
            logging.debug("File path returned by TG on attempt %s", i + 1)
            return file

    raise RuntimeError("File path not found returned by TG after 3 attempts")
