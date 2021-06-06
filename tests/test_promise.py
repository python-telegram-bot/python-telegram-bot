#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import logging
import pytest

from telegram import TelegramError
from telegram.ext.utils.promise import Promise


class TestPromise:
    """
    Here we just test the things that are not covered by the other tests anyway
    """

    test_flag = False

    def test_slot_behaviour(self, recwarn, mro_slots):
        inst = Promise(self.test_call, [], {})
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not inst.__dict__, f"got missing slot(s): {inst.__dict__}"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"
        inst.custom, inst.args = 'should give warning', []
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def test_call(self):
        def callback():
            self.test_flag = True

        promise = Promise(callback, [], {})
        promise()

        assert promise.done
        assert self.test_flag

    def test_run_with_exception(self):
        def callback():
            raise TelegramError('Error')

        promise = Promise(callback, [], {})
        promise.run()

        assert promise.done
        assert not self.test_flag
        assert isinstance(promise.exception, TelegramError)

    def test_wait_for_exception(self):
        def callback():
            raise TelegramError('Error')

        promise = Promise(callback, [], {})
        promise.run()

        with pytest.raises(TelegramError, match='Error'):
            promise.result()

    def test_done_cb_after_run(self):
        def callback():
            return "done!"

        def done_callback(_):
            self.test_flag = True

        promise = Promise(callback, [], {})
        promise.run()
        promise.add_done_callback(done_callback)
        assert promise.result() == "done!"
        assert self.test_flag is True

    def test_done_cb_after_run_excp(self):
        def callback():
            return "done!"

        def done_callback(_):
            raise Exception("Error!")

        promise = Promise(callback, [], {})
        promise.run()
        assert promise.result() == "done!"
        with pytest.raises(Exception) as err:
            promise.add_done_callback(done_callback)
            assert str(err) == "Error!"

    def test_done_cb_before_run(self):
        def callback():
            return "done!"

        def done_callback(_):
            self.test_flag = True

        promise = Promise(callback, [], {})
        promise.add_done_callback(done_callback)
        assert promise.result(0) != "done!"
        assert self.test_flag is False
        promise.run()
        assert promise.result() == "done!"
        assert self.test_flag is True

    def test_done_cb_before_run_excp(self, caplog):
        def callback():
            return "done!"

        def done_callback(_):
            raise Exception("Error!")

        promise = Promise(callback, [], {})
        promise.add_done_callback(done_callback)
        assert promise.result(0) != "done!"
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            promise.run()
        assert len(caplog.records) == 2
        assert caplog.records[0].message == (
            "`done_callback` of a Promise raised the following exception."
            " The exception won't be handled by error handlers."
        )
        assert caplog.records[1].message.startswith("Full traceback:")
        assert promise.result() == "done!"

    def test_done_cb_not_run_on_excp(self):
        def callback():
            raise TelegramError('Error')

        def done_callback(_):
            self.test_flag = True

        promise = Promise(callback, [], {})
        promise.add_done_callback(done_callback)
        promise.run()
        assert isinstance(promise.exception, TelegramError)
        assert promise.done
        assert self.test_flag is False
