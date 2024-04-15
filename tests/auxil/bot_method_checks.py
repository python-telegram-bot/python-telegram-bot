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
"""Provides functions to test both methods."""
import datetime
import functools
import inspect
import re
from typing import Any, Callable, Collection, Dict, Iterable, List, Optional, Tuple

import pytest

import telegram  # for ForwardRef resolution
from telegram import (
    Bot,
    ChatPermissions,
    File,
    InlineQueryResultArticle,
    InlineQueryResultCachedPhoto,
    InputMediaPhoto,
    InputTextMessageContent,
    LinkPreviewOptions,
    ReplyParameters,
    TelegramObject,
)
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram.constants import InputMediaType
from telegram.ext import Defaults, ExtBot
from telegram.request import RequestData
from tests.auxil.envvars import TEST_WITH_OPT_DEPS

if TEST_WITH_OPT_DEPS:
    import pytz


FORWARD_REF_PATTERN = re.compile(r"ForwardRef\('(?P<class_name>\w+)'\)")
""" A pattern to find a class name in a ForwardRef typing annotation.
Class name (in a named group) is surrounded by parentheses and single quotes.
"""


def check_shortcut_signature(
    shortcut: Callable,
    bot_method: Callable,
    shortcut_kwargs: List[str],
    additional_kwargs: List[str],
    annotation_overrides: Optional[Dict[str, Tuple[Any, Any]]] = None,
) -> bool:
    """
    Checks that the signature of a shortcut matches the signature of the underlying bot method.

    Args:
        shortcut: The shortcut, e.g. :meth:`telegram.Message.reply_text`
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``
        additional_kwargs: Additional kwargs of the shortcut that the bot method doesn't have, e.g.
            ``quote``.
        annotation_overrides: A dictionary of exceptions for the annotation comparison. The key is
            the name of the argument, the value is a tuple of the expected annotation and
            the default value. E.g. ``{'parse_mode': (str, 'None')}``.

    Returns:
        :obj:`bool`: Whether or not the signature matches.
    """
    annotation_overrides = annotation_overrides or {}

    def resolve_class(class_name: str) -> Optional[type]:
        """Attempts to resolve a PTB class (telegram module only) from a ForwardRef.

        E.g. resolves <class 'telegram._files.sticker.StickerSet'> from "StickerSet".

        Returns a class on success, :obj:`None` if nothing could be resolved.
        """
        for module in telegram, telegram.request:
            cls = getattr(module, class_name, None)
            if cls is not None:
                return cls
        return None  # for ruff

    shortcut_sig = inspect.signature(shortcut)
    effective_shortcut_args = set(shortcut_sig.parameters.keys()).difference(additional_kwargs)
    effective_shortcut_args.discard("self")

    bot_sig = inspect.signature(bot_method)
    expected_args = set(bot_sig.parameters.keys()).difference(shortcut_kwargs)
    expected_args.discard("self")

    len_expected = len(expected_args)
    len_effective = len(effective_shortcut_args)
    if len_expected > len_effective:
        raise Exception(
            f"Shortcut signature is missing {len_expected - len_effective} arguments "
            f"of the underlying Bot method: {expected_args - effective_shortcut_args}"
        )
    if len_expected < len_effective:
        raise Exception(
            f"Shortcut signature has {len_effective - len_expected} additional arguments "
            f"that the Bot method doesn't have: {effective_shortcut_args - expected_args}"
        )

    # TODO: Also check annotation of return type. Would currently be a hassle b/c typing doesn't
    # resolve `ForwardRef('Type')` to `Type`. For now we rely on MyPy, which probably allows the
    # shortcuts to return more specific types than the bot method, but it's only annotations after
    # all
    for kwarg in effective_shortcut_args:
        expected_kind = bot_sig.parameters[kwarg].kind
        if shortcut_sig.parameters[kwarg].kind != expected_kind:
            raise Exception(f"Argument {kwarg} must be of kind {expected_kind}.")

        if kwarg in annotation_overrides:
            if shortcut_sig.parameters[kwarg].annotation != annotation_overrides[kwarg][0]:
                raise Exception(
                    f"For argument {kwarg} I expected {annotation_overrides[kwarg]}, "
                    f"but got {shortcut_sig.parameters[kwarg].annotation}"
                )
            continue

        if bot_sig.parameters[kwarg].annotation != shortcut_sig.parameters[kwarg].annotation:
            if FORWARD_REF_PATTERN.search(str(shortcut_sig.parameters[kwarg])):
                # If a shortcut signature contains a ForwardRef, the simple comparison of
                # annotations can fail. Try and resolve the .__args__, then compare them.

                for shortcut_arg, bot_arg in zip(
                    shortcut_sig.parameters[kwarg].annotation.__args__,
                    bot_sig.parameters[kwarg].annotation.__args__,
                ):
                    shortcut_arg_to_check = shortcut_arg  # for ruff
                    match = FORWARD_REF_PATTERN.search(str(shortcut_arg))
                    if match:
                        shortcut_arg_to_check = resolve_class(match.group("class_name"))

                    if shortcut_arg_to_check != bot_arg:
                        raise Exception(
                            f"For argument {kwarg} I expected "
                            f"{bot_sig.parameters[kwarg].annotation}, but "
                            f"got {shortcut_sig.parameters[kwarg].annotation}."
                            f"Comparison of {shortcut_arg} and {bot_arg} failed."
                        )
            elif isinstance(bot_sig.parameters[kwarg].annotation, type):
                if bot_sig.parameters[kwarg].annotation.__name__ != str(
                    shortcut_sig.parameters[kwarg].annotation
                ):
                    raise Exception(
                        f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation}, "
                        f"but got {shortcut_sig.parameters[kwarg].annotation}"
                    )
            else:
                raise Exception(
                    f"For argument {kwarg} I expected {bot_sig.parameters[kwarg].annotation},"
                    f"but got {shortcut_sig.parameters[kwarg].annotation}"
                )

    bot_method_sig = inspect.signature(bot_method)
    shortcut_sig = inspect.signature(shortcut)
    for arg in expected_args:
        if arg in annotation_overrides:
            if shortcut_sig.parameters[arg].default == annotation_overrides[arg][1]:
                continue
            raise Exception(
                f"For argument {arg} I expected default {annotation_overrides[arg][1]}, "
                f"but got {shortcut_sig.parameters[arg].default}"
            )
        if not shortcut_sig.parameters[arg].default == bot_method_sig.parameters[arg].default:
            raise Exception(
                f"Default for argument {arg} does not match the default of the Bot method."
            )

    for kwarg in additional_kwargs:
        if kwarg == "reply_to_message_id":
            # special case for deprecated argument of Message.reply_*
            continue
        if not shortcut_sig.parameters[kwarg].kind == inspect.Parameter.KEYWORD_ONLY:
            raise Exception(f"Argument {kwarg} must be a positional-only argument!")

    return True


