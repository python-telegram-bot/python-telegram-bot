from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.sync import TelegramClient
import asyncio
from telethon.tl.types import InputMessagesFilterUrl

api_id = 1289229
api_hash = 'bd7544a4727e8b03f5a7698dbf4394e5'
phone = '+84368195865'
client = TelegramClient(phone, api_id, api_hash)
'''
client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))
for dialog in client.iter_dialogs():
    pass
##    print(dialog.name, 'has ID', dialog.id)
# get message and extract from other groups
'''

def get_mes():   
    client.connect()
    mess=[]
    for message in client.iter_messages('Testbot2',10,filter=InputMessagesFilterUrl):
        m=[]
        #print(message.text.split(" ")[-1])
        tmp=message.text.split(" ")[-1]
        m.append(tmp[1:tmp.find('](')+1])
        m.append(tmp[tmp.find('](')+2:tmp.find('))')])
        mess.append(m)
    return mess

'''
def get_id():
    for dialog in client.iter_dialogs():
        print(dialog.name, 'has id ',dialog.id)
#get messages from my group
def get_mes2():   
    client.connect()
    mess=[]
    for message in client.iter_messages('Testbot2',10,filter=InputMessagesFilterUrl):
        m=[]
        print(message.text)
        tmp=message.text.split(" ")
        m.append(tmp[1])
        m.append(tmp[4])
        mess.append(m)
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

# print(get_mes2())
#print('-------------------------')
# t='@'+a[6:a.find(']')]
# # client.send_message('Testbot2',t)
# # client.send_message('Testbot2',a[a.find('](')+2:a.find('))')])
# print(a[6:a.find(']')])
# print(a[a.find('](')+2:a.find('))')])

print(get_mes())
a=get_mes()
lit=[]
for i in a:
    c=i[1]
    lit.append(c[c.find('com/')+4:])

'''
