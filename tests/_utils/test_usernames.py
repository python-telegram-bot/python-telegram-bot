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
import pytest
from typing import TYPE_CHECKING
from telegram import SharedUser
from tests.test_user import user
from telegram._utils.usernames import get_name, get_full_name, get_link

if TYPE_CHECKING:
    from telegram._utils.usernames import UserLike, MiniUserLike


@pytest.fixture(scope="class")
def shared_user():
    result = SharedUser(
        user_id=1,
        first_name="first\u2022name",
        last_name="last\u2022name",
        username="username",
    )
    result._unfreeze()
    return result


def test_get_name(user, ):
    assert get_name(user=user) == "@username"
    user.username = None
    assert get_name(user=user) == "first\u2022name last\u2022name"


def test_full_name_both_exists(user: UserLike, shared_user: MiniUserLike, ):
    assert get_full_name(user=user) == get_full_name(user=shared_user) == "first\u2022name last\u2022name"


def test_full_name_last_name_missed(user: UserLike, shared_user: MiniUserLike, ):
    user.last_name = shared_user.last_name = None
    assert get_full_name(user=user) == get_full_name(user=shared_user) == "first\u2022name"


def test_full_name_first_name_missed(user: UserLike, shared_user: MiniUserLike, ):
    user.first_name = shared_user.first_name = None
    assert get_full_name(user=user) == get_full_name(user=shared_user) == "last\u2022name"


def test_full_name_both_missed(user: UserLike, shared_user: MiniUserLike, ):
    user.first_name = user.last_name = shared_user.first_name = shared_user.last_name = None
    assert get_full_name(user=user) is get_full_name(user=shared_user) is None


def test_link(user: UserLike, shared_user: MiniUserLike, ):
    assert get_link(user=user, ) == get_link(user=shared_user, ) == f"https://t.me/{user.username}"
    user.username = shared_user.username = None
    assert get_link(user=user, ) is get_link(user=shared_user, ) is None
