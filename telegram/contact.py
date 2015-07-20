#!/usr/bin/env python


from telegram import TelegramObject


class Contact(TelegramObject):
    def __init__(self,
                 phone_number,
                 first_name,
                 last_name=None,
                 user_id=None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

    @staticmethod
    def de_json(data):
        return Contact(phone_number=data.get('phone_number', None),
                       first_name=data.get('first_name', None),
                       last_name=data.get('last_name', None),
                       user_id=data.get('user_id', None))

    def to_dict(self):
        data = {'phone_number': self.phone_number,
                'first_name': self.first_name}
        if self.last_name:
            data['last_name'] = self.last_name
        if self.user_id:
            data['user_id'] = self.user_id
        return data
