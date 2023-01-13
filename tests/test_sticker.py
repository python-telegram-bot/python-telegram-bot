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

from telegram import Audio, Bot, File, InputFile, MaskPosition, PhotoSize, Sticker, StickerSet
from telegram.error import BadRequest, TelegramError
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.conftest import data_file


@pytest.fixture(scope="function")
def sticker_file():
    with data_file("telegram.webp").open("rb") as file:
        yield file


@pytest.fixture(scope="module")
async def sticker(bot, chat_id):
    with data_file("telegram.webp").open("rb") as f:
        return (await bot.send_sticker(chat_id, sticker=f, read_timeout=50)).sticker


@pytest.fixture(scope="function")
def animated_sticker_file():
    with data_file("telegram_animated_sticker.tgs").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def animated_sticker(bot, chat_id):
    with data_file("telegram_animated_sticker.tgs").open("rb") as f:
        return (await bot.send_sticker(chat_id, sticker=f, read_timeout=50)).sticker


@pytest.fixture(scope="function")
def video_sticker_file():
    with data_file("telegram_video_sticker.webm").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
def video_sticker(bot, chat_id):
    with data_file("telegram_video_sticker.webm").open("rb") as f:
        return bot.send_sticker(chat_id, sticker=f, timeout=50).sticker


class TestStickerBase:
    # sticker_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.webp'
    # Serving sticker from gh since our server sends wrong content_type
    sticker_file_url = (
        "https://github.com/python-telegram-bot/python-telegram-bot/blob/master"
        "/tests/data/telegram.webp?raw=true"
    )

    emoji = "💪"
    width = 510
    height = 512
    is_animated = False
    is_video = False
    file_size = 39518
    thumb_width = 319
    thumb_height = 320
    thumb_file_size = 21472
    type = Sticker.REGULAR
    custom_emoji_id = "ThisIsSuchACustomEmojiID"

    sticker_file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    sticker_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"

    premium_animation = File("this_is_an_id", "this_is_an_unique_id")


class TestStickerWithoutRequest(TestStickerBase):
    def test_slot_behaviour(self, sticker, mro_slots):
        for attr in sticker.__slots__:
            assert getattr(sticker, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(sticker)) == len(set(mro_slots(sticker))), "duplicate slot"

    def test_creation(self, sticker):
        # Make sure file has been uploaded.
        assert isinstance(sticker, Sticker)
        assert isinstance(sticker.file_id, str)
        assert isinstance(sticker.file_unique_id, str)
        assert sticker.file_id != ""
        assert sticker.file_unique_id != ""
        assert isinstance(sticker.thumb, PhotoSize)
        assert isinstance(sticker.thumb.file_id, str)
        assert isinstance(sticker.thumb.file_unique_id, str)
        assert sticker.thumb.file_id != ""
        assert sticker.thumb.file_unique_id != ""

    def test_expected_values(self, sticker):
        assert sticker.width == self.width
        assert sticker.height == self.height
        assert sticker.is_animated == self.is_animated
        assert sticker.is_video == self.is_video
        assert sticker.file_size == self.file_size
        assert sticker.thumb.width == self.thumb_width
        assert sticker.thumb.height == self.thumb_height
        assert sticker.thumb.file_size == self.thumb_file_size
        assert sticker.type == self.type
        # we need to be a premium TG user to send a premium sticker, so the below is not tested
        # assert sticker.premium_animation == self.premium_animation

    def test_to_dict(self, sticker):
        sticker_dict = sticker.to_dict()

        assert isinstance(sticker_dict, dict)
        assert sticker_dict["file_id"] == sticker.file_id
        assert sticker_dict["file_unique_id"] == sticker.file_unique_id
        assert sticker_dict["width"] == sticker.width
        assert sticker_dict["height"] == sticker.height
        assert sticker_dict["is_animated"] == sticker.is_animated
        assert sticker_dict["is_video"] == sticker.is_video
        assert sticker_dict["file_size"] == sticker.file_size
        assert sticker_dict["thumb"] == sticker.thumb.to_dict()
        assert sticker_dict["type"] == sticker.type

    def test_de_json(self, bot, sticker):
        json_dict = {
            "file_id": self.sticker_file_id,
            "file_unique_id": self.sticker_file_unique_id,
            "width": self.width,
            "height": self.height,
            "is_animated": self.is_animated,
            "is_video": self.is_video,
            "thumb": sticker.thumb.to_dict(),
            "emoji": self.emoji,
            "file_size": self.file_size,
            "premium_animation": self.premium_animation.to_dict(),
            "type": self.type,
            "custom_emoji_id": self.custom_emoji_id,
        }
        json_sticker = Sticker.de_json(json_dict, bot)
        assert json_sticker.api_kwargs == {}

        assert json_sticker.file_id == self.sticker_file_id
        assert json_sticker.file_unique_id == self.sticker_file_unique_id
        assert json_sticker.width == self.width
        assert json_sticker.height == self.height
        assert json_sticker.is_animated == self.is_animated
        assert json_sticker.is_video == self.is_video
        assert json_sticker.emoji == self.emoji
        assert json_sticker.file_size == self.file_size
        assert json_sticker.thumb == sticker.thumb
        assert json_sticker.premium_animation == self.premium_animation
        assert json_sticker.type == self.type
        assert json_sticker.custom_emoji_id == self.custom_emoji_id

    def test_equality(self, sticker):
        a = Sticker(
            sticker.file_id,
            sticker.file_unique_id,
            self.width,
            self.height,
            self.is_animated,
            self.is_video,
            self.type,
        )
        b = Sticker(
            "",
            sticker.file_unique_id,
            self.width,
            self.height,
            self.is_animated,
            self.is_video,
            self.type,
        )
        c = Sticker(
            sticker.file_id,
            sticker.file_unique_id,
            0,
            0,
            False,
            True,
            self.type,
        )
        d = Sticker(
            "",
            "",
            self.width,
            self.height,
            self.is_animated,
            self.is_video,
            self.type,
        )
        e = PhotoSize(
            sticker.file_id,
            sticker.file_unique_id,
            self.width,
            self.height,
            self.is_animated,
        )

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_sticker(chat_id)

    async def test_send_with_sticker(self, monkeypatch, bot, chat_id, sticker):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["sticker"] == sticker.file_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_sticker(sticker=sticker, chat_id=chat_id)

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_sticker_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = data.get("sticker") == expected
                else:
                    test_flag = isinstance(data.get("sticker"), InputFile)

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_sticker(chat_id, file)
            assert test_flag
        finally:
            bot._local_mode = False


