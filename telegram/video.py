#!/usr/bin/env python


from telegram import TelegramObject


class Video(TelegramObject):
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

    def to_dict(self):
        data = {'file_id': self.file_id,
                'width': self.width,
                'height': self.height,
                'duration': self.duration}
        if self.thumb:
            data['thumb'] = self.thumb.to_dict()
        if self.mime_type:
            data['mime_type'] = self.mime_type
        if self.file_size:
            data['file_size'] = self.file_size
        if self.caption:
            data['caption'] = self.caption
        return data
