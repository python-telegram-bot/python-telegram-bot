#!/usr/bin/env python


class Update(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'update_id': None,
            'message': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        if 'message' in data:
            from telegram import Message
            message = Message.de_json(data['message'])
        else:
            message = None

        return Update(update_id=data.get('update_id', None),
                      message=message)
