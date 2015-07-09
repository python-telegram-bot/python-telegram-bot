#!/usr/bin/env python


class Document(object):
    def __init__(self,
                 file_id,
                 thumb,
                 file_name=None,
                 mime_type=None,
                 file_size=None):
        self.file_id = file_id
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

    @staticmethod
    def de_json(data):
        if 'thumb' in data:
            from telegram import PhotoSize
            thumb = PhotoSize.de_json(data['thumb'])
        else:
            thumb = None

        return Document(file_id=data.get('file_id', None),
                        thumb=thumb,
                        file_name=data.get('file_name', None),
                        mime_type=data.get('mime_type', None),
                        file_size=data.get('file_size', None))
