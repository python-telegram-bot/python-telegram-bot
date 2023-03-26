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
import os
from pathlib import Path

import pytest

from telegram import Bot, ChatPhoto, Voice
from telegram.error import TelegramError
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.files import data_file
from tests.auxil.networking import expect_bad_request
from tests.auxil.slots import mro_slots


@pytest.fixture()
def chatphoto_file():
    with data_file("telegram.jpg").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def chat_photo(bot, super_group_id):
    async def func():
        return (await bot.get_chat(super_group_id, read_timeout=50)).photo

    return await expect_bad_request(
        func, "Type of file mismatch", "Telegram did not accept the file."
    )


class TestChatPhotoBase:
    chatphoto_small_file_id = "smallCgADAQADngIAAuyVeEez0xRovKi9VAI"
    chatphoto_big_file_id = "bigCgADAQADngIAAuyVeEez0xRovKi9VAI"
    chatphoto_small_file_unique_id = "smalladc3145fd2e84d95b64d68eaa22aa33e"
    chatphoto_big_file_unique_id = "bigadc3145fd2e84d95b64d68eaa22aa33e"
    chatphoto_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.jpg"


class TestChatPhotoWithoutRequest(TestChatPhotoBase):
    def test_slot_behaviour(self, chat_photo):
        for attr in chat_photo.__slots__:
            assert getattr(chat_photo, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(chat_photo)) == len(set(mro_slots(chat_photo))), "duplicate slot"

    def test_de_json(self, bot, chat_photo):
        json_dict = {
            "small_file_id": self.chatphoto_small_file_id,
            "big_file_id": self.chatphoto_big_file_id,
            "small_file_unique_id": self.chatphoto_small_file_unique_id,
            "big_file_unique_id": self.chatphoto_big_file_unique_id,
        }
        chat_photo = ChatPhoto.de_json(json_dict, bot)
        assert chat_photo.api_kwargs == {}
        assert chat_photo.small_file_id == self.chatphoto_small_file_id
        assert chat_photo.big_file_id == self.chatphoto_big_file_id
        assert chat_photo.small_file_unique_id == self.chatphoto_small_file_unique_id
        assert chat_photo.big_file_unique_id == self.chatphoto_big_file_unique_id

    async def test_to_dict(self, chat_photo):
        chat_photo_dict = chat_photo.to_dict()

        assert isinstance(chat_photo_dict, dict)
        assert chat_photo_dict["small_file_id"] == chat_photo.small_file_id
        assert chat_photo_dict["big_file_id"] == chat_photo.big_file_id
        assert chat_photo_dict["small_file_unique_id"] == chat_photo.small_file_unique_id
        assert chat_photo_dict["big_file_unique_id"] == chat_photo.big_file_unique_id

    def test_equality(self):
        a = ChatPhoto(
            self.chatphoto_small_file_id,
            self.chatphoto_big_file_id,
            self.chatphoto_small_file_unique_id,
            self.chatphoto_big_file_unique_id,
        )
        b = ChatPhoto(
            self.chatphoto_small_file_id,
            self.chatphoto_big_file_id,
            self.chatphoto_small_file_unique_id,
            self.chatphoto_big_file_unique_id,
        )
        c = ChatPhoto(
            "", "", self.chatphoto_small_file_unique_id, self.chatphoto_big_file_unique_id
        )
        d = ChatPhoto("", "", 0, 0)
        e = Voice(self.chatphoto_small_file_id, self.chatphoto_small_file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_send_with_chat_photo(self, monkeypatch, bot, super_group_id, chat_photo):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.parameters["photo"] == chat_photo.to_dict()

        monkeypatch.setattr(bot.request, "post", make_assertion)
        message = await bot.set_chat_photo(photo=chat_photo, chat_id=super_group_id)
        assert message

    async def test_get_small_file_instance_method(self, monkeypatch, chat_photo):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == chat_photo.small_file_id

        assert check_shortcut_signature(ChatPhoto.get_small_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(
            chat_photo.get_small_file, chat_photo.get_bot(), "get_file"
        )
        assert await check_defaults_handling(chat_photo.get_small_file, chat_photo.get_bot())

        monkeypatch.setattr(chat_photo.get_bot(), "get_file", make_assertion)
        assert await chat_photo.get_small_file()

    async def test_get_big_file_instance_method(self, monkeypatch, chat_photo):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == chat_photo.big_file_id

        assert check_shortcut_signature(ChatPhoto.get_big_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(chat_photo.get_big_file, chat_photo.get_bot(), "get_file")
        assert await check_defaults_handling(chat_photo.get_big_file, chat_photo.get_bot())

        monkeypatch.setattr(chat_photo.get_bot(), "get_file", make_assertion)
        assert await chat_photo.get_big_file()


class TestChatPhotoWithRequest:
    async def test_get_and_download(self, bot, chat_photo):
        jpg_file = Path("telegram.jpg")
        if jpg_file.is_file():
            jpg_file.unlink()

        tasks = {bot.get_file(chat_photo.small_file_id), bot.get_file(chat_photo.big_file_id)}
        asserts = []

        for task in asyncio.as_completed(tasks):
            file = await task
            if file.file_unique_id == chat_photo.small_file_unique_id:
                asserts.append("small")
            elif file.file_unique_id == chat_photo.big_file_unique_id:
                asserts.append("big")
            assert file.file_path.startswith("https://")

            await file.download_to_drive(jpg_file)
            assert jpg_file.is_file()

        assert "small" in asserts
        assert "big" in asserts

    async def test_send_all_args(self, bot, super_group_id, chatphoto_file):
        async def func():
            assert await bot.set_chat_photo(super_group_id, chatphoto_file)

        await expect_bad_request(
            func, "Type of file mismatch", "Telegram did not accept the file."
        )

    async def test_error_send_empty_file(self, bot, super_group_id):
        with Path(os.devnull).open("rb") as chatphoto_file, pytest.raises(TelegramError):
            await bot.set_chat_photo(chat_id=super_group_id, photo=chatphoto_file)

    async def test_error_send_empty_file_id(self, bot, super_group_id):
        with pytest.raises(TelegramError):
            await bot.set_chat_photo(chat_id=super_group_id, photo="")

    async def test_error_send_without_required_args(self, bot, super_group_id):
        with pytest.raises(TypeError):
            await bot.set_chat_photo(chat_id=super_group_id)
