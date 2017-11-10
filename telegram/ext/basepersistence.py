#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains the BasePersistence class."""

class BasePersistence(object):
    def __init__(self):
        pass

    def get_job_queue(self):
        raise NotImplemented

    def get_datas(self):
        raise NotImplemented

    def get_conversation(self):
        raise NotImplemented

    def change_conversation(self):
        raise NotImplemented

    def update_job_queue(self):
        raise NotImplemented

    def set_user_data(self):
        raise NotImplemented

    def set_chat_data(self):
        raise NotImplemented

    def flush(self):
        raise NotImplemented
