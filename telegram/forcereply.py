#!/usr/bin/env python


import json
from replymarkup import ReplyMarkup


class ForceReply(ReplyMarkup):
    def __init__(self, **kwargs):
        param_defaults = {
            'force_reply': True,
            'selective': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        return ForceReply(force_reply=data.get('force_reply', None),
                          selective=data.get('selective', None))

    def to_json(self):
        json_data = {'force_reply': self.force_reply}
        if self.selective:
            json_data['selective'] = self.selective
        return json.dumps(json_data)
