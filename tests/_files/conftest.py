#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2026
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

from telegram import Animation, Audio, Document, PhotoSize, Sticker, Video
from tests.auxil.files import data_file
from tests.auxil.networking import expect_bad_request

FILE_ID = "5a3128a4d2a04750b5b58397f3b5e812"
FILE_UNIQUE_ID = "adc3145fd2e84d95b64d68eaa22aa33e"


def _with_bot(file, bot):
    file.set_bot(bot)
    return file


def _thumbnail(bot, *, width, height, file_size):
    return _with_bot(
        PhotoSize(
            file_id=f"thumbnail-{FILE_ID}",
            file_unique_id=f"thumbnail-{FILE_UNIQUE_ID}",
            width=width,
            height=height,
            file_size=file_size,
        ),
        bot,
    )


@pytest.fixture(scope="session")
def offline_animation(offline_bot):
    return _with_bot(
        Animation(
            file_id=FILE_ID,
            file_unique_id=FILE_UNIQUE_ID,
            width=320,
            height=180,
            duration=1,
            file_name="game.gif.webm",
            mime_type="video/mp4",
            file_size=5859,
            thumbnail=_thumbnail(offline_bot, width=320, height=180, file_size=5859),
        ),
        offline_bot,
    )


@pytest.fixture(scope="session")
async def animation(bot, chat_id):
    with data_file("game.gif").open("rb") as f, data_file("thumb.jpg").open("rb") as thumb:
        return (
            await bot.send_animation(chat_id, animation=f, read_timeout=50, thumbnail=thumb)
        ).animation


@pytest.fixture
def animation_file():
    with data_file("game.gif").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
async def animated_sticker(bot, chat_id):
    with data_file("telegram_animated_sticker.tgs").open("rb") as f:
        return (await bot.send_sticker(chat_id, sticker=f, read_timeout=50)).sticker


@pytest.fixture
def animated_sticker_file():
    with data_file("telegram_animated_sticker.tgs").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
def offline_audio(offline_bot):
    return _with_bot(
        Audio(
            file_id=FILE_ID,
            file_unique_id=FILE_UNIQUE_ID,
            duration=3,
            file_name="telegram.mp3",
            mime_type="audio/mpeg",
            file_size=122920,
            thumbnail=_thumbnail(offline_bot, width=50, height=50, file_size=1427),
        ),
        offline_bot,
    )


@pytest.fixture(scope="session")
async def audio(bot, chat_id):
    with data_file("telegram.mp3").open("rb") as f, data_file("thumb.jpg").open("rb") as thumb:
        return (await bot.send_audio(chat_id, audio=f, read_timeout=50, thumbnail=thumb)).audio


@pytest.fixture
def audio_file():
    with data_file("telegram.mp3").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
def offline_document(offline_bot):
    return _with_bot(
        Document(
            file_id=FILE_ID,
            file_unique_id=FILE_UNIQUE_ID,
            file_name="telegram.png",
            mime_type="image/png",
            file_size=12948,
            thumbnail=_thumbnail(offline_bot, width=300, height=300, file_size=8090),
        ),
        offline_bot,
    )


@pytest.fixture(scope="session")
async def document(bot, chat_id):
    with data_file("telegram.png").open("rb") as f:
        return (await bot.send_document(chat_id, document=f, read_timeout=50)).document


@pytest.fixture
def document_file():
    with data_file("telegram.png").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
def offline_photo(offline_photolist):
    return offline_photolist[-1]


@pytest.fixture(scope="session")
def photo(photolist):
    return photolist[-1]


@pytest.fixture
def photo_file():
    with data_file("telegram.jpg").open("rb") as f:
        yield f


@pytest.fixture(scope="session")
def offline_photolist(offline_bot):
    return (
        _with_bot(
            PhotoSize(
                file_id=f"small-{FILE_ID}",
                file_unique_id=f"small-{FILE_UNIQUE_ID}",
                width=90,
                height=90,
                file_size=1474,
            ),
            offline_bot,
        ),
        _with_bot(
            PhotoSize(
                file_id=FILE_ID,
                file_unique_id=FILE_UNIQUE_ID,
                width=800,
                height=800,
                file_size=29176,
            ),
            offline_bot,
        ),
    )


@pytest.fixture(scope="session")
async def photolist(bot, chat_id):
    async def func():
        with data_file("telegram.jpg").open("rb") as f:
            return (await bot.send_photo(chat_id, photo=f, read_timeout=50)).photo

    return await expect_bad_request(
        func, "Type of file mismatch", "Telegram did not accept the file."
    )


@pytest.fixture(scope="module")
def offline_sticker(offline_bot):
    return _with_bot(
        Sticker(
            file_id=FILE_ID,
            file_unique_id=FILE_UNIQUE_ID,
            width=510,
            height=512,
            is_animated=False,
            is_video=False,
            type=Sticker.REGULAR,
            file_size=39518,
            thumbnail=_thumbnail(offline_bot, width=319, height=320, file_size=21448),
            needs_repainting=True,
        ),
        offline_bot,
    )


@pytest.fixture(scope="module")
async def sticker(bot, chat_id):
    with data_file("telegram.webp").open("rb") as f:
        sticker = (await bot.send_sticker(chat_id, sticker=f, read_timeout=50)).sticker
        # necessary to properly test needs_repainting
        with sticker._unfrozen():
            sticker.needs_repainting = True
        return sticker


@pytest.fixture
def sticker_file():
    with data_file("telegram.webp").open("rb") as file:
        yield file


@pytest.fixture
def sticker_set_thumb_file():
    with data_file("sticker_set_thumb.png").open("rb") as file:
        yield file


@pytest.fixture(scope="session")
def offline_thumb(offline_photolist):
    return offline_photolist[0]


@pytest.fixture(scope="session")
def thumb(photolist):
    return photolist[0]


@pytest.fixture(scope="session")
def offline_video(offline_bot):
    return _with_bot(
        Video(
            file_id=FILE_ID,
            file_unique_id=FILE_UNIQUE_ID,
            width=360,
            height=640,
            duration=5,
            file_name="telegram.mp4",
            mime_type="video/mp4",
            file_size=326534,
            thumbnail=_thumbnail(offline_bot, width=180, height=320, file_size=1767),
            start_timestamp=3,
        ),
        offline_bot,
    )


@pytest.fixture(scope="session")
async def video(bot, chat_id):
    with data_file("telegram.mp4").open("rb") as f:
        return (await bot.send_video(chat_id, video=f, start_timestamp=3, read_timeout=50)).video


@pytest.fixture
def video_file():
    with data_file("telegram.mp4").open("rb") as f:
        yield f


@pytest.fixture
def video_sticker_file():
    with data_file("telegram_video_sticker.webm").open("rb") as f:
        yield f


@pytest.fixture(scope="module")
def video_sticker(bot, chat_id):
    with data_file("telegram_video_sticker.webm").open("rb") as f:
        return bot.send_sticker(chat_id, sticker=f, timeout=50).sticker


@pytest.fixture(scope="session")
async def real_live_photo(bot, chat_id):
    with (
        data_file("telegram.jpg").open("rb") as photo,
        data_file("telegram.mp4").open("rb") as video,
    ):
        return (
            await bot.send_live_photo(
                chat_id,
                live_photo=video,
                photo=photo,
                read_timeout=50,
            )
        ).live_photo
