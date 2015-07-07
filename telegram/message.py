#!/usr/bin/env python


class Message(object):
    def __init__(self, **kwargs):
        param_defaults = {
            'message_id': None,
            'user': None,
            'date': None,
            'chat': None,
            'forward_from': None,
            'forward_date': None,
            'reply_to_message': None,
            'text': None,
            'audio': None,
            'document': None,
            'photo': None,
            'sticker': None,
            'video': None,
            'contact': None,
            'location': None,
            'new_chat_participant': None,
            'left_chat_participant': None,
            'new_chat_title': None,
            'new_chat_photo': None,
            'delete_chat_photo': None,
            'group_chat_created': None
        }

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    @staticmethod
    def newFromJsonDict(data):
        if 'from' in data:  # from on api
            from telegram import User
            user = User.newFromJsonDict(data['from'])
        else:
            user = None

        if 'chat' in data:
            if 'username' in data['chat']:
                from telegram import User
                chat = User.newFromJsonDict(data['chat'])
            if 'title' in data['chat']:
                from telegram import GroupChat
                chat = GroupChat.newFromJsonDict(data['chat'])
        else:
            chat = None

        if 'forward_from' in data:
            from telegram import User
            forward_from = User.newFromJsonDict(data['forward_from'])
        else:
            forward_from = None

        if 'reply_to_message' in data:
            reply_to_message = Message.newFromJsonDict(
                data['reply_to_message']
            )
        else:
            reply_to_message = None

        if 'audio' in data:
            from telegram import Audio
            audio = Audio.newFromJsonDict(data['audio'])
        else:
            audio = None

        if 'photo' in data:
            from telegram import PhotoSize
            photo = [PhotoSize.newFromJsonDict(x) for x in data['photo']]
        else:
            photo = None

        if 'new_chat_participant' in data:
            from telegram import User
            new_chat_participant = User.newFromJsonDict(
                data['new_chat_participant']
            )
        else:
            new_chat_participant = None

        if 'left_chat_participant' in data:
            from telegram import User
            left_chat_participant = User.newFromJsonDict(
                data['left_chat_participant']
            )
        else:
            left_chat_participant = None

        return Message(message_id=data.get('message_id', None),
                       user=user,
                       date=data.get('date', None),
                       chat=chat,
                       forward_from=forward_from,
                       forward_date=data.get('forward_date', None),
                       reply_to_message=reply_to_message,
                       text=data.get('text', None),
                       audio=audio,
                       document=data.get('document', None),
                       photo=photo,
                       sticker=data.get('sticker', None),
                       video=data.get('video', None),
                       contact=data.get('contact', None),
                       location=data.get('location', None),
                       new_chat_participant=new_chat_participant,
                       left_chat_participant=left_chat_participant,
                       new_chat_title=data.get('new_chat_title', None),
                       new_chat_photo=data.get('new_chat_photo', None),
                       delete_chat_photo=data.get('delete_chat_photo', None),
                       group_chat_created=data.get('group_chat_created', None))
