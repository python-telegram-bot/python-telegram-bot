#!/usr/bin/env python


import json
from .telegram_boject_base import Base


class GroupChat(Base):
    def __init__(self,
                 id,
                 title):
        self.id = id
        self.title = title

    @staticmethod
    def de_json(data):
        return GroupChat(id=data.get('id', None),
                         title=data.get('title', None))

    def to_json(self):
        json_data = {'id': self.id,
                     'title': self.title}
        return json.dumps(json_data)