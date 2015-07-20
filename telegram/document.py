#!/usr/bin/env python


from telegram import TelegramObject


class Document(TelegramObject):
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

    def to_dict(self):
        data = {'file_id': self.file_id}
        if self.thumb:
            data['thumb'] = self.thumb.to_dict()
        if self.file_name:
            data['file_name'] = self.file_name
        if self.mime_type:
            data['mime_type'] = self.mime_type
        if self.file_size:
            data['file_size'] = self.file_size
        return data
