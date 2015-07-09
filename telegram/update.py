#!/usr/bin/env python


import json


class Update(object):
    def __init__(self,
                 update_id,
                 message=None):
        self.update_id = update_id
        self.message = message

    @staticmethod
    def de_json(data):
        if 'message' in data:
            from telegram import Message
            message = Message.de_json(data['message'])
        else:
            message = None

        return Update(update_id=data.get('update_id', None),
                      message=message)

    def to_json(self):
        json_data = {'update_id': self.update_id}
        if self.message:
            json_data['message'] = self.message.to_json()
        return json.dumps(json_data)

    def __str__(self):
        return self.to_json()
