#!/usr/bin/env python


class Contact(object):
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
