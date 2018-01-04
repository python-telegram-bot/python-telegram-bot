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
import datetime

import pytest

from telegram import Message, User, Chat, MessageEntity
from telegram.ext import Filters, BaseFilter


@pytest.fixture(scope='function')
def message():
    return Message(0, User(0, 'Testuser', False), datetime.datetime.now(), Chat(0, 'private'))


@pytest.fixture(scope='function',
                params=MessageEntity.ALL_TYPES)
def message_entity(request):
    return MessageEntity(request.param, 0, 0, url='', user='')


class TestFilters(object):
    def test_filters_all(self, message):
        assert Filters.all(message)

    def test_filters_text(self, message):
        message.text = 'test'
        assert Filters.text(message)
        message.text = '/test'
        assert not Filters.text(message)

    def test_filters_command(self, message):
        message.text = 'test'
        assert not Filters.command(message)
        message.text = '/test'
        assert Filters.command(message)

    def test_filters_reply(self, message):
        another_message = Message(1, User(1, 'TestOther', False), datetime.datetime.now(),
                                  Chat(0, 'private'))
        message.text = 'test'
        assert not Filters.reply(message)
        message.reply_to_message = another_message
        assert Filters.reply(message)

    def test_filters_audio(self, message):
        assert not Filters.audio(message)
        message.audio = 'test'
        assert Filters.audio(message)

    def test_filters_document(self, message):
        assert not Filters.document(message)
        message.document = 'test'
        assert Filters.document(message)

    def test_filters_photo(self, message):
        assert not Filters.photo(message)
        message.photo = 'test'
        assert Filters.photo(message)

    def test_filters_sticker(self, message):
        assert not Filters.sticker(message)
        message.sticker = 'test'
        assert Filters.sticker(message)

    def test_filters_video(self, message):
        assert not Filters.video(message)
        message.video = 'test'
        assert Filters.video(message)

    def test_filters_voice(self, message):
        assert not Filters.voice(message)
        message.voice = 'test'
        assert Filters.voice(message)

    def test_filters_contact(self, message):
        assert not Filters.contact(message)
        message.contact = 'test'
        assert Filters.contact(message)

    def test_filters_location(self, message):
        assert not Filters.location(message)
        message.location = 'test'
        assert Filters.location(message)

    def test_filters_venue(self, message):
        assert not Filters.venue(message)
        message.venue = 'test'
        assert Filters.venue(message)

    def test_filters_status_update(self, message):
        assert not Filters.status_update(message)

        message.new_chat_members = ['test']
        assert Filters.status_update(message)
        assert Filters.status_update.new_chat_members(message)
        message.new_chat_members = None

        message.left_chat_member = 'test'
        assert Filters.status_update(message)
        assert Filters.status_update.left_chat_member(message)
        message.left_chat_member = None

        message.new_chat_title = 'test'
        assert Filters.status_update(message)
        assert Filters.status_update.new_chat_title(message)
        message.new_chat_title = ''

        message.new_chat_photo = 'test'
        assert Filters.status_update(message)
        assert Filters.status_update.new_chat_photo(message)
        message.new_chat_photo = None

        message.delete_chat_photo = True
        assert Filters.status_update(message)
        assert Filters.status_update.delete_chat_photo(message)
        message.delete_chat_photo = False

        message.group_chat_created = True
        assert Filters.status_update(message)
        assert Filters.status_update.chat_created(message)
        message.group_chat_created = False

        message.supergroup_chat_created = True
        assert Filters.status_update(message)
        assert Filters.status_update.chat_created(message)
        message.supergroup_chat_created = False

        message.channel_chat_created = True
        assert Filters.status_update(message)
        assert Filters.status_update.chat_created(message)
        message.channel_chat_created = False

        message.migrate_to_chat_id = 100
        assert Filters.status_update(message)
        assert Filters.status_update.migrate(message)
        message.migrate_to_chat_id = 0

        message.migrate_from_chat_id = 100
        assert Filters.status_update(message)
        assert Filters.status_update.migrate(message)
        message.migrate_from_chat_id = 0

        message.pinned_message = 'test'
        assert Filters.status_update(message)
        assert Filters.status_update.pinned_message(message)
        message.pinned_message = None

    def test_filters_forwarded(self, message):
        assert not Filters.forwarded(message)
        message.forward_date = 'test'
        assert Filters.forwarded(message)

    def test_filters_game(self, message):
        assert not Filters.game(message)
        message.game = 'test'
        assert Filters.game(message)

    def test_entities_filter(self, message, message_entity):
        message.entities = [message_entity]
        assert Filters.entity(message_entity.type)(message)

        message.entities = []
        assert not Filters.entity(MessageEntity.MENTION)(message)

        second = message_entity.to_dict()
        second['type'] = 'bold'
        second = MessageEntity.de_json(second, None)
        message.entities = [message_entity, second]
        assert Filters.entity(message_entity.type)(message)

    def test_private_filter(self, message):
        assert Filters.private(message)
        message.chat.type = 'group'
        assert not Filters.private(message)

    def test_group_filter(self, message):
        assert not Filters.group(message)
        message.chat.type = 'group'
        assert Filters.group(message)
        message.chat.type = 'supergroup'
        assert Filters.group(message)

    def test_filters_user(self):
        with pytest.raises(ValueError, match='user_id or username'):
            Filters.user(user_id=1, username='user')
        with pytest.raises(ValueError, match='user_id or username'):
            Filters.user()

    def test_filters_user_id(self, message):
        assert not Filters.user(user_id=1)(message)
        message.from_user.id = 1
        assert Filters.user(user_id=1)(message)
        message.from_user.id = 2
        assert Filters.user(user_id=[1, 2])(message)
        assert not Filters.user(user_id=[3, 4])(message)

    def test_filters_username(self, message):
        assert not Filters.user(username='user')(message)
        assert not Filters.user(username='Testuser')(message)
        message.from_user.username = 'user'
        assert Filters.user(username='@user')(message)
        assert Filters.user(username='user')(message)
        assert Filters.user(username=['user1', 'user', 'user2'])(message)
        assert not Filters.user(username=['@username', '@user_2'])(message)

    def test_filters_chat(self):
        with pytest.raises(ValueError, match='chat_id or username'):
            Filters.chat(chat_id=-1, username='chat')
        with pytest.raises(ValueError, match='chat_id or username'):
            Filters.chat()

    def test_filters_chat_id(self, message):
        assert not Filters.chat(chat_id=-1)(message)
        message.chat.id = -1
        assert Filters.chat(chat_id=-1)(message)
        message.chat.id = -2
        assert Filters.chat(chat_id=[-1, -2])(message)
        assert not Filters.chat(chat_id=[-3, -4])(message)

    def test_filters_chat_username(self, message):
        assert not Filters.chat(username='chat')(message)
        message.chat.username = 'chat'
        assert Filters.chat(username='@chat')(message)
        assert Filters.chat(username='chat')(message)
        assert Filters.chat(username=['chat1', 'chat', 'chat2'])(message)
        assert not Filters.chat(username=['@chat1', 'chat_2'])(message)

    def test_filters_invoice(self, message):
        assert not Filters.invoice(message)
        message.invoice = 'test'
        assert Filters.invoice(message)

    def test_filters_successful_payment(self, message):
        assert not Filters.successful_payment(message)
        message.successful_payment = 'test'
        assert Filters.successful_payment(message)

    def test_language_filter_single(self, message):
        message.from_user.language_code = 'en_US'
        assert (Filters.language('en_US'))(message)
        assert (Filters.language('en'))(message)
        assert not (Filters.language('en_GB'))(message)
        assert not (Filters.language('da'))(message)
        message.from_user.language_code = 'da'
        assert not (Filters.language('en_US'))(message)
        assert not (Filters.language('en'))(message)
        assert not (Filters.language('en_GB'))(message)
        assert (Filters.language('da'))(message)

    def test_language_filter_multiple(self, message):
        f = Filters.language(['en_US', 'da'])
        message.from_user.language_code = 'en_US'
        assert f(message)
        message.from_user.language_code = 'en_GB'
        assert not f(message)
        message.from_user.language_code = 'da'
        assert f(message)

    def test_and_filters(self, message):
        message.text = 'test'
        message.forward_date = True
        assert (Filters.text & Filters.forwarded)(message)
        message.text = '/test'
        assert not (Filters.text & Filters.forwarded)(message)
        message.text = 'test'
        message.forward_date = None
        assert not (Filters.text & Filters.forwarded)(message)

        message.text = 'test'
        message.forward_date = True
        assert (Filters.text & Filters.forwarded & Filters.private)(message)

    def test_or_filters(self, message):
        message.text = 'test'
        assert (Filters.text | Filters.status_update)(message)
        message.group_chat_created = True
        assert (Filters.text | Filters.status_update)(message)
        message.text = None
        assert (Filters.text | Filters.status_update)(message)
        message.group_chat_created = False
        assert not (Filters.text | Filters.status_update)(message)

    def test_and_or_filters(self, message):
        message.text = 'test'
        message.forward_date = True
        assert (Filters.text & (Filters.forwarded | Filters.status_update))(message)
        message.forward_date = False
        assert not (Filters.text & (Filters.forwarded | Filters.status_update))(message)
        message.pinned_message = True
        assert (Filters.text & (Filters.forwarded | Filters.status_update)(message))

        assert str((Filters.text & (Filters.forwarded | Filters.entity(
            MessageEntity.MENTION)))) == '<Filters.text and <Filters.forwarded or ' \
                                         'Filters.entity(mention)>>'

    def test_inverted_filters(self, message):
        message.text = '/test'
        assert Filters.command(message)
        assert not (~Filters.command)(message)
        message.text = 'test'
        assert not Filters.command(message)
        assert (~Filters.command)(message)

    def test_inverted_and_filters(self, message):
        message.text = '/test'
        message.forward_date = 1
        assert (Filters.forwarded & Filters.command)(message)
        assert not (~Filters.forwarded & Filters.command)(message)
        assert not (Filters.forwarded & ~Filters.command)(message)
        assert not (~(Filters.forwarded & Filters.command))(message)
        message.forward_date = None
        assert not (Filters.forwarded & Filters.command)(message)
        assert (~Filters.forwarded & Filters.command)(message)
        assert not (Filters.forwarded & ~Filters.command)(message)
        assert (~(Filters.forwarded & Filters.command))(message)
        message.text = 'test'
        assert not (Filters.forwarded & Filters.command)(message)
        assert not (~Filters.forwarded & Filters.command)(message)
        assert not (Filters.forwarded & ~Filters.command)(message)
        assert (~(Filters.forwarded & Filters.command))(message)

    def test_faulty_custom_filter(self, message):
        class _CustomFilter(BaseFilter):
            pass

        custom = _CustomFilter()

        with pytest.raises(NotImplementedError):
            (custom & Filters.text)(message)

    def test_custom_unnamed_filter(self, message):
        class Unnamed(BaseFilter):
            def filter(self, mes):
                return True

        unnamed = Unnamed()
        assert str(unnamed) == Unnamed.__name__
