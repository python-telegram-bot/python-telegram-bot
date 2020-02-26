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
import sys

from copy import deepcopy
from telegram import Message, User, InlineQuery, Update, ChatMember, Chat, TelegramError
from telegram.ext import Role, Roles, MessageHandler, InlineQueryHandler


@pytest.fixture(scope='function')
def update():
    return Update(0, Message(0, User(0, 'Testuser', False), datetime.datetime.utcnow(),
                             Chat(0, 'private')))


@pytest.fixture(scope='function')
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
        r = Role(parent_roles=[parent_role, parent_role])
        assert r.chat_ids == set()
        assert r.name == 'Role({})'
        assert r.parent_roles == set([parent_role])

        r = Role(child_roles=[parent_role, parent_role])
        assert r.chat_ids == set()
        assert r.name == 'Role({})'
        assert r.child_roles == set([parent_role])

        parent_role_2 = Role(name='parent_role_2')
        r = Role(parent_roles=[parent_role, parent_role_2])
        assert r.chat_ids == set()
        assert r.name == 'Role({})'
        assert r.parent_roles == set([parent_role, parent_role_2])

        r = Role(1)
        assert r.chat_ids == set([1])
        assert r.name == 'Role({1})'
        assert r.parent_roles == set()

        r = Role([1, 2])
        assert r.chat_ids == set([1, 2])
        assert r.name == 'Role({1, 2})'
        assert r.parent_roles == set()

        r = Role([1, 2], name='role')
        assert r.chat_ids == set([1, 2])
        assert r.name == 'Role(role)'
        assert r.parent_roles == set()

    def test_chat_ids_property(self, role):
        assert role.chat_ids is role.user_ids
        role.chat_ids = 5
        assert role.chat_ids == set([5])

    def test_add_member(self, role):
        assert role.chat_ids == set()
        role.add_member(1)
        assert role.chat_ids == set([1])
        role.add_member(2)
        assert role.chat_ids == set([1, 2])
        role.add_member(1)
        assert role.chat_ids == set([1, 2])

    def test_kick_member(self, role):
        assert role.chat_ids == set()
        role.add_member(1)
        role.add_member(2)
        assert role.chat_ids == set([1, 2])
        role.kick_member(1)
        assert role.chat_ids == set([2])
        role.kick_member(1)
        assert role.chat_ids == set([2])
        role.kick_member(2)
        assert role.chat_ids == set()

    def test_add_remove_parent_role(self, role, parent_role):
        assert role.parent_roles == set()
        parent_role_2 = Role(chat_ids=456, name='pr2')
        role.add_parent_role(parent_role)
        assert role.parent_roles == set([parent_role])
        role.add_parent_role(parent_role_2)
        assert role.parent_roles == set([parent_role, parent_role_2])

        role.remove_parent_role(parent_role)
        assert role.parent_roles == set([parent_role_2])
        role.remove_parent_role(parent_role_2)
        assert role.parent_roles == set()

        with pytest.raises(ValueError, match='You must not add a role as its own parent!'):
            role.add_parent_role(role)

        parent_role.add_parent_role(role)
        with pytest.raises(ValueError, match='You must not add a child role as a parent!'):
            role.add_parent_role(parent_role)

    def test_add_remove_child_role(self, role, parent_role):
        assert role.child_roles == set()
        parent_role_2 = Role(chat_ids=456, name='pr2')
        role.add_child_role(parent_role)
        assert role.child_roles == set([parent_role])
        role.add_child_role(parent_role_2)
        assert role.child_roles == set([parent_role, parent_role_2])

        role.remove_child_role(parent_role)
        assert role.child_roles == set([parent_role_2])
        role.remove_child_role(parent_role_2)
        assert role.child_roles == set()

        with pytest.raises(ValueError, match='You must not add a role as its own child!'):
            role.add_child_role(role)

        parent_role.add_child_role(role)
        with pytest.raises(ValueError, match='You must not add a parent role as a child!'):
            role.add_child_role(parent_role)

    def test_equals(self, role, parent_role):
        r = Role(name='test')
        r2 = Role(name='test')
        assert role.equals(parent_role)
        role.add_child_role(r)
        assert not role.equals(parent_role)
        parent_role.add_child_role(r2)
        assert role.equals(parent_role)

        role.add_member(1)
        assert not role.equals(parent_role)
        parent_role.add_member(1)
        assert role.equals(parent_role)
        role.add_member(2)
        assert not role.equals(parent_role)
        parent_role.add_member(2)
        assert role.equals(parent_role)
        role.kick_member(2)
        assert not role.equals(parent_role)
        parent_role.kick_member(2)
        assert role.equals(parent_role)

        r.add_member(1)
        assert not role.equals(parent_role)
        r2.add_member(1)
        assert role.equals(parent_role)

    def test_comparison(self, role, parent_role):
        assert not role < parent_role
        assert not parent_role < role
        assert role <= role
        assert role >= role
        assert parent_role <= parent_role
        assert parent_role >= parent_role

        role.add_parent_role(parent_role)
        assert role < parent_role
        assert role <= parent_role
        assert parent_role >= role
        assert parent_role > role

        role.remove_parent_role(parent_role)
        assert not role < parent_role
        assert not parent_role < role

        role.add_parent_role(parent_role)
        assert role < parent_role
        assert role <= parent_role
        assert parent_role >= role
        assert parent_role > role

    def test_hash(self, role, parent_role):
        assert role != parent_role
        assert hash(role) != hash(parent_role)

        assert role == role
        assert hash(role) == hash(role)

        assert parent_role == parent_role
        assert hash(parent_role) == hash(parent_role)

    def test_deepcopy(self, role, parent_role):
        role.add_parent_role(parent_role)
        child = Role(name='cr', chat_ids=[1, 2, 3], parent_roles=role)
        crole = deepcopy(role)

        assert role is not crole
        assert role.equals(crole)
        assert role.chat_ids is not crole.chat_ids
        assert role.chat_ids == crole.chat_ids
        assert role.parent_roles is not crole.parent_roles
        parent = role.parent_roles.pop()
        cparent = crole.parent_roles.pop()
        assert parent is not cparent
        assert parent.equals(cparent)
        cchild = crole.child_roles.pop()
        assert child is not cchild
        assert child.equals(cchild)

    def test_handler_user(self, update, role, parent_role):
        handler = MessageHandler(role, None)
        assert not handler.check_update(update)

        role.add_member(0)
        parent_role.add_member(1)

        assert handler.check_update(update)
        update.message.from_user.id = 1
        update.message.chat.id = 1
        assert not handler.check_update(update)
        role.add_parent_role(parent_role)
        assert handler.check_update(update)

    def test_handler_chat(self, update, role, parent_role):
        handler = MessageHandler(role, None)
        update.message.chat.id = 5
        assert not handler.check_update(update)

        role.add_member(5)
        parent_role.add_member(6)

        assert handler.check_update(update)
        update.message.chat.id = 6
        assert not handler.check_update(update)
        role.add_parent_role(parent_role)
        assert handler.check_update(update)

    def test_handler_merged_roles(self, update, role):
        role.add_member(0)
        r = Role(0)

        handler = MessageHandler(None, None, roles=role & (~r))
        assert not handler.check_update(update)

        r = Role(1)
        handler = MessageHandler(None, None, roles=role & r)
        assert not handler.check_update(update)
        handler = MessageHandler(None, None, roles=role | r)
        assert handler.check_update(update)

    def test_handler_allow_parent(self, update, role, parent_role):
        role.add_member(0)
        parent_role.add_member(1)
        role.add_parent_role(parent_role)

        handler = MessageHandler(None, None, roles=~role)
        assert not handler.check_update(update)
        update.message.from_user.id = 1
        update.message.chat.id = 1
        assert handler.check_update(update)

    def test_handler_exclude_children(self, update, role, parent_role):
        role.add_parent_role(parent_role)
        parent_role.add_member(0)
        role.add_member(1)

        handler = MessageHandler(None, None, roles=~parent_role)
        assert not handler.check_update(update)
        update.message.from_user.id = 1
        update.message.chat.id = 1
        assert not handler.check_update(update)

    def test_handler_without_user(self, update, role):
        handler = MessageHandler(role, None)
        role.add_member(0)
        update.message = None
        update.channel_post = Message(0, None, datetime.datetime.utcnow(), Chat(-1, 'channel'))
        assert not handler.check_update(update)

        role.add_member(-1)
        assert handler.check_update(update)


