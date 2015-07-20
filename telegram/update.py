#!/usr/bin/env python


from telegram import TelegramObject


class Update(TelegramObject):
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

    def to_dict(self):
        data = {'update_id': self.update_id}
        if self.message:
            data['message'] = self.message.to_dict()
        return data
