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

from telegram import Video, TelegramError, Voice, PhotoSize


@pytest.fixture(scope='function')
def video_file():
    f = open('tests/data/telegram.mp4', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def video(bot, chat_id):
    with open('tests/data/telegram.mp4', 'rb') as f:
        return bot.send_video(chat_id, video=f, timeout=50).video


class TestVideo(object):
    width = 360
    height = 640
    duration = 5
    file_size = 326534
    mime_type = 'video/mp4'
    supports_streaming = True

    caption = u'<b>VideoTest</b> - *Caption*'
    video_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp4'

    def test_creation(self, video):
        # Make sure file has been uploaded.
        assert isinstance(video, Video)
        assert isinstance(video.file_id, str)
        assert video.file_id is not ''

        assert isinstance(video.thumb, PhotoSize)
        assert isinstance(video.thumb.file_id, str)
        assert video.thumb.file_id is not ''

    def test_expected_values(self, video):
        assert video.width == self.width
        assert video.height == self.height
        assert video.duration == self.duration
        assert video.file_size == self.file_size
        assert video.mime_type == self.mime_type

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, video_file, video, thumb_file):
        message = bot.send_video(chat_id, video_file, duration=self.duration,
                                 caption=self.caption, supports_streaming=self.supports_streaming,
                                 disable_notification=False, width=video.width,
                                 height=video.height, parse_mode='Markdown', thumb=thumb_file)

        assert isinstance(message.video, Video)
        assert isinstance(message.video.file_id, str)
        assert message.video.file_id != ''
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert message.caption == self.caption.replace('*', '')

        assert message.video.thumb.width == 50
        assert message.video.thumb.height == 50

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, video):
        new_file = bot.get_file(video.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == video.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.mp4')

        assert os.path.isfile('telegram.mp4')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_mp4_file_url(self, bot, chat_id, video):
        message = bot.send_video(chat_id, self.video_file_url, caption=self.caption)

        assert isinstance(message.video, Video)
        assert isinstance(message.video.file_id, str)
        assert message.video.file_id != ''
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert isinstance(message.video.thumb, PhotoSize)
        assert isinstance(message.video.thumb.file_id, str)
        assert message.video.thumb.file_id != ''
        assert message.video.thumb.width == video.thumb.width
        assert message.video.thumb.height == video.thumb.height
        assert message.video.thumb.file_size == video.thumb.file_size

        assert message.caption == self.caption

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_resend(self, bot, chat_id, video):
        message = bot.send_video(chat_id, video.file_id)

        assert message.video == video

    def test_send_with_video(self, monkeypatch, bot, chat_id, video):
        def test(_, url, data, **kwargs):
            return data['video'] == video.file_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_video(chat_id, video=video)
        assert message

    def test_de_json(self, bot):
        json_dict = {
            'file_id': 'not a file id',
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        json_video = Video.de_json(json_dict, bot)

        assert json_video.file_id == 'not a file id'
        assert json_video.width == self.width
        assert json_video.height == self.height
        assert json_video.duration == self.duration
        assert json_video.mime_type == self.mime_type
        assert json_video.file_size == self.file_size

    def test_to_dict(self, video):
        video_dict = video.to_dict()

        assert isinstance(video_dict, dict)
        assert video_dict['file_id'] == video.file_id
        assert video_dict['width'] == video.width
        assert video_dict['height'] == video.height
        assert video_dict['duration'] == video.duration
        assert video_dict['mime_type'] == video.mime_type
        assert video_dict['file_size'] == video.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_video(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_video(chat_id, '')

    def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_video(chat_id=chat_id)

    def test_get_file_instance_method(self, monkeypatch, video):
        def test(*args, **kwargs):
            return args[1] == video.file_id

        monkeypatch.setattr('telegram.Bot.get_file', test)
        assert video.get_file()

    def test_equality(self, video):
        a = Video(video.file_id, self.width, self.height, self.duration)
        b = Video(video.file_id, self.width, self.height, self.duration)
        c = Video(video.file_id, 0, 0, 0)
        d = Video('', self.width, self.height, self.duration)
        e = Voice(video.file_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
