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
import os
from pathlib import Path

import pytest

from telegram import Animation, Bot, InputFile, MessageEntity, PhotoSize, ReplyParameters, Voice
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.build_messages import make_message
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture()
def animation_file():
    with data_file("game.gif").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def animation(bot, chat_id):
    with data_file("game.gif").open("rb") as f, data_file("thumb.jpg").open("rb") as thumb:
        return (
            await bot.send_animation(chat_id, animation=f, read_timeout=50, thumbnail=thumb)
        ).animation


class TestAnimationBase:
    animation_file_id = "CgADAQADngIAAuyVeEez0xRovKi9VAI"
    animation_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"
    width = 320
    height = 180
    duration = 1
    # animation_file_url = 'https://python-telegram-bot.org/static/testfiles/game.gif'
    # Shortened link, the above one is cached with the wrong duration.
    animation_file_url = "http://bit.ly/2L18jua"
    file_name = "game.gif.webm"
    mime_type = "video/mp4"
    file_size = 5859
    caption = "Test *animation*"


class TestAnimationWithoutRequest(TestAnimationBase):
    def test_slot_behaviour(self, animation):
        for attr in animation.__slots__:
            assert getattr(animation, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(animation)) == len(set(mro_slots(animation))), "duplicate slot"

    def test_creation(self, animation):
        assert isinstance(animation, Animation)
        assert isinstance(animation.file_id, str)
        assert isinstance(animation.file_unique_id, str)
        assert animation.file_id
        assert animation.file_unique_id

    def test_expected_values(self, animation):
        assert animation.mime_type == self.mime_type
        assert animation.file_name.startswith("game.gif") == self.file_name.startswith("game.gif")
        assert isinstance(animation.thumbnail, PhotoSize)

    def test_de_json(self, bot, animation):
        json_dict = {
            "file_id": self.animation_file_id,
            "file_unique_id": self.animation_file_unique_id,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnail": animation.thumbnail.to_dict(),
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        animation = Animation.de_json(json_dict, bot)
        assert animation.api_kwargs == {}
        assert animation.file_id == self.animation_file_id
        assert animation.file_unique_id == self.animation_file_unique_id
        assert animation.file_name == self.file_name
        assert animation.mime_type == self.mime_type
        assert animation.file_size == self.file_size

    def test_to_dict(self, animation):
        animation_dict = animation.to_dict()

        assert isinstance(animation_dict, dict)
        assert animation_dict["file_id"] == animation.file_id
        assert animation_dict["file_unique_id"] == animation.file_unique_id
        assert animation_dict["width"] == animation.width
        assert animation_dict["height"] == animation.height
        assert animation_dict["duration"] == animation.duration
        assert animation_dict["thumbnail"] == animation.thumbnail.to_dict()
        assert animation_dict["file_name"] == animation.file_name
        assert animation_dict["mime_type"] == animation.mime_type
        assert animation_dict["file_size"] == animation.file_size

    def test_equality(self):
        a = Animation(
            self.animation_file_id,
            self.animation_file_unique_id,
            self.height,
            self.width,
            self.duration,
        )
        b = Animation("", self.animation_file_unique_id, self.height, self.width, self.duration)
        d = Animation("", "", 0, 0, 0)
        e = Voice(self.animation_file_id, self.animation_file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_send_animation_custom_filename(self, bot, chat_id, animation_file, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return next(iter(request_data.multipart_data.values()))[0] == "custom_filename"

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_animation(chat_id, animation_file, filename="custom_filename")

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_animation_local_files(self, monkeypatch, bot, chat_id, local_mode):
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
                        data.get("animation") == expected and data.get("thumbnail") == expected
                    )
                else:
                    test_flag = isinstance(data.get("animation"), InputFile) and isinstance(
                        data.get("thumbnail"), InputFile
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_animation(chat_id, file, thumbnail=file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_send_with_animation(self, monkeypatch, bot, chat_id, animation):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["animation"] == animation.file_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_animation(animation=animation, chat_id=chat_id)

    async def test_get_file_instance_method(self, monkeypatch, animation):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == animation.file_id

        assert check_shortcut_signature(Animation.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(animation.get_file, animation.get_bot(), "get_file")
        assert await check_defaults_handling(animation.get_file, animation.get_bot())

        monkeypatch.setattr(animation.get_bot(), "get_file", make_assertion)
        assert await animation.get_file()

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_animation_default_quote_parse_mode(
        self, default_bot, chat_id, animation, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": 1}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_animation(
            chat_id, animation, reply_parameters=ReplyParameters(**kwargs)
        )


class TestAnimationWithRequest(TestAnimationBase):
    async def test_send_all_args(self, bot, chat_id, animation_file, animation, thumb_file):
        message = await bot.send_animation(
            chat_id,
            animation_file,
            duration=self.duration,
            width=self.width,
            height=self.height,
            caption=self.caption,
            parse_mode="Markdown",
            disable_notification=False,
            protect_content=True,
            thumbnail=thumb_file,
            has_spoiler=True,
        )

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert isinstance(message.animation.file_unique_id, str)
        assert message.animation.file_id
        assert message.animation.file_unique_id
        assert message.animation.file_name == animation.file_name
        assert message.animation.mime_type == animation.mime_type
        assert message.animation.file_size == animation.file_size
        assert message.animation.thumbnail.width == self.width
        assert message.animation.thumbnail.height == self.height
        assert message.has_protected_content
        try:
            assert message.has_media_spoiler
        except AssertionError:
            pytest.xfail("This is a bug on Telegram's end")

    async def test_get_and_download(self, bot, animation, tmp_file):
        new_file = await bot.get_file(animation.file_id)

        assert new_file.file_path.startswith("https://")

        new_filepath = await new_file.download_to_drive(tmp_file)
        assert new_filepath.is_file()

    async def test_send_animation_url_file(self, bot, chat_id, animation):
        message = await bot.send_animation(
            chat_id=chat_id, animation=self.animation_file_url, caption=self.caption
        )

        assert message.caption == self.caption

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert isinstance(message.animation.file_unique_id, str)
        assert message.animation.file_id
        assert message.animation.file_unique_id

        assert message.animation.duration == animation.duration
        assert message.animation.file_name.startswith(
            "game.gif"
        ) == animation.file_name.startswith("game.gif")
        assert message.animation.mime_type == animation.mime_type

    async def test_send_animation_caption_entities(self, bot, chat_id, animation):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_animation(
            chat_id, animation, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_animation_default_parse_mode_1(self, default_bot, chat_id, animation_file):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string
        )
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_animation_default_parse_mode_2(self, default_bot, chat_id, animation_file):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_animation_default_parse_mode_3(self, default_bot, chat_id, animation_file):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string, parse_mode="HTML"
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_animation_default_allow_sending_without_reply(
        self, default_bot, chat_id, animation, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_animation(
                chat_id,
                animation,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_animation(
                chat_id, animation, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_animation(
                    chat_id, animation, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_animation_default_protect_content(self, default_bot, chat_id, animation):
        tasks = asyncio.gather(
            default_bot.send_animation(chat_id, animation),
            default_bot.send_animation(chat_id, animation, protect_content=False),
        )
        anim_protected, anim_unprotected = await tasks
        assert anim_protected.has_protected_content
        assert not anim_unprotected.has_protected_content

    async def test_resend(self, bot, chat_id, animation):
        message = await bot.send_animation(chat_id, animation.file_id)
        assert message.animation == animation

    async def test_error_send_empty_file(self, bot, chat_id):
        with Path(os.devnull).open("rb") as animation_file, pytest.raises(TelegramError):
            await bot.send_animation(chat_id=chat_id, animation=animation_file)

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_animation(chat_id=chat_id, animation="")

    async def test_error_send_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_animation(chat_id=chat_id)
