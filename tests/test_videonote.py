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

from telegram import VideoNote, TelegramError, Voice, PhotoSize


@pytest.fixture(scope='function')
def video_note_file():
    f = open('tests/data/telegram2.mp4', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def video_note(bot, chat_id):
    with open('tests/data/telegram2.mp4', 'rb') as f:
        return bot.send_video_note(chat_id, video_note=f, timeout=50).video_note


class TestVideoNote(object):
    length = 240
    duration = 3
    file_size = 132084

    caption = u'VideoNoteTest - Caption'

    def test_creation(self, video_note):
        # Make sure file has been uploaded.
        assert isinstance(video_note, VideoNote)
        assert isinstance(video_note.file_id, str)
        assert video_note.file_id is not ''

        assert isinstance(video_note.thumb, PhotoSize)
        assert isinstance(video_note.thumb.file_id, str)
        assert video_note.thumb.file_id is not ''

    def test_expected_values(self, video_note):
        assert video_note.length == self.length
        assert video_note.duration == self.duration
        assert video_note.file_size == self.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, video_note_file, video_note, thumb_file):
        message = bot.send_video_note(chat_id, video_note_file, duration=self.duration,
                                      length=self.length, disable_notification=False,
                                      thumb=thumb_file)

        assert isinstance(message.video_note, VideoNote)
        assert isinstance(message.video_note.file_id, str)
        assert message.video_note.file_id != ''
        assert message.video_note.length == video_note.length
        assert message.video_note.duration == video_note.duration
        assert message.video_note.file_size == video_note.file_size

        assert message.video_note.thumb.width == 50
        assert message.video_note.thumb.height == 50

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, video_note):
        new_file = bot.get_file(video_note.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == video_note.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram2.mp4')

        assert os.path.isfile('telegram2.mp4')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, video_note):
        message = bot.send_video_note(chat_id, video_note.file_id)

        assert message.video_note == video_note

    def test_send_with_video_note(self, monkeypatch, bot, chat_id, video_note):
        def test(_, url, data, **kwargs):
            return data['video_note'] == video_note.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_video_note(chat_id, video_note=video_note)
        assert message

    def test_de_json(self, bot):
        json_dict = {
            'file_id': 'not a file id',
            'length': self.length,
            'duration': self.duration,
            'file_size': self.file_size
        }
        json_video_note = VideoNote.de_json(json_dict, bot)

        assert json_video_note.file_id == 'not a file id'
        assert json_video_note.length == self.length
        assert json_video_note.duration == self.duration
        assert json_video_note.file_size == self.file_size

    def test_to_dict(self, video_note):
        video_note_dict = video_note.to_dict()

        assert isinstance(video_note_dict, dict)
        assert video_note_dict['file_id'] == video_note.file_id
        assert video_note_dict['length'] == video_note.length
        assert video_note_dict['duration'] == video_note.duration
        assert video_note_dict['file_size'] == video_note.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_video_note(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_video_note(chat_id, '')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_video_note(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, video_note):
        def test(*args, **kwargs):
            return args[1] == video_note.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert video_note.get_file()

    def test_equality(self, video_note):
        a = VideoNote(video_note.file_id, self.length, self.duration)
        b = VideoNote(video_note.file_id, self.length, self.duration)
        c = VideoNote(video_note.file_id, 0, 0)
        d = VideoNote('', self.length, self.duration)
        e = Voice(video_note.file_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
