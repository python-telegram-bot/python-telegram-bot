#!/usr/bin/env python


class PhotoSize(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'file_id': None,
            'width': None,
            'height': None,
            'file_size': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        return PhotoSize(file_id=data.get('file_id', None),
                         width=data.get('width', None),
                         height=data.get('height', None),
                         file_size=data.get('file_size', None))
