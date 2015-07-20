#!/usr/bin/env python


import json
from abc import ABCMeta, abstractmethod


class TelegramObject(object):
    """Base class for most telegram object"""

    __metaclass__ = ABCMeta

    def __str__(self):
        return self.to_data()

    def __getitem__(self, item):
        return self.__dict__[item]

    @staticmethod
    def de_json(data):
        raise NotImplementedError

    def to_json(self):
        return json.dumps(self.to_data())

    @abstractmethod
    def to_data(self):
        return
