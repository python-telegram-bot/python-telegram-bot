#!/usr/bin/env python


class Location(object):
    def __init__(self,
                 longitude,
                 latitude):
        self.longitude = longitude
        self.latitude = latitude

    @staticmethod
    def de_json(data):
        return Location(longitude=data.get('longitude', None),
                        latitude=data.get('latitude', None))
