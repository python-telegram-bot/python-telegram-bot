#!/usr/bin/env python


class Sticker(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'file_id': None,
            'width': None,
            'height': None,
            'thumb': None,
            'file_size': None
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

        return Sticker(file_id=data.get('file_id', None),
                       width=data.get('width', None),
                       height=data.get('height', None),
                       thumb=thumb,
                       file_size=data.get('file_size', None))
