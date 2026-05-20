#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains an object that tests a Telegram LivePhoto."""

import asyncio
import datetime as dtm
import os
from pathlib import Path

import pytest

from telegram import (
    InputFile,
    LivePhoto,
    MessageEntity,
    PhotoSize,
    ReplyParameters,
    Voice,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.auxil.build_messages import make_message
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def live_photo():
    return LivePhoto(
        file_id=LivePhotoTestBase.file_id,
        file_unique_id=LivePhotoTestBase.file_unique_id,
        width=LivePhotoTestBase.width,
        height=LivePhotoTestBase.height,
        duration=LivePhotoTestBase.duration,
        photo=LivePhotoTestBase.photo,
        mime_type=LivePhotoTestBase.mime_type,
        file_size=LivePhotoTestBase.file_size,
    )


class LivePhotoTestBase:
    caption = "LivePhotoTest - *Caption*"
    width = 360
    height = 640
    duration = dtm.timedelta(seconds=5)
    file_size = 326534
    mime_type = "video/mp4"
    photo = (PhotoSize("file_id", "unique_id", 640, 360, file_size=0),)
    file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"


class TestLivePhotoWithoutRequest(LivePhotoTestBase):
    def test_slot_behaviour(self, live_photo):
        for attr in live_photo.__slots__:
            assert getattr(live_photo, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(live_photo)) == len(set(mro_slots(live_photo))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "width": self.width,
            "height": self.height,
            "duration": int(self.duration.total_seconds()),
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "photo": [photo_size.to_dict() for photo_size in self.photo],
        }
        json_live_photo = LivePhoto.de_json(json_dict, offline_bot)
        assert json_live_photo.api_kwargs == {}

        assert json_live_photo.file_id == self.file_id
        assert json_live_photo.file_unique_id == self.file_unique_id
        assert json_live_photo.width == self.width
        assert json_live_photo.height == self.height
        assert json_live_photo.duration == self.duration
        assert json_live_photo.mime_type == self.mime_type
        assert json_live_photo.file_size == self.file_size
        assert json_live_photo.photo == self.photo

    def test_to_dict(self, live_photo):
        live_photo_dict = live_photo.to_dict()

        assert isinstance(live_photo_dict, dict)
        assert live_photo_dict["file_id"] == live_photo.file_id
        assert live_photo_dict["file_unique_id"] == live_photo.file_unique_id
        assert live_photo_dict["width"] == live_photo.width
        assert live_photo_dict["height"] == live_photo.height
        assert live_photo_dict["duration"] == int(self.duration.total_seconds())
        assert isinstance(live_photo_dict["duration"], int)
        assert live_photo_dict["mime_type"] == live_photo.mime_type
        assert live_photo_dict["file_size"] == live_photo.file_size
        assert live_photo_dict["photo"] == [p.to_dict() for p in self.photo]

    def test_equality(self, live_photo):
        a = LivePhoto(
            live_photo.file_id, live_photo.file_unique_id, self.width, self.height, self.duration
        )
        b = LivePhoto("", live_photo.file_unique_id, self.width, self.height, self.duration)
        c = LivePhoto(live_photo.file_id, live_photo.file_unique_id, 0, 0, 0)
        d = LivePhoto("", "", self.width, self.height, self.duration)
        e = Voice(live_photo.file_id, live_photo.file_unique_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_send_with_live_photo(self, monkeypatch, offline_bot, chat_id, live_photo):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            return (
                data["live_photo"] == live_photo.file_id
                and data["photo"] == live_photo.photo[0].file_id
            )

        monkeypatch.setattr(offline_bot.request, "post", make_assertion)

        assert await offline_bot.send_live_photo(
            chat_id=chat_id,
            live_photo=live_photo,
            photo=live_photo.photo[0],
        )

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_live_photo_default_quote_parse_mode(
        self, default_bot, chat_id, live_photo, custom, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            assert request_data.parameters["reply_parameters"].get("quote_parse_mode") == (
                custom or default_bot.defaults.quote_parse_mode
            )
            return make_message("dummy reply").to_dict()

        kwargs = {"message_id": "1"}
        if custom is not None:
            kwargs["quote_parse_mode"] = custom

        monkeypatch.setattr(default_bot.request, "post", make_assertion)
        await default_bot.send_live_photo(
            chat_id=chat_id,
            live_photo=live_photo,
            photo=live_photo.photo[0],
            reply_parameters=ReplyParameters(**kwargs),
        )

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_live_photo(
        self, dummy_message_dict, monkeypatch, offline_bot, chat_id, local_mode
    ):
        try:
            offline_bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local Bot API set up
            test_flag = False
            photo = data_file("telegram.jpg")
            expected_photo = photo.as_uri()

            live_photo = data_file("telegram.mp4")
            expected_live_photo = live_photo.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = (
                        data.get("live_photo") == expected_live_photo
                        and data.get("photo") == expected_photo
                    )
                else:
                    test_flag = isinstance(data.get("live_photo"), InputFile) and isinstance(
                        data.get("photo"), InputFile
                    )
                return dummy_message_dict

            monkeypatch.setattr(offline_bot, "_post", make_assertion)
            await offline_bot.send_live_photo(chat_id, live_photo=live_photo, photo=photo)
            assert test_flag
        finally:
            offline_bot._local_mode = False


class TestLivePhotoWithRequest(LivePhotoTestBase):
    async def test_error_send_empty_file(self, bot, chat_id):
        with Path(os.devnull).open("rb") as f, pytest.raises(TelegramError):
            await bot.send_live_photo(chat_id=chat_id, live_photo=f, photo=f)

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_live_photo(chat_id=chat_id, live_photo="", photo="")

    async def test_get_and_download(self, bot, real_live_photo, tmp_file):
        new_file = await bot.get_file(real_live_photo.file_id)

        assert new_file.file_size == real_live_photo.file_size
        assert new_file.file_unique_id == real_live_photo.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive(tmp_file)

        assert tmp_file.is_file()

    async def test_send_resend(self, bot, chat_id, real_live_photo, photo_file):
        message = await bot.send_live_photo(
            chat_id=chat_id, live_photo=real_live_photo.file_id, photo=photo_file
        )
        assert message.live_photo == real_live_photo

    async def test_send_all_args(self, bot, chat_id, video_file, live_photo, photo_file):
        message = await bot.send_live_photo(
            chat_id,
            live_photo=video_file,
            photo=photo_file,
            caption=self.caption,
            disable_notification=False,
            protect_content=True,
            filename="telegram_custom.png",
            parse_mode="Markdown",
        )

        assert isinstance(message.live_photo, LivePhoto)
        assert isinstance(message.live_photo.file_id, str)
        assert message.live_photo.file_id
        assert isinstance(message.live_photo.file_unique_id, str)
        assert message.live_photo.file_unique_id
        assert message.live_photo.photo
        assert isinstance(message.live_photo.photo[0], PhotoSize)
        assert message.live_photo.mime_type == live_photo.mime_type
        assert message.live_photo.file_size == live_photo.file_size
        assert message.caption == self.caption.replace("*", "")
        assert message.has_protected_content

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_live_photo_default_protect_content(
        self,
        chat_id,
        default_bot,
        real_live_photo,
    ):
        tasks = asyncio.gather(
            default_bot.send_live_photo(
                chat_id, photo=real_live_photo.photo[0], live_photo=real_live_photo
            ),
            default_bot.send_live_photo(
                chat_id,
                photo=real_live_photo.photo[0],
                live_photo=real_live_photo,
                protect_content=False,
            ),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    async def test_send_live_photo_caption_entities(self, bot, chat_id, video_file, photo_file):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_live_photo(
            chat_id,
            photo=photo_file,
            live_photo=video_file,
            caption=test_string,
            caption_entities=entities,
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_live_photo_default_parse_mode_1(
        self, default_bot, chat_id, video_file, photo_file
    ):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_live_photo(
            chat_id, photo=photo_file, live_photo=video_file, caption=test_markdown_string
        )
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_live_photo_default_parse_mode_2(
        self, default_bot, chat_id, video_file, photo_file
    ):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_live_photo(
            chat_id,
            photo=photo_file,
            live_photo=video_file,
            caption=test_markdown_string,
            parse_mode=None,
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_live_photo_default_parse_mode_3(
        self, default_bot, chat_id, video_file, photo_file
    ):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_live_photo(
            chat_id,
            photo=photo_file,
            live_photo=video_file,
            caption=test_markdown_string,
            parse_mode="HTML",
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
    async def test_send_live_photo_default_allow_sending_without_reply(
        self, default_bot, chat_id, video_file, photo_file, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_live_photo(
                chat_id,
                photo=photo_file,
                live_photo=video_file,
                reply_parameters=ReplyParameters(
                    message_id=reply_to_message.message_id, allow_sending_without_reply=custom
                ),
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_live_photo(
                chat_id,
                photo=photo_file,
                live_photo=video_file,
                reply_parameters=ReplyParameters(message_id=reply_to_message.message_id),
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to be replied not found"):
                await default_bot.send_live_photo(
                    chat_id,
                    photo=photo_file,
                    live_photo=video_file,
                    reply_parameters=ReplyParameters(message_id=reply_to_message.message_id),
                )
