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
import inspect

keyword_args = [
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.read_timeout: Value to pass to "
    ":paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to {read_timeout}.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.read_timeout: {read_timeout_type}, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.write_timeout: Value to pass to "
    ":paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to {write_timeout}.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.write_timeout: :obj:`float` | :obj:`None`, "
    "optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.connect_timeout: Value to pass to "
    ":paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to "
    ":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.connect_timeout: :obj:`float` | "
    ":obj:`None`, optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.pool_timeout: Value to pass to "
    ":paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to "
    ":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.pool_timeout: :obj:`float` | :obj:`None`, "
    "optional",
    ":keyword _sphinx_paramlinks_telegram.Bot.{method}.api_kwargs: Arbitrary keyword arguments "
    "to be passed to the Telegram API.",
    ":kwtype _sphinx_paramlinks_telegram.Bot.{method}.api_kwargs: :obj:`dict`, optional",
    "",
]
write_timeout_sub = [":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`", "``20``"]
read_timeout_sub = [
    ":attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    "``2``. :paramref:`timeout` will be added to this value",
]
read_timeout_type = [":obj:`float` | :obj:`None`", ":obj:`float`"]


def find_insert_pos_for_kwargs(lines: list[str]) -> int:
    """Finds the correct position to insert the keyword arguments and returns the index."""
    for idx, value in reversed(list(enumerate(lines))):  # reversed since :returns: is at the end
        if value.startswith(":returns:"):
            return idx
    else:
        return False


def is_write_timeout_20(obj: object) -> int:
    """inspects the default value of write_timeout parameter of the bot method."""
    sig = inspect.signature(obj)
    return 1 if (sig.parameters["write_timeout"].default == 20) else 0


def check_timeout_and_api_kwargs_presence(obj: object) -> int:
    """Checks if the method has timeout and api_kwargs keyword only parameters."""
    sig = inspect.signature(obj)
    params_to_check = (
        "read_timeout",
        "write_timeout",
        "connect_timeout",
        "pool_timeout",
        "api_kwargs",
    )
    return all(
        param in sig.parameters and sig.parameters[param].kind == inspect.Parameter.KEYWORD_ONLY
        for param in params_to_check
    )
