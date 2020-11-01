from get_mess import get_mes
import time
def update_file(): 
    a=get_mes()
    with open('user.txt','w') as f:
        for i in a:
            #f.write(str(i[0]))
            f.write(str(i[1]))
            f.write('\n')
i=1
while True:
    update_file()
    print(i)
    time.sleep(1)
    i+=1