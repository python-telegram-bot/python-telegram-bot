#!/usr/bin/env python


import json


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

    def to_json(self):
        json_data = {'longitude': self.longitude,
                     'latitude': self.latitude}
        return json.dumps(json_data)

    def __str__(self):
        return self.to_json()
