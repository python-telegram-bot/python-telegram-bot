#!/usr/bin/env python


from .replymarkup import ReplyMarkup


class ReplyKeyboardMarkup(ReplyMarkup):
    def __init__(self,
                 keyboard,
                 resize_keyboard=None,
                 one_time_keyboard=None,
                 selective=None):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ReplyKeyboardMarkup(keyboard=data.get('keyboard', None),
                                   resize_keyboard=data.get(
                                       'resize_keyboard', None
                                       ),
                                   one_time_keyboard=data.get(
                                       'one_time_keyboard', None
                                       ),
                                   selective=data.get('selective', None))

    def to_dict(self):
        data = {'keyboard': self.keyboard}
        if self.resize_keyboard:
            data['resize_keyboard'] = self.resize_keyboard
        if self.one_time_keyboard:
            data['one_time_keyboard'] = self.one_time_keyboard
        if self.selective:
            data['selective'] = self.selective
        return data
