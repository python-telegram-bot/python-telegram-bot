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

import pytest

from telegram import Chat, ChatAction, ChatPermissions
from telegram import User, Message


@pytest.fixture(scope='class')
def chat(bot):
    return Chat(TestChat.id_, TestChat.title, TestChat.type_, username=TestChat.username,
                all_members_are_administrators=TestChat.all_members_are_administrators,
                bot=bot, sticker_set_name=TestChat.sticker_set_name,
                can_set_sticker_set=TestChat.can_set_sticker_set,
                permissions=TestChat.permissions,
                slow_mode_delay=TestChat.slow_mode_delay)


class TestChat(object):
    id_ = -28767330
    title = 'ToledosPalaceBot - Group'
    type_ = 'group'
    username = 'username'
    all_members_are_administrators = False
    sticker_set_name = 'stickers'
    can_set_sticker_set = False
    permissions = ChatPermissions(
        can_send_messages=True,
        can_change_info=False,
        can_invite_users=True,
    )
    slow_mode_delay = 30

    def test_de_json(self, bot):
        json_dict = {
            'id': self.id_,
            'title': self.title,
            'type': self.type_,
            'username': self.username,
            'all_members_are_administrators': self.all_members_are_administrators,
            'sticker_set_name': self.sticker_set_name,
            'can_set_sticker_set': self.can_set_sticker_set,
            'permissions': self.permissions.to_dict(),
            'slow_mode_delay': self.slow_mode_delay
        }
        chat = Chat.de_json(json_dict, bot)

        assert chat.id == self.id_
        assert chat.title == self.title
        assert chat.type == self.type_
        assert chat.username == self.username
        assert chat.all_members_are_administrators == self.all_members_are_administrators
        assert chat.sticker_set_name == self.sticker_set_name
        assert chat.can_set_sticker_set == self.can_set_sticker_set
        assert chat.permissions == self.permissions
        assert chat.slow_mode_delay == self.slow_mode_delay

    def test_de_json_default_quote(self, bot):
        json_dict = {
            'id': self.id_,
            'type': self.type_,
            'pinned_message': Message(
                message_id=123,
                from_user=None,
                date=None,
                chat=None
            ).to_dict(),
            'default_quote': True
        }
        chat = Chat.de_json(json_dict, bot)

        assert chat.pinned_message.default_quote is True

    def test_to_dict(self, chat):
        chat_dict = chat.to_dict()

        assert isinstance(chat_dict, dict)
        assert chat_dict['id'] == chat.id
        assert chat_dict['title'] == chat.title
        assert chat_dict['type'] == chat.type
        assert chat_dict['username'] == chat.username
        assert chat_dict['all_members_are_administrators'] == chat.all_members_are_administrators
        assert chat_dict['permissions'] == chat.permissions.to_dict()
        assert chat_dict['slow_mode_delay'] == chat.slow_mode_delay

    def test_link(self, chat):
        assert chat.link == 'https://t.me/{}'.format(chat.username)
        chat.username = None
        assert chat.link is None

    def test_send_action(self, monkeypatch, chat):
        def test(*args, **kwargs):
            id_ = args[0] == chat.id
            action = kwargs['action'] == ChatAction.TYPING
            return id_ and action

        monkeypatch.setattr(chat.bot, 'send_chat_action', test)
        assert chat.send_action(action=ChatAction.TYPING)

    def test_leave(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id

        monkeypatch.setattr(chat.bot, 'leave_chat', test)
        assert chat.leave()

    def test_get_administrators(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id

        monkeypatch.setattr(chat.bot, 'get_chat_administrators', test)
        assert chat.get_administrators()

    def test_get_members_count(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id

        monkeypatch.setattr(chat.bot, 'get_chat_members_count', test)
        assert chat.get_members_count()

    def test_get_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[0] == chat.id
            user_id = args[1] == 42
            return chat_id and user_id

        monkeypatch.setattr(chat.bot, 'get_chat_member', test)
        assert chat.get_member(42)

    def test_kick_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[0] == chat.id
            user_id = args[1] == 42
            until = kwargs['until_date'] == 43
            return chat_id and user_id and until

        monkeypatch.setattr(chat.bot, 'kick_chat_member', test)
        assert chat.kick_member(42, until_date=43)

    def test_unban_member(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[0] == chat.id
            user_id = args[1] == 42
            return chat_id and user_id

        monkeypatch.setattr(chat.bot, 'unban_chat_member', test)
        assert chat.unban_member(42)

    def test_set_permissions(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[0] == chat.id
            permissions = args[1] == self.permissions
            return chat_id and permissions

        monkeypatch.setattr(chat.bot, 'set_chat_permissions', test)
        assert chat.set_permissions(self.permissions)

    def test_set_administrator_custom_title(self, monkeypatch, chat):
        def test(*args, **kwargs):
            chat_id = args[1] == chat.id
            user_id = args[2] == 42
            custom_title = args[3] == 'custom_title'
            return chat_id and user_id and custom_title

        monkeypatch.setattr('telegram.Bot.set_chat_administrator_custom_title', test)
        assert chat.set_administrator_custom_title(42, 'custom_title')

    def test_instance_method_send_message(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test'

        monkeypatch.setattr(chat.bot, 'send_message', test)
        assert chat.send_message('test')

    def test_instance_method_send_photo(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_photo'

        monkeypatch.setattr(chat.bot, 'send_photo', test)
        assert chat.send_photo('test_photo')

    def test_instance_method_send_audio(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_audio'

        monkeypatch.setattr(chat.bot, 'send_audio', test)
        assert chat.send_audio('test_audio')

    def test_instance_method_send_document(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_document'

        monkeypatch.setattr(chat.bot, 'send_document', test)
        assert chat.send_document('test_document')

    def test_instance_method_send_sticker(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_sticker'

        monkeypatch.setattr(chat.bot, 'send_sticker', test)
        assert chat.send_sticker('test_sticker')

    def test_instance_method_send_video(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_video'

        monkeypatch.setattr(chat.bot, 'send_video', test)
        assert chat.send_video('test_video')

    def test_instance_method_send_video_note(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_video_note'

        monkeypatch.setattr(chat.bot, 'send_video_note', test)
        assert chat.send_video_note('test_video_note')

    def test_instance_method_send_voice(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_voice'

        monkeypatch.setattr(chat.bot, 'send_voice', test)
        assert chat.send_voice('test_voice')

    def test_instance_method_send_animation(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_animation'

        monkeypatch.setattr(chat.bot, 'send_animation', test)
        assert chat.send_animation('test_animation')

    def test_instance_method_send_poll(self, monkeypatch, chat):
        def test(*args, **kwargs):
            return args[0] == chat.id and args[1] == 'test_poll'

        monkeypatch.setattr(chat.bot, 'send_poll', test)
        assert chat.send_poll('test_poll')

    def test_equality(self):
        a = Chat(self.id_, self.title, self.type_)
        b = Chat(self.id_, self.title, self.type_)
        c = Chat(self.id_, '', '')
        d = Chat(0, self.title, self.type_)
        e = User(self.id_, '', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
