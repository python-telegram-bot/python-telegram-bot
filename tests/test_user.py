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

from telegram import User, Update


@pytest.fixture(scope='function')
def json_dict():
    return {
        'id': TestUser.id,
        'is_bot': TestUser.is_bot,
        'first_name': TestUser.first_name,
        'last_name': TestUser.last_name,
        'username': TestUser.username,
        'language_code': TestUser.language_code
    }


@pytest.fixture(scope='function')
def user(bot):
    return User(id=TestUser.id, first_name=TestUser.first_name, is_bot=TestUser.is_bot,
                last_name=TestUser.last_name, username=TestUser.username,
                language_code=TestUser.language_code, bot=bot)


class TestUser(object):
    id = 1
    is_bot = True
    first_name = u'first\u2022name'
    last_name = u'last\u2022name'
    username = 'username'
    language_code = 'en_us'

    def test_de_json(self, json_dict, bot):
        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.is_bot == self.is_bot
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.username == self.username
        assert user.language_code == self.language_code

    def test_de_json_without_username(self, json_dict, bot):
        del json_dict['username']

        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.is_bot == self.is_bot
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.username is None
        assert user.language_code == self.language_code

    def test_de_json_without_username_and_last_name(self, json_dict, bot):
        del json_dict['username']
        del json_dict['last_name']

        user = User.de_json(json_dict, bot)

        assert user.id == self.id
        assert user.is_bot == self.is_bot
        assert user.first_name == self.first_name
        assert user.last_name is None
        assert user.username is None
        assert user.language_code == self.language_code

    def test_name(self, user):
        assert user.name == '@username'
        user.username = None
        assert user.name == u'first\u2022name last\u2022name'
        user.last_name = None
        assert user.name == u'first\u2022name'
        user.username = self.username
        assert user.name == '@username'

    def test_full_name(self, user):
        assert user.full_name == u'first\u2022name last\u2022name'
        user.last_name = None
        assert user.full_name == u'first\u2022name'

    def test_link(self, user):
        assert user.link == 'https://t.me/{}'.format(user.username)
        user.username = None
        assert user.link is None

    def test_get_profile_photos(self, monkeypatch, user):
        def test(_, *args, **kwargs):
            return args[0] == user.id

        monkeypatch.setattr('telegram.Bot.get_user_profile_photos', test)
        assert user.get_profile_photos()

    def test_instance_method_send_message(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test'

        monkeypatch.setattr('telegram.Bot.send_message', test)
        assert user.send_message('test')

    def test_instance_method_send_photo(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_photo'

        monkeypatch.setattr('telegram.Bot.send_photo', test)
        assert user.send_photo('test_photo')

    def test_instance_method_send_audio(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_audio'

        monkeypatch.setattr('telegram.Bot.send_audio', test)
        assert user.send_audio('test_audio')

    def test_instance_method_send_document(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_document'

        monkeypatch.setattr('telegram.Bot.send_document', test)
        assert user.send_document('test_document')

    def test_instance_method_send_sticker(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_sticker'

        monkeypatch.setattr('telegram.Bot.send_sticker', test)
        assert user.send_sticker('test_sticker')

    def test_instance_method_send_video(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_video'

        monkeypatch.setattr('telegram.Bot.send_video', test)
        assert user.send_video('test_video')

    def test_instance_method_send_video_note(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_video_note'

        monkeypatch.setattr('telegram.Bot.send_video_note', test)
        assert user.send_video_note('test_video_note')

    def test_instance_method_send_voice(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_voice'

        monkeypatch.setattr('telegram.Bot.send_voice', test)
        assert user.send_voice('test_voice')

    def test_instance_method_send_animation(self, monkeypatch, user):
        def test(*args, **kwargs):
            return args[1] == user.id and args[2] == 'test_animation'

        monkeypatch.setattr('telegram.Bot.send_animation', test)
        assert user.send_animation('test_animation')

    def test_mention_html(self, user):
        expected = u'<a href="tg://user?id={}">{}</a>'

        assert user.mention_html() == expected.format(user.id, user.full_name)
        assert user.mention_html('the<b>name\u2022') == expected.format(user.id,
                                                                        'the&lt;b&gt;name\u2022')
        assert user.mention_html(user.username) == expected.format(user.id, user.username)

    def test_mention_markdown(self, user):
        expected = u'[{}](tg://user?id={})'

        assert user.mention_markdown() == expected.format(user.full_name, user.id)
        assert user.mention_markdown('the_name*\u2022') == expected.format('the\_name\*\u2022',
                                                                           user.id)
        assert user.mention_markdown(user.username) == expected.format(user.username, user.id)

    def test_equality(self):
        a = User(self.id, self.first_name, self.is_bot, self.last_name)
        b = User(self.id, self.first_name, self.is_bot, self.last_name)
        c = User(self.id, self.first_name, self.is_bot)
        d = User(0, self.first_name, self.is_bot, self.last_name)
        e = Update(self.id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
