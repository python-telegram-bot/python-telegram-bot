#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import pytest
from flaky import flaky

from telegram import Sticker, TelegramError, PhotoSize, InputFile


@pytest.fixture(scope='function')
def photo_file():
    f = open(u'tests/data/telegram.jpg', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def _photo(bot, chat_id):
    with open('tests/data/telegram.jpg', 'rb') as f:
        return bot.send_photo(chat_id, photo=f, timeout=50).photo


@pytest.fixture(scope='class')
def thumb(_photo):
    return _photo[0]


@pytest.fixture(scope='class')
def photo(_photo):
    return _photo[1]


class TestPhoto(object):
    width = 300
    height = 300
    caption = u'<b>PhotoTest</b> - *Caption*'
    photo_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.jpg'
    file_size = 10209

    def test_creation(self, thumb, photo):
        # Make sure file has been uploaded.
        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id is not ''

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert thumb.file_id is not ''

    def test_expected_values(self, photo, thumb):
        assert photo.width == self.width
        assert photo.height == self.height
        assert photo.file_size == self.file_size
        assert thumb.width == 90
        assert thumb.height == 90
        assert thumb.file_size == 1478

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_photo_all_args(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(chat_id, photo_file, caption=self.caption,
                                 disable_notification=False, parse_mode='Markdown')

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('*', '')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_photo_parse_mode_markdown(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(chat_id, photo_file, caption=self.caption,
                                 parse_mode='Markdown')
        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('*', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_photo_parse_mode_html(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(chat_id, photo_file, caption=self.caption,
                                 parse_mode='HTML')
        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('<b>', '').replace('</b>', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, photo):
        new_file = bot.getFile(photo.file_id)

        assert new_file.file_size == photo.file_size
        assert new_file.file_id == photo.file_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('telegram.jpg')

        assert os.path.isfile('telegram.jpg') is True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_url_jpg_file(self, bot, chat_id, thumb, photo):
        message = bot.send_photo(chat_id, photo=self.photo_file_url)

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_url_png_file(self, bot, chat_id):
        message = bot.send_photo(photo='http://dummyimage.com/600x400/000/fff.png&text=telegram',
                                 chat_id=chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_url_gif_file(self, bot, chat_id):
        message = bot.send_photo(photo='http://dummyimage.com/600x400/000/fff.png&text=telegram',
                                 chat_id=chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_file_unicode_filename(self, bot, chat_id):
        """
        Regression test for https://github.com/python-telegram-bot/python-telegram-bot/issues/1202
        """
        with open(u'tests/data/测试.png', 'rb') as f:
            message = bot.send_photo(photo=f, chat_id=chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_bytesio_jpg_file(self, bot, chat_id):
        file_name = 'tests/data/telegram_no_standard_header.jpg'

        # raw image bytes
        raw_bytes = BytesIO(open(file_name, 'rb').read())
        input_file = InputFile(raw_bytes)
        assert input_file.mimetype == 'application/octet-stream'

        # raw image bytes with name info
        raw_bytes = BytesIO(open(file_name, 'rb').read())
        raw_bytes.name = file_name
        input_file = InputFile(raw_bytes)
        assert input_file.mimetype == 'image/jpeg'

        # send raw photo
        raw_bytes = BytesIO(open(file_name, 'rb').read())
        message = bot.send_photo(chat_id, photo=raw_bytes)
        photo = message.photo[-1]
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''
        assert isinstance(photo, PhotoSize)
        assert photo.width == 1280
        assert photo.height == 720
        assert photo.file_size == 33372

    def test_send_with_photosize(self, monkeypatch, bot, chat_id, photo):
        def test(_, url, data, **kwargs):
            return data['photo'] == photo.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_photo(photo=photo, chat_id=chat_id)
        assert message

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, photo):
        message = bot.send_photo(chat_id=chat_id, photo=photo.file_id)

        thumb, photo = message.photo

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

    def test_de_json(self, bot, photo):
        json_dict = {
            'file_id': photo.file_id,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size
        }
        json_photo = PhotoSize.de_json(json_dict, bot)

        assert json_photo.file_id == photo.file_id
        assert json_photo.width == self.width
        assert json_photo.height == self.height
        assert json_photo.file_size == self.file_size

    def test_to_dict(self, photo):
        photo_dict = photo.to_dict()

        assert isinstance(photo_dict, dict)
        assert photo_dict['file_id'] == photo.file_id
        assert photo_dict['width'] == photo.width
        assert photo_dict['height'] == photo.height
        assert photo_dict['file_size'] == photo.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_photo(chat_id=chat_id, photo=open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_photo(chat_id=chat_id, photo='')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_photo(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, photo):
        def test(*args, **kwargs):
            return args[1] == photo.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert photo.get_file()

    def test_equality(self, photo):
        a = PhotoSize(photo.file_id, self.width, self.height)
        b = PhotoSize(photo.file_id, self.width, self.height)
        c = PhotoSize(photo.file_id, 0, 0)
        d = PhotoSize('', self.width, self.height)
        e = Sticker(photo.file_id, self.width, self.height)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
