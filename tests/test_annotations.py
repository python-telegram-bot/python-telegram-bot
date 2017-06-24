#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents Tests for Telegram Animation"""

import unittest
import sys

sys.path.append('.')

from telegram.ext import *
from tests.base import BaseTest


class AnnotationTest(BaseTest, unittest.TestCase):
    def test_annotations_none(self):
        def x(bot, update):
            pass

        h = MessageHandler(Filters.all, x)
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)

    def test_annotations_single(self):
        def x(bot, update, args: Args):
            pass

        h = CommandHandler('test', x)
        self.assertEqual(h.pass_args, 'args')
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)

    def test_annotations_different_name(self):
        def x(bot, update, not_chat_data: ChatData):
            pass

        h = CommandHandler('test', x)
        self.assertFalse(h.pass_args)
        self.assertEqual(h.pass_chat_data, 'not_chat_data')
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)

    def test_no_annotations(self):
        def x(bot, update, groups, groupdict):  # Has to have this naming
            pass

        h = RegexHandler(r'(.*)', x)
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)
        self.assertFalse(h.pass_groups)
        self.assertFalse(h.pass_groupdict)

        h = RegexHandler(r'(.*)', x, pass_groups=True, pass_groupdict=True)
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)
        self.assertEqual(h.pass_groups, 'groups')
        self.assertEqual(h.pass_groupdict, 'groupdict')

    def test_annotation_overwrite(self):
        def x(bot, update, jq: JobQueue = None):
            pass

        h = MessageHandler(Filters.all, x)
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertEqual(h.pass_job_queue, 'jq')
        self.assertFalse(h.pass_update_queue)
        h = MessageHandler(Filters.all, x, pass_job_queue=False)
        self.assertFalse(h.pass_chat_data)
        self.assertFalse(h.pass_user_data)
        self.assertFalse(h.pass_job_queue)
        self.assertFalse(h.pass_update_queue)

