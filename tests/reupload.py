import logging
import sys

sys.path.append('.')

import telegram
from tests.bots import get_bot

logger = logging.getLogger('tests.reupload')

bot_data = get_bot()
bot = telegram.Bot(bot_data['token'])

FILES = {
    'audio': {
        'file': 'telegram.mp3',
        'url': 'https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/tests/data/telegram.mp3'
    }
}

sent_files = {file_type: {t: None for t, file in files.items()} for file_type, files in
              FILES.items()}


def reupload(file_type):
    for t, file in FILES[file_type].items():
        file = file if t == 'url' else open('tests/data/' + file, 'rb')
        msg = getattr(bot, 'send_' + file_type)(bot_data['chat_id'], file)
        sent_files[file_type][t] = getattr(msg, file_type)


def get_file_id(file_type, url=False, thumb=False):
    file = sent_files[file_type]['url' if url else 'file']
    if file is None:
        reupload(file_type)
        return get_file_id(file_type, url, thumb)
    if thumb:
        file = file.thumb
    return file.file_id
