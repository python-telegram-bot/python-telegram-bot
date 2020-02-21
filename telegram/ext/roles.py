#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2020
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
"""This module contains the class Role, which allows to restrict access to handlers."""

try:
    import ujson as json
except ImportError:
    import json

from copy import deepcopy

from telegram import ChatMember, TelegramError
from .filters import Filters


class Role(Filters.user):
    """This class represents a security level used by :class:`telegram.ext.Roles`. Roles have a
    hierarchy, i.e. a role can do everthing, its child roles can do. To compare two roles you may
    use the following syntax::

        role_1 < role_2
        role 2 >= role_3

    Warning:
        ``role_1 == role_2`` does not test for the hierarchical order of the roles, but in fact if
        both roles are the same object. To test for equality in terms of hierarchical order, i.e.
        if both :attr:`parent_roles` and :attr:`user_ids` coincide, use :attr:`equals`.

    Attributes:
        user_ids (set(:obj:`int`)): The ids of the users of this role. May be empty.
        parent_roles (set(:class:`telegram.ext.Role`)): Parent roles of this role. All the parent
            roles can do anything, this role can do. May be empty.
        name (:obj:`str`): A string representation of this role.

    Args:
        user_ids (set(:obj:`int`), optional): The ids of the users of this role.
        parent_roles (set(:class:`telegram.ext.Role`), optional): Parent roles of this role.
        name (:obj:`str`, optional): A name for this role.

    """
    update_filter = True

    def __init__(self, user_ids=None, parent_role=None, name=None):
        if user_ids is None:
            user_ids = set()
        super(Role, self).__init__(user_ids)
        self.parent_roles = set()
        self._name = name
        if parent_role:
            self.add_parent_role(parent_role)

    @property
    def name(self):
        if self._name:
            return 'Role({})'.format(self._name)
        elif self.user_ids or self.usernames:
            return 'Role({})'.format(self.user_ids or self.usernames)
        else:
            return 'Role({})'

    def filter(self, update):
        user = update.effective_user
        if user:
            if user.id in self.user_ids:
                return True
            return any([parent(update) for parent in self.parent_roles])

    def add_member(self, user_id):
        """Adds a user to this role. Will do nothing, if user is already present.

        Args:
            user_id (:obj:`int`): The users id
        """
        self.user_ids.add(user_id)

    def kick_member(self, user_id):
        """Kicks a user to from role. Will do nothing, if user is not present.

        Args:
            user_id (:obj:`int`): The users id
        """
        self.user_ids.discard(user_id)

    def add_parent_role(self, parent_role):
        """Adds a parent role to this role. Will do nothing, if parent role is already present.

        Args:
            parent_role (:class:`telegram.ext.Role`): The parent role
        """
        if self is parent_role:
            raise ValueError('You must not add a role is its own parent!')
        self.parent_roles.add(parent_role)

    def remove_parent_role(self, parent_role):
        """Removes a parent role from this role. Will do nothing, if parent role is not present.

        Args:
            parent_role (:class:`telegram.ext.Role`): The parent role
        """
        self.parent_roles.discard(parent_role)

    def __lt__(self, other):
        # Test for hierarchical order
        if isinstance(other, Role):
            return any([other.equals(pr) for pr in self.parent_roles])
        return False

    def __le__(self, other):
        # Test for hierarchical order
        return self < other

    def __gt__(self, other):
        # Test for hierarchical order
        if isinstance(other, Role):
            return any([self.equals(pr) for pr in other.parent_roles])
        return False

    def __ge__(self, other):
        # Test for hierarchical order
        return self > other

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return not self == other

    def equals(self, other):
        """Test if two roles are equal in terms of hierarchy. Returns ``True``, if the user_ids
        coincide and the parent roles are equal in terms of this method.

        Args:
            other (:class:`telegram.ext.Role`):

        Returns:
            :obj:`bool`:
        """
        for pr in self.parent_roles:
            if not any([pr.equals(opr) for opr in other.parent_roles]):
                return False
        for opr in other.parent_roles:
            if not any([opr.equals(pr) for pr in self.parent_roles]):
                return False
        return self.user_ids == other.user_ids

    def __hash__(self):
        return id(self)

    def __deepcopy__(self, memo):
        new_role = Role(user_ids=self.user_ids, name=self._name)
        memo[id(self)] = new_role
        for pr in self.parent_roles:
            new_role.add_parent_role(deepcopy(pr, memo))
        return new_role


