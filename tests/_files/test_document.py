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

from telegram import Bot, Document, InputFile, MessageEntity, PhotoSize, Voice
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.auxil.bot_method_checks import (
    check_defaults_handling,
    check_shortcut_call,
    check_shortcut_signature,
)
from tests.auxil.deprecations import check_thumb_deprecation_warnings_for_args_and_attrs
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture()
def document_file():
    with data_file("telegram.png").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def document(bot, chat_id):
    with data_file("telegram.png").open("rb") as f:
        return (await bot.send_document(chat_id, document=f, read_timeout=50)).document


class TestDocumentBase:
    caption = "DocumentTest - *Caption*"
    document_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.gif"
    file_size = 12948
    mime_type = "image/png"
    file_name = "telegram.png"
    thumb_file_size = 8090
    thumb_width = 300
    thumb_height = 300
    document_file_id = "5a3128a4d2a04750b5b58397f3b5e812"
    document_file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"


class TestDocumentWithoutRequest(TestDocumentBase):
    def test_slot_behaviour(self, document):
        for attr in document.__slots__:
            assert getattr(document, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(document)) == len(set(mro_slots(document))), "duplicate slot"

    def test_creation(self, document):
        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert isinstance(document.file_unique_id, str)
        assert document.file_id
        assert document.file_unique_id

    def test_expected_values(self, document):
        assert document.file_size == self.file_size
        assert document.mime_type == self.mime_type
        assert document.file_name == self.file_name
        assert document.thumbnail.file_size == self.thumb_file_size
        assert document.thumbnail.width == self.thumb_width
        assert document.thumbnail.height == self.thumb_height

    def test_thumb_property_deprecation_warning(self, recwarn):
        document = Document(file_id="file_id", file_unique_id="file_unique_id", thumb=object())
        assert document.thumb is document.thumbnail
        check_thumb_deprecation_warnings_for_args_and_attrs(recwarn, __file__)

    def test_de_json(self, bot, document):
        json_dict = {
            "file_id": self.document_file_id,
            "file_unique_id": self.document_file_unique_id,
            "thumbnail": document.thumbnail.to_dict(),
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        test_document = Document.de_json(json_dict, bot)
        assert test_document.api_kwargs == {}

        assert test_document.file_id == self.document_file_id
        assert test_document.file_unique_id == self.document_file_unique_id
        assert test_document.thumbnail == document.thumbnail
        assert test_document.file_name == self.file_name
        assert test_document.mime_type == self.mime_type
        assert test_document.file_size == self.file_size

    def test_to_dict(self, document):
        document_dict = document.to_dict()

        assert isinstance(document_dict, dict)
        assert document_dict["file_id"] == document.file_id
        assert document_dict["file_unique_id"] == document.file_unique_id
        assert document_dict["file_name"] == document.file_name
        assert document_dict["mime_type"] == document.mime_type
        assert document_dict["file_size"] == document.file_size

    def test_equality(self, document):
        a = Document(document.file_id, document.file_unique_id)
        b = Document("", document.file_unique_id)
        d = Document("", "")
        e = Voice(document.file_id, document.file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_error_send_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_document(chat_id=chat_id)

    @pytest.mark.parametrize("disable_content_type_detection", [True, False, None])
    async def test_send_with_document(
        self, monkeypatch, bot, chat_id, document, disable_content_type_detection
    ):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            data = request_data.parameters
            type_detection = (
                data.get("disable_content_type_detection") == disable_content_type_detection
            )
            return data["document"] == document.file_id and type_detection

        monkeypatch.setattr(bot.request, "post", make_assertion)

        message = await bot.send_document(
            document=document,
            chat_id=chat_id,
            disable_content_type_detection=disable_content_type_detection,
        )

        assert message

    @pytest.mark.parametrize("local_mode", [True, False])
    async def test_send_document_local_files(self, monkeypatch, bot, chat_id, local_mode):
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
                        data.get("document") == expected and data.get("thumbnail") == expected
                    )
                else:
                    test_flag = isinstance(data.get("document"), InputFile) and isinstance(
                        data.get("thumbnail"), InputFile
                    )

            monkeypatch.setattr(bot, "_post", make_assertion)
            await bot.send_document(chat_id, file, thumbnail=file)
            assert test_flag
        finally:
            bot._local_mode = False

    async def test_send_document_with_local_files_throws_error_with_different_thumb_and_thumbnail(
        self, bot, chat_id
    ):
        file = data_file("telegram.jpg")
        different_file = data_file("telegram_no_standard_header.jpg")

        with pytest.raises(ValueError, match="different entities as 'thumb' and 'thumbnail'"):
            await bot.send_document(chat_id, file, thumbnail=file, thumb=different_file)

    async def test_get_file_instance_method(self, monkeypatch, document):
        async def make_assertion(*_, **kwargs):
            return kwargs["file_id"] == document.file_id

        assert check_shortcut_signature(Document.get_file, Bot.get_file, ["file_id"], [])
        assert await check_shortcut_call(document.get_file, document.get_bot(), "get_file")
        assert await check_defaults_handling(document.get_file, document.get_bot())

        monkeypatch.setattr(document.get_bot(), "get_file", make_assertion)
        assert await document.get_file()


class TestDocumentWithRequest(TestDocumentBase):
    async def test_error_send_empty_file(self, bot, chat_id):
        with Path(os.devnull).open("rb") as f, pytest.raises(TelegramError):
            await bot.send_document(chat_id=chat_id, document=f)

    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_document(chat_id=chat_id, document="")

    async def test_get_and_download(self, bot, document, chat_id):
        path = Path("telegram.png")
        if path.is_file():
            path.unlink()

        new_file = await bot.get_file(document.file_id)

        assert new_file.file_size == document.file_size
        assert new_file.file_unique_id == document.file_unique_id
        assert new_file.file_path.startswith("https://")

        await new_file.download_to_drive("telegram.png")

        assert path.is_file()

    async def test_send_resend(self, bot, chat_id, document):
        message = await bot.send_document(chat_id=chat_id, document=document.file_id)
        assert message.document == document

    async def test_send_all_args(self, bot, chat_id, document_file, document, thumb_file):
        message = await bot.send_document(
            chat_id,
            document=document_file,
            caption=self.caption,
            disable_notification=False,
            protect_content=True,
            filename="telegram_custom.png",
            parse_mode="Markdown",
            thumbnail=thumb_file,
        )

        assert isinstance(message.document, Document)
        assert isinstance(message.document.file_id, str)
        assert message.document.file_id
        assert isinstance(message.document.file_unique_id, str)
        assert message.document.file_unique_id
        assert isinstance(message.document.thumbnail, PhotoSize)
        assert message.document.file_name == "telegram_custom.png"
        assert message.document.mime_type == document.mime_type
        assert message.document.file_size == document.file_size
        assert message.caption == self.caption.replace("*", "")
        assert message.document.thumbnail.width == self.thumb_width
        assert message.document.thumbnail.height == self.thumb_height
        assert message.has_protected_content

    async def test_send_url_gif_file(self, bot, chat_id):
        message = await bot.send_document(chat_id, self.document_file_url)

        document = message.document

        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert document.file_id
        assert isinstance(message.document.file_unique_id, str)
        assert message.document.file_unique_id
        assert isinstance(document.thumbnail, PhotoSize)
        assert document.file_name == "telegram.gif"
        assert document.mime_type == "image/gif"
        assert document.file_size == 3878

    @pytest.mark.parametrize("default_bot", [{"protect_content": True}], indirect=True)
    async def test_send_document_default_protect_content(self, chat_id, default_bot, document):
        tasks = asyncio.gather(
            default_bot.send_document(chat_id, document),
            default_bot.send_document(chat_id, document, protect_content=False),
        )
        protected, unprotected = await tasks
        assert protected.has_protected_content
        assert not unprotected.has_protected_content

    async def test_send_document_caption_entities(self, bot, chat_id, document):
        test_string = "Italic Bold Code"
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_document(
            chat_id, document, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == tuple(entities)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_document_default_parse_mode_1(self, default_bot, chat_id, document):
        test_string = "Italic Bold Code"
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_document(chat_id, document, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_document_default_parse_mode_2(self, default_bot, chat_id, document):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_document(
            chat_id, document, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.parametrize("default_bot", [{"parse_mode": "Markdown"}], indirect=True)
    async def test_send_document_default_parse_mode_3(self, default_bot, chat_id, document):
        test_markdown_string = "_Italic_ *Bold* `Code`"

        message = await default_bot.send_document(
            chat_id, document, caption=test_markdown_string, parse_mode="HTML"
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
    async def test_send_document_default_allow_sending_without_reply(
        self, default_bot, chat_id, document, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, "test")
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_document(
                chat_id,
                document,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_document(
                chat_id, document, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match="message not found"):
                await default_bot.send_document(
                    chat_id, document, reply_to_message_id=reply_to_message.message_id
                )
