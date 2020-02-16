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
import datetime

import pytest

from telegram import Message, User, InlineQuery, Update, Bot, ChatMember, Chat, TelegramError
from telegram.ext import Role, Roles, MessageHandler, InlineQueryHandler, Filters


@pytest.fixture(scope='function')
def update():
    return Update(0, Message(0, User(0, 'Testuser', False), datetime.datetime.utcnow(),
                             Chat(0, 'private')))


@pytest.fixture(scope='class')
def roles(bot):
    return Roles(bot)


@pytest.fixture(scope='function')
def parent_role():
    return Role(name='parent_role')


@pytest.fixture(scope='function')
def role():
    return Role(name='role')


class TestRole(object):
    def test_creation(self, parent_role):
        r = Role(parent_role=parent_role)
        assert r.user_ids == set()
        assert r.child_roles == set()
        assert r.name == 'Role({})'
        assert r in parent_role.child_roles
        parent_role.remove_child_role(r)

        r = Role(1)
        assert r.user_ids == set([1])
        assert r.child_roles == set()
        assert r.name == 'Role({1})'
        assert r not in parent_role.child_roles

        r = Role([1, 2])
        assert r.user_ids == set([1, 2])
        assert r.child_roles == set()
        assert r.name == 'Role({1, 2})'
        assert r not in parent_role.child_roles

        r = Role([1, 2], name='role')
        assert r.user_ids == set([1, 2])
        assert r.child_roles == set()
        assert r.name == 'Role(role)'
        assert r not in parent_role.child_roles

    def test_add_member(self, role):
        assert role.user_ids == set()
        role.add_member(1)
        assert role.user_ids == set([1])
        role.add_member(2)
        assert role.user_ids == set([1, 2])
        role.add_member(1)
        assert role.user_ids == set([1, 2])

    def test_kick_member(self, role):
        assert role.user_ids == set()
        role.add_member(1)
        role.add_member(2)
        assert role.user_ids == set([1, 2])
        role.kick_member(1)
        assert role.user_ids == set([2])
        role.kick_member(1)
        assert role.user_ids == set([2])
        role.kick_member(2)
        assert role.user_ids == set()

    def test_add_remove_child_role(self, role, parent_role):
        assert role.child_roles == set()
        role.add_child_role(parent_role)
        assert role.child_roles == set([parent_role])
        role.add_child_role(role)
        assert role.child_roles == set([parent_role, role])
        role.add_child_role(parent_role)
        assert role.child_roles == set([parent_role, role])

        role.remove_child_role(parent_role)
        assert role.child_roles == set([role])
        role.remove_child_role(role)
        assert role.child_roles == set()
        role.remove_child_role(role)
        assert role.child_roles == set()

    def test_add_remove_parent_role(self, role, parent_role):
        assert parent_role.child_roles == set()
        role.add_parent_role(parent_role)
        assert parent_role.child_roles == set([role])
        role.add_parent_role(role)
        assert role.child_roles == set([role])

        role.remove_parent_role(parent_role)
        assert parent_role.child_roles == set()
        role.remove_parent_role(role)
        assert role.child_roles == set()
        role.remove_parent_role(role)
        assert role.child_roles == set()

    def test_equality(self, role, parent_role):
        r = Role(name='test')
        assert role == parent_role
        role.add_child_role(r)
        assert role != parent_role
        parent_role.add_child_role(r)
        assert role == parent_role
        role.add_parent_role(r)
        assert role != parent_role
        parent_role.add_parent_role(r)
        assert role == parent_role

        role.add_member(1)
        assert role != parent_role
        parent_role.add_member(1)
        assert role == parent_role
        role.add_member(2)
        assert role != parent_role
        parent_role.add_member(2)
        assert role == parent_role
        role.kick_member(2)
        assert role != parent_role
        parent_role.kick_member(2)
        assert role == parent_role

    def test_comparison(self, role, parent_role):
        assert not role < parent_role
        assert not parent_role < role
        parent_role.add_child_role(role)
        assert role < parent_role
        assert role <= parent_role
        assert parent_role >= role
        assert parent_role > role

        parent_role.remove_child_role(role)
        assert not role < parent_role
        assert not parent_role < role
        role.add_parent_role(parent_role)
        assert role < parent_role
        assert role <= parent_role
        assert parent_role >= role
        assert parent_role > role

    def test_hash(self):
        a = Role([1, 2])
        b = Role([1, 2])
        c = Role([2, 1])
        d = Role()
        e = Role([1, 2, 3])

        assert hash(a) == hash(b)
        assert hash(a) == hash(c)
        assert hash(a) != hash(d)
        assert hash(a) != hash(e)

    def test_handler_simple(self, update, role, parent_role):
        handler = MessageHandler(role, None)
        assert not handler.check_update(update)

        role.add_member(0)
        parent_role.add_member(1)

        assert handler.check_update(update)
        update.message.from_user.id = 1
        assert not handler.check_update(update)
        parent_role.add_child_role(role)
        assert handler.check_update(update)

    def test_handler_merged_roles(self, update, role):
        role.add_member(0)
        r = Role(0)

        handler = MessageHandler(role & (~r), None)
        assert not handler.check_update(update)

        r = Role(1)
        handler = MessageHandler(role & r, None)
        assert not handler.check_update(update)
        handler = MessageHandler(role | r, None)
        assert handler.check_update(update)

    def test_handler_merged_filters(self, update, role):
        role.add_member(0)

        handler = MessageHandler(role & Filters.sticker, None)
        assert not handler.check_update(update)
        handler = MessageHandler(role | Filters.sticker, None)
        assert handler.check_update(update)
        handler = MessageHandler(role & Filters.all, None)
        assert handler.check_update(update)

    def test_handler_without_user(self, update, role):
        handler = MessageHandler(role, None)
        role.add_member(0)
        update.message = None
        update.channel_post = True
        assert not handler.check_update(update)


