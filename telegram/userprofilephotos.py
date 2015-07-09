#!/usr/bin/env python


class UserProfilePhotos(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'total_count': None,
            'photos': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

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
