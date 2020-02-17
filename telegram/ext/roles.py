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

from copy import deepcopy

from telegram import ChatMember, TelegramError
from .filters import Filters


class Role(Filters.user):
    """This class represents a security level used by :class:`telegram.ext.Roles`. Roles have a
    hierarchie, i.e. a role can do everthing, its child roles can do. To compare two roles you may
    use the following syntax::

        role_1 < role_2
        role 2 >= role_3

    Note:
        ``role_1 == role_2`` does not test for the hierarchical order of the roles, but in fact for
        equality. Two roles are considerd equal, if their :attr:`user_ids` and :attr:`parent_roles`
        coincide.

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
            return other in self.parent_roles
        return False

    def __le__(self, other):
        # Test for hierarchical order
        return self < other

    def __gt__(self, other):
        # Test for hierarchical order
        if isinstance(other, Role):
            return self in other.parent_roles
        return False

    def __ge__(self, other):
        # Test for hierarchical order
        return self > other

    def __eq__(self, other):
        # Acutally tests for equality in terms of parent roles and user_ids
        if isinstance(other, Role):
            return (self.parent_roles == other.parent_roles
                    and self.user_ids == other.user_ids)
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.name, tuple(sorted(self.user_ids))))

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

    def __deepcopy__(self, memo):
        new_roles = Roles(self._bot)
        memo[id(self)] = new_roles
        new_roles.ADMINS = deepcopy(self.ADMINS)
        for role in self.values():
            new_roles.add_role(name=role._name, user_ids=role.user_ids)
            for pr in role.parent_roles:
                new_roles[role._name].add_parent_role(deepcopy(pr, memo))
        return new_roles
