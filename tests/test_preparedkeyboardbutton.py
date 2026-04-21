#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
# along with this program. If not, see [http://www.gnu.org/licenses/].

from telegram import PreparedKeyboardButton
from tests.auxil.slots import mro_slots


class TestPreparedKeyboardButtonWithoutRequest:
    id_ = "prepared-button-id"

    def test_slot_behaviour(self):
        prepared_button = PreparedKeyboardButton(self.id_)
        for attr in prepared_button.__slots__:
            assert getattr(prepared_button, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(prepared_button)) == len(set(mro_slots(prepared_button)))

    def test_de_json(self):
        prepared_button = PreparedKeyboardButton.de_json({"id": self.id_}, None)
        assert prepared_button.api_kwargs == {}
        assert prepared_button.id == self.id_

    def test_to_dict(self):
        prepared_button = PreparedKeyboardButton(self.id_)
        assert prepared_button.to_dict() == {"id": self.id_}

    def test_equality(self):
        assert PreparedKeyboardButton(self.id_) == PreparedKeyboardButton(self.id_)
        assert PreparedKeyboardButton(self.id_) != PreparedKeyboardButton("other")