class TestStickerWithRequest(TestStickerBase):
    async def test_send_all_args(self, bot, chat_id, sticker_file, sticker):
        message = await bot.send_sticker(
            chat_id, sticker=sticker_file, disable_notification=False, protect_content=True
        )

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert isinstance(message.sticker.file_unique_id, str)
        assert message.sticker.file_id != ""
        assert message.sticker.file_unique_id != ""
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.is_animated == sticker.is_animated
        assert message.sticker.is_video == sticker.is_video
        assert message.sticker.file_size == sticker.file_size
        assert message.sticker.type == sticker.type
        assert message.has_protected_content
        # we need to be a premium TG user to send a premium sticker, so the below is not tested
        # assert message.sticker.premium_animation == sticker.premium_animation

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert isinstance(message.sticker.thumb.file_unique_id, str)
        assert message.sticker.thumb.file_id != ""
        assert message.sticker.thumb.file_unique_id != ""
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    async def test_get_and_download(self, bot, sticker, chat_id):
        path = Path("telegram.webp")
        if path.is_file():
            path.unlink()

        new_file = await bot.get_file(sticker.file_id)

        assert new_file.file_size == sticker.file_size
        assert new_file.file_unique_id == sticker.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive("telegram.webp")

        assert path.is_file()

    async def test_resend(self, bot, chat_id, sticker):
        message = await bot.send_sticker(chat_id=chat_id, sticker=sticker.file_id)

        assert message.sticker == sticker

    async def test_send_on_server_emoji(self, bot, chat_id):
        server_file_id = "CAADAQADHAADyIsGAAFZfq1bphjqlgI"
        message = await bot.send_sticker(chat_id=chat_id, sticker=server_file_id)
        sticker = message.sticker
        assert sticker.emoji == self.emoji

    async def test_send_from_url(self, bot, chat_id):
        message = await bot.send_sticker(chat_id=chat_id, sticker=self.sticker_file_url)
        sticker = message.sticker

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert isinstance(message.sticker.file_unique_id, str)
        assert message.sticker.file_id != ""
        assert message.sticker.file_unique_id != ""
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.is_animated == sticker.is_animated
        assert message.sticker.is_video == sticker.is_video
        assert message.sticker.file_size == sticker.file_size
        assert message.sticker.type == sticker.type

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert isinstance(message.sticker.thumb.file_unique_id, str)
        assert message.sticker.thumb.file_id != ""
        assert message.sticker.thumb.file_unique_id != ""
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    @pytest.mark.parametrize(
        "default_bot,custom",
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_sticker_default_allow_sending_without_reply(
        self, default_bot, chat_id, sticker, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_sticker(
                chat_id,
                sticker,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_sticker(
                chat_id, sticker, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="message not found"):
                await default_bot.send_sticker(
                    chat_id, sticker, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_sticker_default_protect_content(self, chat_id, sticker, default_bot):
        tasks = asyncio.gather(
            default_bot.send_sticker(chat_id, sticker),
            default_bot.send_sticker(chat_id, sticker, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    async def test_premium_animation(self, bot):
        # testing animation sucks a bit since we can't create a premium sticker. What we can do is
        # get a sticker set which includes a premium sticker and check that specific one.
        premium_sticker_set = await bot.get_sticker_set("Flame")
        # the first one to appear here is a sticker with unique file id of AQADOBwAAifPOElr
        # this could change in the future ofc.
        premium_sticker = premium_sticker_set.stickers[20]
        assert premium_sticker.premium_animation.file_unique_id == "AQADOBwAAifPOElr"
        assert isinstance(premium_sticker.premium_animation.file_id, str)
        assert premium_sticker.premium_animation.file_id != ""
        premium_sticker_dict = {
            "file_unique_id": "AQADOBwAAifPOElr",
            "file_id": premium_sticker.premium_animation.file_id,
            "file_size": premium_sticker.premium_animation.file_size,
        }
        assert premium_sticker.premium_animation.to_dict() == premium_sticker_dict

    async def test_custom_emoji(self, bot):
        # testing custom emoji stickers is as much of an annoyance as the premium animation, see
        # in test_premium_animation
        custom_emoji_set = await bot.get_sticker_set("PTBStaticEmojiTestPack")
        # the first one to appear here is a sticker with unique file id of AQADjBsAAkKD0Uty
        # this could change in the future ofc.
        custom_emoji_sticker = custom_emoji_set.stickers[0]
        assert custom_emoji_sticker.custom_emoji_id == "6046140249875156202"

    async def test_custom_emoji_sticker(self, bot):
        # we use the same ID as in test_custom_emoji
        emoji_sticker_list = await bot.get_custom_emoji_stickers(["6046140249875156202"])
        assert emoji_sticker_list[0].emoji == "😎"
        assert emoji_sticker_list[0].height == 100
        assert emoji_sticker_list[0].width == 100
        assert not emoji_sticker_list[0].is_animated
        assert not emoji_sticker_list[0].is_video
        assert emoji_sticker_list[0].set_name == "PTBStaticEmojiTestPack"
        assert emoji_sticker_list[0].type == Sticker.CUSTOM_EMOJI
        assert emoji_sticker_list[0].custom_emoji_id == "6046140249875156202"
        assert emoji_sticker_list[0].thumb.width == 100
        assert emoji_sticker_list[0].thumb.height == 100
        assert emoji_sticker_list[0].thumb.file_size == 3614
        assert emoji_sticker_list[0].thumb.file_unique_id == "AQAD6gwAAoY06FNy"
        assert emoji_sticker_list[0].file_size == 3678
        assert emoji_sticker_list[0].file_unique_id == "AgAD6gwAAoY06FM"

    async def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_sticker(chat_id, open(os.devnull, "rb"))

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_sticker(chat_id, "")


@pytest.fixture(scope="function")
async def sticker_set(bot):
    ss = await bot.get_sticker_set(f"test_by_{bot.username}")
    if len(ss.stickers) > 100:
        try:
            for i in range(1, 50):
                await bot.delete_sticker_from_set(ss.stickers[-i].file_id)
        except BadRequest as e:
            if e.message == "Stickerset_not_modified":
                return ss
            raise Exception("stickerset is growing too large.")
    return ss


@pytest.fixture(scope="function")
async def animated_sticker_set(bot):
    ss = await bot.get_sticker_set(f"animated_test_by_{bot.username}")
    if len(ss.stickers) > 100:
        try:
            for i in range(1, 50):
                bot.delete_sticker_from_set(ss.stickers[-i].file_id)
        except BadRequest as e:
            if e.message == "Stickerset_not_modified":
                return ss
            raise Exception("stickerset is growing too large.")
    return ss


@pytest.fixture(scope="function")
async def video_sticker_set(bot):
    ss = await bot.get_sticker_set(f"video_test_by_{bot.username}")
    if len(ss.stickers) > 100:
        try:
            for i in range(1, 50):
                await bot.delete_sticker_from_set(ss.stickers[-i].file_id)
        except BadRequest as e:
            if e.message == "Stickerset_not_modified":
                return ss
            raise Exception("stickerset is growing too large.")
    return ss


@pytest.fixture(scope="function")
def sticker_set_thumb_file():
    with data_file("sticker_set_thumb.png").open("rb") as file:
        yield file


class TestStickerSetBase:
    title = "Test stickers"
    is_animated = True
    is_video = True
    stickers = [Sticker("file_id", "file_un_id", 512, 512, True, True, Sticker.REGULAR)]
    name = "NOTAREALNAME"
    sticker_type = Sticker.REGULAR
    contains_masks = True


class TestStickerSetWithoutRequest(TestStickerSetBase):
    def test_slot_behaviour(self, mro_slots):
        inst = StickerSet("this", "is", True, self.stickers, True, "not")
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, bot, sticker):
        name = f"test_by_{bot.username}"
        json_dict = {
            "name": name,
            "title": self.title,
            "is_animated": self.is_animated,
            "is_video": self.is_video,
            "stickers": [x.to_dict() for x in self.stickers],
            "thumb": sticker.thumb.to_dict(),
            "sticker_type": self.sticker_type,
            "contains_masks": self.contains_masks,
        }
        sticker_set = StickerSet.de_json(json_dict, bot)

        assert sticker_set.name == name
        assert sticker_set.title == self.title
        assert sticker_set.is_animated == self.is_animated
        assert sticker_set.is_video == self.is_video
        assert sticker_set.stickers == tuple(self.stickers)
        assert sticker_set.thumb == sticker.thumb
        assert sticker_set.sticker_type == self.sticker_type
        assert sticker_set.api_kwargs == {"contains_masks": self.contains_masks}

    def test_sticker_set_to_dict(self, sticker_set):
        sticker_set_dict = sticker_set.to_dict()

        assert isinstance(sticker_set_dict, dict)
        assert sticker_set_dict["name"] == sticker_set.name
        assert sticker_set_dict["title"] == sticker_set.title
        assert sticker_set_dict["is_animated"] == sticker_set.is_animated
        assert sticker_set_dict["is_video"] == sticker_set.is_video
        assert sticker_set_dict["stickers"][0] == sticker_set.stickers[0].to_dict()
        assert sticker_set_dict["thumb"] == sticker_set.thumb.to_dict()
        assert sticker_set_dict["sticker_type"] == sticker_set.sticker_type

    def test_equality(self):
        a = StickerSet(
            self.name,
            self.title,
            self.is_animated,
            self.stickers,
            self.is_video,
            self.sticker_type,
        )
        b = StickerSet(
            self.name,
            self.title,
            self.is_animated,
            self.stickers,
            self.is_video,
            self.sticker_type,
        )
        c = StickerSet(self.name, "title", False, [], True, Sticker.CUSTOM_EMOJI)
        d = StickerSet(
            "blah",
            self.title,
            self.is_animated,
            self.stickers,
            self.is_video,
            self.sticker_type,
        )
        e = Audio(self.name, "", 0, None, None)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_upload_sticker_file_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = data.get("png_sticker") == expected
                else:
                    test_flag = isinstance(data.get("png_sticker"), InputFile)

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.upload_sticker_file(chat_id, file)
            assert test_flag
        finally:
            bot._local_mode = False

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_create_new_sticker_set_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = (
                        data.get("png_sticker") == expected
                        and data.get("tgs_sticker") == expected
                        and data.get("webm_sticker") == expected
                    )
                else:
                    test_flag = (
                        isinstance(data.get("png_sticker"), InputFile)
                        and isinstance(data.get("tgs_sticker"), InputFile)
                        and isinstance(data.get("webm_sticker"), InputFile)
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.create_new_sticker_set(
                chat_id,
                "name",
                "title",
                "emoji",
                png_sticker=file,
                tgs_sticker=file,
                webm_sticker=file,
            )
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_create_new_sticker_all_params(self, monkeypatch, bot, chat_id, mask_position):
        async def make_assertion(_, data, *args, **kwargs):
            assert data["user_id"] == chat_id
            assert data["name"] == "name"
            assert data["title"] == "title"
            assert data["emojis"] == "emoji"
            assert data["mask_position"] == mask_position
            assert data["png_sticker"] == "wow.png"
            assert data["tgs_sticker"] == "wow.tgs"
            assert data["webm_sticker"] == "wow.webm"
            assert data["sticker_type"] == Sticker.MASK

        monkeypatch.setattr(bot, "_post", make_assertion)
        await bot.create_new_sticker_set(
            chat_id,
            "name",
            "title",
            "emoji",
            mask_position=mask_position,
            png_sticker="wow.png",
            tgs_sticker="wow.tgs",
            webm_sticker="wow.webm",
            sticker_type=Sticker.MASK,
        )

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_add_sticker_to_set_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = (
                        data.get("png_sticker") == expected and data.get("tgs_sticker") == expected
                    )
                else:
                    test_flag = isinstance(data.get("png_sticker"), InputFile) and isinstance(
                        data.get("tgs_sticker"), InputFile
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.add_sticker_to_set(
                chat_id, "name", "emoji", png_sticker=file, tgs_sticker=file
            )
            assert test_flag
        finally:
            bot._local_mode = False

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_set_sticker_set_thumb_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = data.get("thumb") == expected
                else:
                    test_flag = isinstance(data.get("thumb"), InputFile)

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.set_sticker_set_thumb("name", chat_id, thumb=file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_get_file_instance_method(self, monkeypatch, sticker):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == sticker.file_id

        assert check_shortcut_signature(Sticker.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(sticker.get_file, sticker.get_bot(), "get_file")
        assert await check_defaults_handling(sticker.get_file, sticker.get_bot())

        monkeypatch.setattr(sticker.get_bot(), "get_file", make_assertion)
        assert await sticker.get_file()


@pytest.mark.xdist_group("stickerset")
class TestStickerSetWithRequest:
    async def test_create_sticker_set(
        self, bot, chat_id, sticker_file, animated_sticker_file, video_sticker_file
    ):
        """Creates the sticker set (if needed) which is required for tests. Make sure that this
        test comes before the tests that actually use the sticker sets!
        """
        test_by = f"test_by_{bot.username}"
        for sticker_set in [test_by, f"animated_{test_by}", f"video_{test_by}"]:
            try:
                ss = await bot.get_sticker_set(sticker_set)
                assert isinstance(ss, StickerSet)
            except BadRequest as e:
                if not e.message == "Stickerset_invalid":
                    raise e

                if sticker_set.startswith(test_by):
                    s = await bot.create_new_sticker_set(
                        chat_id,
                        name=sticker_set,
                        title="Sticker Test",
                        png_sticker=sticker_file,
                        emojis="😄",
                    )
                    assert s
                elif sticker_set.startswith("animated"):
                    a = await bot.create_new_sticker_set(
                        chat_id,
                        name=sticker_set,
                        title="Animated Test",
                        tgs_sticker=animated_sticker_file,
                        emojis="😄",
                    )
                    assert a
                elif sticker_set.startswith("video"):
                    v = await bot.create_new_sticker_set(
                        chat_id,
                        name=sticker_set,
                        title="Video Test",
                        webm_sticker=video_sticker_file,
                        emojis="🤔",
                    )
                    assert v

    async def test_bot_methods_1_png(self, bot, chat_id, sticker_file):
        with data_file("telegram_sticker.png").open("rb") as f:
            # chat_id was hardcoded as 95205500 but it stopped working for some reason
            file = await bot.upload_sticker_file(chat_id, f)
        assert file

        await asyncio.sleep(1)
        tasks = asyncio.gather(
            bot.add_sticker_to_set(
                chat_id, f"test_by_{bot.username}", png_sticker=file.file_id, emojis="😄"
            ),
            bot.add_sticker_to_set(  # Also test with file input and mask
                chat_id,
                f"test_by_{bot.username}",
                png_sticker=sticker_file,
                emojis="😄",
                mask_position=MaskPosition(MaskPosition.EYES, -1, 1, 2),
            ),
        )
        assert all(await tasks)

    async def test_bot_methods_1_tgs(self, bot, chat_id):
        await asyncio.sleep(1)
        assert await bot.add_sticker_to_set(
            chat_id,
            f"animated_test_by_{bot.username}",
            tgs_sticker=data_file("telegram_animated_sticker.tgs").open("rb"),
            emojis="😄",
        )

    async def test_bot_methods_1_webm(self, bot, chat_id):
        await asyncio.sleep(1)
        with data_file("telegram_video_sticker.webm").open("rb") as f:
            assert await bot.add_sticker_to_set(
                chat_id, f"video_test_by_{bot.username}", webm_sticker=f, emojis="🤔"
            )

    async def test_bot_methods_2_png(self, bot, sticker_set):
        await asyncio.sleep(1)
        file_id = sticker_set.stickers[0].file_id
        assert await bot.set_sticker_position_in_set(file_id, 1)

    async def test_bot_methods_2_tgs(self, bot, animated_sticker_set):
        await asyncio.sleep(1)
        file_id = animated_sticker_set.stickers[0].file_id
        assert await bot.set_sticker_position_in_set(file_id, 1)

    async def test_bot_methods_2_webm(self, bot, video_sticker_set):
        await asyncio.sleep(1)
        file_id = video_sticker_set.stickers[0].file_id
        assert await bot.set_sticker_position_in_set(file_id, 1)

    async def test_bot_methods_3_png(self, bot, chat_id, sticker_set_thumb_file):
        await asyncio.sleep(1)
        assert await bot.set_sticker_set_thumb(
            f"test_by_{bot.username}", chat_id, sticker_set_thumb_file
        )

    async def test_bot_methods_3_tgs(
        self, bot, chat_id, animated_sticker_file, animated_sticker_set
    ):
        await asyncio.sleep(1)
        animated_test = f"animated_test_by_{bot.username}"
        file_id = animated_sticker_set.stickers[-1].file_id
        tasks = asyncio.gather(
            bot.set_sticker_set_thumb(animated_test, chat_id, animated_sticker_file),
            bot.set_sticker_set_thumb(animated_test, chat_id, file_id),
        )
        assert all(await tasks)

    # TODO: Try the below by creating a custom .webm and not by downloading another pack's thumb
    @pytest.mark.skip(
        "Skipped for now since Telegram throws a 'File is too big' error "
        "regardless of the .webm file size."
    )
    def test_bot_methods_3_webm(self, bot, chat_id, video_sticker_file, video_sticker_set):
        pass

    async def test_bot_methods_4_png(self, bot, sticker_set):
        await asyncio.sleep(1)
        file_id = sticker_set.stickers[-1].file_id
        assert await bot.delete_sticker_from_set(file_id)

    async def test_bot_methods_4_tgs(self, bot, animated_sticker_set):
        await asyncio.sleep(1)
        file_id = animated_sticker_set.stickers[-1].file_id
        assert await bot.delete_sticker_from_set(file_id)

    async def test_bot_methods_4_webm(self, bot, video_sticker_set):
        await asyncio.sleep(1)
        file_id = video_sticker_set.stickers[-1].file_id
        assert await bot.delete_sticker_from_set(file_id)


@pytest.fixture(scope="module")
def mask_position():
    return MaskPosition(
        TestMaskPositionBase.point,
        TestMaskPositionBase.x_shift,
        TestMaskPositionBase.y_shift,
        TestMaskPositionBase.scale,
    )


class TestMaskPositionBase:
    point = MaskPosition.EYES
    x_shift = -1
    y_shift = 1
    scale = 2


class TestMaskPositionWithoutRequest(TestMaskPositionBase):
    def test_slot_behaviour(self, mask_position, mro_slots):
        inst = mask_position
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_mask_position_de_json(self, bot):
        json_dict = {
            "point": self.point,
            "x_shift": self.x_shift,
            "y_shift": self.y_shift,
            "scale": self.scale,
        }
        mask_position = MaskPosition.de_json(json_dict, bot)
        assert mask_position.api_kwargs == {}

        assert mask_position.point == self.point
        assert mask_position.x_shift == self.x_shift
        assert mask_position.y_shift == self.y_shift
        assert mask_position.scale == self.scale

    def test_mask_position_to_dict(self, mask_position):
        mask_position_dict = mask_position.to_dict()

        assert isinstance(mask_position_dict, dict)
        assert mask_position_dict["point"] == mask_position.point
        assert mask_position_dict["x_shift"] == mask_position.x_shift
        assert mask_position_dict["y_shift"] == mask_position.y_shift
        assert mask_position_dict["scale"] == mask_position.scale

    def test_equality(self):
        a = MaskPosition(self.point, self.x_shift, self.y_shift, self.scale)
        b = MaskPosition(self.point, self.x_shift, self.y_shift, self.scale)
        c = MaskPosition(MaskPosition.FOREHEAD, self.x_shift, self.y_shift, self.scale)
        d = MaskPosition(self.point, 0, 0, self.scale)
        e = Audio("", "", 0, None, None)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
