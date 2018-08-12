#!/usr/bin/env python
#
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

import pytest
from flaky import flaky

from telegram import Audio, TelegramError, Voice


@pytest.fixture(scope='function')
def audio_file():
    f = open('tests/data/telegram.mp3', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def audio(bot, chat_id):
    with open('tests/data/telegram.mp3', 'rb') as f:
        return bot.send_audio(chat_id, audio=f, timeout=50,
                              thumb=open('tests/data/thumb.jpg', 'rb')).audio


class TestAudio(object):
    caption = 'Test *audio*'
    performer = 'Leandro Toledo'
    title = 'Teste'
    duration = 3
    # audio_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp3'
    # Shortened link, the above one is cached with the wrong duration.
    audio_file_url = 'https://goo.gl/3En24v'
    mime_type = 'audio/mpeg'
    file_size = 122920
    thumb_file_size = 2744
    thumb_width = 50
    thumb_height = 50

    def test_creation(self, audio):
        # Make sure file has been uploaded.
        assert isinstance(audio, Audio)
        assert isinstance(audio.file_id, str)
        assert audio.file_id is not ''

    def test_expected_values(self, audio):
        assert audio.duration == self.duration
        assert audio.performer is None
        assert audio.title is None
        assert audio.mime_type == self.mime_type
        assert audio.file_size == self.file_size
        assert audio.thumb.file_size == self.thumb_file_size
        assert audio.thumb.width == self.thumb_width
        assert audio.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, audio_file, thumb_file):
        message = bot.send_audio(chat_id, audio=audio_file, caption=self.caption,
                                 duration=self.duration, performer=self.performer,
                                 title=self.title, disable_notification=False,
                                 parse_mode='Markdown', thumb=thumb_file)

        assert message.caption == self.caption.replace('*', '')

        assert isinstance(message.audio, Audio)
        assert isinstance(message.audio.file_id, str)
        assert message.audio.file_id is not None
        assert message.audio.duration == self.duration
        assert message.audio.performer == self.performer
        assert message.audio.title == self.title
        assert message.audio.mime_type == self.mime_type
        assert message.audio.file_size == self.file_size
        assert message.audio.thumb.file_size == self.thumb_file_size
        assert message.audio.thumb.width == self.thumb_width
        assert message.audio.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, audio):
        new_file = bot.get_file(audio.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == audio.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.mp3')

        assert os.path.isfile('telegram.mp3')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_mp3_url_file(self, bot, chat_id, audio):
        message = bot.send_audio(chat_id=chat_id, audio=self.audio_file_url, caption=self.caption)

        assert message.caption == self.caption

        assert isinstance(message.audio, Audio)
        assert isinstance(message.audio.file_id, str)
        assert message.audio.file_id is not None
        assert message.audio.duration == audio.duration
        assert message.audio.mime_type == audio.mime_type
        assert message.audio.file_size == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, audio):
        message = bot.send_audio(chat_id=chat_id, audio=audio.file_id)

        assert message.audio == audio

    def test_send_with_audio(self, monkeypatch, bot, chat_id, audio):
        def test(_, url, data, **kwargs):
            return data['audio'] == audio.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_audio(audio=audio, chat_id=chat_id)
        assert message

    def test_de_json(self, bot, audio):
        json_dict = {'file_id': 'not a file id',
                     'duration': self.duration,
                     'performer': self.performer,
                     'title': self.title,
                     'caption': self.caption,
                     'mime_type': self.mime_type,
                     'file_size': self.file_size,
                     'thumb': audio.thumb.to_dict()}
        json_audio = Audio.de_json(json_dict, bot)

        assert json_audio.file_id == 'not a file id'
        assert json_audio.duration == self.duration
        assert json_audio.performer == self.performer
        assert json_audio.title == self.title
        assert json_audio.mime_type == self.mime_type
        assert json_audio.file_size == self.file_size
        assert json_audio.thumb == audio.thumb

    def test_to_dict(self, audio):
        audio_dict = audio.to_dict()

        assert isinstance(audio_dict, dict)
        assert audio_dict['file_id'] == audio.file_id
        assert audio_dict['duration'] == audio.duration
        assert audio_dict['mime_type'] == audio.mime_type
        assert audio_dict['file_size'] == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        audio_file = open(os.devnull, 'rb')

        with pytest.raises(TelegramError):
            bot.send_audio(chat_id=chat_id, audio=audio_file)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_audio(chat_id=chat_id, audio='')

    def test_error_send_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_audio(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, audio):
        def test(*args, **kwargs):
            return args[1] == audio.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert audio.get_file()

    def test_equality(self, audio):
        a = Audio(audio.file_id, audio.duration)
        b = Audio(audio.file_id, audio.duration)
        c = Audio(audio.file_id, 0)
        d = Audio('', audio.duration)
        e = Voice(audio.file_id, audio.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
