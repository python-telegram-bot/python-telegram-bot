import json

import pytest

from telegram import PhotoSize, Animation, Voice


@pytest.fixture(scope="class")
def thumb():
    return PhotoSize(height=50, file_size=1613, file_id='AAQEABPQUWQZAAT7gZuQAAH0bd93VwACAg',
                     width=90)


@pytest.fixture()
def json_dict(thumb):
    return {
        'file_id': TestAnimation.animation_file_id,
        'thumb': thumb.to_dict(),
        'file_name': TestAnimation.file_name,
        'mime_type': TestAnimation.mime_type,
        'file_size': TestAnimation.file_size
    }


@pytest.fixture(scope="class")
def animation(thumb, bot):
    return Animation(file_id=TestAnimation.animation_file_id, thumb=thumb.to_dict(),
                     file_name=TestAnimation.file_name, mime_type=TestAnimation.mime_type,
                     file_size=TestAnimation.file_size, bot=bot)


class TestAnimation:
    """Tests for telegram.Animation"""

    animation_file_id = 'CgADBAADFQEAAny4rAUgukhiTv2TWwI'
    file_name = "game.gif.mp4"
    mime_type = "video/mp4"
    file_size = 4008

    def test_animation_de_json(self, json_dict, bot, thumb):
        animation = Animation.de_json(json_dict, bot)
        assert animation.file_id == self.animation_file_id
        assert animation.thumb == thumb
        assert animation.file_name == self.file_name
        assert animation.mime_type == self.mime_type
        assert animation.file_size == self.file_size

    def test_animation_to_json(self, animation):
        json.loads(animation.to_json())

    def test_animation_to_dict(self, animation, thumb):
        animation_dict = animation.to_dict()

        assert isinstance(animation_dict, dict)
        assert animation_dict['file_id'] == self.animation_file_id
        assert animation_dict['thumb'] == thumb.to_dict()
        assert animation_dict['file_name'] == self.file_name
        assert animation_dict['mime_type'] == self.mime_type
        assert animation_dict['file_size'] == self.file_size

    def test_equality(self):
        a = Animation(self.animation_file_id)
        b = Animation(self.animation_file_id)
        d = Animation("")
        e = Voice(self.animation_file_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
