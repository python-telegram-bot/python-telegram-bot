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

from telegram import Video, TelegramError, Voice, PhotoSize
from telegram.utils.helpers import escape_markdown


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

    thumb_width = 180
    thumb_height = 320
    thumb_file_size = 1767

    caption = u'<b>VideoTest</b> - *Caption*'
    video_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp4'

    video_file_id = '5a3128a4d2a04750b5b58397f3b5e812'
    video_file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'

    def test_creation(self, video):
        # Make sure file has been uploaded.
        assert isinstance(video, Video)
        assert isinstance(video.file_id, str)
        assert isinstance(video.file_unique_id, str)
        assert video.file_id != ''
        assert video.file_unique_id != ''

        assert isinstance(video.thumb, PhotoSize)
        assert isinstance(video.thumb.file_id, str)
        assert isinstance(video.thumb.file_unique_id, str)
        assert video.thumb.file_id != ''
        assert video.thumb.file_unique_id != ''

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
        assert isinstance(message.video.file_unique_id, str)
        assert message.video.file_id != ''
        assert message.video.file_unique_id != ''
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert message.caption == self.caption.replace('*', '')

        assert message.video.thumb.file_size == self.thumb_file_size
        assert message.video.thumb.width == self.thumb_width
        assert message.video.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download(self, bot, video):
        new_file = bot.get_file(video.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == video.file_id
        assert new_file.file_unique_id == video.file_unique_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.mp4')

        assert os.path.isfile('telegram.mp4')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_mp4_file_url(self, bot, chat_id, video):
        message = bot.send_video(chat_id, self.video_file_url, caption=self.caption)

        assert isinstance(message.video, Video)
        assert isinstance(message.video.file_id, str)
        assert isinstance(message.video.file_unique_id, str)
        assert message.video.file_id != ''
        assert message.video.file_unique_id != ''
        assert message.video.width == video.width
        assert message.video.height == video.height
        assert message.video.duration == video.duration
        assert message.video.file_size == video.file_size

        assert isinstance(message.video.thumb, PhotoSize)
        assert isinstance(message.video.thumb.file_id, str)
        assert isinstance(message.video.thumb.file_unique_id, str)
        assert message.video.thumb.file_id != ''
        assert message.video.thumb.file_unique_id != ''
        assert message.video.thumb.width == 51  # This seems odd that it's not self.thumb_width
        assert message.video.thumb.height == 90  # Ditto
        assert message.video.thumb.file_size == 645  # same

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

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_video_default_parse_mode_1(self, default_bot, chat_id, video):
        test_string = 'Italic Bold Code'
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_video(chat_id, video, caption=test_markdown_string)
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_video_default_parse_mode_2(self, default_bot, chat_id, video):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_video(chat_id, video, caption=test_markdown_string,
                                         parse_mode=None)
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    def test_send_video_default_parse_mode_3(self, default_bot, chat_id, video):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = default_bot.send_video(chat_id, video, caption=test_markdown_string,
                                         parse_mode='HTML')
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    def test_de_json(self, bot):
        json_dict = {
            'file_id': self.video_file_id,
            'file_unique_id': self.video_file_unique_id,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        json_video = Video.de_json(json_dict, bot)

        assert json_video.file_id == self.video_file_id
        assert json_video.file_unique_id == self.video_file_unique_id
        assert json_video.width == self.width
        assert json_video.height == self.height
        assert json_video.duration == self.duration
        assert json_video.mime_type == self.mime_type
        assert json_video.file_size == self.file_size

    def test_to_dict(self, video):
        video_dict = video.to_dict()

        assert isinstance(video_dict, dict)
        assert video_dict['file_id'] == video.file_id
        assert video_dict['file_unique_id'] == video.file_unique_id
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
        a = Video(video.file_id, video.file_unique_id, self.width, self.height, self.duration)
        b = Video('', video.file_unique_id, self.width, self.height, self.duration)
        c = Video(video.file_id, video.file_unique_id, 0, 0, 0)
        d = Video('', '', self.width, self.height, self.duration)
        e = Voice(video.file_id, video.file_unique_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
