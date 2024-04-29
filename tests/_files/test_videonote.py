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

from telegram import Bot, InputFile, PhotoSize, ReplyParameters, VideoNote, Voice
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
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
def video_note_file():
    with data_file("telegram2.mp4").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def video_note(bot, chat_id):
    with data_file("telegram2.mp4").open("rb") as f:
        return (await bot.send_video_note(chat_id, video_note=f, read_timeout=50)).video_note


class TestVideoNoteBase:
    length = 240
    duration = 3
    file_size = 132084
    thumb_width = 240
    thumb_height = 240
    thumb_file_size = 11547
    caption = "VideoNoteTest - Caption"
    videonote_file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    videonote_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"


class TestVideoNoteWithoutRequest(TestVideoNoteBase):
    def test_slot_behaviour(self, video_note):
        for attr in video_note.__slots__:
            assert getattr(video_note, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(video_note)) == len(set(mro_slots(video_note))), "duplicate slot"

    def test_creation(self, video_note):
        # Make sure file has been uploaded.
        assert isinstance(video_note, VideoNote)
        assert isinstance(video_note.file_id, str)
        assert isinstance(video_note.file_unique_id, str)
        assert video_note.file_id
        assert video_note.file_unique_id

        assert isinstance(video_note.thumbnail, PhotoSize)
        assert isinstance(video_note.thumbnail.file_id, str)
        assert isinstance(video_note.thumbnail.file_unique_id, str)
        assert video_note.thumbnail.file_id
        assert video_note.thumbnail.file_unique_id

    def test_expected_values(self, video_note):
        assert video_note.length == self.length
        assert video_note.duration == self.duration
        assert video_note.file_size == self.file_size

    def test_de_json(self, bot):
        json_dict = {
            "file_id": self.videonote_file_id,
            "file_unique_id": self.videonote_file_unique_id,
            "length": self.length,
            "duration": self.duration,
            "file_size": self.file_size,
        }
        json_video_note = VideoNote.de_json(json_dict, bot)
        assert json_video_note.api_kwargs == {}

        assert json_video_note.file_id == self.videonote_file_id
        assert json_video_note.file_unique_id == self.videonote_file_unique_id
        assert json_video_note.length == self.length
        assert json_video_note.duration == self.duration
        assert json_video_note.file_size == self.file_size

    def test_to_dict(self, video_note):
        video_note_dict = video_note.to_dict()

        assert isinstance(video_note_dict, dict)
        assert video_note_dict["file_id"] == video_note.file_id
        assert video_note_dict["file_unique_id"] == video_note.file_unique_id
        assert video_note_dict["length"] == video_note.length
        assert video_note_dict["duration"] == video_note.duration
        assert video_note_dict["file_size"] == video_note.file_size

    def test_equality(self, video_note):
        a = VideoNote(video_note.file_id, video_note.file_unique_id, self.length, self.duration)
        b = VideoNote("", video_note.file_unique_id, self.length, self.duration)
        c = VideoNote(video_note.file_id, video_note.file_unique_id, 0, 0)
        d = VideoNote("", "", self.length, self.duration)
        e = Voice(video_note.file_id, video_note.file_unique_id, self.duration)

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
            await bot.send_video_note(chat_id=chat_id)

    async def test_send_with_video_note(self, monkeypatch, bot, chat_id, video_note):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["video_note"] == video_note.file_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_video_note(chat_id, video_note=video_note)

    async def test_send_video_note_custom_filename(
        self, bot, chat_id, video_note_file, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return next(iter(request_data.multipart_data.values()))[0] == "custom_filename"

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.send_video_note(chat_id, video_note_file, filename="custom_filename")

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_video_note_local_files(self, monkeypatch, bot, chat_id, local_mode):
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
                        data.get("video_note") == expected and data.get("thumbnail") == expected
                    )
                else:
                    test_flag = isinstance(data.get("video_note"), InputFile) and isinstance(
                        data.get("thumbnail"), InputFile
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_video_note(chat_id, file, thumbnail=file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_get_file_instance_method(self, monkeypatch, video_note):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == video_note.file_id

        assert check_shortcut_signature(VideoNote.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(video_note.get_file, video_note.get_bot(), "get_file")
        assert await check_defaults_handling(video_note.get_file, video_note.get_bot())

        monkeypatch.setattr(video_note.get_bot(), "get_file", make_assertion)
        assert await video_note.get_file()

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"parse_mode": ParseMode.HTML}, None),
            ({"parse_mode": ParseMode.HTML}, ParseMode.MARKDOWN_V2),
            ({"parse_mode": None}, ParseMode.MARKDOWN_V2),
        ],
        indirect=["default_bot"],
    )
    async def test_send_video_note_default_quote_parse_mode(
        self, default_bot, chat_id, video_note, custom, monkeypatch
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
        await default_bot.send_video_note(
            chat_id, video_note, reply_parameters=ReplyParameters(**kwargs)
        )


class TestVideoNoteWithRequest(TestVideoNoteBase):
    async def test_send_all_args(self, bot, chat_id, video_note_file, video_note, thumb_file):
        message = await bot.send_video_note(
            chat_id,
            video_note_file,
            duration=self.duration,
            length=self.length,
            disable_notification=False,
            protect_content=True,
            thumbnail=thumb_file,
        )

        assert isinstance(message.video_note, VideoNote)
        assert isinstance(message.video_note.file_id, str)
        assert isinstance(message.video_note.file_unique_id, str)
        assert message.video_note.file_id
        assert message.video_note.file_unique_id
        assert message.video_note.length == video_note.length
        assert message.video_note.duration == video_note.duration
        assert message.video_note.file_size == video_note.file_size

        assert message.video_note.thumbnail.file_size == self.thumb_file_size
        assert message.video_note.thumbnail.width == self.thumb_width
        assert message.video_note.thumbnail.height == self.thumb_height
        assert message.has_protected_content

    async def test_get_and_download(self, bot, video_note, chat_id, tmp_file):
        new_file = await bot.get_file(video_note.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_unique_id == video_note.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive(tmp_file)

        assert tmp_file.is_file()

    async def test_resend(self, bot, chat_id, video_note):
        message = await bot.send_video_note(chat_id, video_note.file_id)
        assert message.video_note == video_note

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_video_note_default_allow_sending_without_reply(
        self, default_bot, chat_id, video_note, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_video_note(
                chat_id,
                video_note,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_video_note(
                chat_id, video_note, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="Message to reply not found"):
                await default_bot.send_video_note(
                    chat_id, video_note, reply_to_message_id=reply_to_message.message_id
                )

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_video_note_default_protect_content(self, chat_id, default_bot, video_note):
        tasks = asyncio.gather(
            default_bot.send_video_note(chat_id, video_note),
            default_bot.send_video_note(chat_id, video_note, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    async def test_error_send_empty_file(self, bot, chat_id):
        with Path(os.devnull).open("rb") as file, pytest.raises(TelegramError):
            await bot.send_video_note(chat_id, file)

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_video_note(chat_id, "")
