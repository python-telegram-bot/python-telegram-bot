#!/usr/bin/env python


from telegram import TelegramObject


class UserProfilePhotos(TelegramObject):
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

    def to_dict(self):
        data = {}
        if self.total_count:
            data['total_count'] = self.total_count
        if self.photos:
            data['photos'] = []
            for photo in self.photos:
                data['photos'].append([x.to_dict() for x in photo])
        return data
