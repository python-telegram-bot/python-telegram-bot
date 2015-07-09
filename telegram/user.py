#!/usr/bin/env python


class User(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'id': None,
            'first_name': None,
            'last_name': None,
            'username': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        return User(id=data.get('id', None),
                    first_name=data.get('first_name', None),
                    last_name=data.get('last_name', None),
                    username=data.get('username', None))
