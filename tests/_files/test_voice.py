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

from telegram import Audio, Bot, InputFile, MessageEntity, Voice
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture()
def voice_file():
    with data_file("telegram.ogg").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def voice(bot, chat_id):
    with data_file("telegram.ogg").open("rb") as f:
        return (await bot.send_voice(chat_id, voice=f, read_timeout=50)).voice


class TestVoiceBase:
    duration = 3
    mime_type = "audio/ogg"
    file_size = 9199
    caption = "Test *voice*"
    voice_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.ogg"
    voice_file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    voice_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"


class TestVoiceWithoutRequest(TestVoiceBase):
    def test_slot_behaviour(self, voice):
        for attr in voice.__slots__:
            assert getattr(voice, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(voice)) == len(set(mro_slots(voice))), "duplicate slot"

    async def test_creation(self, voice):
        # Make sure file has been uploaded.
        assert isinstance(voice, Voice)
        assert isinstance(voice.file_id, str)
        assert isinstance(voice.file_unique_id, str)
        assert voice.file_id
        assert voice.file_unique_id

    def test_expected_values(self, voice):
        assert voice.duration == self.duration
        assert voice.mime_type == self.mime_type
        assert voice.file_size == self.file_size

    def test_de_json(self, bot):
        json_dict = {
            "file_id": self.voice_file_id,
            "file_unique_id": self.voice_file_unique_id,
            "duration": self.duration,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        json_voice = Voice.de_json(json_dict, bot)
        assert json_voice.api_kwargs == {}

        assert json_voice.file_id == self.voice_file_id
        assert json_voice.file_unique_id == self.voice_file_unique_id
        assert json_voice.duration == self.duration
        assert json_voice.mime_type == self.mime_type
        assert json_voice.file_size == self.file_size

    def test_to_dict(self, voice):
        voice_dict = voice.to_dict()

        assert isinstance(voice_dict, dict)
        assert voice_dict["file_id"] == voice.file_id
        assert voice_dict["file_unique_id"] == voice.file_unique_id
        assert voice_dict["duration"] == voice.duration
        assert voice_dict["mime_type"] == voice.mime_type
        assert voice_dict["file_size"] == voice.file_size

    def test_equality(self, voice):
        a = Voice(voice.file_id, voice.file_unique_id, self.duration)
        b = Voice("", voice.file_unique_id, self.duration)
        c = Voice(voice.file_id, voice.file_unique_id, 0)
        d = Voice("", "", self.duration)
        e = Audio(voice.file_id, voice.file_unique_id, self.duration)

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
            await bot.sendVoice(chat_id)

    async def test_send_voice_custom_filename(self, bot, chat_id, voice_file, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return list(request_data.multipart_data.values())[0][0] == "custom_filename"

        monkeypatch.setattr(bot.request, "post", make_assertion)

        assert await bot.send_voice(chat_id, voice_file, filename="custom_filename")

    async def test_send_with_voice(self, monkeypatch, bot, chat_id, voice):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters["voice"] == voice.file_id

        monkeypatch.setattr(bot.request, "post", make_assertion)
        assert await bot.send_voice(chat_id, voice=voice)

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_voice_local_files(self, monkeypatch, bot, chat_id, local_mode):
        try:
            bot._local_mode = local_mode
            # For just test that the correct paths are passed as we have no local bot API set up
            test_flag = False
            file = data_file("telegram.jpg")
            expected = file.as_uri()

            async def make_assertion(_, data, *args, **kwargs):
                nonlocal test_flag
                if local_mode:
                    test_flag = data.get("voice") == expected
                else:
                    test_flag = isinstance(data.get("voice"), InputFile)

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_voice(chat_id, file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_get_file_instance_method(self, monkeypatch, voice):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == voice.file_id

        assert check_shortcut_signature(Voice.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(voice.get_file, voice.get_bot(), "get_file")
        assert await check_defaults_handling(voice.get_file, voice.get_bot())

        monkeypatch.setattr(voice.get_bot(), "get_file", make_assertion)
        assert await voice.get_file()


class TestVoiceWithRequest(TestVoiceBase):
    async def test_send_all_args(self, bot, chat_id, voice_file, voice):
        message = await bot.send_voice(
            chat_id,
            voice_file,
            duration=self.duration,
            caption=self.caption,
            disable_notification=False,
            protect_content=True,
            parse_mode="Markdown",
        )

        assert isinstance(message.voice, Voice)
        assert isinstance(message.voice.file_id, str)
        assert isinstance(message.voice.file_unique_id, str)
        assert message.voice.file_id
        assert message.voice.file_unique_id
        assert message.voice.duration == voice.duration
        assert message.voice.mime_type == voice.mime_type
        assert message.voice.file_size == voice.file_size
        assert message.caption == self.caption.replace("*", "")
        assert message.has_protected_content

    async def test_get_and_download(self, bot, voice, chat_id):
        path = Path("telegram.ogg")
        if path.is_file():
            path.unlink()

        new_file = await bot.get_file(voice.file_id)

        assert new_file.file_size == voice.file_size
        assert new_file.file_unique_id == voice.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive("telegram.ogg")

        assert path.is_file()

    async def test_send_ogg_url_file(self, bot, chat_id, voice):
        message = await bot.sendVoice(chat_id, self.voice_file_url, duration=self.duration)

        assert isinstance(message.voice, Voice)
        assert isinstance(message.voice.file_id, str)
        assert isinstance(message.voice.file_unique_id, str)
        assert message.voice.file_id
        assert message.voice.file_unique_id
        assert message.voice.duration == voice.duration
        assert message.voice.mime_type == voice.mime_type
        assert message.voice.file_size == voice.file_size

    async def test_resend(self, bot, chat_id, voice):
        message = await bot.sendVoice(chat_id, voice.file_id)

        assert message.voice == voice

    async def test_send_voice_caption_entities(self, bot, chat_id, voice_file):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_voice(
            chat_id, voice_file, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_voice_default_parse_mode_1(self, default_bot, chat_id, voice):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_voice(chat_id, voice, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_voice_default_parse_mode_2(self, default_bot, chat_id, voice):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_voice(
            chat_id, voice, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_voice_default_parse_mode_3(self, default_bot, chat_id, voice):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_voice(
            chat_id, voice, caption=test_markdown_string, parse_mode="HTML"
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_voice_default_protect_content(self, chat_id, default_bot, voice):
        tasks = asyncio.gather(
            default_bot.send_voice(chat_id, voice),
            default_bot.send_voice(chat_id, voice, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    @pytest.mark.parametrize(
        ("default_bot", "custom"),
        [
            ({"allow_sending_without_reply": True}, None),
            ({"allow_sending_without_reply": False}, None),
            ({"allow_sending_without_reply": False}, True),
        ],
        indirect=["default_bot"],
    )
    async def test_send_voice_default_allow_sending_without_reply(
        self, default_bot, chat_id, voice, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_voice(
                chat_id,
                voice,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_voice(
                chat_id, voice, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="message not found"):
                await default_bot.send_voice(
                    chat_id, voice, reply_to_message_id=reply_to_message.message_id
                )

    async def test_error_send_empty_file(self, bot, chat_id):
        with Path(os.devnull).open("rb") as file, pytest.raises(TelegramError):
            await bot.sendVoice(chat_id, file)

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.sendVoice(chat_id, "")
