#!/usr/bin/env python


import json
from .replymarkup import ReplyMarkup


class ReplyKeyboardHide(ReplyMarkup):
    def __init__(self,
                 hide_keyboard=True,
                 selective=None):
        self.hide_keyboard = hide_keyboard
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ReplyKeyboardHide(hide_keyboard=data.get('hide_keyboard', None),
                                 selective=data.get('selective', None))

    def to_json(self):
        json_data = {'hide_keyboard': self.hide_keyboard}
        if self.selective:
            json_data['selective'] = self.selective
        return json.dumps(json_data)
