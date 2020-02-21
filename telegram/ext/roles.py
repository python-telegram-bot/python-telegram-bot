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

from telegram import ChatMember, TelegramError, Bot
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
        if both :attr:`parent_roles` and :attr:`chat_ids` coincide, use :attr:`equals`.

    Attributes:
        chat_ids (set(:obj:`int`)): The ids of the users/chats of this role. Updates
            will only be parsed, if the id of :attr:`telegram.Update.effective_user` or
            :attr:`telegram.Update.effective_chat` respectiveley is listed here. May be empty.
        parent_roles (set(:class:`telegram.ext.Role`)): Parent roles of this role. All the parent
            roles can do anything, this role can do. May be empty.
        name (:obj:`str`): A string representation of this role.

    Args:
        chat_ids (:obj:`int` | iterable(:obj:`int`), optional): The ids of the users/chats of this
            role. Updates will only be parsed, if the id of :attr:`telegram.Update.effective_user`
            or :attr:`telegram.Update.effective_chat` respectiveley is listed here.
        parent_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`)), optional):
            Parent roles of this role.
        name (:obj:`str`, optional): A name for this role.

    """
    update_filter = True

    def __init__(self, chat_ids=None, parent_roles=None, name=None):
        if chat_ids is None:
            chat_ids = set()
        super(Role, self).__init__(chat_ids)
        self._name = name
        self.parent_roles = set()
        if isinstance(parent_roles, Role):
            self.add_parent_role(parent_roles)
        elif parent_roles is not None:
            for pr in parent_roles:
                self.add_parent_role(pr)

    @property
    def chat_ids(self):
        return self.user_ids

    @chat_ids.setter
    def chat_ids(self, chat_id):
        self.user_ids = chat_id

    @property
    def name(self):
        if self._name:
            return 'Role({})'.format(self._name)
        elif self.chat_ids:
            return 'Role({})'.format(self.chat_ids)
        else:
            return 'Role({})'

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user:
            if user.id in self.chat_ids:
                return True
        if chat:
            if chat.id in self.chat_ids:
                return True
        if user or chat:
            return any([parent(update) for parent in self.parent_roles])

    def add_member(self, chat_id):
        """Adds a user/chat to this role. Will do nothing, if user/chat is already present.

        Args:
            chat_id (:obj:`int`): The users/chats id
        """
        self.chat_ids.add(chat_id)

    def kick_member(self, chat_id):
        """Kicks a user/chat to from role. Will do nothing, if user/chat is not present.

        Args:
            chat_id (:obj:`int`): The users/chats id
        """
        self.chat_ids.discard(chat_id)

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
        """Test if two roles are equal in terms of hierarchy. Returns ``True``, if the chat_ids
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
        return self.chat_ids == other.chat_ids

    def __hash__(self):
        return id(self)

    def __deepcopy__(self, memo):
        new_role = Role(chat_ids=self.chat_ids, name=self._name)
        memo[id(self)] = new_role
        for pr in self.parent_roles:
            new_role.add_parent_role(deepcopy(pr, memo))
        return new_role


class _chat_admins(Role):
    def __init__(self, bot):
        super(_chat_admins, self).__init__(name='chat_admins')
        self._bot = bot

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            admins = self._bot.get_chat_administrators(chat.id)
            return user.id in [m.user.id for m in admins]


class _chat_creator(Role):
    def __init__(self, bot):
        super(_chat_creator, self).__init__(name='chat_creator')
        self._bot = bot

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            try:
                member = self._bot.get_chat_member(chat.id, user.id)
                return member.status == ChatMember.CREATOR
            except TelegramError:
                # user is not a chat member or bot has no access
                return False


class Roles(dict):
    """This class represents a collection of :class:`telegram.ext.Role` s that can be used to
    manage access control to functionality of a bot. Each role can be accessed by its name, e.g.::

            roles.add_role('my_role')
            role = roles['my_role']

    Note:
        In fact, :class:`telegram.ext.Roles` inherits from :obj:`dict` and thus provides most
        methods needed for the common use cases. Methods that are *not* supported are:
        ``__delitem__``, ``__setitem__``, ``setdefault``, ``update``, ``pop``, ``popitem``,
        ``clear`` and ``copy``.
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

    def set_bot(self, bot):
        """If for some reason you can't pass the bot on initialization, you can set it with this
        method. Make sure to set the bot before the first call of :attr:`CHAT_ADMINS` or
        :attr:`CHAT_CREATOR`.

        Args:
            bot (:class:`telegram.Bot`): The bot to set.

        Raises:
            ValueError
        """
        if isinstance(self._bot, Bot):
            raise ValueError('Bot is already set for this Roles instance')
        self._bot = bot

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

    def add_admin(self, chat_id):
        """Adds a user/chat to the :attr:`ADMINS` role. Will do nothing if user/chat is already
        present.

        Args:
            chat_id (:obj:`int`): The users id
        """
        self.ADMINS.add_member(chat_id)

    def kick_admin(self, chat_id):
        """Kicks a user/chat from the :attr:`ADMINS` role. Will do nothing if user/chat is not
        present.

        Args:
            chat_id (:obj:`int`): The users/chats id
        """
        self.ADMINS.kick_member(chat_id)

    def add_role(self, name, chat_ids=None, parent_roles=None):
        """Creates and registers a new role. :attr:`ADMINS` will automatically be added to
        roles parent roles, i.e. admins can do everyhing. The role can be accessed by it's
        name.

        Args:
            name (:obj:`str`, optional): A name for this role.
            chat_ids (:obj:`int` | iterable(:obj:`int`), optional): The ids of the users/chats of
                this role.
            parent_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`), optional):
                Parent roles of this role.

        Raises:
            ValueError
        """
        if name in self:
            raise ValueError('Role name is already taken.')
        role = Role(chat_ids=chat_ids, parent_roles=parent_roles, name=name)
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
            new_roles.add_role(name=role._name, chat_ids=role.chat_ids)
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
                inner_tmp = {'name': role._name, 'chat_ids': sorted(role.chat_ids)}
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
            role = Role(name=tmp['name'], chat_ids=tmp['chat_ids'])
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
