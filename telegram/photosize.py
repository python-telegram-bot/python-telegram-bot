#!/usr/bin/env python


class PhotoSize(object):
    def __init__(self,
                 file_id,
                 width,
                 height,
                 file_size=None):
        self.file_id = file_id
        self.width = width
        self.height = height
        self.file_size = file_size

    @staticmethod
    def de_json(data):
        return PhotoSize(file_id=data.get('file_id', None),
                         width=data.get('width', None),
                         height=data.get('height', None),
                         file_size=data.get('file_size', None))
