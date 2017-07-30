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
import os

import pytest
from flaky import flaky

from telegram import Document, PhotoSize, TelegramError, Voice


@pytest.fixture()
def document_file():
    f = open('tests/data/telegram.png', 'rb')
    yield f
    f.close()


@pytest.fixture(scope="class")
def document(bot, chat_id):
    with open('tests/data/telegram.png', 'rb') as f:
        return bot.send_document(chat_id, document=f).document


class TestDocument:
    caption = u'DocumentTest - Caption'
    document_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.gif'

    def test_creation(self, document):
        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert document.file_id is not ''

    def test_expected_values(self, document):
        assert document.file_size == 12948
        assert document.mime_type == 'image/png'
        assert document.file_name == 'telegram.png'
        assert document.thumb.file_size == 2364
        assert document.thumb.width == 90
        assert document.thumb.height == 90

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_document_all_args(self, bot, chat_id, document_file, document):
        message = bot.send_document(chat_id, document=document_file, caption=self.caption,
                                    disable_notification=False, filename='telegram_custom.png')

        assert isinstance(message.document, Document)
        assert isinstance(message.document.file_id, str)
        assert message.document.file_id != ''
        assert isinstance(message.document.thumb, PhotoSize)
        assert message.document.file_name == 'telegram_custom.png'
        assert message.document.mime_type == document.mime_type
        assert message.document.file_size == document.file_size
        assert message.document.thumb == document.thumb
        assert message.caption == self.caption

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download_document(self, bot, document):
        new_file = bot.get_file(document.file_id)

        assert new_file.file_size == document.file_size
        assert new_file.file_id == document.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.png')

        assert os.path.isfile('png')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_document_url_gif_file(self, bot, chat_id):
        message = bot.send_document(chat_id, self.document_file_url)

        document = message.document

        assert isinstance(document, Document)
        assert isinstance(document.file_id, str)
        assert document.file_id != ''
        assert isinstance(document.thumb, PhotoSize)
        assert document.file_name == 'telegram.gif'
        assert document.mime_type == 'image/gif'
        assert document.file_size == 3878

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_document_resend(self, bot, chat_id, document):
        message = bot.send_document(chat_id=chat_id, document=document.file_id)

        message.document

        assert message.document == document

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_document_with_document(self, bot, chat_id, document):
        message = bot.send_document(document=document, chat_id=chat_id)

        assert message.document == document

    def test_document_de_json(self, bot, document):
        json_dict = {'file_id': document.file_id,
                     'thumb': document.thumb.to_dict(),
                     'file_name': document.file_name,
                     'mime_type': document.mime_type,
                     'file_size': document.file_size
                     }
        test_document = Document.de_json(json_dict, bot)

        assert test_document == document

    def test_document_to_json(self, document):
        json.loads(document.to_json())

    def test_document_to_dict(self, document):
        document_dict = document.to_dict()

        assert isinstance(document_dict, dict)
        assert document_dict['file_id'] == document.file_id
        assert document_dict['file_name'] == document.file_name
        assert document_dict['mime_type'] == document.mime_type
        assert document_dict['file_size'] == document.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_document_empty_file(self, bot, chat_id):
        with open(os.devnull, 'rb') as f:
            with pytest.raises(TelegramError):
                bot.send_document(chat_id=chat_id, document=f)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_document_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_document(chat_id=chat_id, document="")

    def test_error_document_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_document(chat_id=chat_id)

    def test_equality(self, document):
        a = Document(document.file_id)
        b = Document(document.file_id)
        d = Document("")
        e = Voice(document.file_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
