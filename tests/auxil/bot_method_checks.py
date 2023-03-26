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
import datetime
import functools
import inspect
from typing import Any, Callable, Dict, Iterable, List

import pytest

from telegram import (
    Bot,
    ChatPermissions,
    File,
    InlineQueryResultArticle,
    InlineQueryResultCachedPhoto,
    InputMediaPhoto,
    InputTextMessageContent,
    TelegramObject,
)
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram.constants import InputMediaType
from telegram.ext import Defaults, ExtBot
from telegram.request import RequestData
from tests.auxil.envvars import TEST_WITH_OPT_DEPS

if TEST_WITH_OPT_DEPS:
    import pytz


def check_shortcut_signature(
    shortcut: Callable,
    bot_method: Callable,
    shortcut_kwargs: List[str],
    additional_kwargs: List[str],
) -> bool:
    """
    Checks that the signature of a shortcut matches the signature of the underlying bot method.

    Args:
        shortcut: The shortcut, e.g. :meth:`telegram.Message.reply_text`
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``
        additional_kwargs: Additional kwargs of the shortcut that the bot method doesn't have, e.g.
            ``quote``.

    Returns:
        :obj:`bool`: Whether or not the signature matches.
    """
    shortcut_sig = inspect.signature(shortcut)
    effective_shortcut_args = set(shortcut_sig.parameters.keys()).difference(additional_kwargs)
    effective_shortcut_args.discard("self")

    bot_sig = inspect.signature(bot_method)
    expected_args = set(bot_sig.parameters.keys()).difference(shortcut_kwargs)
    expected_args.discard("self")

    args_check = expected_args == effective_shortcut_args
    if not args_check:
        raise Exception(f"Expected arguments {expected_args}, got {effective_shortcut_args}")

    # TODO: Also check annotation of return type. Would currently be a hassle b/c typing doesn't
    # resolve `ForwardRef('Type')` to `Type`. For now we rely on MyPy, which probably allows the
    # shortcuts to return more specific types than the bot method, but it's only annotations after
    # all
    for kwarg in effective_shortcut_args:
        expected_kind = bot_sig.parameters[kwarg].kind
        if shortcut_sig.parameters[kwarg].kind != expected_kind:
            raise Exception(f"Argument {kwarg} must be of kind {expected_kind}.")

        if bot_sig.parameters[kwarg].annotation != shortcut_sig.parameters[kwarg].annotation:
            if isinstance(bot_sig.parameters[kwarg].annotation, type):
                if bot_sig.parameters[kwarg].annotation.__name__ != str(
                    shortcut_sig.parameters[kwarg].annotation
                ):
                    raise Exception(
                        f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, "
                        f"but got {shortcut_sig.parameters[kwarg].annotation}"
                    )
            else:
                raise Exception(
                    f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, but "
                    f"got {shortcut_sig.parameters[kwarg].annotation}"
                )

    bot_method_sig = inspect.signature(bot_method)
    shortcut_sig = inspect.signature(shortcut)
    for arg in expected_args:
        if not shortcut_sig.parameters[arg].default == bot_method_sig.parameters[arg].default:
            raise Exception(
                f"Default for argument {arg} does not match the default of the Bot method."
            )

    for kwarg in additional_kwargs:
        if not shortcut_sig.parameters[kwarg].kind == inspect.Parameter.KEYWORD_ONLY:
            raise Exception(f"Argument {kwarg} must be a positional-only argument!")

    return True


async def check_shortcut_call(
    shortcut_method: Callable,
    bot: ExtBot,
    bot_method_name: str,
    skip_params: Iterable[str] = None,
    shortcut_kwargs: Iterable[str] = None,
) -> bool:
    """
    Checks that a shortcut passes all the existing arguments to the underlying bot method. Use as::

        assert await check_shortcut_call(message.reply_text, message.bot, 'send_message')

    Args:
        shortcut_method: The shortcut method, e.g. `message.reply_text`
        bot: The bot
        bot_method_name: The bot methods name, e.g. `'send_message'`
        skip_params: Parameters that are allowed to be missing, e.g. `['inline_message_id']`
            `rate_limit_args` will be skipped by default
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``

    Returns:
        :obj:`bool`
    """
    skip_params = set() if not skip_params else set(skip_params)
    skip_params.add("rate_limit_args")
    shortcut_kwargs = set() if not shortcut_kwargs else set(shortcut_kwargs)

    orig_bot_method = getattr(bot, bot_method_name)
    bot_signature = inspect.signature(orig_bot_method)
    expected_args = set(bot_signature.parameters.keys()) - {"self"} - set(skip_params)
    positional_args = {
        name for name, param in bot_signature.parameters.items() if param.default == param.empty
    }
    ignored_args = positional_args | set(shortcut_kwargs)

    shortcut_signature = inspect.signature(shortcut_method)
    # auto_pagination: Special casing for InlineQuery.answer
    kwargs = {name: name for name in shortcut_signature.parameters if name != "auto_pagination"}

    async def make_assertion(**kw):
        # name == value makes sure that
        # a) we receive non-None input for all parameters
        # b) we receive the correct input for each kwarg
        received_kwargs = {
            name for name, value in kw.items() if name in ignored_args or value == name
        }
        if not received_kwargs == expected_args:
            raise Exception(
                f"{orig_bot_method.__name__} did not receive correct value for the parameters "
                f"{expected_args - received_kwargs}"
            )

        if bot_method_name == "get_file":
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            return File(file_id="result", file_unique_id="result")
        return True

    setattr(bot, bot_method_name, make_assertion)
    try:
        await shortcut_method(**kwargs)
    except Exception as exc:
        raise exc
    finally:
        setattr(bot, bot_method_name, orig_bot_method)

    return True


