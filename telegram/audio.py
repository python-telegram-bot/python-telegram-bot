#!/usr/bin/env python


class Audio(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'file_id': None,
            'duration': None,
            'mime_type': None,
            'file_size': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def newFromJsonDict(data):
        return Audio(file_id=data.get('file_id', None),
                         duration=data.get('duration', None),
                         mime_type=data.get('mime_type', None),
                         file_size=data.get('file_size', None))
