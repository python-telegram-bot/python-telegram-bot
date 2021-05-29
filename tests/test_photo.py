#!/usr/bin/env python
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import Sticker, TelegramError, PhotoSize, InputFile, MessageEntity, Bot
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown
from tests.conftest import (
    expect_bad_request,
    check_shortcut_call,
    check_shortcut_signature,
    check_defaults_handling,
)


@pytest.fixture(scope='function')
def photo_file():
    f = open('tests/data/telegram.jpg', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def _photo(bot, chat_id):
    def func():
        with open('tests/data/telegram.jpg', 'rb') as f:
            return bot.send_photo(chat_id, photo=f, timeout=50).photo

    return expect_bad_request(func, 'Type of file mismatch', 'Telegram did not accept the file.')


@pytest.fixture(scope='class')
def thumb(_photo):
    return _photo[0]


@pytest.fixture(scope='class')
def photo(_photo):
    return _photo[1]


class TestPhoto:
    width = 320
    height = 320
    caption = '<b>PhotoTest</b> - *Caption*'
    photo_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.jpg'
    file_size = 29176

    def test_slot_behaviour(self, photo, recwarn, mro_slots):
        for attr in photo.__slots__:
            assert getattr(photo, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not photo.__dict__, f"got missing slot(s): {photo.__dict__}"
        assert len(mro_slots(photo)) == len(set(mro_slots(photo))), "duplicate slot"
        photo.custom, photo.width = 'should give warning', self.width
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

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
        # We used to test for file_size as well, but TG apparently at some point apparently changed
        # the compression method and it's not really our job anyway ...
        assert photo.width == self.width
        assert photo.height == self.height
        assert thumb.width == 90
        assert thumb.height == 90

    @flaky(3, 1)
    def test_send_photo_all_args(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(
            chat_id,
            photo_file,
            caption=self.caption,
            disable_notification=False,
            parse_mode='Markdown',
        )

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert isinstance(message.photo[0].file_unique_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].file_unique_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert isinstance(message.photo[1].file_unique_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].file_unique_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('*', '')

    @flaky(3, 1)
    def test_send_photo_custom_filename(self, bot, chat_id, photo_file, monkeypatch):
        def make_assertion(url, data, **kwargs):
            return data['photo'].filename == 'custom_filename'

        monkeypatch.setattr(bot.request, 'post', make_assertion)

        assert bot.send_photo(chat_id, photo_file, filename='custom_filename')

    @flaky(3, 1)
    def test_send_photo_parse_mode_markdown(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(chat_id, photo_file, caption=self.caption, parse_mode='Markdown')
        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert isinstance(message.photo[0].file_unique_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].file_unique_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert isinstance(message.photo[1].file_unique_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].file_unique_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('*', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    def test_send_photo_parse_mode_html(self, bot, chat_id, photo_file, thumb, photo):
        message = bot.send_photo(chat_id, photo_file, caption=self.caption, parse_mode='HTML')
        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert isinstance(message.photo[0].file_unique_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].file_unique_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert isinstance(message.photo[1].file_unique_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].file_unique_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

        assert message.caption == TestPhoto.caption.replace('<b>', '').replace('</b>', '')
        assert len(message.caption_entities) == 1

    @flaky(3, 1)
    def test_send_photo_caption_entities(self, bot, chat_id, photo_file, thumb, photo):
        test_string = 'Italic Bold Code'
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = bot.send_photo(
            chat_id, photo_file, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == entities

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_photo_default_parse_mode_1(self, default_bot, chat_id, photo_file, thumb, photo):
        test_string = 'Italic Bold Code'
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_photo(chat_id, photo_file, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_photo_default_parse_mode_2(self, default_bot, chat_id, photo_file, thumb, photo):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_photo(
            chat_id, photo_file, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_photo_default_parse_mode_3(self, default_bot, chat_id, photo_file, thumb, photo):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_photo(
            chat_id, photo_file, caption=test_markdown_string, parse_mode='HTML'
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    def test_send_photo_local_files(self, monkeypatch, bot, chat_id):
        # For just test that the correct paths are passed as we have no local bot API set up
        test_flag = False
        expected = (Path.cwd() / 'tests/data/telegram.jpg/').as_uri()
        file = 'tests/data/telegram.jpg'

        def make_assertion(_, data, *args, **kwargs):
            nonlocal test_flag
            test_flag = data.get('photo') == expected

        monkeypatch.setattr(bot, '_post', make_assertion)
        bot.send_photo(chat_id, file)
        assert test_flag
        monkeypatch.delattr(bot, '_post')

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
    def test_send_photo_default_allow_sending_without_reply(
        self, default_bot, chat_id, photo_file, thumb, photo, custom
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            message = default_bot.send_photo(
                chat_id,
                photo_file,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = default_bot.send_photo(
                chat_id, photo_file, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_photo(
                    chat_id, photo_file, reply_to_message_id=reply_to_message.message_id
                )

    @flaky(3, 1)
    def test_get_and_download(self, bot, photo):
        new_file = bot.getFile(photo.file_id)

        assert new_file.file_size == photo.file_size
        assert new_file.file_unique_id == photo.file_unique_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('telegram.jpg')

        assert os.path.isfile('telegram.jpg') is True

    @flaky(3, 1)
    def test_send_url_jpg_file(self, bot, chat_id, thumb, photo):
        message = bot.send_photo(chat_id, photo=self.photo_file_url)

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert isinstance(message.photo[0].file_unique_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].file_unique_id != ''
        # We used to test for width, height and file_size, but TG apparently started to treat
        # sending by URL and sending by upload differently and it's not really our job anyway ...

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert isinstance(message.photo[1].file_unique_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].file_unique_id != ''
        # We used to test for width, height and file_size, but TG apparently started to treat
        # sending by URL and sending by upload differently and it's not really our job anyway ...

    @flaky(3, 1)
    def test_send_url_png_file(self, bot, chat_id):
        message = bot.send_photo(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=chat_id
        )

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
    def test_send_url_gif_file(self, bot, chat_id):
        message = bot.send_photo(
            photo='http://dummyimage.com/600x400/000/fff.png&text=telegram', chat_id=chat_id
        )

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
    def test_send_file_unicode_filename(self, bot, chat_id):
        """
        Regression test for https://github.com/python-telegram-bot/python-telegram-bot/issues/1202
        """
        with open('tests/data/测试.png', 'rb') as f:
            message = bot.send_photo(photo=f, chat_id=chat_id)

        photo = message.photo[-1]

        assert isinstance(photo, PhotoSize)
        assert isinstance(photo.file_id, str)
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''

    @flaky(3, 1)
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
        assert isinstance(photo.file_unique_id, str)
        assert photo.file_id != ''
        assert photo.file_unique_id != ''
        assert isinstance(photo, PhotoSize)
        assert photo.width == 1280
        assert photo.height == 720
        assert photo.file_size == 33372

    def test_send_with_photosize(self, monkeypatch, bot, chat_id, photo):
        def test(url, data, **kwargs):
            return data['photo'] == photo.file_id

        monkeypatch.setattr(bot.request, 'post', test)
        message = bot.send_photo(photo=photo, chat_id=chat_id)
        assert message

    @flaky(3, 1)
    def test_resend(self, bot, chat_id, photo):
        message = bot.send_photo(chat_id=chat_id, photo=photo.file_id)

        thumb, photo, _ = message.photo

        assert isinstance(message.photo[0], PhotoSize)
        assert isinstance(message.photo[0].file_id, str)
        assert isinstance(message.photo[0].file_unique_id, str)
        assert message.photo[0].file_id != ''
        assert message.photo[0].file_unique_id != ''
        assert message.photo[0].width == thumb.width
        assert message.photo[0].height == thumb.height
        assert message.photo[0].file_size == thumb.file_size

        assert isinstance(message.photo[1], PhotoSize)
        assert isinstance(message.photo[1].file_id, str)
        assert isinstance(message.photo[1].file_unique_id, str)
        assert message.photo[1].file_id != ''
        assert message.photo[1].file_unique_id != ''
        assert message.photo[1].width == photo.width
        assert message.photo[1].height == photo.height
        assert message.photo[1].file_size == photo.file_size

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
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_photo(chat_id=chat_id, photo=open(os.devnull, 'rb'))

    @flaky(3, 1)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_photo(chat_id=chat_id, photo='')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_photo(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, photo):
        def make_assertion(*_, **kwargs):
            return kwargs['file_id'] == photo.file_id

        assert check_shortcut_signature(PhotoSize.get_file, Bot.get_file, ['file_id'], [])
        assert check_shortcut_call(photo.get_file, photo.bot, 'get_file')
        assert check_defaults_handling(photo.get_file, photo.bot)

        monkeypatch.setattr(photo.bot, 'get_file', make_assertion)
        assert photo.get_file()

    def test_equality(self, photo):
        a = PhotoSize(photo.file_id, photo.file_unique_id, self.width, self.height)
        b = PhotoSize('', photo.file_unique_id, self.width, self.height)
        c = PhotoSize(photo.file_id, photo.file_unique_id, 0, 0)
        d = PhotoSize('', '', self.width, self.height)
        e = Sticker(photo.file_id, photo.file_unique_id, self.width, self.height, False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
