#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2024
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Module to provide fixtures most of which are used in test_inputmedia.py."""
import pytest

from tests.auxil.files import data_file
from tests.auxil.networking import expect_bad_request


@pytest.fixture()
def animation_file():
    with data_file("game.gif").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
async def animation(bot, chat_id, aiolib):
    with data_file("game.gif").open("rb") as f, data_file("thumb.jpg").open("rb") as thumb:
        return (
            await bot.send_animation(chat_id, animation=f, read_timeout=50, thumbnail=thumb)
        ).animation


@pytest.fixture()
def audio_file():
    with data_file("telegram.mp3").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
async def audio(bot, chat_id, aiolib):
    with data_file("telegram.mp3").open("rb") as f, data_file("thumb.jpg").open("rb") as thumb:
        return (await bot.send_audio(chat_id, audio=f, read_timeout=50, thumbnail=thumb)).audio


@pytest.fixture()
def document_file():
    with data_file("telegram.png").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
async def document(bot, chat_id, aiolib):
    with data_file("telegram.png").open("rb") as f:
        return (await bot.send_document(chat_id, document=f, read_timeout=50)).document


@pytest.fixture()
def photo_file():
    with data_file("telegram.jpg").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
async def photolist(bot, chat_id, aiolib):
    async def func():
        with data_file("telegram.jpg").open("rb") as f:
            return (await bot.send_photo(chat_id, photo=f, read_timeout=50)).photo

    return await expect_bad_request(
        func, "Type of file mismatch", "Telegram did not accept the file."
    )


@pytest.fixture(scope="session")
def thumb(photolist):
    return photolist[0]


@pytest.fixture(scope="session")
def photo(photolist):
    return photolist[-1]


@pytest.fixture()
def video_file():
    with data_file("telegram.mp4").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
async def video(bot, chat_id, aiolib):
    with data_file("telegram.mp4").open("rb") as f:
        return (await bot.send_video(chat_id, video=f, read_timeout=50)).video


@pytest.fixture()
def video_sticker_file():
    with data_file("telegram_video_sticker.webm").open("rb") as f:
        yield f
