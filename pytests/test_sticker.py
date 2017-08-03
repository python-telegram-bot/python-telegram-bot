#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import os

import pytest
from flaky import flaky
from future.utils import PY2

from telegram import Sticker, PhotoSize, TelegramError


@pytest.fixture()
def sticker_file():
    f = open('tests/data/telegram.webp', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def sticker(bot, chat_id):
    with open('tests/data/telegram.webp', 'rb') as f:
        return bot.send_sticker(chat_id, sticker=f, timeout=10).sticker


class TestSticker:
    # sticker_file_url = "https://python-telegram-bot.org/static/testfiles/telegram.webp"
    # Serving sticker from gh since our server sends wrong content_type
    sticker_file_url = ("https://github.com/python-telegram-bot/python-telegram-bot/blob/master"
                        "/tests/data/telegram.webp?raw=true")

    emoji = '💪'
    width = 510
    height = 512
    file_size = 39518

    def test_creation(self, sticker):
        # Make sure file has been uploaded.
        assert isinstance(sticker, Sticker)
        assert isinstance(sticker.file_id, str)
        assert sticker.file_id != ''
        assert isinstance(sticker.thumb, PhotoSize)
        assert isinstance(sticker.thumb.file_id, str)
        assert sticker.thumb.file_id != ''

    def test_expected_values(self, sticker):
        assert sticker.width == 510
        assert sticker.height == 512
        assert sticker.file_size == 39518
        assert sticker.thumb.width == 90
        assert sticker.thumb.height == 90
        assert sticker.thumb.file_size == 3672

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_sticker_all_args(self, bot, chat_id, sticker_file, sticker):
        message = bot.send_sticker(chat_id, sticker=sticker_file, disable_notification=False)

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download_sticker(self, bot, sticker):
        new_file = bot.get_file(sticker.file_id)

        assert new_file.file_size == sticker.file_size
        assert new_file.file_id == sticker.file_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('telegram.webp')

        assert os.path.isfile('telegram.webp') is True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_sticker_resend(self, bot, chat_id, sticker):
        message = bot.sendSticker(chat_id=chat_id, sticker=sticker.file_id)

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_sticker_on_server_emoji(self, bot, chat_id):
        server_file_id = "CAADAQADHAADyIsGAAFZfq1bphjqlgI"
        message = bot.sendSticker(chat_id=chat_id, sticker=server_file_id)
        sticker = message.sticker
        if PY2:
            assert sticker.emoji == self.emoji.decode('utf-8')
        else:
            assert sticker.emoji == self.emoji

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_sticker_from_url(self, bot, chat_id):
        message = bot.sendSticker(chat_id=chat_id, sticker=self.sticker_file_url)
        sticker = message.sticker

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    def test_de_json(self, bot, sticker):
        json_dict = {
            'file_id': sticker.file_id,
            'width': self.width,
            'height': self.height,
            'thumb': sticker.thumb.to_dict(),
            'emoji': self.emoji,
            'file_size': self.file_size
        }
        json_sticker = Sticker.de_json(json_dict, bot)

        assert json_sticker.file_id == sticker.file_id
        assert json_sticker.width == self.width
        assert json_sticker.height == self.height
        assert json_sticker.emoji == self.emoji
        assert json_sticker.file_size == self.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_sticker_with_sticker(self, bot, chat_id, sticker):
        message = bot.send_sticker(chat_id, sticker=sticker)

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    def test_to_json(self, sticker):
        json.loads(sticker.to_json())

    def test_to_dict(self, sticker):
        sticker_dict = sticker.to_dict()

        assert isinstance(sticker_dict, dict)
        assert sticker_dict['file_id'] == sticker.file_id
        assert sticker_dict['width'] == sticker.width
        assert sticker_dict['height'] == sticker.height
        assert sticker_dict['file_size'] == sticker.file_size
        assert sticker_dict['thumb'] == sticker.thumb.to_dict()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_sticker_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.sendSticker(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_sticker_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.sendSticker(chat_id, '')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_sticker_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.sendSticker(chat_id)

    def test_equality(self, sticker):
        a = Sticker(sticker.file_id, self.width, self.height)
        b = Sticker(sticker.file_id, self.width, self.height)
        c = Sticker(sticker.file_id, 0, 0)
        d = Sticker("", self.width, self.height)
        e = PhotoSize(sticker.file_id, self.width, self.height)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
