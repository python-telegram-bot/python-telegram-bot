#!/usr/bin/env python


class Audio(object):
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
