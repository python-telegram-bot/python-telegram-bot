#!/usr/bin/env python


import json
from .telegram_boject_base import Base


class UserProfilePhotos(Base):
    def __init__(self,
                 total_count,
                 photos):
        self.total_count = total_count
        self.photos = photos

    @staticmethod
    def de_json(data):
        if 'photos' in data:
            from telegram import PhotoSize
            photos = []
            for photo in data['photos']:
                photos.append([PhotoSize.de_json(x) for x in photo])
        else:
            photos = None

        return UserProfilePhotos(total_count=data.get('total_count', None),
                                 photos=photos)

    def to_json(self):
        json_data = {}
        if self.total_count:
            json_data['total_count'] = self.total_count
        if self.photos:
            json_data['photos'] = []
            for photo in self.photos:
                json_data['photos'].append([x.to_json() for x in photo])
        return json.dumps(json_data)