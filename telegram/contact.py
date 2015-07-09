#!/usr/bin/env python


class Contact(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'phone_number': None,
            'first_name': None,
            'last_name': None,
            'user_id': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        return Contact(phone_number=data.get('phone_number', None),
                       first_name=data.get('first_name', None),
                       last_name=data.get('last_name', None),
                       user_id=data.get('user_id', None))
