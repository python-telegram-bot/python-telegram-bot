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
import time

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

    ``role_1 < role_2`` will be true, if ``role_2`` is a parent of ``role_1`` or a parents of one
    of ``role_1`` s parents and similarly for ``role_1 < role_2``.
    ``role_2 >= role_3`` will be true, if ``role_3`` is ``role_2`` or ``role_2 > role_3`` and
    similarly for ``role_2 <= role_3``.

    Note:
        If two roles are not related, i.e. neither is a (indirect) parent of the other, comparing
        the roles will always yield ``False``.

    Warning:
        ``role_1 == role_2`` does not test for the hierarchical order of the roles, but in fact if
        both roles are the same object. To test for equality in terms of hierarchical order, i.e.
        if :attr:`child_roles` and :attr:`chat_ids` coincide, use :attr:`equals`.

    Roles can be combined using bitwise operators:

    And:

        >>> (Roles(name='group_1') & Roles(name='user_2'))

    Grants access only for ``user_2`` within the chat ``group_1``.

    Or:

        >>> (Roles(name='group_1') | Roles(name='user_2'))

    Grants access for ``user_2`` and the whole chat ``group_1``.

    Not:

        >>> ~ Roles(name='user_1')

    Grants access to everyone except ``user_1``

    Note:
        Negated roles do `not` exclude their parent roles. E.g. with

            >>> ~ Roles(name='user_1', parent_roles=Role(name='user_2'))

        ``user_2`` will still have access, where ``user_1`` is restricted. Child roles, however
        will be excluded.

    Also works with more than two roles:

        >>> (Roles(name='group_1') & (Roles(name='user_2') | Roles(name='user_3')))
        >>> Roles(name='group_1') & (~ FRoles(name='user_2'))

    Note:
        Roles use the same short circuiting logic that pythons `and`, `or` and `not`.
        This means that for example:

            >>> Role(chat_ids=123) | Role(chat_ids=456)

        With an update from user ``123``, will only ever evaluate the first role.

    Attributes:
        chat_ids (set(:obj:`int`)): The ids of the users/chats of this role. Updates
            will only be parsed, if the id of :attr:`telegram.Update.effective_user` or
            :attr:`telegram.Update.effective_chat` respectiveley is listed here. May be empty.
        parent_roles (set(:class:`telegram.ext.Role`)): Parent roles of this role. All the parent
            roles can do anything, this role can do. May be empty.
        child_roles (set(:class:`telegram.ext.Role`)): Child roles of this role. This role can do
            anything, its child roles can do. May be empty.

    Args:
        chat_ids (:obj:`int` | iterable(:obj:`int`), optional): The ids of the users/chats of this
            role. Updates will only be parsed, if the id of :attr:`telegram.Update.effective_user`
            or :attr:`telegram.Update.effective_chat` respectiveley is listed here.
        parent_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`)), optional):
            Parent roles of this role.
        child_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`)), optional):
            Child roles of this role.
        name (:obj:`str`, optional): A name for this role.

    """
    update_filter = True

    def __init__(self, chat_ids=None, parent_roles=None, child_roles=None, name=None):
        if chat_ids is None:
            chat_ids = set()
        super(Role, self).__init__(chat_ids)
        self.name = name

        self.parent_roles = set()
        if isinstance(parent_roles, Role):
            self.add_parent_role(parent_roles)
        elif parent_roles is not None:
            for pr in parent_roles:
                self.add_parent_role(pr)

        self.child_roles = set()
        if isinstance(child_roles, Role):
            self.add_child_role(child_roles)
        elif child_roles is not None:
            for cr in child_roles:
                self.add_child_role(cr)

        self._inverted = False

    def __invert__(self):
        self._inverted = True
        return super(Role, self).__invert__()

    @property
    def chat_ids(self):
        return self.user_ids

    @chat_ids.setter
    def chat_ids(self, chat_id):
        self.user_ids = chat_id

    def filter_children(self, user, chat):
        # filters only downward
        if user and user.id in self.chat_ids:
            return True
        if chat and chat.id in self.chat_ids:
            return True
        if any([child.filter_children(user, chat) for child in self.child_roles]):
            return True

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and user.id in self.chat_ids:
            return True
        if chat and chat.id in self.chat_ids:
            return True
        if user or chat:
            if self._inverted:
                # If this is an inverted role (i.e. ~role) and we arrived here, the user is
                # either ...
                if self.filter_children(user, chat):
                    # ... in a child role of this. In this case, and must be excluded. Since the
                    # output of this will be negated, return True
                    return True
                # ... not in a child role of this and must *nto* be excluded. In particular, we
                # dont want to exclude the parents (see below). Since the output of this will be
                # negated, return False
                return False
            else:
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
        """Adds a parent role to this role. Also adds this role to the parents child roles. Will do
        nothing, if parent role is already present.

        Args:
            parent_role (:class:`telegram.ext.Role`): The parent role
        """
        if self is parent_role:
            raise ValueError('You must not add a role as its own parent!')
        if self >= parent_role:
            raise ValueError('You must not add a child role as a parent!')
        self.parent_roles.add(parent_role)
        parent_role.child_roles.add(self)

    def remove_parent_role(self, parent_role):
        """Removes a parent role from this role. Also removes this role from the parents child
        roles. Will do nothing, if parent role is not present.

        Args:
            parent_role (:class:`telegram.ext.Role`): The parent role
        """
        self.parent_roles.discard(parent_role)
        parent_role.child_roles.discard(self)

    def add_child_role(self, child_role):
        """Adds a child role to this role. Also adds this role to the childs parent roles. Will do
        nothing, if child role is already present.

        Args:
            child_role (:class:`telegram.ext.Role`): The child role
        """
        if self is child_role:
            raise ValueError('You must not add a role as its own child!')
        if self <= child_role:
            raise ValueError('You must not add a parent role as a child!')
        self.child_roles.add(child_role)
        child_role.parent_roles.add(self)

    def remove_child_role(self, child_role):
        """Removes a child role from this role. Also removes this role from the childs parent
        roles. Will do nothing, if child role is not present.

        Args:
            child_role (:class:`telegram.ext.Role`): The child role
        """
        self.child_roles.discard(child_role)
        child_role.parent_roles.discard(self)

    def __lt__(self, other):
        # Test for hierarchical order
        if isinstance(other, Role):
            return any([pr <= other for pr in self.parent_roles])
        return False

    def __le__(self, other):
        # Test for hierarchical order
        return self is other or self < other

    def __gt__(self, other):
        # Test for hierarchical order
        if isinstance(other, Role):
            return any([self >= pr for pr in other.parent_roles])
        return False

    def __ge__(self, other):
        # Test for hierarchical order
        return self is other or self > other

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return not self == other

    def equals(self, other):
        """Test if two roles are equal in terms of hierarchy. Returns ``True``, if the chat_ids
        coincide and the child roles are equal in terms of this method. Note, that the result of
        this comparison may change by adding or removing child/parent roles or members.

        Args:
            other (:class:`telegram.ext.Role`):

        Returns:
            :obj:`bool`:
        """
        if self.chat_ids == other.chat_ids:
            if len(self.child_roles) == len(other.child_roles):
                if len(self.child_roles) == 0:
                    return True
                for cr in self.child_roles:
                    if not any([cr.equals(ocr) for ocr in other.child_roles]):
                        return False
                for ocr in other.child_roles:
                    if not any([ocr.equals(cr) for cr in self.child_roles]):
                        return False
                return True
        return False

    def __hash__(self):
        return id(self)

    def __deepcopy__(self, memo):
        new_role = Role(chat_ids=self.chat_ids, name=self.name)
        memo[id(self)] = new_role
        for pr in self.parent_roles:
            new_role.add_parent_role(deepcopy(pr, memo))
        for cr in self.child_roles:
            new_role.add_child_role(deepcopy(cr, memo))
        return new_role

    def __repr__(self):
        if self.name:
            return 'Role({})'.format(self.name)
        elif self.chat_ids:
            return 'Role({})'.format(self.chat_ids)
        else:
            return 'Role({})'


class ChatAdminsRole(Role):
    """A :class:`telegram.ext.Role` that allows only the administrators of a chat. Private chats
    always allowed. To minimize the number of API calls, for each chat the admins will be cached.

    Attributes:
        parent_roles (set(:class:`telegram.ext.Role`)): Parent roles of this role. All the parent
            roles can do anything, this role can do. May be empty.
        child_roles (set(:class:`telegram.ext.Role`)): Child roles of this role. This role can do
            anything, its child roles can do. May be empty.
        timeout (:obj:`int`): The caching timeout in seconds. For each chat, the admins will be
            cached and refreshed only after this timeout.

    Args:
        bot (:class:`telegram.Bot`): A bot to use for getting the administrators of a chat.
        timeout (:obj:`int`, optional): The caching timeout in seconds. For each chat, the admins
            will be cached and refreshed only after this timeout. Defaults to ``1800`` (half an
            hour).

    """
    def __init__(self, bot, timeout=1800):
        super(ChatAdminsRole, self).__init__(name='chat_admins')
        self.bot = bot
        self.cache = {}
        self.timeout = timeout

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            # Always true in private chats
            if user.id == chat.id:
                return True
            # Check for cached info first
            if (self.cache.get(chat.id, None)
                    and (time.time() - self.cache[chat.id][0]) < self.timeout):
                return user.id in self.cache[chat.id][1]
            admins = [m.user.id for m in self.bot.get_chat_administrators(chat.id)]
            self.cache[chat.id] = (time.time(), admins)
            return user.id in admins

    def __deepcopy__(self, memo):
        new_role = super(ChatAdminsRole, self).__deepcopy__(memo)
        new_role.bot = self.bot
        new_role.cache = self.cache
        new_role.timeout = self.timeout
        return new_role


class ChatCreatorRole(Role):
    """A :class:`telegram.ext.Role` that allows only the creator of a chat. Private chats are
    always allowed. To minimize the number of API calls, for each chat the creator will be saved.

    Attributes:
        parent_roles (set(:class:`telegram.ext.Role`)): Parent roles of this role. All the parent
            roles can do anything, this role can do. May be empty.
        child_roles (set(:class:`telegram.ext.Role`)): Child roles of this role. This role can do
            anything, its child roles can do. May be empty.

    Args:
        bot (:class:`telegram.Bot`): A bot to use for getting the creator of a chat.

    """
    def __init__(self, bot):
        super(ChatCreatorRole, self).__init__(name='chat_creator')
        self.bot = bot
        self.cache = {}

    def filter(self, update):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            # Always true in private chats
            if user.id == chat.id:
                return True
            # Check for cached info first
            if self.cache.get(chat.id, None):
                return user.id == self.cache[chat.id]
            try:
                member = self.bot.get_chat_member(chat.id, user.id)
                if member.status == ChatMember.CREATOR:
                    self.cache[chat.id] = user.id
                    return True
                return False
            except TelegramError:
                # user is not a chat member or bot has no access
                return False

    def __deepcopy__(self, memo):
        new_role = super(ChatCreatorRole, self).__deepcopy__(memo)
        new_role.bot = self.bot
        new_role.cache = self.cache
        return new_role


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
        CHAT_ADMINS (:class:`telegram.ext.roles.ChatAdminsRole`): Use this role to restrict access
            to admins of a chat. Handlers with this role wont handle updates that don't have an
            ``effective_chat``. Admins are cached for each chat.
        CHAT_CREATOR (:class:`telegram.ext.roles.ChatCreatorRole`): Use this role to restrict
            access to the creator of a chat. Handlers with this role wont handle updates that don't
            have an ``effective_chat``.

    Args:
        bot (:class:`telegram.Bot`): A bot associated with this instance.

    """

    def __init__(self, bot):
        super(Roles, self).__init__()
        self.bot = bot
        self.ADMINS = Role(name='admins')
        self.CHAT_ADMINS = ChatAdminsRole(bot=self.bot)
        self.CHAT_CREATOR = ChatCreatorRole(bot=self.bot)

    def set_bot(self, bot):
        """If for some reason you can't pass the bot on initialization, you can set it with this
        method. Make sure to set the bot before the first call of :attr:`CHAT_ADMINS` or
        :attr:`CHAT_CREATOR`.

        Args:
            bot (:class:`telegram.Bot`): The bot to set.

        Raises:
            ValueError
        """
        if isinstance(self.bot, Bot):
            raise ValueError('Bot is already set for this Roles instance')
        self.bot = bot

    def __delitem__(self, key):
        """"""  # Remove method from docs
        raise NotImplementedError('Please use remove_role.')

    def __setitem__(self, key, value):
        """"""  # Remove method from docs
        raise ValueError('Roles are immutable!')

    def setitem(self, key, value):
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

    def add_role(self, name, chat_ids=None, parent_roles=None, child_roles=None):
        """Creates and registers a new role. :attr:`ADMINS` will automatically be added to the
        roles parent roles, i.e. admins can do everything. The role can be accessed by it's
        name.

        Args:
            name (:obj:`str`, optional): A name for this role.
            chat_ids (:obj:`int` | iterable(:obj:`int`), optional): The ids of the users/chats of
                this role.
            parent_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`), optional):
                Parent roles of this role.
            child_roles (:class:`telegram.ext.Role` | set(:class:`telegram.ext.Role`), optional):
                Child roles of this role.

        Raises:
            ValueError
        """
        if name in self:
            raise ValueError('Role name is already taken.')
        role = Role(chat_ids=chat_ids, parent_roles=parent_roles,
                    child_roles=child_roles, name=name)
        self.setitem(name, role)
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
        new_roles = Roles(self.bot)
        new_roles.CHAT_ADMINS.timeout = self.CHAT_ADMINS.timeout
        memo[id(self)] = new_roles
        for chat_id in self.ADMINS.chat_ids:
            new_roles.add_admin(chat_id)
        for role in self.values():
            new_roles.add_role(name=role.name, chat_ids=role.chat_ids)
            for pr in role.parent_roles:
                if pr is not self.ADMINS:
                    new_roles[role.name].add_parent_role(deepcopy(pr, memo))
            for cr in role.child_roles:
                new_roles[role.name].add_child_role(deepcopy(cr, memo))
        return new_roles

    def encode_to_json(self):
        """Helper method to encode a roles object to a JSON-serializable way. Use
        :attr:`decode_from_json` to decode.

        Args:
            roles (:class:`telegram.ext.Roles`): The roles object to transofrm to JSON.

        Returns:
            :obj:`str`: The JSON-serialized roles object
        """
        def _encode_role_to_json(role, memo, trace):
            id_ = id(role)
            if id_ not in memo and id_ not in trace:
                trace.append(id_)
                inner_tmp = {'name': role.name, 'chat_ids': sorted(role.chat_ids)}
                inner_tmp['parent_roles'] = [
                    _encode_role_to_json(pr, memo, trace) for pr in role.parent_roles
                ]
                inner_tmp['child_roles'] = [
                    _encode_role_to_json(cr, memo, trace) for cr in role.child_roles
                ]
                memo[id_] = inner_tmp
            return id_

        tmp = {'admins': id(self.ADMINS), 'admins_timeout': self.CHAT_ADMINS.timeout,
               'roles': [], 'memo': {}}
        tmp['roles'] = [_encode_role_to_json(self[name], tmp['memo'], []) for name in self]
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
            memo[id_] = role
            for pid in tmp['parent_roles']:
                role.add_parent_role(_decode_role_from_json(pid, memo))
            for cid in tmp['child_roles']:
                role.add_child_role(_decode_role_from_json(cid, memo))
            return role

        tmp = json.loads(json_string)
        memo = tmp['memo']
        roles = Roles(bot)
        roles.ADMINS = _decode_role_from_json(tmp['admins'], memo)
        roles.CHAT_ADMINS.timeout = tmp['admins_timeout']
        for id_ in tmp['roles']:
            role = _decode_role_from_json(id_, memo)
            roles.setitem(role.name, role)
        return roles
