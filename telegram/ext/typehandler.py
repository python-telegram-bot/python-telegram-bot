#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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

""" This module contains the base class for handlers as used by the
Dispatcher """

from .handler import Handler


class TypeHandler(Handler):

    def __init__(self, type, callback, pass_update_queue=False):
        super(Handler).__init__(callback, pass_update_queue)
        self.type = type

    def checkUpdate(self, update):
        return isinstance(update, self.type)

    def handleUpdate(self, update, dispatcher):
        optional_args = self.collectOptionalArgs(dispatcher)

        self.callback(dispatcher.bot, update, **optional_args)
