#!/usr/bin/env python


class GroupChat(object):
    def __init__(self,
                 id,
                 title):
        self.id = id
        self.title = title

    @staticmethod
    def de_json(data):
        return GroupChat(id=data.get('id', None),
                         title=data.get('title', None))