def build_kwargs(signature: inspect.Signature, default_kwargs, dfv: Any = DEFAULT_NONE):
    kws = {}
    for name, param in signature.parameters.items():
        # For required params we need to pass something
        if param.default is inspect.Parameter.empty:
            # Some special casing
            if name == "permissions":
                kws[name] = ChatPermissions()
            elif name in ["prices", "commands", "errors"]:
                kws[name] = []
            elif name == "media":
                media = InputMediaPhoto("media", parse_mode=dfv)
                if "list" in str(param.annotation).lower():
                    kws[name] = [media]
                else:
                    kws[name] = media
            elif name == "results":
                itmc = InputTextMessageContent(
                    "text", parse_mode=dfv, disable_web_page_preview=dfv
                )
                kws[name] = [
                    InlineQueryResultArticle("id", "title", input_message_content=itmc),
                    InlineQueryResultCachedPhoto(
                        "id", "photo_file_id", parse_mode=dfv, input_message_content=itmc
                    ),
                ]
            elif name == "ok":
                kws["ok"] = False
                kws["error_message"] = "error"
            else:
                kws[name] = True
        # pass values for params that can have defaults only if we don't want to use the
        # standard default
        elif name in default_kwargs:
            if dfv != DEFAULT_NONE:
                kws[name] = dfv
        # Some special casing for methods that have "exactly one of the optionals" type args
        elif name in ["location", "contact", "venue", "inline_message_id"]:
            kws[name] = True
        # Special casing for some methods where the parameter is actually required, but is optional
        # for compatibility reasons
        # TODO: remove this once these arguments are marked as required
        elif name in {"sticker", "stickers", "sticker_format"}:
            kws[name] = "something passed"
        elif name == "until_date":
            if dfv == "non-None-value":
                # Europe/Berlin
                kws[name] = pytz.timezone("Europe/Berlin").localize(
                    datetime.datetime(2000, 1, 1, 0)
                )
            else:
                # UTC
                kws[name] = datetime.datetime(2000, 1, 1, 0)
    return kws


