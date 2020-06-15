#!/usr/bin/env python
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

import pytest
from flaky import flaky

from telegram import Document, PhotoSize, TelegramError, Voice
from telegram.utils.helpers import escape_markdown


@pytest.fixture(scope='function')
def document_file():
    f = open('tests/data/telegram.png', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def document(bot, chat_id):
    with open('tests/data/telegram.png', 'rb') as f:
        return bot.send_document(chat_id, document=f, timeout=50).document


class TestDocument:
    caption = 'DocumentTest - *Caption*'
    document_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.gif'
    file_size = 12948
    mime_type = 'image/png'
    file_name = 'telegram.png'
    thumb_file_size = 8090
    thumb_width = 300
    thumb_height = 300
    document_file_id = '5a3128a4d2a04750b5b58397f3b5e812'
    document_file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'

    def test_creation(self, document):
        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert isinstance(document.file_unique_id, str)
        assert document.file_id != ''
        assert document.file_unique_id != ''

    def test_expected_values(self, document):
        assert document.file_size == self.file_size
        assert document.mime_type == self.mime_type
        assert document.file_name == self.file_name
        assert document.thumb.file_size == self.thumb_file_size
        assert document.thumb.width == self.thumb_width
        assert document.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, document_file, document, thumb_file):
        message = bot.send_document(chat_id, document=document_file, caption=self.caption,
                                    disable_notification=False, filename='telegram_custom.png',
                                    parse_mode='Markdown', thumb=thumb_file)

        assert isinstance(message.document, Document)
        assert isinstance(message.document.file_id, str)
        assert message.document.file_id != ''
        assert isinstance(message.document.file_unique_id, str)
        assert message.document.file_unique_id != ''
        assert isinstance(message.document.thumb, PhotoSize)
        assert message.document.file_name == 'telegram_custom.png'
        assert message.document.mime_type == document.mime_type
        assert message.document.file_size == document.file_size
        assert message.caption == self.caption.replace('*', '')
        assert message.document.thumb.width == self.thumb_width
        assert message.document.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, document):
        new_file = bot.get_file(document.file_id)

        assert new_file.file_size == document.file_size
        assert new_file.file_id == document.file_id
        assert new_file.file_unique_id == document.file_unique_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.png')

        assert os.path.isfile('telegram.png')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_url_gif_file(self, bot, chat_id):
        message = bot.send_document(chat_id, self.document_file_url)

        document = message.document

        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert document.file_id != ''
        assert isinstance(message.document.file_unique_id, str)
        assert message.document.file_unique_id != ''
        assert isinstance(document.thumb, PhotoSize)
        assert document.file_name == 'telegram.gif'
        assert document.mime_type == 'image/gif'
        assert document.file_size == 3878

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_resend(self, bot, chat_id, document):
        message = bot.send_document(chat_id=chat_id, document=document.file_id)

        assert message.document == document

    def test_send_with_document(self, monkeypatch, bot, chat_id, document):
        def test(_, url, data, **kwargs):
            return data['document'] == document.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)

        message = bot.send_document(document=document, chat_id=chat_id)

        assert message

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_document_default_parse_mode_1(self, default_bot, chat_id, document):
        test_string = 'Italic Bold Code'
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_document(chat_id, document, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_document_default_parse_mode_2(self, default_bot, chat_id, document):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_document(chat_id, document, caption=test_markdown_string,
                                            parse_mode=None)
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_document_default_parse_mode_3(self, default_bot, chat_id, document):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_document(chat_id, document, caption=test_markdown_string,
                                            parse_mode='HTML')
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    def test_de_json(self, bot, document):
        json_dict = {
            'file_id': self.document_file_id,
            'file_unique_id': self.document_file_unique_id,
            'thumb': document.thumb.to_dict(),
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        test_document = Document.de_json(json_dict, bot)

        assert test_document.file_id == self.document_file_id
        assert test_document.file_unique_id == self.document_file_unique_id
        assert test_document.thumb == document.thumb
        assert test_document.file_name == self.file_name
        assert test_document.mime_type == self.mime_type
        assert test_document.file_size == self.file_size

    def test_to_dict(self, document):
        document_dict = document.to_dict()

        assert isinstance(document_dict, dict)
        assert document_dict['file_id'] == document.file_id
        assert document_dict['file_unique_id'] == document.file_unique_id
        assert document_dict['file_name'] == document.file_name
        assert document_dict['mime_type'] == document.mime_type
        assert document_dict['file_size'] == document.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with open(os.devnull, 'rb') as f:
            with pytest.raises(TelegramError):
                bot.send_document(chat_id=chat_id, document=f)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_document(chat_id=chat_id, document='')

    def test_error_send_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_document(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, document):
        def test(*args, **kwargs):
            return args[1] == document.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert document.get_file()

    def test_equality(self, document):
        a = Document(document.file_id, document.file_unique_id)
        b = Document('', document.file_unique_id)
        d = Document('', '')
        e = Voice(document.file_id, document.file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
