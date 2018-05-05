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

from telegram import Audio, Voice, TelegramError


@pytest.fixture(scope='function')
def voice_file():
    f = open('tests/data/telegram.ogg', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def voice(bot, chat_id):
    with open('tests/data/telegram.ogg', 'rb') as f:
        return bot.send_voice(chat_id, voice=f, timeout=50).voice


class TestVoice(object):
    duration = 3
    mime_type = 'audio/ogg'
    file_size = 9199

    caption = u'Test *voice*'
    voice_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.ogg'

    def test_creation(self, voice):
        # Make sure file has been uploaded.
        assert isinstance(voice, Voice)
        assert isinstance(voice.file_id, str)
        assert voice.file_id != ''

    def test_expected_values(self, voice):
        assert voice.duration == self.duration
        assert voice.mime_type == self.mime_type
        assert voice.file_size == self.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, voice_file, voice):
        message = bot.send_voice(chat_id, voice_file, duration=self.duration,
                                 caption=self.caption, disable_notification=False,
                                 parse_mode='Markdown')

        assert isinstance(message.voice, Voice)
        assert isinstance(message.voice.file_id, str)
        assert message.voice.file_id != ''
        assert message.voice.duration == voice.duration
        assert message.voice.mime_type == voice.mime_type
        assert message.voice.file_size == voice.file_size
        assert message.caption == self.caption.replace('*', '')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, voice):
        new_file = bot.get_file(voice.file_id)

        assert new_file.file_size == voice.file_size
        assert new_file.file_id == voice.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.ogg')

        assert os.path.isfile('telegram.ogg')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_ogg_url_file(self, bot, chat_id, voice):
        message = bot.sendVoice(chat_id, self.voice_file_url, duration=self.duration)

        assert isinstance(message.voice, Voice)
        assert isinstance(message.voice.file_id, str)
        assert message.voice.file_id != ''
        assert message.voice.duration == voice.duration
        assert message.voice.mime_type == voice.mime_type
        assert message.voice.file_size == voice.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, voice):
        message = bot.sendVoice(chat_id, voice.file_id)

        assert message.voice == voice

    def test_send_with_voice(self, monkeypatch, bot, chat_id, voice):
        def test(_, url, data, **kwargs):
            return data['voice'] == voice.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_voice(chat_id, voice=voice)
        assert message

    def test_de_json(self, bot):
        json_dict = {
            'file_id': 'not a file id',
            'duration': self.duration,
            'caption': self.caption,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        json_voice = Voice.de_json(json_dict, bot)

        assert json_voice.file_id == 'not a file id'
        assert json_voice.duration == self.duration
        assert json_voice.mime_type == self.mime_type
        assert json_voice.file_size == self.file_size

    def test_to_dict(self, voice):
        voice_dict = voice.to_dict()

        assert isinstance(voice_dict, dict)
        assert voice_dict['file_id'] == voice.file_id
        assert voice_dict['duration'] == voice.duration
        assert voice_dict['mime_type'] == voice.mime_type
        assert voice_dict['file_size'] == voice.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.sendVoice(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.sendVoice(chat_id, '')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.sendVoice(chat_id)

    def test_get_file_instance_method(self, monkeypatch, voice):
        def test(*args, **kwargs):
            return args[1] == voice.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert voice.get_file()

    def test_equality(self, voice):
        a = Voice(voice.file_id, self.duration)
        b = Voice(voice.file_id, self.duration)
        c = Voice(voice.file_id, 0)
        d = Voice('', self.duration)
        e = Audio(voice.file_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
