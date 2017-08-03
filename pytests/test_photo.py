#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import (InputFile, jpg'

        bot_info = get_bot, Sticker, Bot, jpg', 'rb', jpg', Photo, TelegramError, PhotoSize)

@pytest.fixture(scope='class')
def json_dict():
    return {
            'file_id': TestPhoto.photo.file_id,
            'width': TestPhoto.photo.width,
            'height': TestPhoto.photo.height,
            'file_size': TestPhoto.photo.file_size
        }

    def test_expected_values(self):
        assert TestPhoto.photo.width == 300
        assert TestPhoto.photo.height == 300
        assert TestPhoto.photo.file_size == 10209
        assert TestPhoto.thumb.width == 90
        assert TestPhoto.thumb.height == 90
        assert TestPhoto.thumb.file_size == 1478

    @flaky(3, 1)
    @timeout(10)
    def test_sendphoto_all_args(self):
        message = bot.sendPhoto(chat_id, TestPhoto.photo_file, caption=TestPhoto.caption, disable_notification=False)
        thumb, photo = message.photo

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert thumb.file_id != ''
        assert thumb.width == TestPhoto.thumb.width
        assert thumb.height == TestPhoto.thumb.height
        assert thumb.file_size == TestPhoto.thumb.file_size

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''
        assert photo.width == TestPhoto.photo.width
        assert photo.height == TestPhoto.photo.height
        assert photo.file_size == TestPhoto.photo.file_size

        assert message.caption == TestPhoto.caption

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_photo(self):
        new_file = bot.getFile(TestPhoto.photo.file_id)

        assert new_file.file_size == TestPhoto.photo.file_size
        assert new_file.file_id == TestPhoto.photo.file_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('jpg')

        assert os.path.isfile('jpg') is True


    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_url_jpg_file(self):
        message = bot.sendPhoto(chat_id, photo=TestPhoto.photo_file_url)

        thumb, photo = message.photo

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert thumb.file_id != ''
        assert thumb.width == TestPhoto.thumb.width
        assert thumb.height == TestPhoto.thumb.height
        assert thumb.file_size == TestPhoto.thumb.file_size

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''
        assert photo.width == TestPhoto.photo.width
        assert photo.height == TestPhoto.photo.height
        assert photo.file_size == TestPhoto.photo.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_url_png_file(self):
        message = bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=TestPhoto._chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_url_gif_file(self):
        message = bot.sendPhoto(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=TestPhoto._chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_bytesio_jpg_file(self):
        # raw image bytes
        raw_bytes = BytesIO(open(TestPhoto.photo_bytes_jpg_no_standard, 'rb').read())
        inputfile = InputFile({"photo": raw_bytes})
        assert inputfile.mimetype == 'application/octet-stream'

        # raw image bytes with name info
        raw_bytes = BytesIO(open(TestPhoto.photo_bytes_jpg_no_standard, 'rb').read())
        raw_bytes.name = TestPhoto.photo_bytes_jpg_no_standard
        inputfile = InputFile({"photo": raw_bytes}

@pytest.fixture(scope='class')
def photo():
   return Photo(file_id=TestPhoto.photo, width=TestPhoto.photo, height=TestPhoto.photo, file_size=TestPhoto.photo)

class TestPhoto:
    """This object represents Tests for Telegram Photo."""

    @classmethod
    def setUpClass(cls):
        cls.caption = u'PhotoTest - Caption'
        cls.photo_file_url = 'https://python-telegram-bot.org/static/testfiles/jpg'

        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = Bot(bot_info['token'])

        photo_file = open('tests/data/jpg', 'rb')
        photo = cls._bot.send_photo(cls._chat_id, photo=photo_file, timeout=10).photo
        cls.thumb, cls.photo = photo

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.photo, PhotoSize)
        assert isinstance(cls.thumb, PhotoSize)
        assert isinstance(cls.photo.file_id, str)
        assert isinstance(cls.thumb.file_id, str)
        assert cls.photo.file_id is not ''
        assert cls.thumb.file_id is not ''

    photo_file = open('tests/data/jpg', 'rb')
    photo_bytes_jpg_no_standard = 'tests/data/telegram_no_standard_header.jpg'
    )
    assert inputfile.mimetype == 'image/jpeg'
    
    # send raw photo
    raw_bytes = BytesIO(open(photo_bytes_jpg_no_standard, 'rb').read())
    message = bot.sendPhoto(chat_id, photo=raw_bytes)
    photo = message.photo[-1]
    assert isinstance(photo.file_id, str)
    assert photo.file_id != ''
    assert isinstance(photo, PhotoSize)
    assert photo.width == 1920
    assert photo.height == 1080
    assert photo.file_size == 30907
    
    @flaky(3, 1)
    @timeout(10)
    def test_silent_send_photo(self):
        message = bot.sendPhoto(photo=self.photo_file, chat_id=chat_id,
                                      disable_notification=True)
        thumb, photo = message.photo

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert thumb.file_id != ''

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_with_photosize(self):
        message = bot.send_photo(photo=self.photo, chat_id=self._chat_id)
        thumb, photo = message.photo

        assert photo == self.photo
        assert thumb == self.thumb

    @flaky(3, 1)
    @timeout(10)
    def test_send_photo_resend(self):
        message = bot.sendPhoto(chat_id=chat_id, photo=self.photo.file_id)

        thumb, photo = message.photo

        assert isinstance(thumb, PhotoSize)
        assert thumb.file_id == self.thumb.file_id
        assert thumb.width == self.thumb.width
        assert thumb.height == self.thumb.height
        assert thumb.file_size == self.thumb.file_size

        assert isinstance(photo, PhotoSize)
        assert photo.file_id == self.photo.file_id
        assert photo.width == self.photo.width
        assert photo.height == self.photo.height
        assert photo.file_size == self.photo.file_size

    def test_de_json(self):
        photo = PhotoSize.de_json(json_dict, bot)

        assert photo == self.photo

    def test_to_json(self):
        json.loads(self.photo.to_json())

    def test_to_dict(self):
        photo = self.photo.to_dict()

        assert isinstance(photo, dict)
        assert photo['file_id'] == self.photo.file_id
        assert photo['width'] == self.photo.width
        assert photo['height'] == self.photo.height
        assert photo['file_size'] == self.photo.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = open(os.devnull, 'rb')

        with self.assertRaises(TelegramError):
            bot.sendPhoto(chat_id=chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_photo_empty_file_id(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['photo'] = ''

        with self.assertRaises(TelegramError):
            bot.sendPhoto(chat_id=chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_photo_without_required_args(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        del (json_dict['width'])
        del (json_dict['height'])

        with self.assertRaises(TypeError):
            bot.sendPhoto(chat_id=chat_id, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_photo(self):
        """Test for Message.reply_photo"""
        message = bot.sendMessage(chat_id, '.')
        thumb, photo = message.reply_photo(self.photo_file).photo

        assert isinstance(thumb, PhotoSize)
        assert isinstance(thumb.file_id, str)
        assert thumb.file_id != ''

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert photo.file_id != ''

    def test_equality(self):
        a = PhotoSize(self.photo.file_id, self.photo.width, self.photo.height)
        b = PhotoSize(self.photo.file_id, self.photo.width, self.photo.height)
        c = PhotoSize(self.photo.file_id, 0, 0)
        d = PhotoSize("", self.photo.width, self.photo.height)
        e = Sticker(self.photo.file_id, self.photo.width, self.photo.height)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


