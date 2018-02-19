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

import pytest

from telegram.ext import Handler


class TestHandler(object):
    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, bot, update):
        pass

    def callback_some_passable(self, bot, update, update_queue, chat_data):
        pass

    def callback_all_passable(self, bot, update, update_queue, job_queue, chat_data, user_data):
        pass

    def test_set_autowired_flags_all(self):
        handler = Handler(self.callback_all_passable, autowire=True)
        assert handler._autowire_initialized is False
        assert handler.pass_update_queue is False
        assert handler.pass_job_queue is False
        assert handler.pass_chat_data is False
        assert handler.pass_user_data is False

        handler.set_autowired_flags()

        assert handler._autowire_initialized is True
        assert handler.pass_update_queue is True
        assert handler.pass_job_queue is True
        assert handler.pass_chat_data is True
        assert handler.pass_user_data is True

    def test_set_autowired_flags_some(self):
        handler = Handler(self.callback_some_passable, autowire=True)
        assert handler.pass_update_queue is False
        assert handler.pass_chat_data is False

        handler.set_autowired_flags()

        assert handler._autowire_initialized is True
        assert handler.pass_update_queue is True
        assert handler.pass_chat_data is True

    def test_set_autowired_flags_wrong(self):
        handler = Handler(self.callback_all_passable, autowire=True)
        with pytest.raises(UserWarning):
            handler.set_autowired_flags({'kektus'})
        with pytest.raises(UserWarning):
            handler.set_autowired_flags({'chat_data', 'kektus'})
        with pytest.raises(UserWarning):
            handler.set_autowired_flags({'bot', 'update'})

    def test_autowire_and_pass(self):
        handler = Handler(self.callback_all_passable, autowire=True, pass_chat_data=True)
        with pytest.raises(UserWarning):
            handler.set_autowired_flags()

    def test_not_autowired_set_flags(self):
        handler = Handler(self.callback_all_passable, autowire=False)
        with pytest.raises(ValueError):
            handler.set_autowired_flags()

    def test_autowire_reinitialize(self):
        handler = Handler(self.callback_all_passable, autowire=True)
        assert handler._autowire_initialized is False
        assert handler.pass_update_queue is False
        assert handler.pass_job_queue is False
        assert handler.pass_chat_data is False
        assert handler.pass_user_data is False

        handler.set_autowired_flags()

        assert handler._autowire_initialized is True
        assert handler.pass_update_queue is True
        assert handler.pass_job_queue is True
        assert handler.pass_chat_data is True
        assert handler.pass_user_data is True

        handler.callback = self.callback_some_passable
        handler.set_autowired_flags()

        assert handler._autowire_initialized is True
        assert handler.pass_update_queue is True
        assert handler.pass_job_queue is False
        assert handler.pass_chat_data is True
        assert handler.pass_user_data is False

    def test_get_available_pass_flags(self):
        handler = Handler(self.callback_all_passable, autowire=True)
        assert handler.pass_update_queue is False
        assert handler.pass_job_queue is False
        assert handler.pass_chat_data is False
        assert handler.pass_user_data is False

        handler.set_autowired_flags()

        assert set(handler._get_available_pass_flags()) == {'pass_update_queue', 'pass_job_queue',
                                                            'pass_chat_data',
                                                            'pass_user_data'}
