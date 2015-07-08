#!/usr/bin/env python


class Document(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'file_id': None,
            'thumb': None,
            'file_name': None,
            'mime_type': None,
            'file_size': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def newFromJsonDict(data):
        if 'thumb' in data:
            from telegram import PhotoSize
            thumb = PhotoSize.newFromJsonDict(data['thumb'])
        else:
            thumb = None

        return Document(file_id=data.get('file_id', None),
                        thumb=thumb,
                        file_name=data.get('file_name', None),
                        mime_type=data.get('mime_type', None),
                        file_size=data.get('file_size', None))
