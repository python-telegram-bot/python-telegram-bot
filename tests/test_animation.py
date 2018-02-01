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

from telegram import PhotoSize, Animation, Voice


@pytest.fixture(scope='class')
def thumb():
    return PhotoSize(height=50, file_size=1613, file_id='AAQEABPQUWQZAAT7gZuQAAH0bd93VwACAg',
                     width=90)


@pytest.fixture(scope='class')
def animation(thumb, bot):
    return Animation(TestAnimation.animation_file_id, thumb=thumb.to_dict(),
                     file_name=TestAnimation.file_name, mime_type=TestAnimation.mime_type,
                     file_size=TestAnimation.file_size, bot=bot)


class TestAnimation(object):
    animation_file_id = 'CgADBAADFQEAAny4rAUgukhiTv2TWwI'
    file_name = 'game.gif.mp4'
    mime_type = 'video/mp4'
    file_size = 4008

    def test_de_json(self, bot, thumb):
        json_dict = {
            'file_id': self.animation_file_id,
            'thumb': thumb.to_dict(),
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size
        }
        animation = Animation.de_json(json_dict, bot)
        assert animation.file_id == self.animation_file_id
        assert animation.thumb == thumb
        assert animation.file_name == self.file_name
        assert animation.mime_type == self.mime_type
        assert animation.file_size == self.file_size

    def test_to_dict(self, animation, thumb):
        animation_dict = animation.to_dict()

        assert isinstance(animation_dict, dict)
        assert animation_dict['file_id'] == animation.file_id
        assert animation_dict['thumb'] == thumb.to_dict()
        assert animation_dict['file_name'] == animation.file_name
        assert animation_dict['mime_type'] == animation.mime_type
        assert animation_dict['file_size'] == animation.file_size

    def test_equality(self):
        a = Animation(self.animation_file_id)
        b = Animation(self.animation_file_id)
        d = Animation('')
        e = Voice(self.animation_file_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
