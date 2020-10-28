from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.sync import TelegramClient
import csv
from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterUrl

api_id = 1289229
api_hash = 'bd7544a4727e8b03f5a7698dbf4394e5'
phone = '+84368195865'
client = TelegramClient(phone, api_id, api_hash)
client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))
for dialog in client.iter_dialogs():
    pass
##    print(dialog.name, 'has ID', dialog.id)

def get_mes():
    
    client.connect()
    mess=[]
    i=1
    for message in client.iter_messages('[Dx5] BoostGram | L+C',10,filter=InputMessagesFilterUrl):
        print(type(message.text), message.text)
        mess.append('{}. '.format(i) + (message.text).split(" ")[-1])
        i+=1
    return mess
def get_new_mes():
    client.connect()
    mess=list(client.iter_messages('[Dx5] BoostGram | L+C',1,filter=InputMessagesFilterUrl))
    print('get_new_mess ',mess[0].message,'\n',((mess[0].text).split(" "))[-1])   

def get_chat_mem():
    mess=list(client.iter_messages('Testbot2',1))
    print('get_new_mess ',mess[0].from_id,'\n')

# get_chat_member
def return_list():
    a=get_mes()
    for i in a:
        print(i)

# get_chat_mem()
'''
return_list()
import time
while True:
    
    a=get_mes()
    b='.\n'+a[0]+'\n.'
    client.send_message('Testbot2',a[0])
    time.sleep(15*60)
'''