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
import inspect
from typing import List

keyword_args = [
    "Keyword Arguments:",
    (
        "    read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`. "
    ),
    (
        "    write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments"
        "        to be passed to the Telegram API. See :meth:`~telegram.Bot.do_api_request` for"
        "        limitations."
    ),
    "",
]

media_write_timeout_deprecation_methods = [
    "send_photo",
    "send_audio",
    "send_document",
    "send_sticker",
    "send_video",
    "send_video_note",
    "send_animation",
    "send_voice",
    "send_media_group",
    "set_chat_photo",
    "upload_sticker_file",
    "add_sticker_to_set",
    "create_new_sticker_set",
]
media_write_timeout_deprecation = [
    "    write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
    "        :paramref:`telegram.request.BaseRequest.post.write_timeout`. By default, ``20`` "
    "        seconds are used as write timeout."
    "",
    "",
    "       .. deprecated:: 20.7",
    "           In future versions, the default value will be changed to "
    "           :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    "",
    "",
]
get_updates_read_timeout_addition = [
    "        :paramref:`timeout` will be added to this value.",
    "",
    "",
    "        .. versionchanged:: 20.7",
    "           Defaults to :attr:`~telegram.request.BaseRequest.DEFAULT_NONE` instead of ",
    "           ``2``.",
]


def find_insert_pos_for_kwargs(lines: List[str]) -> int:
    """Finds the correct position to insert the keyword arguments and returns the index."""
    for idx, value in reversed(list(enumerate(lines))):  # reversed since :returns: is at the end
        if value.startswith("Returns"):
            return idx
    return False


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
