

import time
import telnetlib
import re

HOST = "10.61.207.22"
user = 'ecelousov'
password = 'egor@1'



tn = telnetlib.Telnet(HOST,23,1)

tn.read_until(b"user: ")
tn.write(user.encode('ascii') + b"\r")
if password:
    tn.read_until(b"pass: ")
    tn.write(password.encode('ascii') + b"\r")
    print('OK')

tn.write(b"\r")
tn.write(b"en\r")
tn.write(b"set pagelen 0\r")
tn.write(b"sh pack state\r")
tn.write(b"abr\r\r")
ap = tn.read_until(b"abr",5).decode('ascii')
#print(ap)
#with open ('log_for_cli.txt','w') as outfail:
#   outfail.write(log)    

#log = tn.read_until(b"abr",1).decode('ascii')

ActiveAPonShelf = re.findall(r'GP8 OLT-+(\d{0,2})',ap)
print (ActiveAPonShelf)
for i in ActiveAPonShelf:
    for j in range(1,9):
        J = str(j)
        tn.write(b"sh ont olt-"+i.encode("utf-8")+b"-"+J.encode("utf-8")+b" pon\r")
tn.write(b"abt\r\r")
test = tn.read_until(b"abt").decode('ascii')
#print(test)
#with open ('log_ont.txt','w') as outfail:
#    outfail.write(test)  
tn.close()
for i in ActiveAPonShelf:
    for j in range(1,9):
        SumONTforPON = re.findall(r'ONT-'+i,test)
        print ('OLT-2-'+j+':'+len(SumONTforPON))
        
    
#SumONTforPON = re.findall()
#SumONTforOLT = re.findall(r'ERSN',test)
#print('Total = ',len(SumONTforOLT))
