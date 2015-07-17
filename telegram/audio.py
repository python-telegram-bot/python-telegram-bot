#!/usr/bin/env python


import json
from .telegram_boject_base import Base


class Audio(Base):
    def __init__(self,
                 file_id,
                 duration,
                 mime_type=None,
                 file_size=None):
        self.file_id = file_id
        self.duration = duration
        self.mime_type = mime_type
        self.file_size = file_size

    @staticmethod
    def de_json(data):
        return Audio(file_id=data.get('file_id', None),
                     duration=data.get('duration', None),
                     mime_type=data.get('mime_type', None),
                     file_size=data.get('file_size', None))

    def to_json(self):
        json_data = {'file_id': self.file_id,
                     'duration': self.duration}
        if self.mime_type:
            json_data['mime_type'] = self.mime_type
        if self.file_size:
            json_data['file_size'] = self.file_size
        return json.dumps(json_data)
