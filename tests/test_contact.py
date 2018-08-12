#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from telegram import Contact, Voice


@pytest.fixture(scope='class')
def contact():
    return Contact(TestContact.phone_number, TestContact.first_name, TestContact.last_name,
                   TestContact.user_id)


class TestContact(object):
    phone_number = '+11234567890'
    first_name = 'Leandro'
    last_name = 'Toledo'
    user_id = 23

    def test_de_json_required(self, bot):
        json_dict = {'phone_number': self.phone_number, 'first_name': self.first_name}
        contact = Contact.de_json(json_dict, bot)

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name

    def test_de_json_all(self, bot):
        json_dict = {'phone_number': self.phone_number, 'first_name': self.first_name,
                     'last_name': self.last_name, 'user_id': self.user_id}
        contact = Contact.de_json(json_dict, bot)

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name
        assert contact.last_name == self.last_name
        assert contact.user_id == self.user_id

    def test_send_with_contact(self, monkeypatch, bot, chat_id, contact):
        def test(_, url, data, **kwargs):
            phone = data['phone_number'] == contact.phone_number
            first = data['first_name'] == contact.first_name
            last = data['last_name'] == contact.last_name
            return phone and first and last

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        message = bot.send_contact(contact=contact, chat_id=chat_id)
        assert message

    def test_send_contact_without_required(self, bot, chat_id):
        with pytest.raises(ValueError, match='Either contact or phone_number and first_name'):
            bot.send_contact(chat_id=chat_id)

    def test_to_dict(self, contact):
        contact_dict = contact.to_dict()

        assert isinstance(contact_dict, dict)
        assert contact_dict['phone_number'] == contact.phone_number
        assert contact_dict['first_name'] == contact.first_name
        assert contact_dict['last_name'] == contact.last_name
        assert contact_dict['user_id'] == contact.user_id

    def test_equality(self):
        a = Contact(self.phone_number, self.first_name)
        b = Contact(self.phone_number, self.first_name)
        c = Contact(self.phone_number, '')
        d = Contact('', self.first_name)
        e = Voice('', 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
