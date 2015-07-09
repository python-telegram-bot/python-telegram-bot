#!/usr/bin/env python


class Video(object):
    def __init__(self,
                 file_id,
                 width,
                 height,
                 duration,
                 thumb,
                 mime_type=None,
                 file_size=None,
                 caption=None):
        self.file_id = file_id
        self.width = width
        self.height = height
        self.duration = duration
        self.thumb = thumb
        self.mime_type = mime_type
        self.file_size = file_size
        self.caption = caption

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