class TestRoles(object):
    def test_creation(self, bot):
        roles = Roles(bot)
        assert isinstance(roles, dict)
        assert isinstance(roles.ADMINS, Role)
        assert isinstance(roles.CHAT_ADMINS, Role)
        assert isinstance(roles.CHAT_ADMINS._bot, Bot)
        assert isinstance(roles.CHAT_CREATOR, Role)
        assert isinstance(roles.CHAT_CREATOR._bot, Bot)
        assert isinstance(roles._bot, Bot)

    def test_add_kick_admin(self, roles):
        assert roles.ADMINS.user_ids == set()
        roles.add_admin(1)
        assert roles.ADMINS.user_ids == set([1])
        roles.add_admin(2)
        assert roles.ADMINS.user_ids == set([1, 2])
        roles.kick_admin(1)
        assert roles.ADMINS.user_ids == set([2])
        roles.kick_admin(2)
        assert roles.ADMINS.user_ids == set()

    def test_raise_errors(self, roles):
        with pytest.raises(NotImplementedError, match='remove_role'):
            del roles['test']
        with pytest.raises(ValueError, match='immutable'):
            roles['test'] = True
        with pytest.raises(ValueError, match='immutable'):
            roles.setdefault('test', None)
        with pytest.raises(ValueError, match='immutable'):
            roles.update({'test': None})
        with pytest.raises(NotImplementedError, match='remove_role'):
            roles.pop('test', None)
        with pytest.raises(NotImplementedError, match='remove_role'):
            roles.popitem('test')
        with pytest.raises(NotImplementedError, match='remove_role'):
            roles.clear()
        with pytest.raises(NotImplementedError):
            roles.copy()

    def test_dict_functionality(self, roles):
        roles.add_role('role0', 0)
        roles.add_role('role1', 1)
        roles.add_role('role2', 2)

        assert 'role2' in roles
        assert 'role3' not in roles

        a = set([name for name in roles])
        assert a == set(['role{}'.format(k) for k in range(3)])

        b = {name: role.user_ids for name, role in roles.items()}
        assert b == {'role{}'.format(k): set([k]) for k in range(3)}

        c = [name for name in roles.keys()]
        assert c == ['role{}'.format(k) for k in range(3)]

        d = [r.user_ids for r in roles.values()]
        assert d == [set([k]) for k in range(3)]

    def test_add_remove_role(self, roles, parent_role):
        roles.add_role('role', parent_role=parent_role)
        role = roles['role']
        assert role.user_ids == set()
        assert role.parent_roles == set([parent_role, roles.ADMINS])
        assert role.name == 'Role(role)'
        assert role in roles.ADMINS.child_roles

        with pytest.raises(ValueError, match='Role name is already taken.'):
            roles.add_role('role', parent_role=parent_role)

        roles.remove_role('role')
        assert not roles.get('role', None)
        assert role not in roles.ADMINS.child_roles

    def test_handler_admins(self, roles, update):
        roles.add_role('role', 0)
        roles.add_admin(1)
        handler = MessageHandler(roles['role'], None)
        assert handler.check_update(update)
        update.message.from_user.id = 1
        assert handler.check_update(update)
        roles.kick_admin(1)
        assert not handler.check_update(update)

    def test_chat_admins_simple(self, roles, update, monkeypatch):
        def admins(*args, **kwargs):
            return [ChatMember(User(0, 'TestUser0', False), 'administrator'),
                    ChatMember(User(1, 'TestUser1', False), 'creator')]

        monkeypatch.setattr(roles._bot, 'get_chat_administrators', admins)
        handler = MessageHandler(roles.CHAT_ADMINS, None)

        update.message.from_user.id = 2
        assert not handler.check_update(update)
        update.message.from_user.id = 1
        assert handler.check_update(update)
        update.message.from_user.id = 0
        assert handler.check_update(update)

    def test_chat_admins_no_chat(self, roles, update):
        update.message = None
        update.inline_query = InlineQuery(1, User(0, 'TestUser', False), 'query', 0)
        handler = InlineQueryHandler(None, roles=roles.CHAT_ADMINS)

        assert not handler.check_update(update)

    def test_chat_admins_no_user(self, roles, update):
        update.message = None
        update.channel_post = Message(1, None, datetime.datetime.utcnow(), Chat(0, 'channel'))
        handler = InlineQueryHandler(None, roles=roles.CHAT_ADMINS)

        assert not handler.check_update(update)

    def test_chat_creator_simple(self, roles, update, monkeypatch):
        def member(*args, **kwargs):
            if args[1] == 0:
                return ChatMember(User(0, 'TestUser0', False), 'administrator')
            if args[1] == 1:
                return ChatMember(User(1, 'TestUser1', False), 'creator')
            raise TelegramError('User is not a member')

        monkeypatch.setattr(roles._bot, 'get_chat_member', member)
        handler = MessageHandler(roles.CHAT_CREATOR, None)

        update.message.from_user.id = 0
        assert not handler.check_update(update)
        update.message.from_user.id = 1
        assert handler.check_update(update)
        update.message.from_user.id = 2
        assert not handler.check_update(update)

    def test_chat_creator_no_chat(self, roles, update):
        update.message = None
        update.inline_query = InlineQuery(1, User(0, 'TestUser', False), 'query', 0)
        handler = InlineQueryHandler(None, roles=roles.CHAT_CREATOR)

        assert not handler.check_update(update)

    def test_chat_creator_no_user(self, roles, update):
        update.message = None
        update.channel_post = Message(1, None, datetime.datetime.utcnow(), Chat(0, 'channel'))
        handler = InlineQueryHandler(None, roles=roles.CHAT_CREATOR)

        assert not handler.check_update(update)
