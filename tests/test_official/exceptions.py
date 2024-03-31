#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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


from telegram import Animation, Audio, Document, PhotoSize, Sticker, Video, VideoNote, Voice
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
    ADDITIONAL_TYPES = {
        "photo": PhotoSize,
        "video": Video,
        "video_note": VideoNote,
        "audio": Audio,
        "document": Document,
        "animation": Animation,
        "voice": Voice,
        "sticker": Sticker,
    }

    # Exceptions to the "Array of" types, where we accept more types than the official API
    # key: parameter name, value: type which must be present in the annotation
    ARRAY_OF_EXCEPTIONS = {
        "results": "InlineQueryResult",  # + Callable
        "commands": "BotCommand",  # + tuple[str, str]
        "keyboard": "KeyboardButton",  # + sequence[sequence[str]]
        "reaction": "ReactionType",  # + str
        # TODO: Deprecated and will be corrected (and removed) in next major PTB version:
        "file_hashes": "List[str]",
    }

    # Special cases for other parameters that accept more types than the official API, and are
    # too complex to compare/predict with official API:
    COMPLEX_TYPES = (
        {  # (param_name, is_class (i.e appears in a class?)): reduced form of annotation
            ("correct_option_id", False): int,  # actual: Literal
            ("file_id", False): str,  # actual: Union[str, objs_with_file_id_attr]
            ("invite_link", False): str,  # actual: Union[str, ChatInviteLink]
            ("provider_data", False): str,  # actual: Union[str, obj]
            ("callback_data", True): str,  # actual: Union[str, obj]
            ("media", True): str,  # actual: Union[str, InputMedia*, FileInput]
            (
                "data",
                True,
            ): str,  # actual: Union[IdDocumentData, PersonalDetails, ResidentialAddress]
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
    "InputFile": {"attach", "filename", "obj"},
    "MaybeInaccessibleMessage": {"date", "message_id", "chat"},  # attributes common to all subcls
    "ChatBoostSource": {"source"},  # attributes common to all subclasses
    "MessageOrigin": {"type", "date"},  # attributes common to all subclasses
    "ReactionType": {"type"},  # attributes common to all subclasses
    "InputTextMessageContent": {"disable_web_page_preview"},  # convenience arg, here for bw compat
}


def ptb_extra_params(object_name: str) -> set[str]:
    return _get_params_base(object_name, PTB_EXTRA_PARAMS)


# Arguments *removed* from the official API
# Mostly due to the value being fixed anyway
PTB_IGNORED_PARAMS = {
    r"InlineQueryResult\w+": {"type"},
    # TODO: Remove this in v21.0 (API 7.1) when this can stop being optional
    r"ChatAdministratorRights": {"can_post_stories", "can_edit_stories", "can_delete_stories"},
    r"ChatMemberAdministrator": {"can_post_stories", "can_edit_stories", "can_delete_stories"},
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
    # TODO: Remove this in v21.0 (API 7.1) when this can stop being optional
    r"ChatAdministratorRights": {"can_post_stories", "can_edit_stories", "can_delete_stories"},
    r"ChatMemberAdministrator": {"can_post_stories", "can_edit_stories", "can_delete_stories"},
}


def backwards_compat_kwargs(object_name: str) -> set[str]:
    return _get_params_base(object_name, BACKWARDS_COMPAT_KWARGS)


IGNORED_PARAM_REQUIREMENTS.update(BACKWARDS_COMPAT_KWARGS)
