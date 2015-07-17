from abc import ABCMeta, abstractmethod
from telegram import TelegramError


class Base(object):

    """Base class for most telegram object"""

    __metaclass__ = ABCMeta

    def __str__(self):
        return self.to_json()

    def __getitem__(self, item):
        try:
            return self.__dict__[item]
        except KeyError as e:
            raise TelegramError(str(e))

    @staticmethod
    def de_json(data):
        pass

    @abstractmethod
    def to_json(self):
        pass