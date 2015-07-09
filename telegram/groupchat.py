#!/usr/bin/env python


class GroupChat(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'id': None,
            'title': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @property
    def chat_id(self):
        return self.id

    @staticmethod
    def de_json(data):
        return GroupChat(id=data.get('id', None),
                         title=data.get('title', None))
