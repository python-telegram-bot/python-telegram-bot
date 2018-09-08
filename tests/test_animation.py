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

import pytest
from flaky import flaky

from telegram import PhotoSize, Animation, Voice


@pytest.fixture(scope='function')
def animation_file():
    f = open('tests/data/game.gif', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def animation(bot, chat_id):
    with open('tests/data/game.gif', 'rb') as f:
        return bot.send_animation(chat_id, animation=f, timeout=50,
                                  thumb=open('tests/data/thumb.jpg', 'rb')).animation


class TestAnimation(object):
    animation_file_id = 'CgADAQADngIAAuyVeEez0xRovKi9VAI'
    width = 320
    height = 180
    duration = 1
    file_name = 'game.gif.mp4'
    mime_type = 'video/mp4'
    file_size = 4135
    caption = "Test *animation*"

    def test_creation(self, animation):
        assert isinstance(animation, Animation)
        assert isinstance(animation.file_id, str)
        assert animation.file_id is not ''

    def test_expected_values(self, animation):
        assert animation.file_size == self.file_size
        assert animation.mime_type == self.mime_type
        assert animation.file_name == self.file_name
        assert isinstance(animation.thumb, PhotoSize)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_all_args(self, bot, chat_id, animation_file, animation, thumb_file):
        message = bot.send_animation(chat_id, animation_file, duration=self.duration,
                                     width=self.width, height=self.height, caption=self.caption,
                                     parse_mode='Markdown', disable_notification=False,
                                     filename=self.file_name, thumb=thumb_file)

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert message.animation.file_id != ''
        assert message.animation.file_name == animation.file_name
        assert message.animation.mime_type == animation.mime_type
        assert message.animation.file_size == animation.file_size
        assert message.animation.thumb.width == 50
        assert message.animation.thumb.height == 50

    @flaky(3, 1)
    def test_resend(self, bot, chat_id, animation):
        message = bot.send_animation(chat_id, animation.file_id)

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert message.animation.file_id != ''
        assert message.animation.file_name == animation.file_name
        assert message.animation.mime_type == animation.mime_type
        assert message.animation.file_size == animation.file_size

    def test_de_json(self, bot, animation):
        json_dict = {
            'file_id': self.animation_file_id,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumb': animation.thumb.to_dict(),
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        animation = Animation.de_json(json_dict, bot)
        assert animation.file_id == self.animation_file_id
        assert animation.thumb == animation.thumb
        assert animation.file_name == self.file_name
        assert animation.mime_type == self.mime_type
        assert animation.file_size == self.file_size

    def test_to_dict(self, animation):
        animation_dict = animation.to_dict()

        assert isinstance(animation_dict, dict)
        assert animation_dict['file_id'] == animation.file_id
        assert animation_dict['width'] == animation.width
        assert animation_dict['height'] == animation.height
        assert animation_dict['duration'] == animation.duration
        assert animation_dict['thumb'] == animation.thumb.to_dict()
        assert animation_dict['file_name'] == animation.file_name
        assert animation_dict['mime_type'] == animation.mime_type
        assert animation_dict['file_size'] == animation.file_size

    def test_equality(self):
        a = Animation(self.animation_file_id, self.height, self.width, self.duration)
        b = Animation(self.animation_file_id, self.height, self.width, self.duration)
        d = Animation('', 0, 0, 0)
        e = Voice(self.animation_file_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