class _chat_admins(Role):
    def __init__(self, bot):
        super(_chat_admins, self).__init__([], name='chat_admins')
        self._bot = bot

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            admins = self._bot.get_chat_administrators(chat.id)
            return user.id in [m.user.id for m in admins]


class _chat_creator(Role):
    def __init__(self, bot):
        super(_chat_creator, self).__init__([], name='chat_creator')
        self._bot = bot

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            try:
                member = self._bot.get_chat_member(chat.id, user.id)
                return member.status == ChatMember.CREATOR
            except TelegramError:
                # user is not a chat member
                return False


class Roles(dict):
    """This class represents a collection of :class:`telegram.ext.Role` s that can be used to
    manage access control to functionality of a bot. Each role can be accessed by its name, e.g.::

            roles.add_role('my_role')
            role = roles['my_role']

    Note:
        In fact, :class:`telegram.ext.Roles` inherits from :obj:`dict` and thus provides most
        methods needed for the common use cases. Methods that are *not* supported are:
        ``__delitem``, ``__setitem__``, ``setdefault``, ``update``, ``pop``, ``popitem``, ``clear``
        and ``copy``.
        Please use :attr:`add_role` and :attr:`remove_role` instead.

    Attributes:
        ADMINS (:class:`telegram.ext.Role`): A role reserved for administrators of the bot. All
            roles added to this instance will be child roles of :attr:`ADMINS`.
        CHAT_ADMINS (:class:`telegram.ext.Role`): Use this role to restrict access to admins of a
            chat. Handlers with this role wont handle updates that don't have an
            ``effective_chat``.
        CHAT_CREATOR (:class:`telegram.ext.Role`): Use this role to restrict access to the creator
            of a chat. Handlers with this role wont handle updates that don't have an
            ``effective_chat``.

    Args:
        bot (:class:`telegram.Bot`): A bot associated with this instance.

    """

    def __init__(self, bot):
        super(Roles, self).__init__()
        self._bot = bot
        self.ADMINS = Role(name='admins')
        self.CHAT_ADMINS = _chat_admins(bot=self._bot)
        self.CHAT_CREATOR = _chat_creator(bot=self._bot)

    def __delitem__(self, key):
        """"""  # Remove method from docs
        raise NotImplementedError('Please use remove_role.')

    def __setitem__(self, key, value):
        """"""  # Remove method from docs
        raise ValueError('Roles are immutable!')

    def _setitem(self, key, value):
        super(Roles, self).__setitem__(key, value)

    def setdefault(self, key, value=None):
        """"""  # Remove method from docs
        raise ValueError('Roles are immutable!')

    def update(self, other):
        """"""  # Remove method from docs
        raise ValueError('Roles are immutable!')

    def pop(self, key, default=None):
        """"""  # Remove method from docs
        raise NotImplementedError('Please use remove_role.')

    def _pop(self, key, default=None):
        return super(Roles, self).pop(key, default)

    def popitem(self, key):
        """"""  # Remove method from docs
        raise NotImplementedError('Please use remove_role.')

    def clear(self):
        """"""  # Remove method from docs
        raise NotImplementedError('Please use remove_role.')

    def copy(self):
        """"""  # Remove method from docs
        raise NotImplementedError

    def add_admin(self, user_id):
        """Adds a user to the :attr:`ADMINS` role. Will do nothing if user is already present.

        Args:
            user_id (:obj:`int`): The users id
        """
        self.ADMINS.add_member(user_id)

    def kick_admin(self, user_id):
        """Kicks a user from the :attr:`ADMINS` role. Will do nothing if user is not present.

        Args:
            user_id (:obj:`int`): The users id
        """
        self.ADMINS.kick_member(user_id)

    def add_role(self, name, user_ids=None, parent_role=None):
        """Creates and registers a new role. :attr:`ADMINS` will automatically be added to
        roles parent roles, i.e. admins can do everyhing. The role can be accessed by it's
        name.

        Args:
            name (:obj:`str`, optional): A name for this role.
            user_ids (set(:obj:`int`), optional): The ids of the users of this role.
            parent_roles (set(:class:`telegram.ext.Role`), optional): Parent roles of this role.

        Raises:
            ValueError
        """
        if name in self:
            raise ValueError('Role name is already taken.')
        role = Role(user_ids=user_ids, parent_role=parent_role, name=name)
        self._setitem(name, role)
        role.add_parent_role(self.ADMINS)

    def remove_role(self, name):
        """Removes a role.

        Args:
            name (:obj:`str`): The name of the role to be removed
        """
        role = self._pop(name, None)
        role.remove_parent_role(self.ADMINS)

    def __eq__(self, other):
        if isinstance(other, Roles):
            for name, role in self.items():
                orole = other.get(name, None)
                if not orole:
                    return False
                if not role.equals(orole):
                    return False
            if any([self.get(name, None) is None for name in other]):
                return False
            return self.ADMINS.equals(other.ADMINS)
        return False

    def __ne__(self, other):
        return not self == other

    def __deepcopy__(self, memo):
        new_roles = Roles(self._bot)
        memo[id(self)] = new_roles
        new_roles.ADMINS = deepcopy(self.ADMINS)
        for role in self.values():
            new_roles.add_role(name=role._name, user_ids=role.user_ids)
            for pr in role.parent_roles:
                new_roles[role._name].add_parent_role(deepcopy(pr, memo))
        return new_roles

    def encode_to_json(self):
        """Helper method to encode a roles object to a JSON-serializable way. Use
        :attr:`decode_from_json` to decode.

        Args:
            roles (:class:`telegram.ext.Roles`): The roles object to transofrm to JSON.

        Returns:
            :obj:`str`: The JSON-serialized roles object
        """
        def _encode_role_to_json(role, memo):
            id_ = id(role)
            if id_ not in memo:
                inner_tmp = {'name': role._name, 'user_ids': sorted(role.user_ids)}
                inner_tmp['restored_from_persistence'] = role.restored_from_persistence
                inner_tmp['parent_roles'] = [
                    _encode_role_to_json(pr, memo) for pr in role.parent_roles
                ]
                memo[id_] = inner_tmp
            return id_

        tmp = {'admins': id(self.ADMINS), 'roles': [], 'memo': {}}
        tmp['roles'] = [_encode_role_to_json(self[name], tmp['memo']) for name in self]
        return json.dumps(tmp)

    @staticmethod
    def decode_from_json(json_string, bot):
        """Helper method to decode a roles object to a JSON-string created with
        :attr:`encode_roles_to_json`.

        Args:
            json_string (:obj:`str`): The roles object as JSON string.
            bot (:class:`telegram.Bot`): The bot to be passed to the roles object.

        Returns:
            :class:`telegram.ext.Roles`: The roles object after decoding
        """
        def _decode_role_from_json(id_, memo):
            id_ = str(id_)
            if isinstance(memo[id_], Role):
                return memo[id_]

            tmp = memo[id_]
            role = Role(name=tmp['name'], user_ids=tmp['user_ids'])
            role.restored_from_persistence = tmp['restored_from_persistence']
            for pid in tmp['parent_roles']:
                role.add_parent_role(_decode_role_from_json(pid, memo))
            return role

        tmp = json.loads(json_string)
        memo = tmp['memo']
        roles = Roles(bot)
        roles.ADMINS = _decode_role_from_json(tmp['admins'], memo)
        for id_ in tmp['roles']:
            role = _decode_role_from_json(id_, memo)
            roles._setitem(role._name, role)
        return roles
