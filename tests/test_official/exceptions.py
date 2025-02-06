#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains exceptions to our API compared to the official API."""
import datetime as dtm

from telegram import Animation, Audio, Document, Gift, PhotoSize, Sticker, Video, VideoNote, Voice
from tests.test_official.helpers import _get_params_base

IGNORED_OBJECTS = ("ResponseParameters",)
GLOBALLY_IGNORED_PARAMETERS = {
    "self",
    "read_timeout",
    "write_timeout",
    "connect_timeout",
    "pool_timeout",
    "bot",
    "api_kwargs",
}


class ParamTypeCheckingExceptions:
    # Types for certain parameters accepted by PTB but not in the official API
    # structure: method/class_name/regex: {param_name/regex: type}
    ADDITIONAL_TYPES = {
        r"send_\w*": {
            "photo$": PhotoSize,
            "video$": Video,
            "video_note": VideoNote,
            "audio": Audio,
            "document": Document,
            "animation": Animation,
            "voice": Voice,
            "sticker": Sticker,
            "gift_id": Gift,
        },
        "(delete|set)_sticker.*": {
            "sticker$": Sticker,
        },
        "replace_sticker_in_set": {
            "old_sticker$": Sticker,
        },
        # The underscore will match any method
        r"\w+_[\w_]+": {
            "duration": dtm.timedelta,
            r"\w+_period": dtm.timedelta,
            "cache_time": dtm.timedelta,
        },
    }

    # TODO: Look into merging this with COMPLEX_TYPES
    # Exceptions to the "Array of" types, where we accept more types than the official API
    # key: (parameter name, is_class), value: type which must be present in the annotation
    ARRAY_OF_EXCEPTIONS = {
        ("results", False): "InlineQueryResult",  # + Callable
        ("commands", False): "BotCommand",  # + tuple[str, str]
        ("keyboard", True): "KeyboardButton",  # + sequence[sequence[str]]
        ("reaction", False): "ReactionType",  # + str
        ("options", False): "InputPollOption",  # + str
        # TODO: Deprecated and will be corrected (and removed) in next major PTB version:
        ("file_hashes", True): "list[str]",
    }

    # Special cases for other parameters that accept more types than the official API, and are
    # too complex to compare/predict with official API
    # structure: class/method_name: {param_name: reduced form of annotation}
    COMPLEX_TYPES = (
        {  # (param_name, is_class (i.e appears in a class?)): reduced form of annotation
            "send_poll": {"correct_option_id": int},  # actual: Literal
            "get_file": {
                "file_id": str,  # actual: Union[str, objs_with_file_id_attr]
            },
            r"\w+invite_link": {
                "invite_link": str,  # actual: Union[str, ChatInviteLink]
            },
            "send_invoice|create_invoice_link": {
                "provider_data": str,  # actual: Union[str, obj]
            },
            "InlineKeyboardButton": {
                "callback_data": str,  # actual: Union[str, obj]
            },
            "Input(Paid)?Media.*": {
                "media": str,  # actual: Union[str, InputMedia*, FileInput]
            },
            "EncryptedPassportElement": {
                "data": str,  # actual: Union[IdDocumentData, PersonalDetails, ResidentialAddress]
            },
        }
    )

    # param names ignored in the param type checking in classes for the `tg.Defaults` case.
    IGNORED_DEFAULTS_PARAM_NAMES = {
        "quote",
        "link_preview_options",
    }

    # These classes' params are all ODVInput, so we ignore them in the defaults type checking.
    IGNORED_DEFAULTS_CLASSES = {"LinkPreviewOptions"}

    # TODO: Remove this in v22 when it becomes a datetime (also remove from arg_type_checker.py)
    DATETIME_EXCEPTIONS = {
        "file_date",
    }


# Arguments *added* to the official API
PTB_EXTRA_PARAMS = {
    "send_contact": {"contact"},
    "send_location": {"location"},
    "(send_message|edit_message_text)": {  # convenience parameters
        "disable_web_page_preview",
    },
    r"(send|copy)_\w+": {  # convenience parameters
        "reply_to_message_id",
        "allow_sending_without_reply",
    },
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
    "InputFile": {"attach", "filename", "obj", "read_file_handle"},
    "MaybeInaccessibleMessage": {"date", "message_id", "chat"},  # attributes common to all subcls
    "ChatBoostSource": {"source"},  # attributes common to all subclasses
    "MessageOrigin": {"type", "date"},  # attributes common to all subclasses
    "ReactionType": {"type"},  # attributes common to all subclasses
    "BackgroundType": {"type"},  # attributes common to all subclasses
    "BackgroundFill": {"type"},  # attributes common to all subclasses
    "InputTextMessageContent": {"disable_web_page_preview"},  # convenience arg, here for bw compat
    "RevenueWithdrawalState": {"type"},  # attributes common to all subclasses
    "TransactionPartner": {"type"},  # attributes common to all subclasses
    "PaidMedia": {"type"},  # attributes common to all subclasses
    "InputPaidMedia": {"type", "media"},  # attributes common to all subclasses
}


def ptb_extra_params(object_name: str) -> set[str]:
    return _get_params_base(object_name, PTB_EXTRA_PARAMS)


# Arguments *removed* from the official API
# Mostly due to the value being fixed anyway
PTB_IGNORED_PARAMS = {
    r"InlineQueryResult\w+": {"type"},
    r"ChatMember\w+": {"status"},
    r"PassportElementError\w+": {"source"},
    "ForceReply": {"force_reply"},
    "ReplyKeyboardRemove": {"remove_keyboard"},
    r"BotCommandScope\w+": {"type"},
    r"MenuButton\w+": {"type"},
    r"InputMedia\w+": {"type"},
    "InaccessibleMessage": {"date"},
    r"MessageOrigin\w+": {"type"},
    r"ChatBoostSource\w+": {"source"},
    r"ReactionType\w+": {"type"},
    r"BackgroundType\w+": {"type"},
    r"BackgroundFill\w+": {"type"},
    r"RevenueWithdrawalState\w+": {"type"},
    r"TransactionPartner\w+": {"type"},
    r"PaidMedia\w+": {"type"},
    r"InputPaidMedia\w+": {"type"},
}


def ptb_ignored_params(object_name: str) -> set[str]:
    return _get_params_base(object_name, PTB_IGNORED_PARAMS)


IGNORED_PARAM_REQUIREMENTS = {
    # Ignore these since there's convenience params in them (eg. Venue)
    # <----
    "send_location": {"latitude", "longitude"},
    "edit_message_live_location": {"latitude", "longitude"},
    "send_venue": {"latitude", "longitude", "title", "address"},
    "send_contact": {"phone_number", "first_name"},
    # ---->
}


def ignored_param_requirements(object_name: str) -> set[str]:
    return _get_params_base(object_name, IGNORED_PARAM_REQUIREMENTS)


# Arguments that are optional arguments for now for backwards compatibility
BACKWARDS_COMPAT_KWARGS: dict[str, set[str]] = {
    "send_invoice|create_invoice_link|InputInvoiceMessageContent": {"provider_token"},
}


def backwards_compat_kwargs(object_name: str) -> set[str]:
    return _get_params_base(object_name, BACKWARDS_COMPAT_KWARGS)


IGNORED_PARAM_REQUIREMENTS.update(BACKWARDS_COMPAT_KWARGS)
