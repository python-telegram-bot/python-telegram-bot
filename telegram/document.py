#!/usr/bin/env python


import json
from .telegram_boject_base import Base


class Document(Base):
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

    def to_json(self):
        json_data = {'file_id': self.file_id,
                     'thumb': self.thumb.to_json()}
        if self.file_name:
            json_data['file_name'] = self.file_name
        if self.mime_type:
            json_data['mime_type'] = self.mime_type
        if self.file_size:
            json_data['file_size'] = self.file_size
        return json.dumps(json_data)