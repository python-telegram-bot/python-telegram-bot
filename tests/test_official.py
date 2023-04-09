#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
import inspect
import os
import re
from typing import Dict, List, Set

import httpx
import pytest
from bs4 import BeautifulSoup

import telegram
from telegram._utils.defaultvalue import DefaultValue
from tests.auxil.envvars import env_var_2_bool

IGNORED_OBJECTS = ("ResponseParameters", "CallbackGame")
GLOBALLY_IGNORED_PARAMETERS = {
    "self",
    "read_timeout",
    "write_timeout",
    "connect_timeout",
    "pool_timeout",
    "bot",
    "api_kwargs",
}

# Arguments *added* to the official API
PTB_EXTRA_PARAMS = {
    "send_contact": {"contact"},
    "send_location": {"location"},
    "edit_message_live_location": {"location"},
    "send_venue": {"venue"},
    "answer_inline_query": {"current_offset"},
    "send_media_group": {"caption", "parse_mode", "caption_entities"},
    "send_(animation|audio|document|photo|video(_note)?|voice)": {"filename"},
    "InlineQueryResult": {"id", "type"},  # attributes common to all subclasses
    "ChatMember": {"user", "status"},  # attributes common to all subclasses
    "BotCommandScope": {"type"},  # attributes common to all subclasses
    "MenuButton": {"type"},  # attributes common to all subclasses
    "PassportFile": {"credentials"},
    "EncryptedPassportElement": {"credentials"},
    "PassportElementError": {"source", "type", "message"},
    "InputMedia": {"caption", "caption_entities", "media", "media_type", "parse_mode"},
    "InputMedia(Animation|Audio|Document|Photo|Video|VideoNote|Voice)": {"filename"},
    "InputFile": {"attach", "filename", "obj"},
}


def _get_params_base(object_name: str, search_dict: Dict[str, Set[str]]) -> Set[str]:
    """Helper function for the *_params functions below.
    Given an object name and a search dict, goes through the keys of the search dict and checks if
    the object name matches any of the regexes (keys). The union of all the sets (values) of the
    matching regexes is returned. `object_name` may be a CamelCase or snake_case name.
    """
    out = set()
    for regex, params in search_dict.items():
        if re.fullmatch(regex, object_name):
            out.update(params)
        # also check the snake_case version
        snake_case_name = re.sub(r"(?<!^)(?=[A-Z])", "_", object_name).lower()
        if re.fullmatch(regex, snake_case_name):
            out.update(params)
    return out


def ptb_extra_params(object_name) -> Set[str]:
    return _get_params_base(object_name, PTB_EXTRA_PARAMS)


# Arguments *removed* from the official API
PTB_IGNORED_PARAMS = {
    r"InlineQueryResult\w+": {"type"},
    r"ChatMember\w+": {"status"},
    r"PassportElementError\w+": {"source"},
    "ForceReply": {"force_reply"},
    "ReplyKeyboardRemove": {"remove_keyboard"},
    r"BotCommandScope\w+": {"type"},
    r"MenuButton\w+": {"type"},
    r"InputMedia\w+": {"type"},
}


def ptb_ignored_params(object_name) -> Set[str]:
    return _get_params_base(object_name, PTB_IGNORED_PARAMS)


IGNORED_PARAM_REQUIREMENTS = {
    # Ignore these since there's convenience params in them (eg. Venue)
    # <----
    "send_location": {"latitude", "longitude"},
    "edit_message_live_location": {"latitude", "longitude"},
    "send_venue": {"latitude", "longitude", "title", "address"},
    "send_contact": {"phone_number", "first_name"},
    # ---->
    # These are optional for now for backwards compatibility
    # <----
    "InlineQueryResult(Article|Photo|Gif|Mpeg4Gif|Video|Document|Location|Venue)": {
        "thumbnail_url",
    },
    "InlineQueryResultVideo": {"title"},
    # ---->
}


