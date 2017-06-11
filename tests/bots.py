import sys

sys.path.append('.')

import telegram

bots = [
    {
        'token': '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0',
        'chat_id': '12173560',
        'group_id': '-49740850',
        'channel_id': '@pythontelegrambottests',
        'payment_provider_token': '284685063:TEST:ZGJlMmQxZDI3ZTc3',
        'user': telegram.User(133505823, 'PythonTelegramBot', username='PythonTelegramBot')
    }
]


def get_bot():
    return bots[0]