class TestRoles(object):
    def test_creation(self, bot):
        roles = Roles(bot)
        assert isinstance(roles, dict)
        assert isinstance(roles.ADMINS, Role)
        assert isinstance(roles.CHAT_ADMINS, Role)
        assert roles.CHAT_ADMINS._bot is bot
        assert isinstance(roles.CHAT_CREATOR, Role)
        assert roles.CHAT_CREATOR._bot is bot
        assert roles._bot is bot

    def test_set_bot(self, bot):
        roles = Roles(1)
        assert roles._bot == 1
        roles.set_bot(2)
        assert roles._bot == 2
        roles.set_bot(bot)
        assert roles._bot is bot
        with pytest.raises(ValueError, match='already set'):
            roles.set_bot(bot)

    def test_add_kick_admin(self, roles):
        assert roles.ADMINS.chat_ids == set()
        roles.add_admin(1)
        assert roles.ADMINS.chat_ids == set([1])
        roles.add_admin(2)
        assert roles.ADMINS.chat_ids == set([1, 2])
        roles.kick_admin(1)
        assert roles.ADMINS.chat_ids == set([2])
        roles.kick_admin(2)
        assert roles.ADMINS.chat_ids == set()

    def test_equality(self, parent_role, roles, bot):
        parent_role_2 = deepcopy(parent_role)
        child_role = Role(name='child_role')
        child_role_2 = deepcopy(child_role)

        roles2 = Roles(bot)
        assert roles == roles2

        roles.add_admin(1)
        assert roles != roles2

        roles2.add_admin(1)
        assert roles == roles2

        roles.add_role('test_role', chat_ids=123)
        assert roles != roles2

        roles2.add_role('test_role', chat_ids=123)
        assert roles == roles2

        roles.add_role('test_role_2', chat_ids=456)
        assert roles != roles2

        roles2.add_role('test_role_2', chat_ids=456)
        assert roles == roles2

        roles['test_role'].add_parent_role(parent_role)
        roles2['test_role'].add_parent_role(parent_role_2)
        assert roles == roles2

        roles['test_role'].add_child_role(child_role)
        assert roles != roles2

        roles2['test_role'].add_child_role(child_role_2)
        assert roles == roles2

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

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="dicts are not ordered in py<=3.5")
    def test_dict_functionality(self, roles):
        roles.add_role('role0', 0)
        roles.add_role('role1', 1)
        roles.add_role('role2', 2)

        assert 'role2' in roles
        assert 'role3' not in roles

        a = set([name for name in roles])
        assert a == set(['role{}'.format(k) for k in range(3)])

        b = {name: role.chat_ids for name, role in roles.items()}
        assert b == {'role{}'.format(k): set([k]) for k in range(3)}

        c = [name for name in roles.keys()]
        assert c == ['role{}'.format(k) for k in range(3)]

        d = [r.chat_ids for r in roles.values()]
        assert d == [set([k]) for k in range(3)]

    def test_deepcopy(self, roles, parent_role):
        roles.add_admin(123)
        child_role = Role(name='child_role')
        roles.add_role(name='test', chat_ids=[1, 2], parent_roles=parent_role,
                       child_roles=child_role)
        roles.add_role(name='test2', chat_ids=[3, 4], child_roles=roles['test'])
        croles = deepcopy(roles)

        assert croles is not roles
        assert croles == roles
        assert roles.ADMINS is not croles.ADMINS
        assert roles.ADMINS.equals(croles.ADMINS)
        assert roles['test'] is not croles['test']
        assert roles['test'].equals(croles['test'])
        assert roles['test2'] is not croles['test2']
        assert roles['test2'].equals(croles['test2'])

    def test_add_remove_role(self, roles, parent_role):
        roles.add_role('role', parent_roles=parent_role)
        role = roles['role']
        assert role.chat_ids == set()
        assert role.parent_roles == set([parent_role, roles.ADMINS])
        assert role.name == 'Role(role)'
        assert roles.ADMINS in role.parent_roles

        with pytest.raises(ValueError, match='Role name is already taken.'):
            roles.add_role('role', parent_roles=parent_role)

        roles.remove_role('role')
        assert not roles.get('role', None)
        assert roles.ADMINS not in role.parent_roles

    def test_handler_admins(self, roles, update):
        roles.add_role('role', 0)
        roles.add_admin(1)
        handler = MessageHandler(None, None, roles=roles['role'])
        assert handler.check_update(update)
        update.message.from_user.id = 1
        update.message.chat.id = 1
        assert handler.check_update(update)
        roles.kick_admin(1)
        assert not handler.check_update(update)

    def test_handler_admins_merged(self, roles, update):
        roles.add_role('role_1', 0)
        roles.add_role('role_2', 1)
        roles.add_admin(2)
        handler = MessageHandler(None, None, roles=roles['role_1'] & ~roles['role_2'])
        assert handler.check_update(update)
        update.message.from_user.id = 2
        update.message.chat.id = 2
        assert handler.check_update(update)
        roles.kick_admin(2)
        assert not handler.check_update(update)

    def test_chat_admins_simple(self, roles, update, monkeypatch):
        def admins(*args, **kwargs):
            return [ChatMember(User(0, 'TestUser0', False), 'administrator'),
                    ChatMember(User(1, 'TestUser1', False), 'creator')]

        monkeypatch.setattr(roles._bot, 'get_chat_administrators', admins)
        handler = MessageHandler(None, None, roles=roles.CHAT_ADMINS)

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
        handler = MessageHandler(None, None, roles=roles.CHAT_CREATOR)

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

    def test_json_encoding_decoding(self, roles, parent_role, bot):
        child_role = Role(name='child_role')
        roles.add_role('role_1', chat_ids=[1, 2, 3])
        roles.add_role('role_2', chat_ids=[4, 5, 6], parent_roles=parent_role,
                       child_roles=child_role)
        roles.add_role('role_3', chat_ids=[7, 8], parent_roles=parent_role, child_roles=child_role)
        roles.add_admin(9)
        roles.add_admin(10)

        json_str = roles.encode_to_json()
        assert isinstance(json_str, str)
        assert json_str != ''

        rroles = Roles.decode_from_json(json_str, bot)
        assert rroles == roles
        assert rroles._bot is bot
        for name in rroles:
            assert rroles[name] <= rroles.ADMINS
        assert rroles.ADMINS.chat_ids == set([9, 10])
        assert rroles.ADMINS.equals(roles.ADMINS)
        assert rroles['role_1'].chat_ids == set([1, 2, 3])
        assert rroles['role_1'].equals(Role(name='role_1', chat_ids=[1, 2, 3]))
        assert rroles['role_2'].chat_ids == set([4, 5, 6])
        assert rroles['role_2'].equals(Role(name='role_2', chat_ids=[4, 5, 6],
                                       parent_roles=parent_role, child_roles=child_role))
        assert rroles['role_3'].chat_ids == set([7, 8])
        assert rroles['role_3'].equals(Role(name='role_3', chat_ids=[7, 8],
                                            parent_roles=parent_role, child_roles=child_role))
        for name in rroles:
            assert rroles[name] <= rroles.ADMINS
            assert rroles[name] < rroles.ADMINS
            assert rroles.ADMINS >= rroles[name]
            assert rroles.ADMINS > rroles[name]
