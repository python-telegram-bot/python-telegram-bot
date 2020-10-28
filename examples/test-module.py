from get_mess import get_mes

from telethon.tl.types import InputMessagesFilterUrl
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.messages import GetHistoryRequest
import datetime
from telethon.tl.types.messages import ChannelMessages
from telethon.tl.functions.messages import GetMessagesRequest
api_id = 1289229
api_hash = 'bd7544a4727e8b03f5a7698dbf4394e5'
phone = '+84368195865'

bot = TelegramClient('hoai97nambot', api_id, api_hash).start(bot_token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')

bot.get_messages('Tettt',10,filter=InputMessagesFilterUrl)

# for message in bot.iter_messages('Testbot2',10,filter=InputMessagesFilterUrl):
#     print(type(message.text), message.text)
# bot.send_message('n681997', 'https://www.instagram.com/p/CGuJYr1pOpd')



# a=get_mes()
# print(a)