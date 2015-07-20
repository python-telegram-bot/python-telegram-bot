#!/usr/bin/env python


from telegram import TelegramObject


class Location(TelegramObject):
    def __init__(self,
                 longitude,
                 latitude):
        self.longitude = longitude
        self.latitude = latitude

    @staticmethod
    def de_json(data):
        return Location(longitude=data.get('longitude', None),
                        latitude=data.get('latitude', None))

    def to_dict(self):
        data = {'longitude': self.longitude,
                'latitude': self.latitude}
        return data
