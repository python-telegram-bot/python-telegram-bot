#!/usr/bin/env python


import json


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

    def to_json(self):
        json_data = {'file_id': self.file_id,
                     'width': self.width,
                     'height': self.height}
        if self.file_size:
            json_data['file_size'] = self.file_size
        return json.dumps(json_data)

    def __str__(self):
        return self.to_json()
