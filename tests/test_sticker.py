#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
from time import sleep

import pytest
from flaky import flaky
from future.utils import PY2

from telegram import Sticker, PhotoSize, TelegramError, StickerSet, Audio, MaskPosition


@pytest.fixture(scope='function')
def sticker_file():
    f = open('tests/data/telegram.webp', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def sticker(bot, chat_id):
    with open('tests/data/telegram.webp', 'rb') as f:
        return bot.send_sticker(chat_id, sticker=f, timeout=50).sticker


@pytest.fixture(scope='function')
def animated_sticker_file():
    f = open('tests/data/telegram_animated_sticker.tgs', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def animated_sticker(bot, chat_id):
    with open('tests/data/telegram_animated_sticker.tgs', 'rb') as f:
        return bot.send_sticker(chat_id, sticker=f, timeout=50).sticker


class TestSticker(object):
    # sticker_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.webp'
    # Serving sticker from gh since our server sends wrong content_type
    sticker_file_url = ('https://github.com/python-telegram-bot/python-telegram-bot/blob/master'
                        '/tests/data/telegram.webp?raw=true')

    emoji = '💪'
    width = 510
    height = 512
    is_animated = False
    file_size = 39518
    thumb_width = 319
    thumb_height = 320
    thumb_file_size = 21472

    sticker_file_id = '5a3128a4d2a04750b5b58397f3b5e812'
    sticker_file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'

    def test_creation(self, sticker):
        # Make sure file has been uploaded.
        assert isinstance(sticker, Sticker)
        assert isinstance(sticker.file_id, str)
        assert isinstance(sticker.file_unique_id, str)
        assert sticker.file_id != ''
        assert sticker.file_unique_id != ''
        assert isinstance(sticker.thumb, PhotoSize)
        assert isinstance(sticker.thumb.file_id, str)
        assert isinstance(sticker.thumb.file_unique_id, str)
        assert sticker.thumb.file_id != ''
        assert sticker.thumb.file_unique_id != ''

    def test_expected_values(self, sticker):
        assert sticker.width == self.width
        assert sticker.height == self.height
        assert sticker.is_animated == self.is_animated
        assert sticker.file_size == self.file_size
        assert sticker.thumb.width == self.thumb_width
        assert sticker.thumb.height == self.thumb_height
        assert sticker.thumb.file_size == self.thumb_file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, sticker_file, sticker):
        message = bot.send_sticker(chat_id, sticker=sticker_file, disable_notification=False)

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert isinstance(message.sticker.file_unique_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.file_unique_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.is_animated == sticker.is_animated
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert isinstance(message.sticker.thumb.file_unique_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.file_unique_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, sticker):
        new_file = bot.get_file(sticker.file_id)

        assert new_file.file_size == sticker.file_size
        assert new_file.file_id == sticker.file_id
        assert new_file.file_unique_id == sticker.file_unique_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.webp')

        assert os.path.isfile('telegram.webp')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, sticker):
        message = bot.send_sticker(chat_id=chat_id, sticker=sticker.file_id)

        assert message.sticker == sticker

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_on_server_emoji(self, bot, chat_id):
        server_file_id = 'CAADAQADHAADyIsGAAFZfq1bphjqlgI'
        message = bot.send_sticker(chat_id=chat_id, sticker=server_file_id)
        sticker = message.sticker
        if PY2:
            assert sticker.emoji == self.emoji.decode('utf-8')
        else:
            assert sticker.emoji == self.emoji

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_from_url(self, bot, chat_id):
        message = bot.send_sticker(chat_id=chat_id, sticker=self.sticker_file_url)
        sticker = message.sticker

        assert isinstance(message.sticker, Sticker)
        assert isinstance(message.sticker.file_id, str)
        assert isinstance(message.sticker.file_unique_id, str)
        assert message.sticker.file_id != ''
        assert message.sticker.file_unique_id != ''
        assert message.sticker.width == sticker.width
        assert message.sticker.height == sticker.height
        assert message.sticker.is_animated == sticker.is_animated
        assert message.sticker.file_size == sticker.file_size

        assert isinstance(message.sticker.thumb, PhotoSize)
        assert isinstance(message.sticker.thumb.file_id, str)
        assert isinstance(message.sticker.thumb.file_unique_id, str)
        assert message.sticker.thumb.file_id != ''
        assert message.sticker.thumb.file_unique_id != ''
        assert message.sticker.thumb.width == sticker.thumb.width
        assert message.sticker.thumb.height == sticker.thumb.height
        assert message.sticker.thumb.file_size == sticker.thumb.file_size

    def test_de_json(self, bot, sticker):
        json_dict = {
            'file_id': self.sticker_file_id,
            'file_unique_id': self.sticker_file_unique_id,
            'width': self.width,
            'height': self.height,
            'is_animated': self.is_animated,
            'thumb': sticker.thumb.to_dict(),
            'emoji': self.emoji,
            'file_size': self.file_size
        }
        json_sticker = Sticker.de_json(json_dict, bot)

        assert json_sticker.file_id == self.sticker_file_id
        assert json_sticker.file_unique_id == self.sticker_file_unique_id
        assert json_sticker.width == self.width
        assert json_sticker.height == self.height
        assert json_sticker.is_animated == self.is_animated
        assert json_sticker.emoji == self.emoji
        assert json_sticker.file_size == self.file_size
        assert json_sticker.thumb == sticker.thumb

    def test_send_with_sticker(self, monkeypatch, bot, chat_id, sticker):
        def test(_, url, data, **kwargs):
            return data['sticker'] == sticker.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_sticker(sticker=sticker, chat_id=chat_id)
        assert message

    def test_to_dict(self, sticker):
        sticker_dict = sticker.to_dict()

        assert isinstance(sticker_dict, dict)
        assert sticker_dict['file_id'] == sticker.file_id
        assert sticker_dict['file_unique_id'] == sticker.file_unique_id
        assert sticker_dict['width'] == sticker.width
        assert sticker_dict['height'] == sticker.height
        assert sticker_dict['is_animated'] == sticker.is_animated
        assert sticker_dict['file_size'] == sticker.file_size
        assert sticker_dict['thumb'] == sticker.thumb.to_dict()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_sticker(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_sticker(chat_id, '')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_sticker(chat_id)

    def test_equality(self, sticker):
        a = Sticker(sticker.file_id, sticker.file_unique_id, self.width,
                    self.height, self.is_animated)
        b = Sticker('', sticker.file_unique_id, self.width,
                    self.height, self.is_animated)
        c = Sticker(sticker.file_id, sticker.file_unique_id, 0, 0, False)
        d = Sticker('', '', self.width, self.height, self.is_animated)
        e = PhotoSize(sticker.file_id, sticker.file_unique_id, self.width,
                      self.height, self.is_animated)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope='function')
def sticker_set(bot):
    ss = bot.get_sticker_set('test_by_{}'.format(bot.username))
    if len(ss.stickers) > 100:
        raise Exception('stickerset is growing too large.')
    return ss


@pytest.fixture(scope='function')
def animated_sticker_set(bot):
    ss = bot.get_sticker_set('animated_test_by_{}'.format(bot.username))
    if len(ss.stickers) > 100:
        raise Exception('stickerset is growing too large.')
    return ss


@pytest.fixture(scope='function')
def sticker_set_thumb_file():
    f = open('tests/data/sticker_set_thumb.png', 'rb')
    yield f
    f.close()


class TestStickerSet(object):
    title = 'Test stickers'
    is_animated = True
    contains_masks = False
    stickers = [Sticker('file_id', 'file_un_id', 512, 512, True)]
    name = 'NOTAREALNAME'

    def test_de_json(self, bot, sticker):
        name = 'test_by_{}'.format(bot.username)
        json_dict = {
            'name': name,
            'title': self.title,
            'is_animated': self.is_animated,
            'contains_masks': self.contains_masks,
            'stickers': [x.to_dict() for x in self.stickers],
            'thumb': sticker.thumb.to_dict()
        }
        sticker_set = StickerSet.de_json(json_dict, bot)

        assert sticker_set.name == name
        assert sticker_set.title == self.title
        assert sticker_set.is_animated == self.is_animated
        assert sticker_set.contains_masks == self.contains_masks
        assert sticker_set.stickers == self.stickers
        assert sticker_set.thumb == sticker.thumb

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_1_png(self, bot, chat_id, sticker_file):
        with open('tests/data/telegram_sticker.png', 'rb') as f:
            file = bot.upload_sticker_file(95205500, f)
        assert file
        assert bot.add_sticker_to_set(chat_id, 'test_by_{}'.format(bot.username),
                                      png_sticker=file.file_id, emojis='😄')
        # Also test with file input and mask
        assert bot.add_sticker_to_set(chat_id, 'test_by_{}'.format(bot.username),
                                      png_sticker=sticker_file, emojis='😄',
                                      mask_position=MaskPosition(MaskPosition.EYES, -1, 1, 2))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_1_tgs(self, bot, chat_id):
        assert bot.add_sticker_to_set(
            chat_id, 'animated_test_by_{}'.format(bot.username),
            tgs_sticker=open('tests/data/telegram_animated_sticker.tgs', 'rb'),
            emojis='😄')

    def test_sticker_set_to_dict(self, sticker_set):
        sticker_set_dict = sticker_set.to_dict()

        assert isinstance(sticker_set_dict, dict)
        assert sticker_set_dict['name'] == sticker_set.name
        assert sticker_set_dict['title'] == sticker_set.title
        assert sticker_set_dict['is_animated'] == sticker_set.is_animated
        assert sticker_set_dict['contains_masks'] == sticker_set.contains_masks
        assert sticker_set_dict['stickers'][0] == sticker_set.stickers[0].to_dict()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_2_png(self, bot, sticker_set):
        file_id = sticker_set.stickers[0].file_id
        assert bot.set_sticker_position_in_set(file_id, 1)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_2_tgs(self, bot, animated_sticker_set):
        file_id = animated_sticker_set.stickers[0].file_id
        assert bot.set_sticker_position_in_set(file_id, 1)

    @flaky(10, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_3_png(self, bot, chat_id, sticker_set_thumb_file):
        sleep(1)
        assert bot.set_sticker_set_thumb('test_by_{}'.format(bot.username), chat_id,
                                         sticker_set_thumb_file)

    @flaky(10, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_3_tgs(self, bot, chat_id, animated_sticker_file, animated_sticker_set):
        sleep(1)
        assert bot.set_sticker_set_thumb('animated_test_by_{}'.format(bot.username), chat_id,
                                         animated_sticker_file)
        file_id = animated_sticker_set.stickers[-1].file_id
        # also test with file input and mask
        assert bot.set_sticker_set_thumb('animated_test_by_{}'.format(bot.username), chat_id,
                                         file_id)

    @flaky(10, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_4_png(self, bot, sticker_set):
        sleep(1)
        file_id = sticker_set.stickers[-1].file_id
        assert bot.delete_sticker_from_set(file_id)

    @flaky(10, 1)
    @pytest.mark.timeout(10)
    def test_bot_methods_4_tgs(self, bot, animated_sticker_set):
        sleep(1)
        file_id = animated_sticker_set.stickers[-1].file_id
        assert bot.delete_sticker_from_set(file_id)

    def test_get_file_instance_method(self, monkeypatch, sticker):
        def test(*args, **kwargs):
            return args[1] == sticker.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert sticker.get_file()

    def test_equality(self):
        a = StickerSet(self.name, self.title, self.is_animated, self.contains_masks, self.stickers)
        b = StickerSet(self.name, self.title, self.is_animated, self.contains_masks, self.stickers)
        c = StickerSet(self.name, None, None, None, None)
        d = StickerSet('blah', self.title, self.is_animated, self.contains_masks, self.stickers)
        e = Audio(self.name, '', 0, None, None)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


@pytest.fixture(scope='class')
def mask_position():
    return MaskPosition(TestMaskPosition.point,
                        TestMaskPosition.x_shift,
                        TestMaskPosition.y_shift,
                        TestMaskPosition.scale)


class TestMaskPosition(object):
    point = MaskPosition.EYES
    x_shift = -1
    y_shift = 1
    scale = 2

    def test_mask_position_de_json(self, bot):
        json_dict = {
            'point': self.point,
            'x_shift': self.x_shift,
            'y_shift': self.y_shift,
            'scale': self.scale
        }
        mask_position = MaskPosition.de_json(json_dict, bot)

        assert mask_position.point == self.point
        assert mask_position.x_shift == self.x_shift
        assert mask_position.y_shift == self.y_shift
        assert mask_position.scale == self.scale

    def test_mask_position_to_dict(self, mask_position):
        mask_position_dict = mask_position.to_dict()

        assert isinstance(mask_position_dict, dict)
        assert mask_position_dict['point'] == mask_position.point
        assert mask_position_dict['x_shift'] == mask_position.x_shift
        assert mask_position_dict['y_shift'] == mask_position.y_shift
        assert mask_position_dict['scale'] == mask_position.scale
