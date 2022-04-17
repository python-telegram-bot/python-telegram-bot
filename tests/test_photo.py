#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import os
from io import BytesIO
from pathlib import Path

import pytest
from flaky import flaky

from telegram import Sticker, PhotoSize, InputFile, MessageEntity, Bot
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.conftest import (
    expect_bad_request,
    check_shortcut_call,
    check_shortcut_signature,
    check_defaults_handling,
    data_file,
)


@pytest.fixture(scope='function')
def photo_file():
    f = data_file('telegram.jpg').open('rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
@pytest.mark.asyncio
async def _photo(bot, chat_id):
    async def func():
        with data_file('telegram.jpg').open('rb') as f:
            photo = (await bot.send_photo(chat_id, photo=f, read_timeout=50)).photo
            return photo

    return await expect_bad_request(
        func, 'Type of file mismatch', 'Telegram did not accept the file.'
    )


@pytest.fixture(scope='class')
def thumb(_photo):
    return _photo[0]


@pytest.fixture(scope='class')
def photo(_photo):
    return _photo[-1]


class TestPhoto:
    width = 800
    height = 800
    caption = '<b>PhotoTest</b> - *Caption*'
    photo_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram_new.jpg'
    # For some reason the file size is not the same after switching to httpx
    # so we accept three different sizes here. Shouldn't be too much
    file_size = [29176, 27662]

    def test_slot_behaviour(self, photo, mro_slots):
        for attr in photo.__slots__:
            assert getattr(photo, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(photo)) == len(set(mro_slots(photo))), "duplicate slot"

    def test_creation(self, thumb, photo):
        # Make sure file has been uploaded.
        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert isinstance(thumb.file_unique_id, str)
        assert thumb.file_id != ''
        assert thumb.file_unique_id != ''

    def test_expected_values(self, photo, thumb):
        assert photo.width == self.width
        assert photo.height == self.height
        assert photo.file_size in self.file_size
        assert thumb.width == 90
        assert thumb.height == 90
        assert thumb.file_size == 1477

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_photo_all_args(self, bot, chat_id, photo_file, thumb, photo):
        message = await bot.send_photo(
            chat_id,
            photo_file,
            caption=self.caption,
            disable_notification=False,
            protect_content=True,
            parse_mode='Markdown',
        )

        assert isinstance(message.photo[-2], PhotoSize)
        assert isinstance(message.photo[-2].file_id, str)
        assert isinstance(message.photo[-2].file_unique_id, str)
        assert message.photo[-2].file_id != ''
        assert message.photo[-2].file_unique_id != ''

        assert isinstance(message.photo[-1], PhotoSize)
        assert isinstance(message.photo[-1].file_id, str)
        assert isinstance(message.photo[-1].file_unique_id, str)
        assert message.photo[-1].file_id != ''
        assert message.photo[-1].file_unique_id != ''

        assert message.caption == TestPhoto.caption.replace('*', '')
        assert message.has_protected_content

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_photo_custom_filename(self, bot, chat_id, photo_file, monkeypatch):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return list(request_data.multipart_data.values())[0][0] == 'custom_filename'

        monkeypatch.setattr(bot.request, 'post', make_assertion)

        assert await bot.send_photo(chat_id, photo_file, filename='custom_filename')

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_photo_parse_mode_markdown(self, bot, chat_id, photo_file, thumb, photo):
        message = await bot.send_photo(
            chat_id, photo_file, caption=self.caption, parse_mode='Markdown'
        )
        assert isinstance(message.photo[-2], PhotoSize)
        assert isinstance(message.photo[-2].file_id, str)
        assert isinstance(message.photo[-2].file_unique_id, str)
        assert message.photo[-2].file_id != ''
        assert message.photo[-2].file_unique_id != ''

        assert isinstance(message.photo[-1], PhotoSize)
        assert isinstance(message.photo[-1].file_id, str)
        assert isinstance(message.photo[-1].file_unique_id, str)
        assert message.photo[-1].file_id != ''
        assert message.photo[-1].file_unique_id != ''

        assert message.caption == TestPhoto.caption.replace('*', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_photo_parse_mode_html(self, bot, chat_id, photo_file, thumb, photo):
        message = await bot.send_photo(
            chat_id, photo_file, caption=self.caption, parse_mode='HTML'
        )
        assert isinstance(message.photo[-2], PhotoSize)
        assert isinstance(message.photo[-2].file_id, str)
        assert isinstance(message.photo[-2].file_unique_id, str)
        assert message.photo[-2].file_id != ''
        assert message.photo[-2].file_unique_id != ''

        assert isinstance(message.photo[-1], PhotoSize)
        assert isinstance(message.photo[-1].file_id, str)
        assert isinstance(message.photo[-1].file_unique_id, str)
        assert message.photo[-1].file_id != ''
        assert message.photo[-1].file_unique_id != ''

        assert message.caption == TestPhoto.caption.replace('<b>', '').replace('</b>', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_photo_caption_entities(self, bot, chat_id, photo_file, thumb, photo):
        test_string = 'Italic Bold Code'
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_photo(
            chat_id, photo_file, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == entities

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_photo_default_parse_mode_1(
        self, default_bot, chat_id, photo_file, thumb, photo
    ):
        test_string = 'Italic Bold Code'
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_photo(chat_id, photo_file, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_photo_default_parse_mode_2(
        self, default_bot, chat_id, photo_file, thumb, photo
    ):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_photo(
            chat_id, photo_file, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_photo_default_parse_mode_3(
        self, default_bot, chat_id, photo_file, thumb, photo
    ):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_photo(
            chat_id, photo_file, caption=test_markdown_string, parse_mode='HTML'
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.asyncio
    @pytest.mark.parametrize('default_bot', [{'protect_content': True}], indirect=True)
    async def test_send_photo_default_protect_content(self, chat_id, default_bot, photo):
        protected = await default_bot.send_photo(chat_id, photo)
        assert protected.has_protected_content
        unprotected = await default_bot.send_photo(chat_id, photo, protect_content=False)
        assert not unprotected.has_protected_content

    @pytest.mark.asyncio
    async def test_send_photo_local_files(self, monkeypatch, bot, chat_id):
        # For just test that the correct paths are passed as we have no local bot API set up
        test_flag = False
        file = data_file('telegram.jpg')
        expected = file.as_uri()

        async def make_assertion(_, data, *args, **kwargs):
            nonlocal test_flag
            test_flag = data.get('photo') == expected

        monkeypatch.setattr(bot, '_post', make_assertion)
        await bot.send_photo(chat_id, file)
        assert test_flag

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    @pytest.mark.asyncio
    async def test_send_photo_default_allow_sending_without_reply(
        self, default_bot, chat_id, photo_file, thumb, photo, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, 'test')
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_photo(
                chat_id,
                photo_file,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_photo(
                chat_id, photo_file, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                await default_bot.send_photo(
                    chat_id, photo_file, reply_to_message_id=reply_to_message.message_id
                )

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_get_and_download(self, bot, photo):
        path = Path('telegram.jpg')
        if path.is_file():
            path.unlink()

        new_file = await bot.getFile(photo.file_id)

        assert new_file.file_size == photo.file_size
        assert new_file.file_unique_id == photo.file_unique_id
        assert new_file.file_path.startswith('https://') is True

        await new_file.download('telegram.jpg')

        assert path.is_file()

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_url_jpg_file(self, bot, chat_id, thumb, photo):
        message = await bot.send_photo(chat_id, photo=self.photo_file_url)

        assert isinstance(message.photo[-2], PhotoSize)
        assert isinstance(message.photo[-2].file_id, str)
        assert isinstance(message.photo[-2].file_unique_id, str)
        assert message.photo[-2].file_id != ''
        assert message.photo[-2].file_unique_id != ''

        assert isinstance(message.photo[-1], PhotoSize)
        assert isinstance(message.photo[-1].file_id, str)
        assert isinstance(message.photo[-1].file_unique_id, str)
        assert message.photo[-1].file_id != ''
        assert message.photo[-1].file_unique_id != ''

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_url_png_file(self, bot, chat_id):
        message = await bot.send_photo(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=chat_id
        )

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_url_gif_file(self, bot, chat_id):
        message = await bot.send_photo(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=chat_id
        )

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_file_unicode_filename(self, bot, chat_id):
        """
        Regression test for https://github.com/python-telegram-bot/python-telegram-bot/issues/1202
        """
        with data_file('测试.png').open('rb') as f:
            message = await bot.send_photo(photo=f, chat_id=chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_bytesio_jpg_file(self, bot, chat_id):
        filepath = data_file('telegram_no_standard_header.jpg')

        # raw image bytes
        raw_bytes = BytesIO(filepath.read_bytes())
        input_file = InputFile(raw_bytes)
        assert input_file.mimetype == 'application/octet-stream'

        # raw image bytes with name info
        raw_bytes = BytesIO(filepath.read_bytes())
        raw_bytes.name = str(filepath)
        input_file = InputFile(raw_bytes)
        assert input_file.mimetype == 'image/jpeg'

        # send raw photo
        raw_bytes = BytesIO(filepath.read_bytes())
        message = await bot.send_photo(chat_id, photo=raw_bytes)
        photo = message.photo[-1]
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''
        assert isinstance(photo, PhotoSize)
        assert photo.width == 1280
        assert photo.height == 720
        assert photo.file_size == 33372

    @pytest.mark.asyncio
    async def test_send_with_photosize(self, monkeypatch, bot, chat_id, photo):
        async def make_assertion(url, request_data: RequestData, *args, **kwargs):
            return request_data.json_parameters['photo'] == photo.file_id

        monkeypatch.setattr(bot.request, 'post', make_assertion)
        message = await bot.send_photo(photo=photo, chat_id=chat_id)
        assert message

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_resend(self, bot, chat_id, photo, thumb):
        message = await bot.send_photo(chat_id=chat_id, photo=photo.file_id)

        assert isinstance(message.photo[-2], PhotoSize)
        assert isinstance(message.photo[-2].file_id, str)
        assert isinstance(message.photo[-2].file_unique_id, str)
        assert message.photo[-2].file_id != ''
        assert message.photo[-2].file_unique_id != ''

        assert isinstance(message.photo[-1], PhotoSize)
        assert isinstance(message.photo[-1].file_id, str)
        assert isinstance(message.photo[-1].file_unique_id, str)
        assert message.photo[-1].file_id != ''
        assert message.photo[-1].file_unique_id != ''

    def test_de_json(self, bot, photo):
        json_dict = {
            'file_id': photo.file_id,
            'file_unique_id': photo.file_unique_id,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size,
        }
        json_photo = PhotoSize.de_json(json_dict, bot)

        assert json_photo.file_id == photo.file_id
        assert json_photo.file_unique_id == photo.file_unique_id
        assert json_photo.width == self.width
        assert json_photo.height == self.height
        assert json_photo.file_size == self.file_size

    def test_to_dict(self, photo):
        photo_dict = photo.to_dict()

        assert isinstance(photo_dict, dict)
        assert photo_dict['file_id'] == photo.file_id
        assert photo_dict['file_unique_id'] == photo.file_unique_id
        assert photo_dict['width'] == photo.width
        assert photo_dict['height'] == photo.height
        assert photo_dict['file_size'] == photo.file_size

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_photo(chat_id=chat_id, photo=open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_photo(chat_id=chat_id, photo='')

    @pytest.mark.asyncio
    async def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_photo(chat_id=chat_id)

    @pytest.mark.asyncio
    async def test_get_file_instance_method(self, monkeypatch, photo):
        async def make_assertion(*_, **kwargs):
            return kwargs['file_id'] == photo.file_id

        assert check_shortcut_signature(PhotoSize.get_file, Bot.get_file, ['file_id'], [])
        assert await check_shortcut_call(photo.get_file, photo.get_bot(), 'get_file')
        assert await check_defaults_handling(photo.get_file, photo.get_bot())

        monkeypatch.setattr(photo.get_bot(), 'get_file', make_assertion)
        assert await photo.get_file()

    def test_equality(self, photo):
        a = PhotoSize(photo.file_id, photo.file_unique_id, self.width, self.height)
        b = PhotoSize('', photo.file_unique_id, self.width, self.height)
        c = PhotoSize(photo.file_id, photo.file_unique_id, 0, 0)
        d = PhotoSize('', '', self.width, self.height)
        e = Sticker(photo.file_id, photo.file_unique_id, self.width, self.height, False, False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
