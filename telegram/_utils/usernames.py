#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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


from __future__ import annotations
import typing
"""This module contains auxiliary functionality for building strings for __repr__ method."""


class UserLikeOptional(typing.Protocol):
    """
    Note:
        `User`, `Contact` (and maybe some other) objects always have first_name,
         unlike the `Chat` and `Shared`, were they are optional.
         The `last_name` is always optional.
    """
    last_name: typing.Optional[str]
    username: typing.Optional[str]


class UserLike(UserLikeOptional):
    """
    Note:
        `User`, `Contact` (and maybe some other) objects always have first_name,
         unlike the `Chat` and `Shared`, were they are optional.
         The `last_name` is always optional.
    """
    first_name: str


class MiniUserLike(UserLikeOptional):
    """
    Note:
        `User`, `Contact` (and maybe some other) objects always have first_name,
         unlike the `Chat` and `Shared`, were they are optional.
         The `last_name` is always optional.
    """
    first_name: typing.Optional[str]


@typing.overload
def get_name(user: UserLike) -> str:
    ...


@typing.overload
def get_name(user: MiniUserLike) -> str | None:
    ...


def get_name(user: UserLike | MiniUserLike) -> str | None:
    """:obj:`str`: Convenience property. If available, returns the user's :attr:`username`
    prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`.
    For the UserLike object str will always be returned as `first_name`always exists.
    """
    if user.username:
        return f"@{user.username}"
    return get_full_name(user=user, )


@typing.overload
def get_full_name(user: UserLike) -> str:
    ...

@typing.overload
def get_full_name(user: MiniUserLike) -> str | None:
    ...


def get_full_name(user: UserLike | MiniUserLike) -> str | None:
    """:obj:`str`: Convenience property. The user's :attr:`first_name`, followed by (if
    available) :attr:`last_name`, otherwise None.
    For the UserLike object str will always be returned as `first_name`always exists.
    """
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    if user.first_name or user.last_name:
        return f"{user.first_name or user.last_name}"
    return None


def get_link(user: UserLike | MiniUserLike) -> str | None:
    """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
    of the user.
    """
    if user.username:
        return f"https://t.me/{user.username}"
    return None