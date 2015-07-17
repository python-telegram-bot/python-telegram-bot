#!/usr/bin/env python


import json
from .telegram_boject_base import Base


class Sticker(Base):
    def __init__(self,
                 file_id,
                 width,
                 height,
                 thumb,
                 file_size=None):
        self.file_id = file_id
        self.width = width
        self.height = height
        self.thumb = thumb
        self.file_size = file_size

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

    def to_json(self):
        json_data = {'file_id': self.file_id,
                     'width': self.width,
                     'height': self.height,
                     'thumb': self.thumb.to_json()}
        if self.file_size:
            json_data['file_size'] = self.file_size
        return json.dumps(json_data)