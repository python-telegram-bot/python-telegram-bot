#!/usr/bin/env python


import json
from .replymarkup import ReplyMarkup


class ForceReply(ReplyMarkup):
    def __init__(self,
                 force_reply=True,
                 selective=None):
        self.force_reply = force_reply
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ForceReply(force_reply=data.get('force_reply', None),
                          selective=data.get('selective', None))

    def to_json(self):
        json_data = {'force_reply': self.force_reply}
        if self.selective:
            json_data['selective'] = self.selective
        return json.dumps(json_data)
