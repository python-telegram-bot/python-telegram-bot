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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import asyncio
import inspect
import json
import re

import pytest

from telegram import Message, constants
from telegram._utils.enum import IntEnum, StringEnum
from telegram.error import BadRequest
from tests.auxil.build_messages import make_message
from tests.auxil.files import data_file
from tests.auxil.string_manipulation import to_snake_case


class StrEnumTest(StringEnum):
    FOO = "foo"
    BAR = "bar"


class IntEnumTest(IntEnum):
    FOO = 1
    BAR = 2


class TestConstantsWithoutRequest:
    """Also test _utils.enum.StringEnum on the fly because tg.constants is currently the only
    place where that class is used."""

    def test__all__(self):
        expected = {
            key
            for key, member in constants.__dict__.items()
            if (
                not key.startswith("_")
                # exclude imported stuff
                and getattr(member, "__module__", "telegram.constants") == "telegram.constants"
                and key not in ("sys", "datetime")
            )
        }
        actual = set(constants.__all__)
        assert (
            actual == expected
        ), f"Members {expected - actual} were not listed in constants.__all__"

    def test_message_attachment_type(self):
        assert all(
            getattr(constants.MessageType, x.name, False) for x in constants.MessageAttachmentType
        ), "All MessageAttachmentType members should be in MessageType"

    def test_to_json(self):
        assert json.dumps(StrEnumTest.FOO) == json.dumps("foo")
        assert json.dumps(IntEnumTest.FOO) == json.dumps(1)

    def test_string_representation(self):
        # test __repr__
        assert repr(StrEnumTest.FOO) == "<StrEnumTest.FOO>"

        # test __format__
        assert f"{StrEnumTest.FOO} this {StrEnumTest.BAR}" == "foo this bar"
        assert f"{StrEnumTest.FOO:*^10}" == "***foo****"

        # test __str__
        assert str(StrEnumTest.FOO) == "foo"

    def test_int_representation(self):
        # test __repr__
        assert repr(IntEnumTest.FOO) == "<IntEnumTest.FOO>"
        # test __format__
        assert f"{IntEnumTest.FOO}/0 is undefined!" == "1/0 is undefined!"
        assert f"{IntEnumTest.FOO:*^10}" == "****1*****"
        # test __str__
        assert str(IntEnumTest.FOO) == "1"

    def test_string_inheritance(self):
        assert isinstance(StrEnumTest.FOO, str)
        assert StrEnumTest.FOO + StrEnumTest.BAR == "foobar"
        assert StrEnumTest.FOO.replace("o", "a") == "faa"

        assert StrEnumTest.FOO == StrEnumTest.FOO
        assert StrEnumTest.FOO == "foo"
        assert StrEnumTest.FOO != StrEnumTest.BAR
        assert StrEnumTest.FOO != "bar"
        assert object() != StrEnumTest.FOO

        assert hash(StrEnumTest.FOO) == hash("foo")

    def test_int_inheritance(self):
        assert isinstance(IntEnumTest.FOO, int)
        assert IntEnumTest.FOO + IntEnumTest.BAR == 3

        assert IntEnumTest.FOO == IntEnumTest.FOO
        assert IntEnumTest.FOO == 1
        assert IntEnumTest.FOO != IntEnumTest.BAR
        assert IntEnumTest.FOO != 2
        assert object() != IntEnumTest.FOO

        assert hash(IntEnumTest.FOO) == hash(1)

    def test_bot_api_version_and_info(self):
        assert str(constants.BOT_API_VERSION_INFO) == constants.BOT_API_VERSION
        assert (
            tuple(int(x) for x in constants.BOT_API_VERSION.split("."))
            == constants.BOT_API_VERSION_INFO
        )

    def test_bot_api_version_info(self):
        vi = constants.BOT_API_VERSION_INFO
        assert isinstance(vi, tuple)
        assert repr(vi) == f"BotAPIVersion(major={vi[0]}, minor={vi[1]})"
        assert vi == (vi[0], vi[1])
        assert not (vi < (vi[0], vi[1]))
        assert vi < (vi[0], vi[1] + 1)
        assert vi < (vi[0] + 1, vi[1])
        assert vi < (vi[0] + 1, vi[1] + 1)
        assert vi[0] == vi.major
        assert vi[1] == vi.minor

    @staticmethod
    def is_type_attribute(name: str) -> bool:
        # Return False if the attribute doesn't generate a message type, i.e. only message
        # metadata. Manually excluding a lot of attributes here is a bit of work, but it makes
        # sure that we don't miss any new message types in the future.
        patters = {
            "(text|caption)_(markdown|html)",
            "caption_(entities|html|markdown)",
            "(edit_)?date",
            "forward_",
            "has_",
        }

        if any(re.match(pattern, name) for pattern in patters):
            return False
        if name in {
            "author_signature",
            "api_kwargs",
            "caption",
            "chat",
            "chat_id",
            "effective_attachment",
            "entities",
            "from_user",
            "id",
            "is_automatic_forward",
            "is_topic_message",
            "link",
            "link_preview_options",
            "media_group_id",
            "message_id",
            "message_thread_id",
            "migrate_from_chat_id",
            "reply_markup",
            "reply_to_message",
            "sender_chat",
            "is_accessible",
            "quote",
            "external_reply",
            # attribute is deprecated, no need to add it to MessageType
            "user_shared",
            "via_bot",
        }:
            return False

        return True

    @pytest.mark.parametrize(
        "attribute",
        [
            name
            for name, _ in inspect.getmembers(
                make_message("test"), lambda x: not inspect.isroutine(x)
            )
        ],
    )
    def test_message_type_completeness(self, attribute):
        if attribute.startswith("_") or not self.is_type_attribute(attribute):
            return

        assert hasattr(constants.MessageType, attribute.upper()), (
            f"Missing MessageType.{attribute}. Please also check if this should be present in "
            f"MessageAttachmentType."
        )

    @pytest.mark.parametrize("member", constants.MessageType)
    def test_message_type_completeness_reverse(self, member):
        assert self.is_type_attribute(
            member.value
        ), f"Additional member {member} in MessageType that should not be a message type"

    @pytest.mark.parametrize("member", constants.MessageAttachmentType)
    def test_message_attachment_type_completeness(self, member):
        try:
            constants.MessageType(member)
        except ValueError:
            pytest.fail(f"Missing MessageType for {member}")

    def test_message_attachment_type_completeness_reverse(self):
        # Getting the type hints of a property is a bit tricky, so we instead parse the docstring
        # for now
        for match in re.finditer(r"`telegram.(\w+)`", Message.effective_attachment.__doc__):
            name = to_snake_case(match.group(1))
            if name == "photo_size":
                name = "photo"
            try:
                constants.MessageAttachmentType(name)
            except ValueError:
                pytest.fail(f"Missing MessageAttachmentType for {match.group(1)}")


class TestConstantsWithRequest:
    async def test_max_message_length(self, bot, chat_id):
        good_text = "a" * constants.MessageLimit.MAX_TEXT_LENGTH
        bad_text = good_text + "Z"
        tasks = asyncio.gather(
            bot.send_message(chat_id, text=good_text),
            bot.send_message(chat_id, text=bad_text),
            return_exceptions=True,
        )
        good_msg, bad_msg = await tasks
        assert good_msg.text == good_text
        assert isinstance(bad_msg, BadRequest)
        assert "Message is too long" in str(bad_msg)

    async def test_max_caption_length(self, bot, chat_id):
        good_caption = "a" * constants.MessageLimit.CAPTION_LENGTH
        bad_caption = good_caption + "Z"
        tasks = asyncio.gather(
            bot.send_photo(chat_id, data_file("telegram.png").read_bytes(), good_caption),
            bot.send_photo(chat_id, data_file("telegram.png").read_bytes(), bad_caption),
            return_exceptions=True,
        )
        good_msg, bad_msg = await tasks
        assert good_msg.caption == good_caption
        assert isinstance(bad_msg, BadRequest)
        assert "Message caption is too long" in str(bad_msg)