async def check_defaults_handling(
    method: Callable,
    bot: Bot,
    return_value=None,
) -> bool:
    """
    Checks that tg.ext.Defaults are handled correctly.

    Args:
        method: The shortcut/bot_method
        bot: The bot. May be a telegram.Bot or a telegram.ext.ExtBot. In the former case, all
            default values will be converted to None.
        return_value: Optional. The return value of Bot._post that the method expects. Defaults to
            None. get_file is automatically handled. If this is a `TelegramObject`, Bot._post will
            return the `to_dict` representation of it.

    """
    raw_bot = not isinstance(bot, ExtBot)
    get_updates = method.__name__.lower().replace("_", "") == "getupdates"

    shortcut_signature = inspect.signature(method)
    kwargs_need_default = [
        kwarg
        for kwarg, value in shortcut_signature.parameters.items()
        if isinstance(value.default, DefaultValue) and not kwarg.endswith("_timeout")
    ]

    if method.__name__.endswith("_media_group"):
        # the parse_mode is applied to the first media item, and we test this elsewhere
        kwargs_need_default.remove("parse_mode")

    defaults_no_custom_defaults = Defaults()
    kwargs = {kwarg: "custom_default" for kwarg in inspect.signature(Defaults).parameters}
    kwargs["tzinfo"] = pytz.timezone("America/New_York")
    defaults_custom_defaults = Defaults(**kwargs)

    expected_return_values = [None, ()] if return_value is None else [return_value]

    async def make_assertion(
        url, request_data: RequestData, df_value=DEFAULT_NONE, *args, **kwargs
    ):
        data = request_data.parameters

        # Check regular arguments that need defaults
        for arg in kwargs_need_default:
            # 'None' should not be passed along to Telegram
            if df_value in [None, DEFAULT_NONE]:
                if arg in data:
                    pytest.fail(
                        f"Got value {data[arg]} for argument {arg}, expected it to be absent"
                    )
            else:
                value = data.get(arg, "`not passed at all`")
                if value != df_value:
                    pytest.fail(f"Got value {value} for argument {arg} instead of {df_value}")

        # Check InputMedia (parse_mode can have a default)
        def check_input_media(m: Dict):
            parse_mode = m.get("parse_mode", None)
            if df_value is DEFAULT_NONE:
                if parse_mode is not None:
                    pytest.fail("InputMedia has non-None parse_mode")
            elif parse_mode != df_value:
                pytest.fail(
                    f"Got value {parse_mode} for InputMedia.parse_mode instead of {df_value}"
                )

        media = data.pop("media", None)
        if media:
            if isinstance(media, dict) and isinstance(media.get("type", None), InputMediaType):
                check_input_media(media)
            else:
                for m in media:
                    check_input_media(m)

        # Check InlineQueryResults
        results = data.pop("results", [])
        for result in results:
            if df_value in [DEFAULT_NONE, None]:
                if "parse_mode" in result:
                    pytest.fail("ILQR has a parse mode, expected it to be absent")
            # Here we explicitly use that we only pass ILQRPhoto and ILQRArticle for testing
            # so ILQRPhoto is expected to have parse_mode if df_value is not in [DF_NONE, NONE]
            elif "photo" in result and result.get("parse_mode") != df_value:
                pytest.fail(
                    f'Got value {result.get("parse_mode")} for '
                    f"ILQR.parse_mode instead of {df_value}"
                )
            imc = result.get("input_message_content")
            if not imc:
                continue
            for attr in ["parse_mode", "disable_web_page_preview"]:
                if df_value in [DEFAULT_NONE, None]:
                    if attr in imc:
                        pytest.fail(f"ILQR.i_m_c has a {attr}, expected it to be absent")
                # Here we explicitly use that we only pass InputTextMessageContent for testing
                # which has both attributes
                elif imc.get(attr) != df_value:
                    pytest.fail(
                        f"Got value {imc.get(attr)} for ILQR.i_m_c.{attr} instead of {df_value}"
                    )

        # Check datetime conversion
        until_date = data.pop("until_date", None)
        if until_date:
            if df_value == "non-None-value" and until_date != 946681200:
                pytest.fail("Non-naive until_date was interpreted as Europe/Berlin.")
            if df_value is DEFAULT_NONE and until_date != 946684800:
                pytest.fail("Naive until_date was not interpreted as UTC")
            if df_value == "custom_default" and until_date != 946702800:
                pytest.fail("Naive until_date was not interpreted as America/New_York")

        if method.__name__ in ["get_file", "get_small_file", "get_big_file"]:
            # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
            # return value
            out = File(file_id="result", file_unique_id="result")
            nonlocal expected_return_values
            expected_return_values = [out]
            return out.to_dict()
        # Otherwise return None by default, as TGObject.de_json/list(None) in [None, []]
        # That way we can check what gets passed to Request.post without having to actually
        # make a request
        # Some methods expect specific output, so we allow to customize that
        if isinstance(return_value, TelegramObject):
            return return_value.to_dict()
        return return_value

    request = bot._request[0] if get_updates else bot.request
    orig_post = request.post
    try:
        if raw_bot:
            combinations = [(DEFAULT_NONE, None)]
        else:
            combinations = [
                (DEFAULT_NONE, defaults_no_custom_defaults),
                ("custom_default", defaults_custom_defaults),
            ]

        for default_value, defaults in combinations:
            if not raw_bot:
                bot._defaults = defaults

            # 1: test that we get the correct default value, if we don't specify anything
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
            )
            assertion_callback = functools.partial(make_assertion, df_value=default_value)
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values

            # 2: test that we get the manually passed non-None value
            kwargs = build_kwargs(shortcut_signature, kwargs_need_default, dfv="non-None-value")
            assertion_callback = functools.partial(make_assertion, df_value="non-None-value")
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values

            # 3: test that we get the manually passed None value
            kwargs = build_kwargs(
                shortcut_signature,
                kwargs_need_default,
                dfv=None,
            )
            assertion_callback = functools.partial(make_assertion, df_value=None)
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values
    except Exception as exc:
        raise exc
    finally:
        request.post = orig_post
        if not raw_bot:
            bot._defaults = None

    return True