def ignored_param_requirements(object_name) -> Set[str]:
    return _get_params_base(object_name, IGNORED_PARAM_REQUIREMENTS)


# Arguments that are optional arguments for now for backwards compatibility
BACKWARDS_COMPAT_KWARGS = {
    "create_new_sticker_set": {
        "stickers",
        "sticker_format",
        "emojis",
        "png_sticker",
        "tgs_sticker",
        "mask_position",
        "webm_sticker",
    },
    "add_sticker_to_set": {
        "sticker",
        "tgs_sticker",
        "png_sticker",
        "webm_sticker",
        "mask_position",
        "emojis",
    },
    "upload_sticker_file": {"sticker", "sticker_format", "png_sticker"},
    "send_(animation|audio|document|video(_note)?)": {"thumb"},
    "(Animation|Audio|Document|Photo|Sticker(Set)?|Video|VideoNote|Voice)": {"thumb"},
    "InputMedia(Animation|Audio|Document|Video)": {"thumb"},
    "Chat(MemberRestricted|Permissions)": {"can_send_media_messages"},
    "InlineQueryResult(Article|Contact|Document|Location|Venue)": {
        "thumb_height",
        "thumb_width",
    },
    "InlineQueryResult(Article|Photo|Gif|Mpeg4Gif|Video|Contact|Document|Location|Venue)": {
        "thumb_url",
    },
    "InlineQueryResult(Game|Gif|Mpeg4Gif)": {"thumb_mime_type"},
}


def backwards_compat_kwargs(object_name: str) -> Set[str]:
    return _get_params_base(object_name, BACKWARDS_COMPAT_KWARGS)


IGNORED_PARAM_REQUIREMENTS.update(BACKWARDS_COMPAT_KWARGS)


def find_next_sibling_until(tag, name, until):
    for sibling in tag.next_siblings:
        if sibling is until:
            return None
        if sibling.name == name:
            return sibling
    return None


def parse_table(h4) -> List[List[str]]:
    """Parses the Telegram doc table and has an output of a 2D list."""
    table = find_next_sibling_until(h4, "table", h4.find_next_sibling("h4"))
    if not table:
        return []
    t = []
    for tr in table.find_all("tr")[1:]:
        t.append([td.text for td in tr.find_all("td")])
    return t


def check_method(h4):
    name = h4.text  # name of the method in telegram's docs.
    method = getattr(telegram.Bot, name)  # Retrieve our lib method
    table = parse_table(h4)

    # Check arguments based on source
    sig = inspect.signature(method, follow_wrapped=True)
    checked = []
    for tg_parameter in table:  # Iterates through each row in the table
        # Check if parameter is present in our method
        param = sig.parameters.get(
            tg_parameter[0]  # parameter[0] is first element (the param name)
        )
        if param is None:
            raise AssertionError(f"Parameter {tg_parameter[0]} not found in {method.__name__}")

        # TODO: Check type via docstring
        # Now check if the parameter is required or not
        if not check_required_param(tg_parameter, param, method.__name__):
            raise AssertionError(
                f"Param {param.name!r} of method {method.__name__!r} requirement mismatch!"
            )

        # Now we will check that we don't pass default values if the parameter is not required.
        if param.default is not inspect.Parameter.empty:  # If there is a default argument...
            default_arg_none = check_defaults_type(param)  # check if it's None
            if not default_arg_none:
                raise AssertionError(f"Param {param.name!r} of {method.__name__!r} should be None")
        checked.append(tg_parameter[0])

    expected_additional_args = GLOBALLY_IGNORED_PARAMETERS.copy()
    expected_additional_args |= ptb_extra_params(name)
    expected_additional_args |= backwards_compat_kwargs(name)

    unexpected_args = (sig.parameters.keys() ^ checked) - expected_additional_args
    if unexpected_args != set():
        raise AssertionError(
            f"In {method.__qualname__}, unexpected args were found: {unexpected_args}."
        )

    kw_or_positional_args = [
        p.name for p in sig.parameters.values() if p.kind != inspect.Parameter.KEYWORD_ONLY
    ]
    non_kw_only_args = set(kw_or_positional_args).difference(checked).difference(["self"])
    non_kw_only_args -= backwards_compat_kwargs(name)
    if non_kw_only_args != set():
        raise AssertionError(
            f"In {method.__qualname__}, extra args should be keyword only "
            f"(compared to {name} in API)"
        )


