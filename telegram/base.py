#!/usr/bin/env python


import json
from abc import ABCMeta, abstractmethod


class TelegramObject(object):
    """Base class for most telegram object"""

    __metaclass__ = ABCMeta

    def __str__(self):
        return str(self.to_dict())

    def __getitem__(self, item):
        return self.__dict__[item]

    @staticmethod
    def de_json(data):
        raise NotImplementedError

    def to_json(self):
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_dict(self):
        return
