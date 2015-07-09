#!/usr/bin/env python


class Video(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'file_id': None,
            'width': None,
            'height': None,
            'duration': None,
            'thumb': None,
            'mime_type': None,
            'file_size': None,
            'caption': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def de_json(data):
        if 'thumb' in data:
            from telegram import PhotoSize
            thumb = PhotoSize.de_json(data['thumb'])
        else:
            thumb = None

        return Video(file_id=data.get('file_id', None),
                     width=data.get('width', None),
                     height=data.get('height', None),
                     duration=data.get('duration', None),
                     thumb=thumb,
                     mime_type=data.get('mime_type', None),
                     file_size=data.get('file_size', None),
                     caption=data.get('caption', None))
