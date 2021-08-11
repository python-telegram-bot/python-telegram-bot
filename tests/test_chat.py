#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from telegram import Chat, ChatAction, ChatPermissions, ChatLocation, Location, Bot
from telegram import User
from tests.conftest import check_shortcut_signature, check_shortcut_call, check_defaults_handling


@pytest.fixture(scope='class')
def chat(bot):
    return Chat(
        TestChat.id_,
        TestChat.title,
        TestChat.type_,
        username=TestChat.username,
        all_members_are_administrators=TestChat.all_members_are_administrators,
        bot=bot,
        sticker_set_name=TestChat.sticker_set_name,
        can_set_sticker_set=TestChat.can_set_sticker_set,
        permissions=TestChat.permissions,
        slow_mode_delay=TestChat.slow_mode_delay,
        message_auto_delete_time=TestChat.message_auto_delete_time,
        bio=TestChat.bio,
        linked_chat_id=TestChat.linked_chat_id,
        location=TestChat.location,
    )


class TestChat:
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
    message_auto_delete_time = 42
    bio = "I'm a Barbie Girl in a Barbie World"
    linked_chat_id = 11880
    location = ChatLocation(Location(123, 456), 'Barbie World')

    def test_slot_behaviour(self, chat, recwarn, mro_slots):
        for attr in chat.__slots__:
            assert getattr(chat, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not chat.__dict__, f"got missing slot(s): {chat.__dict__}"
        assert len(mro_slots(chat)) == len(set(mro_slots(chat))), "duplicate slot"
        chat.custom, chat.id = 'should give warning', self.id_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

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
            'slow_mode_delay': self.slow_mode_delay,
            'message_auto_delete_time': self.message_auto_delete_time,
            'bio': self.bio,
            'linked_chat_id': self.linked_chat_id,
            'location': self.location.to_dict(),
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
        assert chat.message_auto_delete_time == self.message_auto_delete_time
        assert chat.bio == self.bio
        assert chat.linked_chat_id == self.linked_chat_id
        assert chat.location.location == self.location.location
        assert chat.location.address == self.location.address

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
        assert chat_dict['message_auto_delete_time'] == chat.message_auto_delete_time
        assert chat_dict['bio'] == chat.bio
        assert chat_dict['linked_chat_id'] == chat.linked_chat_id
        assert chat_dict['location'] == chat.location.to_dict()

    def test_link(self, chat):
        assert chat.link == f'https://t.me/{chat.username}'
        chat.username = None
        assert chat.link is None

    def test_full_name(self):
        chat = Chat(
            id=1, type=Chat.PRIVATE, first_name='first\u2022name', last_name='last\u2022name'
        )
        assert chat.full_name == 'first\u2022name last\u2022name'
        chat = Chat(id=1, type=Chat.PRIVATE, first_name='first\u2022name')
        assert chat.full_name == 'first\u2022name'
        chat = Chat(
            id=1,
            type=Chat.PRIVATE,
        )
        assert chat.full_name is None

    def test_send_action(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == chat.id
            action = kwargs['action'] == ChatAction.TYPING
            return id_ and action

        assert check_shortcut_signature(chat.send_action, Bot.send_chat_action, ['chat_id'], [])
        assert check_shortcut_call(chat.send_action, chat.bot, 'send_chat_action')
        assert check_defaults_handling(chat.send_action, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_chat_action', make_assertion)
        assert chat.send_action(action=ChatAction.TYPING)
        assert chat.send_action(action=ChatAction.TYPING)

    def test_leave(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(Chat.leave, Bot.leave_chat, ['chat_id'], [])
        assert check_shortcut_call(chat.leave, chat.bot, 'leave_chat')
        assert check_defaults_handling(chat.leave, chat.bot)

        monkeypatch.setattr(chat.bot, 'leave_chat', make_assertion)
        assert chat.leave()

    def test_get_administrators(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.get_administrators, Bot.get_chat_administrators, ['chat_id'], []
        )
        assert check_shortcut_call(chat.get_administrators, chat.bot, 'get_chat_administrators')
        assert check_defaults_handling(chat.get_administrators, chat.bot)

        monkeypatch.setattr(chat.bot, 'get_chat_administrators', make_assertion)
        assert chat.get_administrators()

    def test_get_member_count(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.get_member_count, Bot.get_chat_member_count, ['chat_id'], []
        )
        assert check_shortcut_call(chat.get_member_count, chat.bot, 'get_chat_member_count')
        assert check_defaults_handling(chat.get_member_count, chat.bot)

        monkeypatch.setattr(chat.bot, 'get_chat_member_count', make_assertion)
        assert chat.get_member_count()

    def test_get_members_count_warning(self, chat, monkeypatch, recwarn):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        monkeypatch.setattr(chat.bot, 'get_chat_member_count', make_assertion)
        assert chat.get_members_count()
        assert len(recwarn) == 1
        assert '`Chat.get_members_count` is deprecated' in str(recwarn[0].message)

    def test_get_member(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            return chat_id and user_id

        assert check_shortcut_signature(Chat.get_member, Bot.get_chat_member, ['chat_id'], [])
        assert check_shortcut_call(chat.get_member, chat.bot, 'get_chat_member')
        assert check_defaults_handling(chat.get_member, chat.bot)

        monkeypatch.setattr(chat.bot, 'get_chat_member', make_assertion)
        assert chat.get_member(user_id=42)

    def test_ban_member(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            until = kwargs['until_date'] == 43
            return chat_id and user_id and until

        assert check_shortcut_signature(Chat.ban_member, Bot.ban_chat_member, ['chat_id'], [])
        assert check_shortcut_call(chat.ban_member, chat.bot, 'ban_chat_member')
        assert check_defaults_handling(chat.ban_member, chat.bot)

        monkeypatch.setattr(chat.bot, 'ban_chat_member', make_assertion)
        assert chat.ban_member(user_id=42, until_date=43)

    def test_kick_member_warning(self, chat, monkeypatch, recwarn):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            until = kwargs['until_date'] == 43
            return chat_id and user_id and until

        monkeypatch.setattr(chat.bot, 'ban_chat_member', make_assertion)
        assert chat.kick_member(user_id=42, until_date=43)
        assert len(recwarn) == 1
        assert '`Chat.kick_member` is deprecated' in str(recwarn[0].message)

    @pytest.mark.parametrize('only_if_banned', [True, False, None])
    def test_unban_member(self, monkeypatch, chat, only_if_banned):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            o_i_b = kwargs.get('only_if_banned') == only_if_banned
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(Chat.unban_member, Bot.unban_chat_member, ['chat_id'], [])
        assert check_shortcut_call(chat.unban_member, chat.bot, 'unban_chat_member')
        assert check_defaults_handling(chat.unban_member, chat.bot)

        monkeypatch.setattr(chat.bot, 'unban_chat_member', make_assertion)
        assert chat.unban_member(user_id=42, only_if_banned=only_if_banned)

    @pytest.mark.parametrize('is_anonymous', [True, False, None])
    def test_promote_member(self, monkeypatch, chat, is_anonymous):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            o_i_b = kwargs.get('is_anonymous') == is_anonymous
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(
            Chat.promote_member, Bot.promote_chat_member, ['chat_id'], []
        )
        assert check_shortcut_call(chat.promote_member, chat.bot, 'promote_chat_member')
        assert check_defaults_handling(chat.promote_member, chat.bot)

        monkeypatch.setattr(chat.bot, 'promote_chat_member', make_assertion)
        assert chat.promote_member(user_id=42, is_anonymous=is_anonymous)

    def test_restrict_member(self, monkeypatch, chat):
        permissions = ChatPermissions(True, False, True, False, True, False, True, False)

        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            o_i_b = kwargs.get('permissions') == permissions
            return chat_id and user_id and o_i_b

        assert check_shortcut_signature(
            Chat.restrict_member, Bot.restrict_chat_member, ['chat_id'], []
        )
        assert check_shortcut_call(chat.restrict_member, chat.bot, 'restrict_chat_member')
        assert check_defaults_handling(chat.restrict_member, chat.bot)

        monkeypatch.setattr(chat.bot, 'restrict_chat_member', make_assertion)
        assert chat.restrict_member(user_id=42, permissions=permissions)

    def test_set_permissions(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            permissions = kwargs['permissions'] == self.permissions
            return chat_id and permissions

        assert check_shortcut_signature(
            Chat.set_permissions, Bot.set_chat_permissions, ['chat_id'], []
        )
        assert check_shortcut_call(chat.set_permissions, chat.bot, 'set_chat_permissions')
        assert check_defaults_handling(chat.set_permissions, chat.bot)

        monkeypatch.setattr(chat.bot, 'set_chat_permissions', make_assertion)
        assert chat.set_permissions(permissions=self.permissions)

    def test_set_administrator_custom_title(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == chat.id
            user_id = kwargs['user_id'] == 42
            custom_title = kwargs['custom_title'] == 'custom_title'
            return chat_id and user_id and custom_title

        monkeypatch.setattr('telegram.Bot.set_chat_administrator_custom_title', make_assertion)
        assert chat.set_administrator_custom_title(user_id=42, custom_title='custom_title')

    def test_pin_message(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['message_id'] == 42

        assert check_shortcut_signature(Chat.pin_message, Bot.pin_chat_message, ['chat_id'], [])
        assert check_shortcut_call(chat.pin_message, chat.bot, 'pin_chat_message')
        assert check_defaults_handling(chat.pin_message, chat.bot)

        monkeypatch.setattr(chat.bot, 'pin_chat_message', make_assertion)
        assert chat.pin_message(message_id=42)

    def test_unpin_message(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.unpin_message, Bot.unpin_chat_message, ['chat_id'], []
        )
        assert check_shortcut_call(chat.unpin_message, chat.bot, 'unpin_chat_message')
        assert check_defaults_handling(chat.unpin_message, chat.bot)

        monkeypatch.setattr(chat.bot, 'unpin_chat_message', make_assertion)
        assert chat.unpin_message()

    def test_unpin_all_messages(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.unpin_all_messages, Bot.unpin_all_chat_messages, ['chat_id'], []
        )
        assert check_shortcut_call(chat.unpin_all_messages, chat.bot, 'unpin_all_chat_messages')
        assert check_defaults_handling(chat.unpin_all_messages, chat.bot)

        monkeypatch.setattr(chat.bot, 'unpin_all_chat_messages', make_assertion)
        assert chat.unpin_all_messages()

    def test_instance_method_send_message(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['text'] == 'test'

        assert check_shortcut_signature(Chat.send_message, Bot.send_message, ['chat_id'], [])
        assert check_shortcut_call(chat.send_message, chat.bot, 'send_message')
        assert check_defaults_handling(chat.send_message, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_message', make_assertion)
        assert chat.send_message(text='test')

    def test_instance_method_send_media_group(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['media'] == 'test_media_group'

        assert check_shortcut_signature(
            Chat.send_media_group, Bot.send_media_group, ['chat_id'], []
        )
        assert check_shortcut_call(chat.send_media_group, chat.bot, 'send_media_group')
        assert check_defaults_handling(chat.send_media_group, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_media_group', make_assertion)
        assert chat.send_media_group(media='test_media_group')

    def test_instance_method_send_photo(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['photo'] == 'test_photo'

        assert check_shortcut_signature(Chat.send_photo, Bot.send_photo, ['chat_id'], [])
        assert check_shortcut_call(chat.send_photo, chat.bot, 'send_photo')
        assert check_defaults_handling(chat.send_photo, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_photo', make_assertion)
        assert chat.send_photo(photo='test_photo')

    def test_instance_method_send_contact(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['phone_number'] == 'test_contact'

        assert check_shortcut_signature(Chat.send_contact, Bot.send_contact, ['chat_id'], [])
        assert check_shortcut_call(chat.send_contact, chat.bot, 'send_contact')
        assert check_defaults_handling(chat.send_contact, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_contact', make_assertion)
        assert chat.send_contact(phone_number='test_contact')

    def test_instance_method_send_audio(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['audio'] == 'test_audio'

        assert check_shortcut_signature(Chat.send_audio, Bot.send_audio, ['chat_id'], [])
        assert check_shortcut_call(chat.send_audio, chat.bot, 'send_audio')
        assert check_defaults_handling(chat.send_audio, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_audio', make_assertion)
        assert chat.send_audio(audio='test_audio')

    def test_instance_method_send_document(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['document'] == 'test_document'

        assert check_shortcut_signature(Chat.send_document, Bot.send_document, ['chat_id'], [])
        assert check_shortcut_call(chat.send_document, chat.bot, 'send_document')
        assert check_defaults_handling(chat.send_document, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_document', make_assertion)
        assert chat.send_document(document='test_document')

    def test_instance_method_send_dice(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['emoji'] == 'test_dice'

        assert check_shortcut_signature(Chat.send_dice, Bot.send_dice, ['chat_id'], [])
        assert check_shortcut_call(chat.send_dice, chat.bot, 'send_dice')
        assert check_defaults_handling(chat.send_dice, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_dice', make_assertion)
        assert chat.send_dice(emoji='test_dice')

    def test_instance_method_send_game(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['game_short_name'] == 'test_game'

        assert check_shortcut_signature(Chat.send_game, Bot.send_game, ['chat_id'], [])
        assert check_shortcut_call(chat.send_game, chat.bot, 'send_game')
        assert check_defaults_handling(chat.send_game, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_game', make_assertion)
        assert chat.send_game(game_short_name='test_game')

    def test_instance_method_send_invoice(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            title = kwargs['title'] == 'title'
            description = kwargs['description'] == 'description'
            payload = kwargs['payload'] == 'payload'
            provider_token = kwargs['provider_token'] == 'provider_token'
            currency = kwargs['currency'] == 'currency'
            prices = kwargs['prices'] == 'prices'
            args = title and description and payload and provider_token and currency and prices
            return kwargs['chat_id'] == chat.id and args

        assert check_shortcut_signature(Chat.send_invoice, Bot.send_invoice, ['chat_id'], [])
        assert check_shortcut_call(chat.send_invoice, chat.bot, 'send_invoice')
        assert check_defaults_handling(chat.send_invoice, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_invoice', make_assertion)
        assert chat.send_invoice(
            'title',
            'description',
            'payload',
            'provider_token',
            'currency',
            'prices',
        )

    def test_instance_method_send_location(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['latitude'] == 'test_location'

        assert check_shortcut_signature(Chat.send_location, Bot.send_location, ['chat_id'], [])
        assert check_shortcut_call(chat.send_location, chat.bot, 'send_location')
        assert check_defaults_handling(chat.send_location, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_location', make_assertion)
        assert chat.send_location(latitude='test_location')

    def test_instance_method_send_sticker(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['sticker'] == 'test_sticker'

        assert check_shortcut_signature(Chat.send_sticker, Bot.send_sticker, ['chat_id'], [])
        assert check_shortcut_call(chat.send_sticker, chat.bot, 'send_sticker')
        assert check_defaults_handling(chat.send_sticker, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_sticker', make_assertion)
        assert chat.send_sticker(sticker='test_sticker')

    def test_instance_method_send_venue(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['title'] == 'test_venue'

        assert check_shortcut_signature(Chat.send_venue, Bot.send_venue, ['chat_id'], [])
        assert check_shortcut_call(chat.send_venue, chat.bot, 'send_venue')
        assert check_defaults_handling(chat.send_venue, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_venue', make_assertion)
        assert chat.send_venue(title='test_venue')

    def test_instance_method_send_video(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['video'] == 'test_video'

        assert check_shortcut_signature(Chat.send_video, Bot.send_video, ['chat_id'], [])
        assert check_shortcut_call(chat.send_video, chat.bot, 'send_video')
        assert check_defaults_handling(chat.send_video, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_video', make_assertion)
        assert chat.send_video(video='test_video')

    def test_instance_method_send_video_note(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['video_note'] == 'test_video_note'

        assert check_shortcut_signature(Chat.send_video_note, Bot.send_video_note, ['chat_id'], [])
        assert check_shortcut_call(chat.send_video_note, chat.bot, 'send_video_note')
        assert check_defaults_handling(chat.send_video_note, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_video_note', make_assertion)
        assert chat.send_video_note(video_note='test_video_note')

    def test_instance_method_send_voice(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['voice'] == 'test_voice'

        assert check_shortcut_signature(Chat.send_voice, Bot.send_voice, ['chat_id'], [])
        assert check_shortcut_call(chat.send_voice, chat.bot, 'send_voice')
        assert check_defaults_handling(chat.send_voice, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_voice', make_assertion)
        assert chat.send_voice(voice='test_voice')

    def test_instance_method_send_animation(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['animation'] == 'test_animation'

        assert check_shortcut_signature(Chat.send_animation, Bot.send_animation, ['chat_id'], [])
        assert check_shortcut_call(chat.send_animation, chat.bot, 'send_animation')
        assert check_defaults_handling(chat.send_animation, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_animation', make_assertion)
        assert chat.send_animation(animation='test_animation')

    def test_instance_method_send_poll(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['question'] == 'test_poll'

        assert check_shortcut_signature(Chat.send_poll, Bot.send_poll, ['chat_id'], [])
        assert check_shortcut_call(chat.send_poll, chat.bot, 'send_poll')
        assert check_defaults_handling(chat.send_poll, chat.bot)

        monkeypatch.setattr(chat.bot, 'send_poll', make_assertion)
        assert chat.send_poll(question='test_poll', options=[1, 2])

    def test_instance_method_send_copy(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            from_chat_id = kwargs['from_chat_id'] == 'test_copy'
            message_id = kwargs['message_id'] == 42
            chat_id = kwargs['chat_id'] == chat.id
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.send_copy, Bot.copy_message, ['chat_id'], [])
        assert check_shortcut_call(chat.copy_message, chat.bot, 'copy_message')
        assert check_defaults_handling(chat.copy_message, chat.bot)

        monkeypatch.setattr(chat.bot, 'copy_message', make_assertion)
        assert chat.send_copy(from_chat_id='test_copy', message_id=42)

    def test_instance_method_copy_message(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            from_chat_id = kwargs['from_chat_id'] == chat.id
            message_id = kwargs['message_id'] == 42
            chat_id = kwargs['chat_id'] == 'test_copy'
            return from_chat_id and message_id and chat_id

        assert check_shortcut_signature(Chat.copy_message, Bot.copy_message, ['from_chat_id'], [])
        assert check_shortcut_call(chat.copy_message, chat.bot, 'copy_message')
        assert check_defaults_handling(chat.copy_message, chat.bot)

        monkeypatch.setattr(chat.bot, 'copy_message', make_assertion)
        assert chat.copy_message(chat_id='test_copy', message_id=42)

    def test_export_invite_link(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.export_invite_link, Bot.export_chat_invite_link, ['chat_id'], []
        )
        assert check_shortcut_call(chat.export_invite_link, chat.bot, 'export_chat_invite_link')
        assert check_defaults_handling(chat.export_invite_link, chat.bot)

        monkeypatch.setattr(chat.bot, 'export_chat_invite_link', make_assertion)
        assert chat.export_invite_link()

    def test_create_invite_link(self, monkeypatch, chat):
        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id

        assert check_shortcut_signature(
            Chat.create_invite_link, Bot.create_chat_invite_link, ['chat_id'], []
        )
        assert check_shortcut_call(chat.create_invite_link, chat.bot, 'create_chat_invite_link')
        assert check_defaults_handling(chat.create_invite_link, chat.bot)

        monkeypatch.setattr(chat.bot, 'create_chat_invite_link', make_assertion)
        assert chat.create_invite_link()

    def test_edit_invite_link(self, monkeypatch, chat):
        link = "ThisIsALink"

        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['invite_link'] == link

        assert check_shortcut_signature(
            Chat.edit_invite_link, Bot.edit_chat_invite_link, ['chat_id'], []
        )
        assert check_shortcut_call(chat.edit_invite_link, chat.bot, 'edit_chat_invite_link')
        assert check_defaults_handling(chat.edit_invite_link, chat.bot)

        monkeypatch.setattr(chat.bot, 'edit_chat_invite_link', make_assertion)
        assert chat.edit_invite_link(invite_link=link)

    def test_revoke_invite_link(self, monkeypatch, chat):
        link = "ThisIsALink"

        def make_assertion(*_, **kwargs):
            return kwargs['chat_id'] == chat.id and kwargs['invite_link'] == link

        assert check_shortcut_signature(
            Chat.revoke_invite_link, Bot.revoke_chat_invite_link, ['chat_id'], []
        )
        assert check_shortcut_call(chat.revoke_invite_link, chat.bot, 'revoke_chat_invite_link')
        assert check_defaults_handling(chat.revoke_invite_link, chat.bot)

        monkeypatch.setattr(chat.bot, 'revoke_chat_invite_link', make_assertion)
        assert chat.revoke_invite_link(invite_link=link)

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
