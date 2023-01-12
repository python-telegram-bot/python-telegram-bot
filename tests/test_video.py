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

from telegram import Bot, InputFile, MessageEntity, PhotoSize, Video, Voice
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.conftest import data_file


@pytest.fixture(scope="function")
def video_file():
    with data_file("telegram.mp4").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def video(bot, chat_id):
    with data_file("telegram.mp4").open("rb") as f:
        return (await bot.send_video(chat_id, video=f, read_timeout=50)).video


class Space:
    width = 360
    height = 640
    duration = 5
    file_size = 326534
    mime_type = "video/mp4"
    supports_streaming = True
    file_name = "telegram.mp4"
    thumb_width = 180
    thumb_height = 320
    thumb_file_size = 1767
    caption = "<b>VideoTest</b> - *Caption*"
    video_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.mp4"
    video_file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    video_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"


class TestVideoWithoutRequest:
    def test_slot_behaviour(self, video, mro_slots):
        for attr in video.__slots__:
            assert getattr(video, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(video)) == len(set(mro_slots(video))), "duplicate slot"

    def test_creation(self, video):
        # Make sure file has been uploaded.
        assert isinstance(video, Video)
        assert isinstance(video.file_id, str)
        assert isinstance(video.file_unique_id, str)
        assert video.file_id != ""
        assert video.file_unique_id != ""

        assert isinstance(video.thumb, PhotoSize)
        assert isinstance(video.thumb.file_id, str)
        assert isinstance(video.thumb.file_unique_id, str)
        assert video.thumb.file_id != ""
        assert video.thumb.file_unique_id != ""

    def test_expected_values(self, video):
        assert video.width == Space.width
        assert video.height == Space.height
        assert video.duration == Space.duration
        assert video.file_size == Space.file_size
        assert video.mime_type == Space.mime_type

    def test_de_json(self, bot):
        json_dict = {
            "file_id": Space.video_file_id,
            "file_unique_id": Space.video_file_unique_id,
            "width": Space.width,
            "height": Space.height,
            "duration": Space.duration,
            "mime_type": Space.mime_type,
            "file_size": Space.file_size,
            "file_name": Space.file_name,
        }
        json_video = Video.de_json(json_dict, bot)
        assert json_video.api_kwargs == {}

        assert json_video.file_id == Space.video_file_id
        assert json_video.file_unique_id == Space.video_file_unique_id
        assert json_video.width == Space.width
        assert json_video.height == Space.height
        assert json_video.duration == Space.duration
        assert json_video.mime_type == Space.mime_type
        assert json_video.file_size == Space.file_size
        assert json_video.file_name == Space.file_name

    def test_to_dict(self, video):
        video_dict = video.to_dict()

        assert isinstance(video_dict, dict)
        assert video_dict["file_id"] == video.file_id
        assert video_dict["file_unique_id"] == video.file_unique_id
        assert video_dict["width"] == video.width
        assert video_dict["height"] == video.height
        assert video_dict["duration"] == video.duration
        assert video_dict["mime_type"] == video.mime_type
        assert video_dict["file_size"] == video.file_size
        assert video_dict["file_name"] == video.file_name

    def test_equality(self, video):
        a = Video(video.file_id, video.file_unique_id, Space.width, Space.height, Space.duration)
        b = Video("", video.file_unique_id, Space.width, Space.height, Space.duration)
        c = Video(video.file_id, video.file_unique_id, 0, 0, 0)
        d = Video("", "", Space.width, Space.height, Space.duration)
        e = Voice(video.file_id, video.file_unique_id, Space.duration)

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
            await bot.send_video(chat_id=chat_id)

    async def test_send_with_video(self, monkeypatch, bot, chat_id, video):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["video"] == video.file_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_video(chat_id, video=video)

    async def test_send_video_custom_filename(self, bot, chat_id, video_file, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return list(request_data.multipart_data.values())[0][0] == "custom_filename"

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.send_video(chat_id, video_file, filename="custom_filename")

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_video_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = data.get("video") == expected and data.get("thumb") == expected
                else:
                    test_flag = isinstance(data.get("video"), InputFile) and isinstance(
                        data.get("thumb"), InputFile
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_video(chat_id, file, thumb=file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_get_file_instance_method(self, monkeypatch, video):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == video.file_id

        assert check_shortcut_signature(Video.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(video.get_file, video.get_bot(), "get_file")
        assert await check_defaults_handling(video.get_file, video.get_bot())

        monkeypatch.setattr(video.get_bot(), "get_file", make_assertion)
        assert await video.get_file()


class TestVideoWithRequest:
    async def test_send_all_args(self, bot, chat_id, video_file, video, thumb_file):
        message = await bot.send_video(
            chat_id,
            video_file,
            duration=Space.duration,
            caption=Space.caption,
            supports_streaming=Space.supports_streaming,
            disable_notification=False,
            protect_content=True,
            width=video.width,
            height=video.height,
            parse_mode="Markdown",
            thumb=thumb_file,
            has_spoiler=True,
        )

        assert isinstance(message.video, Video)
        assert isinstance(message.video.file_id, str)
        assert isinstance(message.video.file_unique_id, str)
        assert message.video.file_id != ""
        assert message.video.file_unique_id != ""
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert message.caption == Space.caption.replace("*", "")

        assert message.video.thumb.file_size == Space.thumb_file_size
        assert message.video.thumb.width == Space.thumb_width
        assert message.video.thumb.height == Space.thumb_height

        assert message.video.file_name == Space.file_name
        assert message.has_protected_content
        assert message.has_media_spoiler

    async def test_get_and_download(self, bot, video, chat_id):
        path = Path("telegram.mp4")
        if path.is_file():
            path.unlink()

        video = (await bot.send_video(chat_id, video.file_id, read_timeout=50)).video
        new_file = await bot.get_file(video.file_id)

        assert new_file.file_size == Space.file_size
        assert new_file.file_id == video.file_id
        assert new_file.file_unique_id == video.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive("telegram.mp4")

        assert path.is_file()

    async def test_send_mp4_file_url(self, bot, chat_id, video):
        message = await bot.send_video(chat_id, Space.video_file_url, caption=Space.caption)

        assert isinstance(message.video, Video)
        assert isinstance(message.video.file_id, str)
        assert isinstance(message.video.file_unique_id, str)
        assert message.video.file_id != ""
        assert message.video.file_unique_id != ""
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert isinstance(message.video.thumb, PhotoSize)
        assert isinstance(message.video.thumb.file_id, str)
        assert isinstance(message.video.thumb.file_unique_id, str)
        assert message.video.thumb.file_id != ""
        assert message.video.thumb.file_unique_id != ""
        assert message.video.thumb.width == 51  # This seems odd that it's not Space.thumb_width
        assert message.video.thumb.height == 90  # Ditto
        assert message.video.thumb.file_size == 645  # same

        assert message.caption == Space.caption

    async def test_send_video_caption_entities(self, bot, chat_id, video):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_video(
            chat_id, video, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    async def test_resend(self, bot, chat_id, video):
        message = await bot.send_video(chat_id, video.file_id)
        assert message.video == video

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_video_default_parse_mode_1(self, default_bot, chat_id, video):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_video(chat_id, video, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_video_default_parse_mode_2(self, default_bot, chat_id, video):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_video(
            chat_id, video, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_video_default_parse_mode_3(self, default_bot, chat_id, video):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_video(
            chat_id, video, caption=test_markdown_string, parse_mode="HTML"
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_video_default_protect_content(self, chat_id, default_bot, video):
        tasks = asyncio.gather(
            default_bot.send_video(chat_id, video),
            default_bot.send_video(chat_id, video, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    @pytest.mark.parametrize(
        "default_bot,custom",
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_video_default_allow_sending_without_reply(
        self, default_bot, chat_id, video, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_video(
                chat_id,
                video,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_video(
                chat_id, video, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="message not found"):
                await default_bot.send_video(
                    chat_id, video, reply_to_message_id=reply_to_message.message_id
                )

    async def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_video(chat_id, open(os.devnull, "rb"))

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_video(chat_id, "")