async def check_shortcut_call(
    shortcut_method: Callable,
    bot: ExtBot,
    bot_method_name: str,
    skip_params: Optional[Iterable[str]] = None,
    shortcut_kwargs: Optional[Iterable[str]] = None,
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
    # quote: Don't test deprecated "quote" parameter of Message.reply_*
    kwargs = {
        name: name
        for name in shortcut_signature.parameters
        if name not in ["auto_pagination", "quote"]
    }
    if "reply_parameters" in kwargs:
        kwargs["reply_parameters"] = ReplyParameters(message_id=1)

    # We tested this for a long time, but Bot API 7.0 deprecated it in favor of
    # reply_parameters. In the transition phase, both exist in a mutually exclusive
    # way. Testing both cases would require a lot of additional code, so we just
    # ignore this parameter here until it is removed.
    kwargs.pop("reply_to_message_id", None)
    expected_args.discard("reply_to_message_id")

    async def make_assertion(**kw):
        # name == value makes sure that
        # a) we receive non-None input for all parameters
        # b) we receive the correct input for each kwarg
        received_kwargs = {
            name
            for name, value in kw.items()
            if name in ignored_args
            or (value == name or (name == "reply_parameters" and value.message_id == 1))
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


def build_kwargs(
    signature: inspect.Signature, default_kwargs, manually_passed_value: Any = DEFAULT_NONE
):
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
                media = InputMediaPhoto("media", parse_mode=manually_passed_value)
                if "list" in str(param.annotation).lower():
                    kws[name] = [media]
                else:
                    kws[name] = media
            elif name == "results":
                itmc = InputTextMessageContent(
                    "text",
                    parse_mode=manually_passed_value,
                    link_preview_options=LinkPreviewOptions(
                        is_disabled=manually_passed_value, url=manually_passed_value
                    ),
                )
                kws[name] = [
                    InlineQueryResultArticle("id", "title", input_message_content=itmc),
                    InlineQueryResultCachedPhoto(
                        "id",
                        "photo_file_id",
                        parse_mode=manually_passed_value,
                        input_message_content=itmc,
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
            if manually_passed_value != DEFAULT_NONE:
                if name == "link_preview_options":
                    kws[name] = LinkPreviewOptions(
                        is_disabled=manually_passed_value, url=manually_passed_value
                    )
                else:
                    kws[name] = manually_passed_value
        # Some special casing for methods that have "exactly one of the optionals" type args
        elif name in ["location", "contact", "venue", "inline_message_id"]:
            kws[name] = True
        elif name == "until_date":
            if manually_passed_value not in [None, DEFAULT_NONE]:
                # Europe/Berlin
                kws[name] = pytz.timezone("Europe/Berlin").localize(
                    datetime.datetime(2000, 1, 1, 0)
                )
            else:
                # naive UTC
                kws[name] = datetime.datetime(2000, 1, 1, 0)
        elif name == "reply_parameters":
            kws[name] = telegram.ReplyParameters(
                message_id=1,
                allow_sending_without_reply=manually_passed_value,
                quote_parse_mode=manually_passed_value,
            )

    return kws


def make_assertion_for_link_preview_options(
    expected_defaults_value, lpo, manual_value_expected, manually_passed_value
):
    if not lpo:
        return

    # if no_value_expected:
    #     # We always expect a value for link_preview_options, because we don't test the
    #     # case send_message(…, link_preview_options=None). Instead we focus on the more
    #     # compicated case of send_message(…, link_preview_options=LinkPreviewOptions(arg=None))
    if manual_value_expected:
        if lpo.get("is_disabled") != manually_passed_value:
            pytest.fail(
                f"Got value {lpo.get('is_disabled')} for link_preview_options.is_disabled, "
                f"expected it to be {manually_passed_value}"
            )
        if lpo.get("url") != manually_passed_value:
            pytest.fail(
                f"Got value {lpo.get('url')} for link_preview_options.url, "
                f"expected it to be {manually_passed_value}"
            )
    if expected_defaults_value:
        if lpo.get("show_above_text") != expected_defaults_value:
            pytest.fail(
                f"Got value {lpo.get('show_above_text')} for link_preview_options.show_above_text,"
                f" expected it to be {expected_defaults_value}"
            )
        if manually_passed_value is DEFAULT_NONE and lpo.get("url") != expected_defaults_value:
            pytest.fail(
                f"Got value {lpo.get('url')} for link_preview_options.url, "
                f"expected it to be {expected_defaults_value}"
            )


async def make_assertion(
    url,
    request_data: RequestData,
    method_name: str,
    kwargs_need_default: List[str],
    return_value,
    manually_passed_value: Any = DEFAULT_NONE,
    expected_defaults_value: Any = DEFAULT_NONE,
    *args,
    **kwargs,
):
    data = request_data.parameters

    no_value_expected = (manually_passed_value is None) or (
        manually_passed_value is DEFAULT_NONE and expected_defaults_value is None
    )
    manual_value_expected = (manually_passed_value is not DEFAULT_NONE) and not no_value_expected
    default_value_expected = (not manual_value_expected) and (not no_value_expected)

    # Check reply_parameters - needs special handling b/c we merge this with the default
    # value for `allow_sending_without_reply`
    reply_parameters = data.pop("reply_parameters", None)
    if reply_parameters:
        for param in ["allow_sending_without_reply", "quote_parse_mode"]:
            if no_value_expected and param in reply_parameters:
                pytest.fail(f"Got value for reply_parameters.{param}, expected it to be absent")
            param_value = reply_parameters.get(param)
            if manual_value_expected and param_value != manually_passed_value:
                pytest.fail(
                    f"Got value {param_value} for reply_parameters.{param} "
                    f"instead of {manually_passed_value}"
                )
            elif default_value_expected and param_value != expected_defaults_value:
                pytest.fail(
                    f"Got value {param_value} for reply_parameters.{param} "
                    f"instead of {expected_defaults_value}"
                )

    # Check link_preview_options - needs special handling b/c we merge this with the default
    # values specified in `Defaults.link_preview_options`
    make_assertion_for_link_preview_options(
        expected_defaults_value,
        data.get("link_preview_options", None),
        manual_value_expected,
        manually_passed_value,
    )

    # Check regular arguments that need defaults
    for arg in kwargs_need_default:
        if arg == "link_preview_options":
            # already handled above
            continue

        # 'None' should not be passed along to Telegram
        if no_value_expected and arg in data:
            pytest.fail(f"Got value {data[arg]} for argument {arg}, expected it to be absent")

        value = data.get(arg, "`not passed at all`")
        if manual_value_expected and value != manually_passed_value:
            pytest.fail(f"Got value {value} for argument {arg} instead of {manually_passed_value}")
        elif default_value_expected and value != expected_defaults_value:
            pytest.fail(
                f"Got value {value} for argument {arg} instead of {expected_defaults_value}"
            )

    # Check InputMedia (parse_mode can have a default)
    def check_input_media(m: Dict):
        parse_mode = m.get("parse_mode")
        if no_value_expected and parse_mode is not None:
            pytest.fail("InputMedia has non-None parse_mode, expected it to be absent")
        elif default_value_expected and parse_mode != expected_defaults_value:
            pytest.fail(
                f"Got value {parse_mode} for InputMedia.parse_mode instead "
                f"of {expected_defaults_value}"
            )
        elif manual_value_expected and parse_mode != manually_passed_value:
            pytest.fail(
                f"Got value {parse_mode} for InputMedia.parse_mode instead "
                f"of {manually_passed_value}"
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
        if no_value_expected and "parse_mode" in result:
            pytest.fail("ILQR has a parse mode, expected it to be absent")
        # Here we explicitly use that we only pass ILQRPhoto and ILQRArticle for testing
        elif "photo" in result:
            parse_mode = result.get("parse_mode")
            if manually_passed_value and parse_mode != manually_passed_value:
                pytest.fail(
                    f"Got value {parse_mode} for ILQR.parse_mode instead of "
                    f"{manually_passed_value}"
                )
            elif default_value_expected and parse_mode != expected_defaults_value:
                pytest.fail(
                    f"Got value {parse_mode} for ILQR.parse_mode instead of "
                    f"{expected_defaults_value}"
                )

        # Here we explicitly use that we only pass InputTextMessageContent for testing
        # which has both parse_mode and link_preview_options
        imc = result.get("input_message_content")
        if not imc:
            continue
        if no_value_expected and "parse_mode" in imc:
            pytest.fail("ILQR.i_m_c has a parse_mode, expected it to be absent")
        parse_mode = imc.get("parse_mode")
        if manual_value_expected and parse_mode != manually_passed_value:
            pytest.fail(
                f"Got value {imc.parse_mode} for ILQR.i_m_c.parse_mode "
                f"instead of {manual_value_expected}"
            )
        elif default_value_expected and parse_mode != expected_defaults_value:
            pytest.fail(
                f"Got value {imc.parse_mode} for ILQR.i_m_c.parse_mode "
                f"instead of {expected_defaults_value}"
            )

        make_assertion_for_link_preview_options(
            expected_defaults_value,
            imc.get("link_preview_options", None),
            manual_value_expected,
            manually_passed_value,
        )

    # Check datetime conversion
    until_date = data.pop("until_date", None)
    if until_date:
        if manual_value_expected and until_date != 946681200:
            pytest.fail("Non-naive until_date should have been interpreted as Europe/Berlin.")
        if not any((manually_passed_value, expected_defaults_value)) and until_date != 946684800:
            pytest.fail("Naive until_date should have been interpreted as UTC")
        if default_value_expected and until_date != 946702800:
            pytest.fail("Naive until_date should have been interpreted as America/New_York")

    if method_name in ["get_file", "get_small_file", "get_big_file"]:
        # This is here mainly for PassportFile.get_file, which calls .set_credentials on the
        # return value
        out = File(file_id="result", file_unique_id="result")
        return out.to_dict()
    # Otherwise return None by default, as TGObject.de_json/list(None) in [None, []]
    # That way we can check what gets passed to Request.post without having to actually
    # make a request
    # Some methods expect specific output, so we allow to customize that
    if isinstance(return_value, TelegramObject):
        return return_value.to_dict()
    return return_value


async def check_defaults_handling(
    method: Callable,
    bot: Bot,
    return_value=None,
    no_default_kwargs: Collection[str] = frozenset(),
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
        no_default_kwargs: Optional. A collection of keyword arguments that should not have default
            values. Defaults to an empty frozenset.

    """
    raw_bot = not isinstance(bot, ExtBot)
    get_updates = method.__name__.lower().replace("_", "") == "getupdates"

    shortcut_signature = inspect.signature(method)
    kwargs_need_default = {
        kwarg
        for kwarg, value in shortcut_signature.parameters.items()
        if isinstance(value.default, DefaultValue)
        and not kwarg.endswith("_timeout")
        and kwarg not in no_default_kwargs
    }
    # We tested this for a long time, but Bot API 7.0 deprecated it in favor of
    # reply_parameters. In the transition phase, both exist in a mutually exclusive
    # way. Testing both cases would require a lot of additional code, so we for now are content
    # with the explicit tests that we have inplace for allow_sending_without_reply
    kwargs_need_default.discard("allow_sending_without_reply")

    if method.__name__.endswith("_media_group"):
        # the parse_mode is applied to the first media item, and we test this elsewhere
        kwargs_need_default.remove("parse_mode")

    defaults_no_custom_defaults = Defaults()
    kwargs = {kwarg: "custom_default" for kwarg in inspect.signature(Defaults).parameters}
    kwargs["tzinfo"] = pytz.timezone("America/New_York")
    kwargs.pop("disable_web_page_preview")  # mutually exclusive with link_preview_options
    kwargs.pop("quote")  # mutually exclusive with do_quote
    kwargs["link_preview_options"] = LinkPreviewOptions(
        url="custom_default", show_above_text="custom_default"
    )
    defaults_custom_defaults = Defaults(**kwargs)

    expected_return_values = [None, ()] if return_value is None else [return_value]
    if method.__name__ in ["get_file", "get_small_file", "get_big_file"]:
        expected_return_values = [File(file_id="result", file_unique_id="result")]

    request = bot._request[0] if get_updates else bot.request
    orig_post = request.post
    try:
        if raw_bot:
            combinations = [(None, None)]
        else:
            combinations = [
                (None, defaults_no_custom_defaults),
                ("custom_default", defaults_custom_defaults),
            ]

        for expected_defaults_value, defaults in combinations:
            if not raw_bot:
                bot._defaults = defaults

            # 1: test that we get the correct default value, if we don't specify anything
            kwargs = build_kwargs(shortcut_signature, kwargs_need_default)
            assertion_callback = functools.partial(
                make_assertion,
                kwargs_need_default=kwargs_need_default,
                method_name=method.__name__,
                return_value=return_value,
                expected_defaults_value=expected_defaults_value,
            )
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values

            # 2: test that we get the manually passed non-None value
            kwargs = build_kwargs(
                shortcut_signature, kwargs_need_default, manually_passed_value="non-None-value"
            )
            assertion_callback = functools.partial(
                make_assertion,
                manually_passed_value="non-None-value",
                kwargs_need_default=kwargs_need_default,
                method_name=method.__name__,
                return_value=return_value,
                expected_defaults_value=expected_defaults_value,
            )
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values

            # 3: test that we get the manually passed None value
            kwargs = build_kwargs(
                shortcut_signature, kwargs_need_default, manually_passed_value=None
            )
            assertion_callback = functools.partial(
                make_assertion,
                manually_passed_value=None,
                kwargs_need_default=kwargs_need_default,
                method_name=method.__name__,
                return_value=return_value,
                expected_defaults_value=expected_defaults_value,
            )
            request.post = assertion_callback
            assert await method(**kwargs) in expected_return_values
    except Exception as exc:
        raise exc
    finally:
        request.post = orig_post
        if not raw_bot:
            bot._defaults = None

    return True
