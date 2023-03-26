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
import asyncio
import json

from telegram import constants
from telegram._utils.enum import IntEnum, StringEnum
from telegram.error import BadRequest
from tests.auxil.files import data_file


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
                and key != "sys"
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
