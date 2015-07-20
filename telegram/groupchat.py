#!/usr/bin/env python


from telegram import TelegramObject


class GroupChat(TelegramObject):
    def __init__(self,
                 id,
                 title):
        self.id = id
        self.title = title

    @staticmethod
    def de_json(data):
        return GroupChat(id=data.get('id', None),
                         title=data.get('title', None))

    def to_dict(self):
        data = {'id': self.id,
                'title': self.title}
        return data
