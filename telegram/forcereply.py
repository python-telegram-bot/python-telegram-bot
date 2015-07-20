#!/usr/bin/env python


from telegram import TelegramObject


class ForceReply(TelegramObject):
    def __init__(self,
                 force_reply=True,
                 selective=None):
        self.force_reply = force_reply
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ForceReply(force_reply=data.get('force_reply', None),
                          selective=data.get('selective', None))

    def to_dict(self):
        data = {'force_reply': self.force_reply}
        if self.selective:
            data['selective'] = self.selective
        return data
