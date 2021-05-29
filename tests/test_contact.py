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

import pytest
from flaky import flaky

from telegram import Contact, Voice
from telegram.error import BadRequest


@pytest.fixture(scope='class')
def contact():
    return Contact(
        TestContact.phone_number,
        TestContact.first_name,
        TestContact.last_name,
        TestContact.user_id,
    )


class TestContact:
    phone_number = '+11234567890'
    first_name = 'Leandro'
    last_name = 'Toledo'
    user_id = 23

    def test_slot_behaviour(self, contact, recwarn, mro_slots):
        for attr in contact.__slots__:
            assert getattr(contact, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not contact.__dict__, f"got missing slot(s): {contact.__dict__}"
        assert len(mro_slots(contact)) == len(set(mro_slots(contact))), "duplicate slot"
        contact.custom, contact.first_name = 'should give warning', self.first_name
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_de_json_required(self, bot):
        json_dict = {'phone_number': self.phone_number, 'first_name': self.first_name}
        contact = Contact.de_json(json_dict, bot)

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name

    def test_de_json_all(self, bot):
        json_dict = {
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_id': self.user_id,
        }
        contact = Contact.de_json(json_dict, bot)

        assert contact.phone_number == self.phone_number
        assert contact.first_name == self.first_name
        assert contact.last_name == self.last_name
        assert contact.user_id == self.user_id

    def test_send_with_contact(self, monkeypatch, bot, chat_id, contact):
        def test(url, data, **kwargs):
            phone = data['phone_number'] == contact.phone_number
            first = data['first_name'] == contact.first_name
            last = data['last_name'] == contact.last_name
            return phone and first and last

        monkeypatch.setattr(bot.request, 'post', test)
        message = bot.send_contact(contact=contact, chat_id=chat_id)
        assert message

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    def test_send_contact_default_allow_sending_without_reply(
        self, default_bot, chat_id, contact, custom
    ):
        reply_to_message = default_bot.send_message(chat_id, 'test')
        reply_to_message.delete()
        if custom is not None:
            message = default_bot.send_contact(
                chat_id,
                contact=contact,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = default_bot.send_contact(
                chat_id, contact=contact, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                default_bot.send_contact(
                    chat_id, contact=contact, reply_to_message_id=reply_to_message.message_id
                )

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
        e = Voice('', 'unique_id', 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
