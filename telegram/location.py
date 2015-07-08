#!/usr/bin/env python


class Location(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'longitude': None,
            'latitude': None,
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def newFromJsonDict(data):
        return Location(longitude=data.get('longitude', None),
                        latitude=data.get('latitude', None))
