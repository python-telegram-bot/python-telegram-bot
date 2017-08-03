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

from telegram import Bot, Voice, TelegramError, VideoNote

@pytest.fixture(scope='class')
def json_dict():
    return {
            'file_id': TestVideoNote.videonote.file_id,
            'duration': TestVideoNote.videonote.duration,
            'length': TestVideoNote.videonote.length,
            'thumb': TestVideoNote.videonote.thumb.to_dict(),
            'file_size': TestVideoNote.videonote.file_size
        }

@pytest.fixture(scope='class')
def video_note():
   return VideoNote(file_id=TestVideoNote.videonote, duration=TestVideoNote.videonote, length=TestVideoNote.videonote, thumb=TestVideoNote.videonote, file_size=TestVideoNote.videonote)

class TestVideoNote:
    """This object represents Tests for Telegram VideoNote."""

    @classmethod
    def setUpClass(cls):
        bot_info = get_bot()
        cls._chat_id = bot_info['chat_id']
        cls._bot = Bot(bot_info['token'])

        videonote_file = open('tests/data/telegram2.mp4', 'rb')
        video_note = cls._bot.send_video_note(cls._chat_id, video_note=videonote_file, timeout=10).video_note

        cls.videonote = video_note

        # Make sure file has been uploaded.
        # Simple assertions PY2 Only
        assert isinstance(cls.videonote, VideoNote)
        assert isinstance(cls.videonote.file_id, str)
        assert cls.videonote.file_id is not ''

    videonote_file = open('tests/data/telegram2.mp4', 'rb')
    
    
    @flaky(3, 1)
    @timeout(10)
    def test_expected_values(self):
        assert self.videonote.duration == 3
        assert self.videonote.length == 240
        assert self.videonote.file_size == 132084

    @flaky(3, 1)
    @timeout(10)
    def test_send_videonote_all_args(self):
        message = bot.sendVideoNote(
            chat_id,
            self.videonote_file,
            timeout=10,
            duration=self.videonote.duration,
            length=self.videonote.length,
            disable_notification=False)

        videonote = message.video_note

        assert isinstance(videonote.file_id, str)
        assert videonote.file_id != None
        assert videonote.length == self.videonote.length
        assert videonote.duration == self.videonote.duration
        assert videonote.thumb == self.videonote.thumb
        assert videonote.file_size == self.videonote.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_get_and_download_videonote(self):
        new_file = bot.getFile(self.videonote.file_id)

        assert new_file.file_size == self.videonote.file_size
        assert new_file.file_id == self.videonote.file_id
        assert new_file.file_path.startswith('https://') is True

        new_file.download('telegram2.mp4')

        assert os.path.isfile('telegram2.mp4') is True

    @flaky(3, 1)
    @timeout(10)
    def test_send_videonote_resend(self):
        message = bot.sendVideoNote(
            chat_id=chat_id,
            video_note=self.videonote.file_id,
            timeout=10
        )

        videonote = message.video_note

        assert videonote.file_id == self.videonote.file_id
        assert videonote.length == self.videonote.length
        assert videonote.duration == self.videonote.duration
        assert videonote.thumb == self.videonote.thumb
        assert videonote.file_size == self.videonote.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_send_video_note_with_video_note(self):
        message = bot.send_video_note(video_note=self.videonote, chat_id=self._chat_id)
        video_note = message.video_note

        assert video_note == self.videonote

    def test_de_json(self):
        videonote = VideoNote.de_json(json_dict, bot)

        assert videonote == self.videonote

    def test_to_json(self):
        json.loads(self.videonote.to_json())

    def test_to_dict(self):
        videonote = self.videonote.to_dict()

        assert isinstance(videonote, dict)
        assert videonote['file_id'] == self.videonote.file_id
        assert videonote['duration'] == self.videonote.duration
        assert videonote['length'] == self.videonote.length
        assert videonote['file_size'] == self.videonote.file_size

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_videonote_empty_file(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['video_note'] = open(os.devnull, 'rb')

        with self.assertRaises(TelegramError):
            bot.sendVideoNote(chat_id=chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_error_send_videonote_empty_file_id(self):
        json_dict = json_dict

        del (json_dict['file_id'])
        json_dict['video_note'] = ''

        with self.assertRaises(TelegramError):
            bot.sendVideoNote(chat_id=chat_id, timeout=10, **json_dict)

    @flaky(3, 1)
    @timeout(10)
    def test_reply_videonote(self):
        """Test for Message.reply_videonote"""
        message = bot.sendMessage(chat_id, '.')
        message = message.reply_video_note(self.videonote_file)

        assert message.video_note.file_id != None

    def test_equality(self):
        a = VideoNote(self.videonote.file_id, self.videonote.length, self.videonote.duration)
        b = VideoNote(self.videonote.file_id, self.videonote.length, self.videonote.duration)
        c = VideoNote(self.videonote.file_id, 0, 0, 0)
        d = VideoNote("", self.videonote.length, self.videonote.duration)
        e = Voice(self.videonote.file_id, self.videonote.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)