def check_object(h4):
    name = h4.text
    obj = getattr(telegram, name)
    table = parse_table(h4)

    # Check arguments based on source. Makes sure to only check __init__'s signature & nothing else
    sig = inspect.signature(obj.__init__, follow_wrapped=True)

    checked = set()
    fields_removed_by_ptb = ptb_ignored_params(name)
    for tg_parameter in table:
        field: str = tg_parameter[0]  # From telegram docs

        if field in fields_removed_by_ptb:
            continue

        if field == "from":
            field = "from_user"

        param = sig.parameters.get(field)
        if param is None:
            raise AssertionError(f"Attribute {field} not found in {obj.__name__}")
        # TODO: Check type via docstring
        if not check_required_param(tg_parameter, param, obj.__name__):
            raise AssertionError(f"{obj.__name__!r} parameter {param.name!r} requirement mismatch")

        if param.default is not inspect.Parameter.empty:  # If there is a default argument...
            default_arg_none = check_defaults_type(param)  # check if its None
            if not default_arg_none:
                raise AssertionError(f"Param {param.name!r} of {obj.__name__!r} should be `None`")

        checked.add(field)

    expected_additional_args = GLOBALLY_IGNORED_PARAMETERS.copy()
    expected_additional_args |= ptb_extra_params(name)
    expected_additional_args |= backwards_compat_kwargs(name)

    unexpected_args = (sig.parameters.keys() ^ checked) - expected_additional_args
    if unexpected_args != set():
        raise AssertionError(f"In {name}, unexpected args were found: {unexpected_args}.")


def is_parameter_required_by_tg(field: str) -> bool:
    if field in {"Required", "Yes"}:
        return True
    return field.split(".", 1)[0] != "Optional"  # splits the sentence and extracts first word


def check_required_param(
    param_desc: List[str], param: inspect.Parameter, method_or_obj_name: str
) -> bool:
    """Checks if the method/class parameter is a required/optional param as per Telegram docs.

    Returns:
        :obj:`bool`: The boolean returned represents whether our parameter's requirement (optional
        or required) is the same as Telegram's or not.
    """
    is_ours_required = param.default is inspect.Parameter.empty
    telegram_requires = is_parameter_required_by_tg(param_desc[2])
    # Handle cases where we provide convenience intentionally-
    if param.name in ignored_param_requirements(method_or_obj_name):
        return True
    return telegram_requires is is_ours_required


def check_defaults_type(ptb_param: inspect.Parameter) -> bool:
    return DefaultValue.get_value(ptb_param.default) is None


to_run = env_var_2_bool(os.getenv("TEST_OFFICIAL"))
argvalues = []
names = []

if to_run:
    argvalues = []
    names = []
    request = httpx.get("https://core.telegram.org/bots/api")
    soup = BeautifulSoup(request.text, "html.parser")

    for thing in soup.select("h4 > a.anchor"):
        # Methods and types don't have spaces in them, luckily all other sections of the docs do
        # TODO: don't depend on that
        if "-" not in thing["name"]:
            h4 = thing.parent

            # Is it a method
            if h4.text[0].lower() == h4.text[0]:
                argvalues.append((check_method, h4))
                names.append(h4.text)
            elif h4.text not in IGNORED_OBJECTS:  # Or a type/object
                argvalues.append((check_object, h4))
                names.append(h4.text)


@pytest.mark.skipif(not to_run, reason="test_official is not enabled")
@pytest.mark.parametrize(("method", "data"), argvalues=argvalues, ids=names)
def test_official(method, data):
    method(data)
