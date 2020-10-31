from InstagramAPI import InstagramAPI
import time
from datetime import datetime
import requests
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# sign in 
API = InstagramAPI("tnt12dck", "nguyenhnam")
API.login()
#get user id

# usrname='tnt12dck'
# API.searchUsername(usrname)
# usr_id=API.LastJson['user']['pk']
# #get user followings
# API.getUserFollowers(usr_id)
# fl=API.LastJson['users']
# print(API.LastJson['users'][0]['username'])
#----------------------------------------------------- testing block
#put result in list
'''
k=1
list_following=set()
list_following_full=[]
for i in fl:
    print('{}. '.format(k) + i['username'])
    list_following.add(i['username'])
    list_following_full.append(str(i))
    k+=1
print(type(fl))    
print(fl[0]['username'])
#--------------------------------------------------------
'''
def get_latest_follower(list_1):
    latest_follower_list=[]
    for i in list_1:
        API.searchUsername(i)
        # print(API.LastJson['user']['pk'])
        uid=API.LastJson['user']['pk']
        #get user followings
        API.getUserFollowers(uid)
        latest_follower_list.append(API.LastJson['users'][0]['username'])
    return latest_follower_list

def check_follower_step2(list_1):
    check_in=[]
    for i in list_1:
        API.searchUsername(i)
        # print(API.LastJson['user']['pk'])
        uid=API.LastJson['user']['pk']
        #get user followings
        API.getUserFollowers(uid)
        check_in.append(str(API.LastJson['users']).find(i))
    return check_in
# list 1 is target user given to user who call '/list' command
def check_follow_yet(list1): 
    tmp = get_latest_follower(list1)
    print(tmp)
    tmp=set(tmp)
    if len(tmp) == 1:
        print('acceptable')
        return 1
    else:   
        print('inacceptable !!! check step-2')
        tmp2=set(check_follower_step2(list1))
        if len(tmp2) == 1:
            print('acceptable')
            return 1
    return 0
def check_profile(profile):
    if API.searchUsername(profile):
        return 1
    else:
        return 0
